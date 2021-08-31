# Generated from BaserowFormula.g4 by ANTLR 4.8
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .BaserowFormula import BaserowFormula
else:
    from BaserowFormula import BaserowFormula

# This class defines a complete generic visitor for a parse tree produced by BaserowFormula.

class BaserowFormulaVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by BaserowFormula#root.
    def visitRoot(self, ctx:BaserowFormula.RootContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaserowFormula#StringLiteral.
    def visitStringLiteral(self, ctx:BaserowFormula.StringLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaserowFormula#FunctionCall.
    def visitFunctionCall(self, ctx:BaserowFormula.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaserowFormula#IntegerLiteral.
    def visitIntegerLiteral(self, ctx:BaserowFormula.IntegerLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaserowFormula#BinaryOp.
    def visitBinaryOp(self, ctx:BaserowFormula.BinaryOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaserowFormula#func_name.
    def visitFunc_name(self, ctx:BaserowFormula.Func_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaserowFormula#identifier.
    def visitIdentifier(self, ctx:BaserowFormula.IdentifierContext):
        return self.visitChildren(ctx)



del BaserowFormula