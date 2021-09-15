from copy import deepcopy
from typing import List, Tuple, Dict, Any, Optional, Set

from django.db import connection

from baserow.contrib.database.fields.field_converters import FormulaFieldConverter
from baserow.contrib.database.fields.field_types import FormulaFieldType
from baserow.contrib.database.fields.models import (
    Field,
    FormulaField,
)
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.formula.ast.errors import (
    NoSelfReferencesError,
    NoCircularReferencesError,
    InvalidFieldType,
)
from baserow.contrib.database.formula.ast.tree import (
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowIntegerLiteral,
    BaserowFieldByIdReference,
    BaserowFieldReference,
    BaserowExpression,
)
from baserow.contrib.database.formula.ast.type_defs import (
    BaserowFormulaNumberType,
    BaserowFormulaTextType,
)
from baserow.contrib.database.formula.ast.type_types import (
    BaserowFormulaType,
    BaserowFormulaInvalidType,
    BaserowFormulaValidType,
    UnTyped,
)
from baserow.contrib.database.formula.ast.type_handler import BaserowFormulaTypeHandler
from baserow.contrib.database.formula.ast.visitors import BaserowFormulaASTVisitor
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
    replace_field_refs_according_to_new_or_deleted_fields,
)
from baserow.contrib.database.formula.parser.errors import MaximumFormulaSizeError
from baserow.contrib.database.formula.registries import formula_type_handler_registry
from baserow.contrib.database.table.models import Table


class Typer:
    def __init__(
        self,
        table: Table,
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
        self.field_id_to_field: Dict[int, Field] = {f.id: f for f in self.all_fields}
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
        self._fix_formulas_referencing_new_or_deleted_fields(formula_field_id)
        typed_expr = self._type_formula_fields_expression(formula_field_id)
        self._save_type_information_onto_field(formula_field_id, typed_expr)
        typed_expr_with_substituted_field_by_id_references = typed_expr.accept(
            SubsituteFieldByIdWithThatFieldsExpressionVisitor(
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
        typed_expr = untyped_expr.accept(
            TypeAnnotatingASTVisitor(self.typed_field_expressions)
        )
        return typed_expr

    def _save_type_information_onto_field(self, formula_field_id, typed_expr):
        formula_field = self.field_id_to_field[formula_field_id].specific
        expression_type_handler: BaserowFormulaTypeHandler = (
            formula_type_handler_registry.get_by_model(typed_expr.expression_type)
        )
        expression_type_handler.persist_onto_formula_field(
            typed_expr.expression_type, formula_field
        )

    def _override(self, obj1, attrs, obj2):
        for attr in attrs:
            if getattr(obj2, attr) is not None:
                setattr(obj1, attr, getattr(obj2, attr))

    def _required_drop_recreate(self, old_formula_field, new_formula_field):
        old_formula_field_type = old_formula_field.formula_type
        new_formula_field_type = new_formula_field.formula_type
        if new_formula_field_type != old_formula_field_type:
            return True
        if new_formula_field == "NumberField":
            return (
                new_formula_field.number_decimal_places
                != old_formula_field.number_decimal_places
            )
        elif new_formula_field == "DateField":
            return (
                new_formula_field.date_include_time
                != old_formula_field.date_include_time
            )
        return False

    def _fix_formulas_referencing_new_or_deleted_fields(self, formula_field_id):
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
            specific_formula_field = self.field_id_to_field[formula_field_id].specific
            specific_formula_field.formula = (
                replace_field_refs_according_to_new_or_deleted_fields(
                    specific_formula_field.formula,
                    self.deleted_field_id_names,
                    self.new_field_names_to_id,
                )
            )

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
                BaserowFormulaInvalidType(f"Field {field.name} is " f"deleted"),
            )
            self.deleted_field_id_names[field.id] = field.name
        elif field.id in self.deleted_field_id_names:
            name = self.deleted_field_id_names[field.id]
            typed_expr = BaserowFieldReference(
                name, BaserowFormulaInvalidType(f"Field {name} is deleted")
            )
        else:
            specific_field = field.specific
            field_type = field_type_registry.get_by_model(specific_field)
            formula_type = field_type.get_formula_type(specific_field)
            typed_expr = BaserowFieldByIdReference[BaserowFormulaValidType](
                field.id, formula_type
            )
        self.typed_field_expressions[field.id] = typed_expr
        self.field_references[field.id] = []

    def calculate_all_child_fields(self, fields):
        fields_to_check = fields.copy()
        extra_fields = []
        extra_field_ids = set()
        current_field_ids = {f.id for f in fields}
        while len(fields_to_check) > 0:
            field = fields_to_check.pop(0)
            references = self.field_references[field.id]
            for ref in references:
                if ref not in current_field_ids and ref not in extra_field_ids:
                    new_field = self.field_id_to_field[ref]
                    extra_fields.append(new_field)
                    extra_field_ids.add(ref)
                    fields_to_check.append(new_field)
        return extra_fields

    def update_fields(self, field_which_changed=None, be_strict=True):
        if field_which_changed is not None:
            self._update_field_type(field_which_changed, be_strict)
            field_which_changed.save()
        updated_fields = set()
        for formula_field_id in self.formula_field_ids:
            typed_formula_expression = self.typed_field_expressions[formula_field_id]
            formula_field = self.field_id_to_field[formula_field_id]
            if formula_field.trashed:
                continue
            specific_formula_field = self.field_id_to_field[formula_field_id].specific
            old_field = deepcopy(specific_formula_field)

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
        formula_type_handler: BaserowFormulaTypeHandler = (
            formula_type_handler_registry.get(formula_type)
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
            # noinspection PyTypeChecker
            FormulaFieldType.copy_allowed_fields(specific_formula_field, field)

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
            self.field_id_to_field[i].specific
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


class FieldReferenceResolvingVisitor(BaserowFormulaASTVisitor[Any, List[str]]):
    def visit_field_reference(self, field_reference: BaserowFieldReference):
        # The only time when we should encounter a field reference here is when this
        # field is pointing at a trashed or deleted field.
        return []

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> List[str]:
        return []

    def visit_function_call(self, function_call: BaserowFunctionCall) -> List[str]:
        all_arg_references = [expr.accept(self) for expr in function_call.args]
        combined_references = []
        for arg_references in all_arg_references:
            combined_references += arg_references

        return combined_references

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return []

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference
    ):
        return [field_by_id_reference.referenced_field_id]


class TypeAnnotatingASTVisitor(
    BaserowFormulaASTVisitor[UnTyped, BaserowExpression[BaserowFormulaType]]
):
    def __init__(self, field_id_to_type):
        self.field_id_to_type: Dict[
            int, BaserowExpression[BaserowFormulaType]
        ] = field_id_to_type

    def visit_field_reference(
        self, field_reference: BaserowFieldReference[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        return field_reference.with_invalid_type(
            f"Unknown field {field_reference.referenced_field_name}"
        )

    def visit_string_literal(
        self, string_literal: BaserowStringLiteral[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        return string_literal.with_valid_type(BaserowFormulaTextType())

    def visit_function_call(
        self, function_call: BaserowFunctionCall[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        typed_args: List[BaserowExpression[BaserowFormulaValidType]] = []
        for expr in function_call.args:
            typed_args.append(expr.accept(self))
        return function_call.type_function_given_typed_args(typed_args)

    def visit_int_literal(
        self, int_literal: BaserowIntegerLiteral[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        return int_literal.with_valid_type(
            BaserowFormulaNumberType(
                number_decimal_places=0,
            ),
        )

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference[UnTyped]
    ) -> BaserowExpression[BaserowFormulaType]:
        if field_by_id_reference.referenced_field_id in self.field_id_to_type:
            return self.field_id_to_type[field_by_id_reference.referenced_field_id]
        else:
            return field_by_id_reference.with_invalid_type(
                f"Unknown or deleted field referenced: "
                f"{field_by_id_reference.referenced_field_id}"
            )


class SubsituteFieldByIdWithThatFieldsExpressionVisitor(
    BaserowFormulaASTVisitor[Any, BaserowExpression]
):
    def visit_field_reference(self, field_reference: BaserowFieldReference):
        return field_reference

    def __init__(self, field_id_to_expression: Dict[int, BaserowExpression]):
        self.field_id_to_expression = field_id_to_expression

    def visit_string_literal(
        self, string_literal: BaserowStringLiteral
    ) -> BaserowExpression:
        return string_literal

    def visit_function_call(
        self, function_call: BaserowFunctionCall
    ) -> BaserowExpression:
        args = [expr.accept(self) for expr in function_call.args]
        return BaserowFunctionCall(
            function_call.function_def, args, function_call.expression_type
        )

    def visit_int_literal(
        self, int_literal: BaserowIntegerLiteral
    ) -> BaserowExpression:
        return int_literal

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference
    ) -> BaserowExpression:
        if field_by_id_reference.referenced_field_id in self.field_id_to_expression:
            return self.field_id_to_expression[
                field_by_id_reference.referenced_field_id
            ]
        else:
            return field_by_id_reference
