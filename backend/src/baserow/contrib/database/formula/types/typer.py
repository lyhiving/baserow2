from copy import deepcopy
from typing import List, Dict, Optional, Set

from django.db import connection

from baserow.contrib.database.fields.field_converters import FormulaFieldConverter
from baserow.contrib.database.fields.models import (
    Field,
    FormulaField,
)
from baserow.contrib.database.fields.registries import field_type_registry, FieldType
from baserow.contrib.database.formula.ast.tree import (
    BaserowStringLiteral,
    BaserowFieldByIdReference,
    BaserowFieldReference,
    BaserowExpression,
)
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
    replace_field_refs_according_to_new_or_deleted_fields,
)
from baserow.contrib.database.formula.parser.errors import MaximumFormulaSizeError
from baserow.contrib.database.formula.registries import formula_type_handler_registry
from baserow.contrib.database.formula.types.errors import (
    NoCircularReferencesError,
    NoSelfReferencesError,
)
from baserow.contrib.database.formula.types.type_handler import (
    BaserowFormulaTypeHandler,
)
from baserow.contrib.database.formula.types.type_types import (
    BaserowFormulaType,
    BaserowFormulaInvalidType,
    BaserowFormulaValidType,
    UnTyped,
)
from baserow.contrib.database.formula.types.visitors import (
    FieldReferenceResolvingVisitor,
    TypeAnnotatingASTVisitor,
    SubstituteFieldByIdWithThatFieldsExpressionVisitor,
)
from baserow.contrib.database.table import models


class Typer:
    @classmethod
    def type_table_and_update_fields_given_changed_field(
        cls, table: "models.Table", changed_field: Field
    ) -> "Typer":
        return Typer(
            table,
            changed_field=changed_field,
            deleted_field_id_to_name={},
            do_update=True,
        )

    @classmethod
    def type_table_and_update_fields_given_deleted_field(
        cls, table: "models.Table", deleted_field_id: int, deleted_field_name: str
    ):
        return Typer(
            table,
            changed_field=None,
            deleted_field_id_to_name={deleted_field_id: deleted_field_name},
            do_update=True,
        )

    @classmethod
    def type_table(cls, table):
        return Typer(
            table,
            changed_field=None,
            deleted_field_id_to_name={},
            do_update=False,
        )

    def __init__(
        self,
        table: "models.Table",
        changed_field: Optional[Field],
        deleted_field_id_to_name: Dict[int, str],
        do_update=False,
    ):
        self.changed_field = changed_field
        self.table = table
        self.deleted_field_id_to_name = deleted_field_id_to_name
        self._construct_all_fields()
        self.formula_field_ids: List[int] = []
        self.typed_field_expressions: Dict[
            int, BaserowExpression[BaserowFormulaType]
        ] = {}
        self.field_references: Dict[int, List[int]] = {}
        self.field_parents: Dict[int, Set[int]] = {}
        self.untyped_formula_expressions: Dict[int, BaserowExpression[UnTyped]] = {}
        self.fixed_formula_strings = {}

        self._run_type_table()
        if do_update:
            self.updated_fields = self._calculate_and_save_updated_fields(changed_field)
        else:
            self.updated_fields = []

    def get_model(self):
        return self.table.get_model(
            field_ids=[],
            fields=[self.field_id_to_field[self.changed_field.id]]
            + self.updated_fields,
            typer=self,
        )

    def _construct_all_fields(self):
        self.all_fields = []
        self.field_id_to_field = {}
        self.field_name_to_id = {}
        for field in self.table.field_set.all():
            field = field.specific
            self.all_fields.append(field)
            self.field_id_to_field[field.id] = field
            self.field_name_to_id[field.name] = field.id

    def _run_type_table(self):
        try:
            for field in self.all_fields:
                specific_class = field.specific_class
                field_type = field_type_registry.get_by_model(specific_class)
                if field_type.type == "formula":
                    self._generate_formula_expression_and_references(field)
                else:
                    self._calculate_non_formula_field_type(field)

            check_for_self_references(self.field_references)

            formula_field_ids_ordered_by_typing_order = (
                self._calculate_formula_field_type_resolution_order()
            )
            for formula_field_id in formula_field_ids_ordered_by_typing_order:
                self._type_and_substitute_formula_field(formula_field_id)
        except RecursionError:
            raise MaximumFormulaSizeError()

    def _type_and_substitute_formula_field(self, formula_field_id):
        typed_expr = self._type_formula_fields_expression(formula_field_id)
        self._apply_user_formatting_type_overrides(formula_field_id, typed_expr)
        typed_expr_with_substituted_field_by_id_references = typed_expr.accept(
            SubstituteFieldByIdWithThatFieldsExpressionVisitor(
                self.typed_field_expressions
            )
        )
        self.typed_field_expressions[
            formula_field_id
        ] = typed_expr_with_substituted_field_by_id_references

    def _type_formula_fields_expression(
        self, formula_field_id: int
    ) -> BaserowExpression[BaserowFormulaType]:
        untyped_expr = self.untyped_formula_expressions[formula_field_id]
        return untyped_expr.accept(
            TypeAnnotatingASTVisitor(self.typed_field_expressions)
        )

    def _apply_user_formatting_type_overrides(self, formula_field_id, typed_expr):
        formula_field = self.field_id_to_field[formula_field_id]
        expression_type_handler: BaserowFormulaTypeHandler = (
            formula_type_handler_registry.get_by_model(typed_expr.expression_type)
        )
        expression_type_handler.overwrite_type_options_with_user_defined_ones(
            typed_expr.expression_type, formula_field
        )

    def _check_if_formula_type_change_requires_drop_recreate(
        self, old_formula_field: FormulaField, new_type: BaserowFormulaType
    ):
        old_formula_field_type = old_formula_field.formula_type
        old_handler: BaserowFormulaTypeHandler = formula_type_handler_registry.get(
            old_formula_field_type
        )
        old_type = old_handler.construct_type_from_formula_field(old_formula_field)
        return new_type.should_recreate_when_old_type_was(old_type)

    def _generate_formula_expression_and_references(self, field):
        self.formula_field_ids.append(field.id)
        fixed_formula = replace_field_refs_according_to_new_or_deleted_fields(
            field.formula, self.deleted_field_id_to_name, self.field_name_to_id
        )
        untyped_expression = raw_formula_to_untyped_expression(fixed_formula)
        self.fixed_formula_strings[field.id] = fixed_formula
        children = untyped_expression.accept(FieldReferenceResolvingVisitor())
        self.field_references[field.id] = children
        for child in children:
            parents = self.field_parents.setdefault(child, set())
            parents.add(field.id)
        self.untyped_formula_expressions[field.id] = untyped_expression

    def _calculate_non_formula_field_type(self, field):
        field_type: FieldType = field_type_registry.get_by_model(field)
        formula_type = field_type.to_baserow_formula_type(field)
        typed_expr = BaserowFieldByIdReference[BaserowFormulaValidType](
            field.id, formula_type
        )
        self.typed_field_expressions[field.id] = typed_expr
        self.field_references[field.id] = []

    def calculate_all_child_fields(self, field, field_ids_to_ignore):
        fields_to_check = [field]
        extra_fields = []
        while len(fields_to_check) > 0:
            field = fields_to_check.pop(0)
            references = self.field_references[field.id]
            for ref in references:
                if ref not in field_ids_to_ignore:
                    new_field = self.field_id_to_field[ref]
                    extra_fields.append(new_field)
                    field_ids_to_ignore.add(ref)
                    fields_to_check.append(new_field)
        return extra_fields

    def _calculate_and_save_updated_fields(self, field_which_changed=None):
        other_changed_fields = set()
        for formula_field_id in self.formula_field_ids:
            typed_formula_expression = self.typed_field_expressions[formula_field_id]
            # noinspection PyTypeChecker
            specific_formula_field: FormulaField = self.field_id_to_field[
                formula_field_id
            ]

            old_field: FormulaField = deepcopy(specific_formula_field)
            specific_formula_field.formula = self.fixed_formula_strings[
                specific_formula_field.id
            ]
            formula_field_type = typed_formula_expression.expression_type
            self._fix_field_formula_and_persist_new_type_info(
                formula_field_type, specific_formula_field
            )

            checking_field_which_changed = (
                field_which_changed is not None
                and field_which_changed.id == specific_formula_field.id
            )
            if checking_field_which_changed:
                formula_field_type.raise_if_invalid()

            if not (specific_formula_field.compare(old_field)):
                specific_formula_field.save()
                if not checking_field_which_changed:
                    other_changed_fields.add(specific_formula_field)
                    self._recreate_field_if_required(
                        old_field, formula_field_type, specific_formula_field
                    )

        if field_which_changed is not None:
            # All fields that depend on the field_which_changed need to have their
            # values recalculated as a result, even if their formula or type did not
            # change as a result.
            parent_fields = self.calculate_all_parent_valid_fields(field_which_changed)
            return list(other_changed_fields.union(parent_fields))
        else:
            return list(other_changed_fields)

    def _recreate_field_if_required(
        self,
        old_field: FormulaField,
        new_type: BaserowFormulaType,
        new_formula_field: FormulaField,
    ):
        if self._check_if_formula_type_change_requires_drop_recreate(
            old_field, new_type
        ):
            model = self.table.get_model(fields=[new_formula_field], typer=False)
            FormulaFieldConverter().alter_field(
                old_field,
                new_formula_field,
                model,
                model,
                model._meta.get_field(old_field.db_column),
                model._meta.get_field(new_formula_field.db_column),
                None,
                connection,
            )

    def _fix_field_formula_and_persist_new_type_info(
        self, formula_type, specific_formula_field
    ):
        formula_type_handler: BaserowFormulaTypeHandler = (
            formula_type_handler_registry.get_by_model(formula_type)
        )
        formula_type_handler.persist_onto_formula_field(
            formula_type, specific_formula_field
        )

    def get_type(self, field: Field) -> BaserowFormulaType:
        return self.typed_field_expressions[field.id].expression_type

    def _calculate_all_parent_field_ids(self, field_id):
        initial_parents = self.field_parents.get(field_id, [])
        related_field_ids = set(initial_parents)
        parents_to_check = list(initial_parents)
        while len(parents_to_check) > 0:
            parent_id = parents_to_check.pop(0)
            parents = self.field_parents.get(parent_id, [])
            for parent in parents:
                related_field_ids.add(parent)
                related_field_ids.update(self._calculate_all_parent_field_ids(parent))
        return related_field_ids

    def calculate_all_parent_valid_fields(self, field):
        related_field_ids = self._calculate_all_parent_field_ids(field.id)
        return {
            self.field_id_to_field[i]
            for i in related_field_ids
            if i in self.typed_field_expressions
            and self.typed_field_expressions[i].expression_type.is_valid
        }

    def _calculate_formula_field_type_resolution_order(self):
        ordered_formula_fields = []
        unvisited_formula_fields = self.formula_field_ids.copy()
        while len(unvisited_formula_fields) > 0:
            new_starting_formula = unvisited_formula_fields[0]
            self._find_and_order_child_formula_fields_using_depth_first_search(
                new_starting_formula,
                [],
                unvisited_formula_fields,
                ordered_formula_fields,
            )
        return ordered_formula_fields

    def _find_and_order_child_formula_fields_using_depth_first_search(
        self,
        current_field,
        visited_field_names,
        unvisited_formula_fields,
        ordered_formula_fields,
    ):
        if current_field in self.formula_field_ids:
            new_visited_field_names = visited_field_names.copy()
            new_visited_field_names.append(current_field)
            if current_field in visited_field_names:
                raise NoCircularReferencesError(
                    [self.field_id_to_field[i].name for i in new_visited_field_names]
                )
            if current_field in unvisited_formula_fields:
                unvisited_formula_fields.remove(current_field)
            for ref in self.field_references[current_field]:
                # By recursively calling the search on our children, their children
                # will be added before this field in the ordered list, resulting in
                # the correct field type resolution order.
                self._find_and_order_child_formula_fields_using_depth_first_search(
                    ref,
                    new_visited_field_names,
                    unvisited_formula_fields,
                    ordered_formula_fields,
                )
            if current_field not in ordered_formula_fields:
                ordered_formula_fields.append(current_field)

    def trigger_related_field_changed_for_updated_fields(self, to_model):
        for updated_field in self.updated_fields:
            updated_field_type = field_type_registry.get_by_model(updated_field)
            updated_field_type.related_field_changed(updated_field, to_model)


def check_for_self_references(all_field_references):
    for field_db_cloumn, field_references in all_field_references.items():
        if field_db_cloumn in field_references:
            raise NoSelfReferencesError()
