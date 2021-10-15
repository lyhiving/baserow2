from typing import Dict, Optional

from baserow.contrib.database.formula.parser.exceptions import (
    MaximumFormulaSizeError,
    UnknownFieldByIdReference,
)
from baserow.contrib.database.formula.parser.generated.BaserowFormula import (
    BaserowFormula,
)
from baserow.contrib.database.formula.parser.generated.BaserowFormulaVisitor import (
    BaserowFormulaVisitor,
)
from baserow.contrib.database.formula.parser.parser import (
    convert_string_literal_token_to_string,
    convert_string_to_string_literal_token,
    get_parse_tree_for_formula,
)


class UpdateFieldNameFormulaVisitor(BaserowFormulaVisitor):
    def __init__(
        self,
        field_names_to_update: Dict[str, str],
        all_field_ids_to_name: Dict[int, str],
    ):
        self.field_names_to_update = field_names_to_update
        self.all_field_ids_to_name = all_field_ids_to_name

    def visitRoot(self, ctx: BaserowFormula.RootContext):
        return ctx.expr().accept(self)

    def visitStringLiteral(self, ctx: BaserowFormula.StringLiteralContext):
        return ctx.getText()

    def visitDecimalLiteral(self, ctx: BaserowFormula.DecimalLiteralContext):
        return ctx.getText()

    def visitBooleanLiteral(self, ctx: BaserowFormula.BooleanLiteralContext):
        return ctx.getText()

    def visitBrackets(self, ctx: BaserowFormula.BracketsContext):
        return ctx.expr().accept(self)

    def visitFunctionCall(self, ctx: BaserowFormula.FunctionCallContext):
        function_name = ctx.func_name().accept(self).lower()
        args = [expr.accept(self) for expr in (ctx.expr())]
        args_with_any_field_names_replaced = ",".join(args)
        return f"{function_name}({args_with_any_field_names_replaced})"

    def visitBinaryOp(self, ctx: BaserowFormula.BinaryOpContext):
        args = [expr.accept(self) for expr in (ctx.expr())]
        return args[0] + ctx.op.text + args[1]

    def visitFunc_name(self, ctx: BaserowFormula.Func_nameContext):
        return ctx.getText()

    def visitIdentifier(self, ctx: BaserowFormula.IdentifierContext):
        return ctx.getText()

    def visitIntegerLiteral(self, ctx: BaserowFormula.IntegerLiteralContext):
        return ctx.getText()

    def visitFieldReference(self, ctx: BaserowFormula.FieldReferenceContext):
        reference = ctx.field_reference()
        is_single_quote_ref = reference.SINGLEQ_STRING_LITERAL()
        field_name = convert_string_literal_token_to_string(
            reference.getText(), is_single_quote_ref
        )
        if field_name in self.field_names_to_update:
            new_name = self.field_names_to_update[field_name]
            escaped_new_name = convert_string_to_string_literal_token(
                new_name, is_single_quote_ref
            )
            return f"field({escaped_new_name})"
        else:
            return ctx.getText()

    def visitFieldByIdReference(self, ctx: BaserowFormula.FieldByIdReferenceContext):
        field_id = int(str(ctx.INTEGER_LITERAL()))
        if field_id not in self.all_field_ids_to_name:
            raise UnknownFieldByIdReference(field_id)
        new_name = self.all_field_ids_to_name[field_id]
        escaped_new_name = convert_string_to_string_literal_token(new_name, True)
        return f"field({escaped_new_name})"

    def visitLeftWhitespaceOrComments(
        self, ctx: BaserowFormula.LeftWhitespaceOrCommentsContext
    ):
        updated_expr = ctx.expr().accept(self)
        return ctx.ws_or_comment().getText() + updated_expr

    def visitRightWhitespaceOrComments(
        self, ctx: BaserowFormula.RightWhitespaceOrCommentsContext
    ):
        updated_expr = ctx.expr().accept(self)
        return updated_expr + ctx.ws_or_comment().getText()


def update_field_names(
    formula: str,
    old_field_name_to_new_field_name: Dict[str, str],
    all_field_ids_to_names: Optional[Dict[int, str]] = None,
) -> str:
    try:
        if all_field_ids_to_names is None:
            all_field_ids_to_names = {}
        tree = get_parse_tree_for_formula(formula)
        return UpdateFieldNameFormulaVisitor(
            old_field_name_to_new_field_name, all_field_ids_to_names
        ).visit(tree)
    except RecursionError:
        raise MaximumFormulaSizeError()
