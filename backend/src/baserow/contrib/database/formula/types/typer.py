from baserow.contrib.database.formula.parser.exceptions import MaximumFormulaSizeError
from baserow.contrib.database.formula.types.visitors import FormulaTypingVisitor


def calculate_typed_expression(formula_field, field_lookup_cache):
    try:
        untyped_expression = formula_field.cached_untyped_expression

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
