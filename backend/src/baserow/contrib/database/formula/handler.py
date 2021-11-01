from typing import Type, Dict

from django.db.models import Model

from baserow.contrib.database.formula.ast.tree import (
    BaserowExpression,
    BaserowFieldReference,
)
from baserow.contrib.database.formula.expression_generator.generator import (
    baserow_expression_to_django_expression,
)
from baserow.contrib.database.formula.models import FieldDependencyEdge
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
)
from baserow.contrib.database.formula.parser.update_field_names import (
    update_field_names,
)
from baserow.contrib.database.formula.types.formula_type import BaserowFormulaType
from baserow.contrib.database.formula.types.formula_types import (
    construct_type_from_formula_field,
)
from baserow.contrib.database.formula.types.typer import (
    type_and_update_field,
    TypedBaserowFields,
    type_and_update_fields,
    type_formula_field,
)


class FormulaHandler:
    @classmethod
    def field_created_or_updated(cls, field) -> TypedBaserowFields:
        return type_and_update_field(field)

    @classmethod
    def recalculate_type(cls, field):
        typed_field_node = type_formula_field(
            field, TypedBaserowFields(), update_graph=False
        )
        typed_field_node.typed_expression.expression_type.persist_onto_formula_field(
            field
        )

    @classmethod
    def construct_type_from_formula_field(cls, field) -> BaserowFormulaType:
        return construct_type_from_formula_field(field)

    @classmethod
    def baserow_expression_to_django_expression(
        cls, expression: BaserowExpression, model: Type[Model], model_instance: Model
    ):
        return baserow_expression_to_django_expression(
            expression, model, model_instance
        )

    @classmethod
    def get_db_field_reference(cls, field, formula_type: BaserowFormulaType):
        return BaserowFieldReference[BaserowFormulaType](field.db_column, formula_type)

    @classmethod
    def lookup_formula_expression_from_db(cls, field):
        formula_type = cls.construct_type_from_formula_field(field)
        untyped_internal_expr = raw_formula_to_untyped_expression(
            field.internal_formula
        )
        return untyped_internal_expr.with_type(formula_type)

    @classmethod
    def rename_field_references_in_formula_string(
        cls, formula_to_update: str, field_renames: Dict[str, str]
    ) -> str:
        return update_field_names(formula_to_update, field_renames)
