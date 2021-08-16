# Generated from /home/nigel/work/src/baserow/formula_lang/src/BaserowFormula.g4 by ANTLR 4.9.1
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


    # Enter a parse tree produced by BaserowFormula#Indentifier.
    def enterIndentifier(self, ctx:BaserowFormula.IndentifierContext):
        pass

    # Exit a parse tree produced by BaserowFormula#Indentifier.
    def exitIndentifier(self, ctx:BaserowFormula.IndentifierContext):
        pass


    # Enter a parse tree produced by BaserowFormula#func_name.
    def enterFunc_name(self, ctx:BaserowFormula.Func_nameContext):
        pass

    # Exit a parse tree produced by BaserowFormula#func_name.
    def exitFunc_name(self, ctx:BaserowFormula.Func_nameContext):
        pass


    # Enter a parse tree produced by BaserowFormula#func_call.
    def enterFunc_call(self, ctx:BaserowFormula.Func_callContext):
        pass

    # Exit a parse tree produced by BaserowFormula#func_call.
    def exitFunc_call(self, ctx:BaserowFormula.Func_callContext):
        pass


    # Enter a parse tree produced by BaserowFormula#identifier.
    def enterIdentifier(self, ctx:BaserowFormula.IdentifierContext):
        pass

    # Exit a parse tree produced by BaserowFormula#identifier.
    def exitIdentifier(self, ctx:BaserowFormula.IdentifierContext):
        pass



del BaserowFormula