from typing import Optional, Type

from django.db.models import (
    Expression,
    Value,
    F,
    DecimalField,
    BooleanField,
    fields,
    ExpressionWrapper,
    Subquery,
    OuterRef,
    Func,
    Model,
    Case,
    When,
    Q,
    FilteredRelation,
)
from django.db.models.functions import Cast

from baserow.contrib.database.formula.ast.exceptions import UnknownFieldReference
from baserow.contrib.database.formula.ast.tree import (
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowIntegerLiteral,
    BaserowFieldReference,
    BaserowExpression,
    BaserowDecimalLiteral,
    BaserowBooleanLiteral,
)
from baserow.contrib.database.formula.ast.visitors import BaserowFormulaASTVisitor
from baserow.contrib.database.formula.parser.exceptions import (
    MaximumFormulaSizeError,
)
from baserow.contrib.database.formula.types.formula_type import (
    BaserowFormulaType,
    BaserowFormulaInvalidType,
)


def baserow_expression_to_update_django_expression(
    baserow_expression: BaserowExpression[BaserowFormulaType],
    model: Type[Model],
):
    return _baserow_expression_to_django_expression(baserow_expression, model, None)


def baserow_expression_to_insert_django_expression(
    baserow_expression: BaserowExpression[BaserowFormulaType],
    model_instance: Model,
):
    return _baserow_expression_to_django_expression(
        baserow_expression, type(model_instance), model_instance
    )


def _baserow_expression_to_django_expression(
    baserow_expression: BaserowExpression[BaserowFormulaType],
    model: Type[Model],
    model_instance: Optional[Model],
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
    :param model: The Django model that the expression is being generated for.
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
            generator = BaserowExpressionToDjangoExpressionGenerator(
                model, model_instance
            )
            expr = baserow_expression.accept(generator)
            if baserow_expression.aggregate and model is not None:
                if model_instance is not None and model_instance.pk is None:
                    return Value(None)
                filters = {
                    key + "__isnull": False for key in generator.pre_annotations.keys()
                }
                values = (
                    model.objects_and_trash.filter(id=OuterRef("id"))
                    .annotate(**generator.pre_annotations)
                    .filter(**filters)
                    .annotate(result=expr)
                    .values("result")
                )
                if (
                    isinstance(expr, Func)
                    and "function" in expr.extra
                    and expr.extra["function"] == "unnest"
                ):
                    subquery = Subquery(values.distinct())
                    expr = Func(subquery, function="array")
                else:
                    subquery = Subquery(values)
                    expr = subquery

            return expr
    except RecursionError:
        raise MaximumFormulaSizeError()


def _get_model_field_for_type(expression_type):
    (
        field_instance,
        baserow_field_type,
    ) = expression_type.get_baserow_field_instance_and_type()
    model_field = baserow_field_type.get_model_field(field_instance)
    return model_field


class BaserowExpressionToDjangoExpressionGenerator(
    BaserowFormulaASTVisitor[BaserowFormulaType, Expression]
):
    """
    Visits a BaserowExpression replacing it with the equivalent Django Expression.

    If a model_instance is provided then any field references will be replaced with
    direct Value() expressions of those fields on that model_instance. If one is not
    provided then instead a F() expression will be used to reference that field.
    """

    def __init__(
        self,
        model: Type[Model],
        model_instance: Optional[Model],
    ):
        self.model_instance = model_instance
        self.model = model
        self.pre_annotations = {}
        self.aggregate_filters = []

    def visit_field_reference(
        self, field_reference: BaserowFieldReference[BaserowFormulaType]
    ):
        db_column = field_reference.referenced_field_name

        lookup_ref = field_reference.referenced_lookup_field
        is_lookup = lookup_ref is not None
        if is_lookup:
            # TODO
            path = lookup_ref.split("__")
            other_model = self.model
            for step in [db_column] + path[:-1]:
                other_model = other_model._meta.get_field(step).remote_field.model
            model_field = other_model._meta.get_field(path[-1])
            db_column += f"__{lookup_ref}"
        else:
            model_field = self.model._meta.get_field(db_column)
        if self.model_instance is None or is_lookup:
            if is_lookup:
                path = lookup_ref.split("__")

                path_to_row_trashed = (
                    [field_reference.referenced_field_name] + path[:-1] + ["trashed"]
                )
                row_trashed_ref = "__".join(path_to_row_trashed)
                path_to_row = "__".join(path_to_row_trashed[:-1])
                row_not_trashed_filter_dict = {
                    row_trashed_ref: False,
                    f"{path_to_row}__isnull": False,
                }
                if len(path) > 1:
                    path_to_middle_link = "__".join(path_to_row_trashed[:-2])
                    not_trashed_middle_linkt = path_to_middle_link + "__trashed"
                    row_not_trashed_filter_dict[not_trashed_middle_linkt] = False
                relation = FilteredRelation(
                    path_to_row, condition=Q(**row_not_trashed_filter_dict)
                )
                unique_preannotation_name = (
                    f"not_trashed_{'_'.join(path_to_row_trashed[:-1])}"
                )
                self.pre_annotations[unique_preannotation_name] = relation
                return ExpressionWrapper(
                    F(f"{unique_preannotation_name}__{path[-1]}"),
                    output_field=model_field,
                )
            else:
                return ExpressionWrapper(F(db_column), output_field=model_field)
            # if is_lookup:
            #     path = lookup_ref.split("__")
            #     col = [field_reference.referenced_field_name] + path[:-1] + ["trashed"]
            #     notnull = [field_reference.referenced_field_name] + path + ["isnull"]
            #     c = "__".join(col)
            #     d = "__".join(notnull)
            #     self.aggregate_filters.append(Q(**{c: False}))
            #     self.aggregate_filters.append(Q(**{d: False}))

            # return ExpressionWrapper(F(db_column), output_field=model_field)
        elif not hasattr(self.model_instance, db_column):
            raise UnknownFieldReference(db_column)
        else:
            # We need to cast and be super explicit what type this raw value is so
            # postgres does not get angry and claim this is an unknown type.
            return Cast(
                Value(
                    getattr(self.model_instance, db_column),
                ),
                output_field=model_field,
            )

    def visit_function_call(
        self, function_call: BaserowFunctionCall[BaserowFormulaType]
    ) -> Expression:
        args = [expr.accept(self) for expr in function_call.args]
        return function_call.to_django_expression_given_args(
            args, self.model_instance, self.aggregate_filters
        )

    def visit_string_literal(
        self, string_literal: BaserowStringLiteral[BaserowFormulaType]
    ) -> Expression:
        # We need to cast and be super explicit this is a text field so postgres
        # does not get angry and claim this is an unknown type.
        return Cast(
            Value(string_literal.literal, output_field=fields.TextField()),
            output_field=fields.TextField(),
        )

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral[BaserowFormulaType]):
        return Value(
            int_literal.literal,
            output_field=DecimalField(max_digits=50, decimal_places=0),
        )

    def visit_decimal_literal(self, decimal_literal: BaserowDecimalLiteral):
        return Value(
            decimal_literal.literal,
            output_field=DecimalField(
                max_digits=50, decimal_places=decimal_literal.num_decimal_places()
            ),
        )

    def visit_boolean_literal(self, boolean_literal: BaserowBooleanLiteral):
        return Value(boolean_literal.literal, output_field=BooleanField())
