# Generated from BaserowFormula.g4 by ANTLR 4.8
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3Q")
        buf.write("$\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\3\2\3\2\3\2\3\3\3\3")
        buf.write("\3\3\3\3\3\3\3\3\3\3\7\3\25\n\3\f\3\16\3\30\13\3\5\3\32")
        buf.write("\n\3\3\3\3\3\5\3\36\n\3\3\4\3\4\3\5\3\5\3\5\2\2\6\2\4")
        buf.write("\6\b\2\3\3\2\31\32\2#\2\n\3\2\2\2\4\35\3\2\2\2\6\37\3")
        buf.write("\2\2\2\b!\3\2\2\2\n\13\5\4\3\2\13\f\7\2\2\3\f\3\3\2\2")
        buf.write("\2\r\36\7\27\2\2\16\36\7\30\2\2\17\20\5\6\4\2\20\31\7")
        buf.write("\r\2\2\21\26\5\4\3\2\22\23\7\7\2\2\23\25\5\4\3\2\24\22")
        buf.write("\3\2\2\2\25\30\3\2\2\2\26\24\3\2\2\2\26\27\3\2\2\2\27")
        buf.write("\32\3\2\2\2\30\26\3\2\2\2\31\21\3\2\2\2\31\32\3\2\2\2")
        buf.write("\32\33\3\2\2\2\33\34\7\16\2\2\34\36\3\2\2\2\35\r\3\2\2")
        buf.write("\2\35\16\3\2\2\2\35\17\3\2\2\2\36\5\3\2\2\2\37 \5\b\5")
        buf.write("\2 \7\3\2\2\2!\"\t\2\2\2\"\t\3\2\2\2\5\26\31\35")
        return buf.getvalue()


class BaserowFormula ( Parser ):

    grammarFileName = "BaserowFormula.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "','", "':'", "'::'", "'$'", "'$$'", "'*'", 
                     "'('", "')'", "'['", "']'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'.'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'&'", "'&&'", 
                     "'&<'", "'@@'", "'@>'", "'@'", "'!'", "'!!'", "'!='", 
                     "'^'", "'='", "'=>'", "'>'", "'>='", "'>>'", "'#'", 
                     "'#='", "'#>'", "'#>>'", "'##'", "'->'", "'->>'", "'-|-'", 
                     "'<'", "'<='", "'<@'", "'<^'", "'<>'", "'<->'", "'<<'", 
                     "'<<='", "'<?>'", "'-'", "'%'", "'|'", "'||'", "'||/'", 
                     "'|/'", "'+'", "'?'", "'?&'", "'?#'", "'?-'", "'?|'", 
                     "'/'", "'~'", "'~='", "'~>=~'", "'~>~'", "'~<=~'", 
                     "'~<~'", "'~*'", "'~~'", "';'" ]

    symbolicNames = [ "<INVALID>", "WHITESPACE", "BLOCK_COMMENT", "LINE_COMMENT", 
                      "IF", "COMMA", "COLON", "COLON_COLON", "DOLLAR", "DOLLAR_DOLLAR", 
                      "STAR", "OPEN_PAREN", "CLOSE_PAREN", "OPEN_BRACKET", 
                      "CLOSE_BRACKET", "BIT_STRING", "REGEX_STRING", "NUMERIC_LITERAL", 
                      "INTEGER_LITERAL", "HEX_INTEGER_LITERAL", "DOT", "SINGLEQ_STRING_LITERAL", 
                      "DOUBLEQ_STRING_LITERAL", "IDENTIFIER", "IDENTIFIER_UNICODE", 
                      "AMP", "AMP_AMP", "AMP_LT", "AT_AT", "AT_GT", "AT_SIGN", 
                      "BANG", "BANG_BANG", "BANG_EQUAL", "CARET", "EQUAL", 
                      "EQUAL_GT", "GT", "GTE", "GT_GT", "HASH", "HASH_EQ", 
                      "HASH_GT", "HASH_GT_GT", "HASH_HASH", "HYPHEN_GT", 
                      "HYPHEN_GT_GT", "HYPHEN_PIPE_HYPHEN", "LT", "LTE", 
                      "LT_AT", "LT_CARET", "LT_GT", "LT_HYPHEN_GT", "LT_LT", 
                      "LT_LT_EQ", "LT_QMARK_GT", "MINUS", "PERCENT", "PIPE", 
                      "PIPE_PIPE", "PIPE_PIPE_SLASH", "PIPE_SLASH", "PLUS", 
                      "QMARK", "QMARK_AMP", "QMARK_HASH", "QMARK_HYPHEN", 
                      "QMARK_PIPE", "SLASH", "TIL", "TIL_EQ", "TIL_GTE_TIL", 
                      "TIL_GT_TIL", "TIL_LTE_TIL", "TIL_LT_TIL", "TIL_STAR", 
                      "TIL_TIL", "SEMI", "ErrorCharacter" ]

    RULE_root = 0
    RULE_expr = 1
    RULE_func_name = 2
    RULE_identifier = 3

    ruleNames =  [ "root", "expr", "func_name", "identifier" ]

    EOF = Token.EOF
    WHITESPACE=1
    BLOCK_COMMENT=2
    LINE_COMMENT=3
    IF=4
    COMMA=5
    COLON=6
    COLON_COLON=7
    DOLLAR=8
    DOLLAR_DOLLAR=9
    STAR=10
    OPEN_PAREN=11
    CLOSE_PAREN=12
    OPEN_BRACKET=13
    CLOSE_BRACKET=14
    BIT_STRING=15
    REGEX_STRING=16
    NUMERIC_LITERAL=17
    INTEGER_LITERAL=18
    HEX_INTEGER_LITERAL=19
    DOT=20
    SINGLEQ_STRING_LITERAL=21
    DOUBLEQ_STRING_LITERAL=22
    IDENTIFIER=23
    IDENTIFIER_UNICODE=24
    AMP=25
    AMP_AMP=26
    AMP_LT=27
    AT_AT=28
    AT_GT=29
    AT_SIGN=30
    BANG=31
    BANG_BANG=32
    BANG_EQUAL=33
    CARET=34
    EQUAL=35
    EQUAL_GT=36
    GT=37
    GTE=38
    GT_GT=39
    HASH=40
    HASH_EQ=41
    HASH_GT=42
    HASH_GT_GT=43
    HASH_HASH=44
    HYPHEN_GT=45
    HYPHEN_GT_GT=46
    HYPHEN_PIPE_HYPHEN=47
    LT=48
    LTE=49
    LT_AT=50
    LT_CARET=51
    LT_GT=52
    LT_HYPHEN_GT=53
    LT_LT=54
    LT_LT_EQ=55
    LT_QMARK_GT=56
    MINUS=57
    PERCENT=58
    PIPE=59
    PIPE_PIPE=60
    PIPE_PIPE_SLASH=61
    PIPE_SLASH=62
    PLUS=63
    QMARK=64
    QMARK_AMP=65
    QMARK_HASH=66
    QMARK_HYPHEN=67
    QMARK_PIPE=68
    SLASH=69
    TIL=70
    TIL_EQ=71
    TIL_GTE_TIL=72
    TIL_GT_TIL=73
    TIL_LTE_TIL=74
    TIL_LT_TIL=75
    TIL_STAR=76
    TIL_TIL=77
    SEMI=78
    ErrorCharacter=79

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class RootContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self):
            return self.getTypedRuleContext(BaserowFormula.ExprContext,0)


        def EOF(self):
            return self.getToken(BaserowFormula.EOF, 0)

        def getRuleIndex(self):
            return BaserowFormula.RULE_root

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRoot" ):
                listener.enterRoot(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRoot" ):
                listener.exitRoot(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRoot" ):
                return visitor.visitRoot(self)
            else:
                return visitor.visitChildren(self)




    def root(self):

        localctx = BaserowFormula.RootContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_root)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 8
            self.expr()
            self.state = 9
            self.match(BaserowFormula.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExprContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BaserowFormula.RULE_expr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class StringLiteralContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BaserowFormula.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def SINGLEQ_STRING_LITERAL(self):
            return self.getToken(BaserowFormula.SINGLEQ_STRING_LITERAL, 0)
        def DOUBLEQ_STRING_LITERAL(self):
            return self.getToken(BaserowFormula.DOUBLEQ_STRING_LITERAL, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStringLiteral" ):
                listener.enterStringLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStringLiteral" ):
                listener.exitStringLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStringLiteral" ):
                return visitor.visitStringLiteral(self)
            else:
                return visitor.visitChildren(self)


    class FunctionCallContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BaserowFormula.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def func_name(self):
            return self.getTypedRuleContext(BaserowFormula.Func_nameContext,0)

        def OPEN_PAREN(self):
            return self.getToken(BaserowFormula.OPEN_PAREN, 0)
        def CLOSE_PAREN(self):
            return self.getToken(BaserowFormula.CLOSE_PAREN, 0)
        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BaserowFormula.ExprContext)
            else:
                return self.getTypedRuleContext(BaserowFormula.ExprContext,i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(BaserowFormula.COMMA)
            else:
                return self.getToken(BaserowFormula.COMMA, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunctionCall" ):
                listener.enterFunctionCall(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunctionCall" ):
                listener.exitFunctionCall(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFunctionCall" ):
                return visitor.visitFunctionCall(self)
            else:
                return visitor.visitChildren(self)



    def expr(self):

        localctx = BaserowFormula.ExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_expr)
        self._la = 0 # Token type
        try:
            self.state = 27
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [BaserowFormula.SINGLEQ_STRING_LITERAL]:
                localctx = BaserowFormula.StringLiteralContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 11
                self.match(BaserowFormula.SINGLEQ_STRING_LITERAL)
                pass
            elif token in [BaserowFormula.DOUBLEQ_STRING_LITERAL]:
                localctx = BaserowFormula.StringLiteralContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 12
                self.match(BaserowFormula.DOUBLEQ_STRING_LITERAL)
                pass
            elif token in [BaserowFormula.IDENTIFIER, BaserowFormula.IDENTIFIER_UNICODE]:
                localctx = BaserowFormula.FunctionCallContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 13
                self.func_name()
                self.state = 14
                self.match(BaserowFormula.OPEN_PAREN)
                self.state = 23
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << BaserowFormula.SINGLEQ_STRING_LITERAL) | (1 << BaserowFormula.DOUBLEQ_STRING_LITERAL) | (1 << BaserowFormula.IDENTIFIER) | (1 << BaserowFormula.IDENTIFIER_UNICODE))) != 0):
                    self.state = 15
                    self.expr()
                    self.state = 20
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while _la==BaserowFormula.COMMA:
                        self.state = 16
                        self.match(BaserowFormula.COMMA)
                        self.state = 17
                        self.expr()
                        self.state = 22
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)



                self.state = 25
                self.match(BaserowFormula.CLOSE_PAREN)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Func_nameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(BaserowFormula.IdentifierContext,0)


        def getRuleIndex(self):
            return BaserowFormula.RULE_func_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunc_name" ):
                listener.enterFunc_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunc_name" ):
                listener.exitFunc_name(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFunc_name" ):
                return visitor.visitFunc_name(self)
            else:
                return visitor.visitChildren(self)




    def func_name(self):

        localctx = BaserowFormula.Func_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_func_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self.identifier()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IdentifierContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(BaserowFormula.IDENTIFIER, 0)

        def IDENTIFIER_UNICODE(self):
            return self.getToken(BaserowFormula.IDENTIFIER_UNICODE, 0)

        def getRuleIndex(self):
            return BaserowFormula.RULE_identifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdentifier" ):
                listener.enterIdentifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdentifier" ):
                listener.exitIdentifier(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIdentifier" ):
                return visitor.visitIdentifier(self)
            else:
                return visitor.visitChildren(self)




    def identifier(self):

        localctx = BaserowFormula.IdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_identifier)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 31
            _la = self._input.LA(1)
            if not(_la==BaserowFormula.IDENTIFIER or _la==BaserowFormula.IDENTIFIER_UNICODE):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





