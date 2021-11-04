from typing import Type, Dict, Set, Optional

from django.db.models import Model

from baserow.contrib.database.fields.dependencies.update_collector import (
    LookupFieldByNameCache,
)
from baserow.contrib.database.formula.ast.tree import (
    BaserowExpression,
    BaserowFieldReference,
    BaserowFunctionDefinition,
)
from baserow.contrib.database.formula.expression_generator.generator import (
    baserow_expression_to_update_django_expression,
    baserow_expression_to_insert_django_expression,
)
from baserow.contrib.database.formula.field_updater import (
    BulkMultiTableFormulaFieldRefresher,
)
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
)
from baserow.contrib.database.formula.parser.update_field_names import (
    update_field_names,
)
from baserow.contrib.database.formula.types.exceptions import UnknownFormulaType
from baserow.contrib.database.formula.types.formula_type import BaserowFormulaType
from baserow.contrib.database.formula.types.formula_types import BASEROW_FORMULA_TYPES
from baserow.contrib.database.formula.types.typer import (
    calculate_typed_expression,
)
from baserow.contrib.database.formula.types.visitors import (
    FunctionsUsedVisitor,
    FieldReferenceExtractingVisitor,
)


class FormulaHandler:
    @classmethod
    def formula_requires_refresh_on_insert(cls, expression):
        functions_used: Set[BaserowFunctionDefinition] = expression.accept(
            FunctionsUsedVisitor()
        )
        return any(f.requires_refresh_after_insert for f in functions_used)

    @classmethod
    def calculate_typed_expression(
        cls, field, field_lookup_cache=None
    ) -> BaserowExpression[BaserowFormulaType]:
        if field_lookup_cache is None:
            field_lookup_cache = LookupFieldByNameCache()
        return calculate_typed_expression(field, field_lookup_cache)

    @classmethod
    def baserow_expression_to_update_django_expression(
        cls, expression: BaserowExpression, model: Type[Model]
    ):
        return baserow_expression_to_update_django_expression(expression, model)

    @classmethod
    def baserow_expression_to_insert_django_expression(
        cls,
        expression: BaserowExpression,
        model_instance: Model,
    ):
        return baserow_expression_to_insert_django_expression(
            expression, model_instance
        )

    @classmethod
    def get_normal_field_reference_expression(
        cls, field, formula_type: BaserowFormulaType
    ):
        return BaserowFieldReference[BaserowFormulaType](
            field.db_column, None, formula_type
        )

    @classmethod
    def get_lookup_field_reference_expression(
        cls, through_field, lookup_field, formula_type: BaserowFormulaType
    ):
        return BaserowFieldReference[BaserowFormulaType](
            through_field.db_column, lookup_field.db_column, formula_type
        )

    @classmethod
    def rename_field_references_in_formula_string(
        cls,
        formula_to_update: str,
        field_renames: Dict[str, str],
        via_field: Optional[str],
    ) -> str:
        return update_field_names(formula_to_update, field_renames, via_field=via_field)

    @classmethod
    def get_direct_field_name_dependencies_from_expression(cls, table, expr):
        return expr.accept(
            FieldReferenceExtractingVisitor(table, LookupFieldByNameCache())
        )

    @classmethod
    def get_direct_field_name_dependencies(cls, formula_field, field_lookup_cache):
        return formula_field.cached_untyped_expression.accept(
            FieldReferenceExtractingVisitor(formula_field.table, field_lookup_cache)
        )

    @classmethod
    def recreate_and_refresh_formula_fields(cls, updated_fields):
        BulkMultiTableFormulaFieldRefresher().recreate_and_refresh_updated_fields(
            updated_fields
        )

    @classmethod
    def raw_formula_to_untyped_expression(cls, formula_string):
        return raw_formula_to_untyped_expression(formula_string)

    @classmethod
    def recalculate_formula_field(cls, formula_field):
        return

    @classmethod
    def get_type(cls, formula_type_string: str):
        for formula_type in BASEROW_FORMULA_TYPES:
            if formula_type_string == formula_type.type:
                return formula_type
        raise UnknownFormulaType(formula_type_string)
