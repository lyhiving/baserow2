from typing import Optional

from django.db import models
from django.db.models import (
    Expression,
    Value,
    F,
    Field,
    DecimalField,
)

from baserow.contrib.database.formula.ast.errors import UnknownFieldReference
from baserow.contrib.database.formula.ast.tree import (
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowIntegerLiteral,
    BaserowFieldByIdReference,
    BaserowFieldReference,
    BaserowExpression,
    BaserowDecimalLiteral,
)
from baserow.contrib.database.formula.ast.visitors import BaserowFormulaASTVisitor
from baserow.contrib.database.formula.parser.errors import MaximumFormulaSizeError
from baserow.contrib.database.formula.types.type_types import (
    BaserowFormulaType,
    BaserowFormulaInvalidType,
)
from baserow.contrib.database.table.models import GeneratedTableModel


def baserow_expression_to_django_expression(
    baserow_expression: BaserowExpression[BaserowFormulaType],
    model_instance: Optional[GeneratedTableModel],
) -> Expression:
    """
    Takes a BaserowExpression and converts it to a Django Expression which calculates
    the result of the expression when run on the provided model_instance or for the
    entire table when a model_instance is not provided.

    More specifically, when a model_instance is provided all field() references will
    be replaced by the values of those fields on the model_instance. If a model_instance
    is not provided instead these field references will be replaced by F() column
    references. When doing an create operation you will need to provide a model_instance
    as you cannot reference a column for a row that does not yet exist. Instead the
    initial defaults will be found and substituted in.

    :param baserow_expression: The BaserowExpression to convert.
    :param model_instance: If provided the expression will calculate the result for
        this single instance. If not provided then the expression will use F() column
        references and will calculate the result for every row in the table.
    :return: A Django Expression which can be used in a create operation when a
        model_instance is provided or an update operation when one is not provided.
    """

    try:
        if isinstance(baserow_expression.expression_type, BaserowFormulaInvalidType):
            return Value(None)
        else:
            return baserow_expression.accept(
                BaserowExpressionToDjangoExpressionGenerator(model_instance)
            )
    except RecursionError:
        raise MaximumFormulaSizeError()


class BaserowExpressionToDjangoExpressionGenerator(
    BaserowFormulaASTVisitor[Field, Expression]
):
    """
    Visits a BaserowExpression replacing it with the equivalent Django Expression.

    If a model_instance is provided then any field references will be replaced with
    direct Value() expressions of those fields on that model_instance. If one is not
    provided then instead a F() expression will be used to reference that field.
    """

    def __init__(
        self,
        model_instance: Optional[GeneratedTableModel],
    ):
        self.model_instance = model_instance

    def visit_field_reference(self, field_reference: BaserowFieldReference):
        # If a field() reference still exists it must not have been able to find a
        # field with that name and replace it with a field_by_id. This means we cannot
        # proceed as we do not know what field should be referenced here.
        raise UnknownFieldReference(field_reference.referenced_field_name)

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference
    ):
        field_id = field_by_id_reference.referenced_field_id
        db_field_name = f"field_{field_id}"

        if self.model_instance is None:
            return F(db_field_name)
        elif not hasattr(self.model_instance, db_field_name):
            raise UnknownFieldReference(field_id)
        else:
            return Value(
                getattr(self.model_instance, db_field_name),
            )

    def visit_function_call(self, function_call: BaserowFunctionCall) -> Expression:
        args = [expr.accept(self) for expr in function_call.args]
        return function_call.to_django_expression_given_args(args)

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> Expression:
        return Value(string_literal.literal, output_field=models.TextField())

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return Value(
            int_literal.literal,
            output_field=DecimalField(max_digits=50, decimal_places=0),
        )

    def visit_decimal_literal(self, decimal_literal: BaserowDecimalLiteral):
        pass
        return Value(
            decimal_literal.literal,
            output_field=DecimalField(
                max_digits=50, decimal_places=decimal_literal.num_decimal_places()
            ),
        )
