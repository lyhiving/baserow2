# Generated from BaserowFormula.g4 by ANTLR 4.8
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .BaserowFormula import BaserowFormula
else:
    from BaserowFormula import BaserowFormula

# This class defines a complete listener for a parse tree produced by BaserowFormula.
class BaserowFormulaListener(ParseTreeListener):

    # Enter a parse tree produced by BaserowFormula#root.
    def enterRoot(self, ctx:BaserowFormula.RootContext):
        pass

    # Exit a parse tree produced by BaserowFormula#root.
    def exitRoot(self, ctx:BaserowFormula.RootContext):
        pass


    # Enter a parse tree produced by BaserowFormula#StringLiteral.
    def enterStringLiteral(self, ctx:BaserowFormula.StringLiteralContext):
        pass

    # Exit a parse tree produced by BaserowFormula#StringLiteral.
    def exitStringLiteral(self, ctx:BaserowFormula.StringLiteralContext):
        pass


    # Enter a parse tree produced by BaserowFormula#FunctionCall.
    def enterFunctionCall(self, ctx:BaserowFormula.FunctionCallContext):
        pass

    # Exit a parse tree produced by BaserowFormula#FunctionCall.
    def exitFunctionCall(self, ctx:BaserowFormula.FunctionCallContext):
        pass


    # Enter a parse tree produced by BaserowFormula#IntegerLiteral.
    def enterIntegerLiteral(self, ctx:BaserowFormula.IntegerLiteralContext):
        pass

    # Exit a parse tree produced by BaserowFormula#IntegerLiteral.
    def exitIntegerLiteral(self, ctx:BaserowFormula.IntegerLiteralContext):
        pass


    # Enter a parse tree produced by BaserowFormula#BinaryOp.
    def enterBinaryOp(self, ctx:BaserowFormula.BinaryOpContext):
        pass

    # Exit a parse tree produced by BaserowFormula#BinaryOp.
    def exitBinaryOp(self, ctx:BaserowFormula.BinaryOpContext):
        pass


    # Enter a parse tree produced by BaserowFormula#func_name.
    def enterFunc_name(self, ctx:BaserowFormula.Func_nameContext):
        pass

    # Exit a parse tree produced by BaserowFormula#func_name.
    def exitFunc_name(self, ctx:BaserowFormula.Func_nameContext):
        pass


    # Enter a parse tree produced by BaserowFormula#identifier.
    def enterIdentifier(self, ctx:BaserowFormula.IdentifierContext):
        pass

    # Exit a parse tree produced by BaserowFormula#identifier.
    def exitIdentifier(self, ctx:BaserowFormula.IdentifierContext):
        pass



del BaserowFormula