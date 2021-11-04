from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
)
from baserow.contrib.database.formula.parser.exceptions import MaximumFormulaSizeError
from baserow.contrib.database.formula.types.visitors import FormulaTypingVisitor


def calculate_typed_expression(formula_field, field_lookup_cache):
    try:
        if hasattr(formula_field, "cached_untyped_expression"):
            untyped_expression = formula_field.cached_untyped_expression
        else:
            untyped_expression = raw_formula_to_untyped_expression(
                formula_field.formula
            )

        typed_expression = untyped_expression.accept(
            FormulaTypingVisitor(formula_field, field_lookup_cache)
        )
        if typed_expression.many:
            de_many_expr = typed_expression.expression_type.collapse_many(
                typed_expression
            )
        else:
            de_many_expr = typed_expression

        wrapped_expr = de_many_expr.expression_type.wrap_at_field_level(de_many_expr)

        expression_type = wrapped_expr.expression_type
        merged_expression_type = (
            expression_type.new_type_with_user_and_calculated_options_merged(
                formula_field
            )
        )

        # Take into account any user set formatting options on this formula field.
        typed_expr_merged_with_user_options = wrapped_expr.with_type(
            merged_expression_type
        )

        return typed_expr_merged_with_user_options
    except RecursionError:
        raise MaximumFormulaSizeError()
