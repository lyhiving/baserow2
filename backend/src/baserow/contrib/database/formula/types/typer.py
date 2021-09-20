from copy import deepcopy
from typing import List, Dict, Optional, Set

from django.db import connection

from baserow.contrib.database.fields.field_converters import FormulaFieldConverter
from baserow.contrib.database.fields.models import (
    Field,
    FormulaField,
)
from baserow.contrib.database.fields.registries import field_type_registry, FieldType
from baserow.contrib.database.formula.ast.errors import (
    NoSelfReferencesError,
    NoCircularReferencesError,
    InvalidFieldType,
)
from baserow.contrib.database.formula.ast.tree import (
    BaserowStringLiteral,
    BaserowFieldByIdReference,
    BaserowFieldReference,
    BaserowExpression,
)
from baserow.contrib.database.formula.types.type_defs import (
    BASEROW_FORMULA_TYPE_ALLOWED_FIELDS,
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
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
    replace_field_refs_according_to_new_or_deleted_fields,
)
from baserow.contrib.database.formula.parser.errors import MaximumFormulaSizeError
from baserow.contrib.database.formula.registries import formula_type_handler_registry
from baserow.contrib.database.table import models


class Typer:
    def __init__(
        self,
        table: "models.Table",
        field_override: Optional[Field] = None,
        new_field: Optional[Field] = None,
        deleted_field_id_names: Optional[Dict[int, str]] = None,
        new_field_names_to_id: Optional[Dict[str, int]] = None,
    ):
        if deleted_field_id_names is None:
            deleted_field_id_names: Dict[int, str] = {}
        self.deleted_field_id_names = deleted_field_id_names
        if new_field_names_to_id is None:
            new_field_names_to_id: Dict[str, int] = {}
        self.new_field_names_to_id = new_field_names_to_id
        self.all_fields: List[Field] = [
            f for f in table.field_set(manager="objects_and_trash").all()
        ]
        if field_override:
            new_all_fields = []
            for field in self.all_fields:
                if field.id == field_override.id:
                    new_all_fields.append(field_override)
                else:
                    new_all_fields.append(field)
            self.all_fields = new_all_fields
        if new_field is not None:
            self.all_fields.append(new_field)
        self.formula_field_ids: List[int] = []
        self.typed_field_expressions: Dict[
            int, BaserowExpression[BaserowFormulaType]
        ] = {}
        self.field_references: Dict[int, List[int]] = {}
        self.field_parents: Dict[int, Set[int]] = {}
        self.untyped_formula_expressions: Dict[int, BaserowExpression[UnTyped]] = {}
        self.field_id_to_field: Dict[int, Field] = {
            f.id: f.specific for f in self.all_fields
        }
        self.table = table

        self.type_table()

    def type_table(self):
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
                self._fix_and_type_and_substitute_formula_field(formula_field_id)
        except RecursionError:
            raise MaximumFormulaSizeError()

    def _fix_and_type_and_substitute_formula_field(self, formula_field_id):
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

    def _required_drop_recreate(self, old_formula_field, new_formula_field):
        # TODO
        old_formula_field_type = old_formula_field.formula_type
        new_formula_field_type = new_formula_field.formula_type
        if new_formula_field_type != old_formula_field_type:
            return True
        if new_formula_field == "number":
            return (
                new_formula_field.number_decimal_places
                != old_formula_field.number_decimal_places
            )
        elif new_formula_field == "date":
            return (
                new_formula_field.date_include_time
                != old_formula_field.date_include_time
            )
        return False

    def _fix_formulas_referencing_new_or_deleted_fields(self, formula_field):
        formula_field_id = formula_field.id
        reference_fields_set = set(self.field_references[formula_field_id])
        deleted_fields_set = set(self.deleted_field_id_names.keys())
        new_fields_set = set(self.new_field_names_to_id.values())
        formula_field_references_deleted_field = (
            len(reference_fields_set.intersection(deleted_fields_set)) > 0
        )
        formula_field_references_new_field = (
            len(reference_fields_set.intersection(new_fields_set))
        ) > 0
        if formula_field_references_deleted_field or formula_field_references_new_field:
            specific_formula_field = self.field_id_to_field[formula_field_id]
            new_formula = replace_field_refs_according_to_new_or_deleted_fields(
                specific_formula_field.formula,
                self.deleted_field_id_names,
                self.new_field_names_to_id,
            )
            specific_formula_field.formula = new_formula

    def _generate_formula_expression_and_references(self, field):
        self.formula_field_ids.append(field.id)
        if field.trashed or field.id in self.deleted_field_id_names:
            untyped_expression = BaserowFieldReference[UnTyped](
                BaserowStringLiteral(field.name, None), None
            )
            self.deleted_field_id_names[field.id] = field.name
        else:
            untyped_expression = raw_formula_to_untyped_expression(
                field.specific.formula,
                self.field_id_to_field,
                self.new_field_names_to_id,
            )
        children = untyped_expression.accept(FieldReferenceResolvingVisitor())
        self.field_references[field.id] = children
        for child in children:
            parents = self.field_parents.setdefault(child, set())
            parents.add(field.id)
        self.untyped_formula_expressions[field.id] = untyped_expression

    def _calculate_non_formula_field_type(self, field):
        if field.trashed:
            typed_expr = BaserowFieldReference(
                field.name,
                BaserowFormulaInvalidType(f"Field {field.name} is deleted"),
            )
            self.deleted_field_id_names[field.id] = field.name
        elif field.id in self.deleted_field_id_names:
            name = self.deleted_field_id_names[field.id]
            typed_expr = BaserowFieldReference(
                name, BaserowFormulaInvalidType(f"Field {name} is deleted")
            )
        else:
            specific_field = field.specific
            field_type: FieldType = field_type_registry.get_by_model(specific_field)
            formula_type = field_type.to_baserow_formula_type(specific_field)
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

    def update_fields(self, field_which_changed=None, be_strict=True):
        if field_which_changed is not None:
            self._update_field_type(field_which_changed, be_strict)
            field_which_changed.save()
        updated_fields = set()
        for formula_field_id in self.formula_field_ids:
            typed_formula_expression = self.typed_field_expressions[formula_field_id]
            # noinspection PyTypeChecker
            specific_formula_field: FormulaField = self.field_id_to_field[
                formula_field_id
            ]
            if specific_formula_field.trashed:
                continue
            old_field: FormulaField = deepcopy(specific_formula_field)

            formula_field_type = typed_formula_expression.expression_type
            self._update_field(formula_field_type, specific_formula_field)

            if not specific_formula_field.trashed and not (
                specific_formula_field.compare(old_field)
            ):
                if (
                    field_which_changed is None
                    or specific_formula_field.id != field_which_changed.id
                ):
                    specific_formula_field.save()
                    updated_fields.add(specific_formula_field)
                    self._recreate_field_if_required(old_field, specific_formula_field)

        if field_which_changed is not None:
            parent_fields = self.calculate_all_parent_valid_fields(field_which_changed)
            return list(updated_fields.union(parent_fields))
        else:
            return list(updated_fields)

    def _recreate_field_if_required(self, old_field, specific_formula_field):
        if self._required_drop_recreate(old_field, specific_formula_field):
            model = self.table.get_model(fields=[specific_formula_field], typer=False)
            FormulaFieldConverter().alter_field(
                old_field,
                specific_formula_field,
                model,
                model,
                model._meta.get_field(old_field.db_column),
                model._meta.get_field(specific_formula_field.db_column),
                None,
                connection,
            )

    def _update_field(self, formula_type, specific_formula_field):
        self._fix_formulas_referencing_new_or_deleted_fields(specific_formula_field)
        formula_type_handler: BaserowFormulaTypeHandler = (
            formula_type_handler_registry.get_by_model(formula_type)
        )
        formula_type_handler.persist_onto_formula_field(
            formula_type, specific_formula_field
        )

    def get_type(self, field: Field) -> BaserowFormulaType:
        return self.typed_field_expressions[field.id].expression_type

    def _update_field_type(self, field: Field, be_strict):
        specific_formula_field = field.specific
        # TODO Get rid of this isinstance somehow
        if isinstance(specific_formula_field, FormulaField):
            typed_formula_expression = self.get_type(field)
            formula_type = typed_formula_expression
            # TODO Get rid of this isinstance somehow
            if isinstance(formula_type, BaserowFormulaInvalidType) and be_strict:
                raise InvalidFieldType(formula_type.error)
            self._update_field(formula_type, specific_formula_field)
            for attr in BASEROW_FORMULA_TYPE_ALLOWED_FIELDS:
                setattr(field, attr, getattr(specific_formula_field, attr))

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


def check_for_self_references(all_field_references):
    for field_db_cloumn, field_references in all_field_references.items():
        if field_db_cloumn in field_references:
            raise NoSelfReferencesError()
