import typing
from collections import OrderedDict
from copy import deepcopy
from typing import Dict, Optional, Set, List, OrderedDict as OrderedDictType

from baserow.contrib.database.fields.models import (
    Field,
    FormulaField,
)
from baserow.contrib.database.fields.registries import field_type_registry, FieldType
from baserow.contrib.database.formula.ast.tree import (
    BaserowFieldByIdReference,
    BaserowExpression,
)
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
    replace_field_refs_according_to_new_or_deleted_fields,
)
from baserow.contrib.database.formula.parser.errors import MaximumFormulaSizeError
from baserow.contrib.database.formula.registries import formula_type_handler_registry
from baserow.contrib.database.formula.types.errors import (
    NoSelfReferencesError,
    NoCircularReferencesError,
)
from baserow.contrib.database.formula.types.type_defs import (
    BASEROW_FORMULA_TYPE_ALLOWED_FIELDS,
)
from baserow.contrib.database.formula.types.type_handler import (
    BaserowFormulaTypeHandler,
)
from baserow.contrib.database.formula.types.type_types import (
    BaserowFormulaType,
    BaserowFormulaValidType,
    UnTyped,
)
from baserow.contrib.database.formula.types.visitors import (
    FieldReferenceResolvingVisitor,
    TypeAnnotatingASTVisitor,
    SubstituteFieldByIdWithThatFieldsExpressionVisitor,
)
from baserow.contrib.database.table import models


def _construct_all_fields(table):
    all_fields = []
    field_name_to_id = {}
    for field in table.field_set.all():
        field = field.specific
        all_fields.append(field)
        field_name_to_id[field.name] = field.id
    return all_fields, field_name_to_id


def _fix_deleted_or_new_refs_in_formula_and_parse_into_untyped_formula(
    field: FormulaField,
    deleted_field_id_to_name: Dict[int, str],
    field_name_to_id: Dict[str, int],
):
    fixed_formula = replace_field_refs_according_to_new_or_deleted_fields(
        field.formula, deleted_field_id_to_name, field_name_to_id
    )
    untyped_expression = raw_formula_to_untyped_expression(fixed_formula)
    return UntypedFormulaFieldWithReferences(field, fixed_formula, untyped_expression)


class UntypedFormulaFieldWithReferences:
    def __init__(
        self,
        original_formula_field: FormulaField,
        fixed_raw_formula: str,
        untyped_expression: BaserowExpression[UnTyped],
    ):
        self.original_formula_field = original_formula_field
        self.untyped_expression = untyped_expression
        self.fixed_raw_formula = fixed_raw_formula
        self.parents: Dict[int, "UntypedFormulaFieldWithReferences"] = {}
        self.formula_children: Dict[int, "UntypedFormulaFieldWithReferences"] = {}
        self.field_children: Set[int] = set()

    def add_child_formula(self, child_formula: "UntypedFormulaFieldWithReferences"):
        if child_formula.field_id == self.field_id:
            raise NoSelfReferencesError()
        self.formula_children[child_formula.field_id] = child_formula
        child_formula.parents[self.field_id] = self

    @property
    def field_id(self):
        return self.original_formula_field.id

    @property
    def field_name(self):
        return self.original_formula_field.name

    def add_child_field(self, child):
        self.field_children.add(child)

    def add_all_unvisited_nodes_in_depth_first_order(
        self,
        visited_so_far: OrderedDictType[int, "UntypedFormulaFieldWithReferences"],
        ordered_formula_fields: OrderedDictType[
            int, "UntypedFormulaFieldWithReferences"
        ],
    ):
        if self.field_id in visited_so_far:
            raise NoCircularReferencesError(
                [f.field_name for f in visited_so_far.values()] + [self.field_name]
            )

        visited_so_far[self.field_id] = self
        if self.field_id in ordered_formula_fields:
            return
        for formula_child in self.formula_children.values():
            formula_child.add_all_unvisited_nodes_in_depth_first_order(
                visited_so_far.copy(),
                ordered_formula_fields,
            )
        ordered_formula_fields[self.field_id] = self

    def to_typed(
        self,
        typed_expression: BaserowExpression[BaserowFormulaType],
        field_id_to_typed_field: Dict[int, "TypedFieldWithReferences"],
    ) -> "TypedFieldWithReferences":
        updated_formula_field = self._create_untyped_copy_of_original_field()
        updated_formula_field.formula = self.fixed_raw_formula

        new_formula_type = typed_expression.expression_type
        formula_type_handler: BaserowFormulaTypeHandler = (
            formula_type_handler_registry.get_by_model(new_formula_type)
        )
        formula_type_handler.persist_onto_formula_field(
            new_formula_type, updated_formula_field
        )
        typed_field = TypedFieldWithReferences(
            self.original_formula_field, updated_formula_field, typed_expression
        )

        for field_child in self.field_children:
            typed_field.add_child(field_id_to_typed_field[field_child])
        for formula_child in self.formula_children.values():
            typed_field.add_child(field_id_to_typed_field[formula_child.field_id])

        return typed_field

    def _create_untyped_copy_of_original_field(self):
        updated_formula_field = deepcopy(self.original_formula_field)
        for attr in BASEROW_FORMULA_TYPE_ALLOWED_FIELDS:
            setattr(updated_formula_field, attr, None)
        return updated_formula_field


def _add_children_to_untyped_formula(
    untyped_formula_field: UntypedFormulaFieldWithReferences,
    field_id_to_untyped_formula: Dict[int, UntypedFormulaFieldWithReferences],
):
    children = untyped_formula_field.untyped_expression.accept(
        FieldReferenceResolvingVisitor()
    )
    for child in children:
        if child in field_id_to_untyped_formula:
            child_formula = field_id_to_untyped_formula[child]
            untyped_formula_field.add_child_formula(child_formula)
        else:
            untyped_formula_field.add_child_field(child)


def _calculate_formula_field_type_resolution_order(
    field_id_to_untyped_formula: Dict[int, UntypedFormulaFieldWithReferences]
) -> typing.OrderedDict[int, UntypedFormulaFieldWithReferences]:
    ordered_untyped_formulas: OrderedDict[
        int, UntypedFormulaFieldWithReferences
    ] = OrderedDict()
    for untyped_formula in field_id_to_untyped_formula.values():
        untyped_formula.add_all_unvisited_nodes_in_depth_first_order(
            OrderedDict(), ordered_untyped_formulas
        )
    return ordered_untyped_formulas


def _calculate_non_formula_field_typed_expression(
    field: Field,
):
    field_type: FieldType = field_type_registry.get_by_model(field)
    formula_type = field_type.to_baserow_formula_type(field)
    typed_expr = BaserowFieldByIdReference[BaserowFormulaValidType](
        field.id, formula_type
    )
    return TypedFieldWithReferences(
        field,
        field,
        typed_expr,
    )


class TypedFieldWithReferences:
    def __init__(
        self,
        original_field: Field,
        updated_field: Field,
        typed_expression: BaserowExpression[BaserowFormulaType],
    ):
        self.original_field = original_field
        self.new_field = updated_field
        self.typed_expression = typed_expression
        self.children: Dict[int, "TypedFieldWithReferences"] = {}
        self.parents: Dict[int, "TypedFieldWithReferences"] = {}

    @property
    def formula_type(self) -> BaserowFormulaType:
        return self.typed_expression.expression_type

    @property
    def field_id(self) -> int:
        return self.new_field.id

    def add_all_missing_valid_parents(
        self,
        other_changed_fields: Dict[int, Field],
        field_id_to_typed_field: Dict[int, "TypedFieldWithReferences"],
    ):

        for parent in self.parents.values():
            typed_parent_field = field_id_to_typed_field[parent.field_id]
            if typed_parent_field.formula_type.is_valid:
                typed_parent_field.add_all_missing_valid_parents(
                    other_changed_fields, field_id_to_typed_field
                )
                other_changed_fields[parent.field_id] = typed_parent_field.new_field

    def get_all_child_fields_not_already_found_recursively(
        self, already_found_field_ids: Set[int]
    ) -> List[Field]:
        all_not_found_already_child_fields = []
        for child_field_id, child in self.children.items():
            if child_field_id not in already_found_field_ids:
                already_found_field_ids.add(child_field_id)
                all_not_found_already_child_fields += [
                    child.new_field
                ] + child.get_all_child_fields_not_already_found_recursively(
                    already_found_field_ids
                )
        return all_not_found_already_child_fields

    def add_child(self, child: "TypedFieldWithReferences"):
        self.children[child.field_id] = child
        child.parents[self.field_id] = self


def _type_and_substitute_formula_field(
    untyped_formula: UntypedFormulaFieldWithReferences,
    field_id_to_typed_expression: Dict[int, TypedFieldWithReferences],
):
    typed_expr: BaserowExpression[
        BaserowFormulaType
    ] = untyped_formula.untyped_expression.accept(
        TypeAnnotatingASTVisitor(field_id_to_typed_expression)
    )

    expression_type_handler: BaserowFormulaTypeHandler = (
        formula_type_handler_registry.get_by_model(typed_expr.expression_type)
    )
    merged_expression_type = (
        expression_type_handler.new_type_with_user_and_calculated_options_merged(
            typed_expr.expression_type, untyped_formula.original_formula_field
        )
    )
    typed_expr_merged_with_user_options = typed_expr.with_type(merged_expression_type)

    typed_expr_with_substituted_field_by_id_references = (
        typed_expr_merged_with_user_options.accept(
            SubstituteFieldByIdWithThatFieldsExpressionVisitor(
                field_id_to_typed_expression
            )
        )
    )
    return typed_expr_with_substituted_field_by_id_references


def type_all_fields_in_table(
    table: "models.Table", deleted_field_id_to_name: Optional[Dict[int, str]] = None
) -> Dict[int, TypedFieldWithReferences]:
    try:
        if deleted_field_id_to_name is None:
            deleted_field_id_to_name = {}

        all_fields, field_name_to_id = _construct_all_fields(table)
        field_id_to_untyped_formula: Dict[int, UntypedFormulaFieldWithReferences] = {}
        field_id_to_updated_typed_field: Dict[int, TypedFieldWithReferences] = {}

        for field in all_fields:
            specific_class = field.specific_class
            field_type = field_type_registry.get_by_model(specific_class)
            field_id = field.id
            if field_type.type == "formula":
                field_id_to_untyped_formula[
                    field_id
                ] = _fix_deleted_or_new_refs_in_formula_and_parse_into_untyped_formula(
                    field, deleted_field_id_to_name, field_name_to_id
                )
            else:
                updated_typed_field = _calculate_non_formula_field_typed_expression(
                    field
                )
                field_id_to_updated_typed_field[field_id] = updated_typed_field

        for untyped_formula in field_id_to_untyped_formula.values():
            _add_children_to_untyped_formula(
                untyped_formula, field_id_to_untyped_formula
            )

        formula_field_ids_ordered_by_typing_order = (
            _calculate_formula_field_type_resolution_order(field_id_to_untyped_formula)
        )

        for (
            formula_id,
            untyped_formula,
        ) in formula_field_ids_ordered_by_typing_order.items():
            typed_expr = _type_and_substitute_formula_field(
                untyped_formula, field_id_to_updated_typed_field
            )
            field_id = untyped_formula.field_id
            field_id_to_updated_typed_field[field_id] = untyped_formula.to_typed(
                typed_expr, field_id_to_updated_typed_field
            )
        return field_id_to_updated_typed_field
    except RecursionError:
        raise MaximumFormulaSizeError()


class TypedBaserowTable:
    def __init__(self, typed_fields: Dict[int, TypedFieldWithReferences]):
        self.typed_fields_with_references = typed_fields

    def calculate_all_child_fields(self, field: Field, field_ids_to_ignore: Set[int]):
        typed_field = self.typed_fields_with_references[field.id]
        return typed_field.get_all_child_fields_not_already_found_recursively(
            field_ids_to_ignore
        )

    def get_typed_field_expression(
        self, field: Field
    ) -> BaserowExpression[BaserowFormulaType]:
        return self.typed_fields_with_references[field.id].typed_expression


def type_table(table: "models.Table") -> TypedBaserowTable:
    return TypedBaserowTable(type_all_fields_in_table(table))
