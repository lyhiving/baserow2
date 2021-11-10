from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
)
from baserow.contrib.database.formula.parser.exceptions import MaximumFormulaSizeError
from baserow.contrib.database.formula.types.visitors import FormulaTypingVisitor


def calculate_typed_expression(formula_field, field_lookup_cache):
    """
    WARNING: This function is directly used by migration code. Please ensure
    backwards compatability.

    :param formula_field:
    :type formula_field:
    :param field_lookup_cache:
    :type field_lookup_cache:
    :return:
    :rtype:
    """
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

        expression_type = typed_expression.expression_type
        merged_expression_type = (
            expression_type.new_type_with_user_and_calculated_options_merged(
                formula_field
            )
        )

        # Take into account any user set formatting options on this formula field.
        typed_expr_merged_with_user_options = typed_expression.with_type(
            merged_expression_type
        )

        wrapped_typed_expr = (
            typed_expr_merged_with_user_options.expression_type.wrap_at_field_level(
                typed_expr_merged_with_user_options
            )
        )

        return wrapped_typed_expr
    except RecursionError:
        raise MaximumFormulaSizeError()
