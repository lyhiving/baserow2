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
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3S")
        buf.write(";\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\3\2\3\2\3\2")
        buf.write("\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3")
        buf.write("\3\3\3\3\3\3\3\3\3\7\3\"\n\3\f\3\16\3%\13\3\5\3\'\n\3")
        buf.write("\3\3\3\3\5\3+\n\3\3\3\3\3\3\3\7\3\60\n\3\f\3\16\3\63\13")
        buf.write("\3\3\4\3\4\3\5\3\5\3\6\3\6\3\6\2\3\4\7\2\4\6\b\n\2\5\4")
        buf.write("\2==CC\3\2\31\32\3\2\33\34\2=\2\f\3\2\2\2\4*\3\2\2\2\6")
        buf.write("\64\3\2\2\2\b\66\3\2\2\2\n8\3\2\2\2\f\r\5\4\3\2\r\16\7")
        buf.write("\2\2\3\16\3\3\2\2\2\17\20\b\3\1\2\20+\7\31\2\2\21+\7\32")
        buf.write("\2\2\22+\7\26\2\2\23\24\7\7\2\2\24\25\7\17\2\2\25\26\5")
        buf.write("\b\5\2\26\27\7\20\2\2\27+\3\2\2\2\30\31\7\b\2\2\31\32")
        buf.write("\7\17\2\2\32\33\7\26\2\2\33+\7\20\2\2\34\35\5\6\4\2\35")
        buf.write("&\7\17\2\2\36#\5\4\3\2\37 \7\t\2\2 \"\5\4\3\2!\37\3\2")
        buf.write("\2\2\"%\3\2\2\2#!\3\2\2\2#$\3\2\2\2$\'\3\2\2\2%#\3\2\2")
        buf.write("\2&\36\3\2\2\2&\'\3\2\2\2\'(\3\2\2\2()\7\20\2\2)+\3\2")
        buf.write("\2\2*\17\3\2\2\2*\21\3\2\2\2*\22\3\2\2\2*\23\3\2\2\2*")
        buf.write("\30\3\2\2\2*\34\3\2\2\2+\61\3\2\2\2,-\f\6\2\2-.\t\2\2")
        buf.write("\2.\60\5\4\3\7/,\3\2\2\2\60\63\3\2\2\2\61/\3\2\2\2\61")
        buf.write("\62\3\2\2\2\62\5\3\2\2\2\63\61\3\2\2\2\64\65\5\n\6\2\65")
        buf.write("\7\3\2\2\2\66\67\t\3\2\2\67\t\3\2\2\289\t\4\2\29\13\3")
        buf.write("\2\2\2\6#&*\61")
        return buf.getvalue()


class BaserowFormula ( Parser ):

    grammarFileName = "BaserowFormula.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "','", "':'", 
                     "'::'", "'$'", "'$$'", "'*'", "'('", "')'", "'['", 
                     "']'", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'.'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'&'", "'&&'", "'&<'", "'@@'", "'@>'", 
                     "'@'", "'!'", "'!!'", "'!='", "'^'", "'='", "'=>'", 
                     "'>'", "'>='", "'>>'", "'#'", "'#='", "'#>'", "'#>>'", 
                     "'##'", "'->'", "'->>'", "'-|-'", "'<'", "'<='", "'<@'", 
                     "'<^'", "'<>'", "'<->'", "'<<'", "'<<='", "'<?>'", 
                     "'-'", "'%'", "'|'", "'||'", "'||/'", "'|/'", "'+'", 
                     "'?'", "'?&'", "'?#'", "'?-'", "'?|'", "'/'", "'~'", 
                     "'~='", "'~>=~'", "'~>~'", "'~<=~'", "'~<~'", "'~*'", 
                     "'~~'", "';'" ]

    symbolicNames = [ "<INVALID>", "WHITESPACE", "BLOCK_COMMENT", "LINE_COMMENT", 
                      "IF", "FIELD", "FIELDBYID", "COMMA", "COLON", "COLON_COLON", 
                      "DOLLAR", "DOLLAR_DOLLAR", "STAR", "OPEN_PAREN", "CLOSE_PAREN", 
                      "OPEN_BRACKET", "CLOSE_BRACKET", "BIT_STRING", "REGEX_STRING", 
                      "NUMERIC_LITERAL", "INTEGER_LITERAL", "HEX_INTEGER_LITERAL", 
                      "DOT", "SINGLEQ_STRING_LITERAL", "DOUBLEQ_STRING_LITERAL", 
                      "IDENTIFIER", "IDENTIFIER_UNICODE", "AMP", "AMP_AMP", 
                      "AMP_LT", "AT_AT", "AT_GT", "AT_SIGN", "BANG", "BANG_BANG", 
                      "BANG_EQUAL", "CARET", "EQUAL", "EQUAL_GT", "GT", 
                      "GTE", "GT_GT", "HASH", "HASH_EQ", "HASH_GT", "HASH_GT_GT", 
                      "HASH_HASH", "HYPHEN_GT", "HYPHEN_GT_GT", "HYPHEN_PIPE_HYPHEN", 
                      "LT", "LTE", "LT_AT", "LT_CARET", "LT_GT", "LT_HYPHEN_GT", 
                      "LT_LT", "LT_LT_EQ", "LT_QMARK_GT", "MINUS", "PERCENT", 
                      "PIPE", "PIPE_PIPE", "PIPE_PIPE_SLASH", "PIPE_SLASH", 
                      "PLUS", "QMARK", "QMARK_AMP", "QMARK_HASH", "QMARK_HYPHEN", 
                      "QMARK_PIPE", "SLASH", "TIL", "TIL_EQ", "TIL_GTE_TIL", 
                      "TIL_GT_TIL", "TIL_LTE_TIL", "TIL_LT_TIL", "TIL_STAR", 
                      "TIL_TIL", "SEMI", "ErrorCharacter" ]

    RULE_root = 0
    RULE_expr = 1
    RULE_func_name = 2
    RULE_field_reference = 3
    RULE_identifier = 4

    ruleNames =  [ "root", "expr", "func_name", "field_reference", "identifier" ]

    EOF = Token.EOF
    WHITESPACE=1
    BLOCK_COMMENT=2
    LINE_COMMENT=3
    IF=4
    FIELD=5
    FIELDBYID=6
    COMMA=7
    COLON=8
    COLON_COLON=9
    DOLLAR=10
    DOLLAR_DOLLAR=11
    STAR=12
    OPEN_PAREN=13
    CLOSE_PAREN=14
    OPEN_BRACKET=15
    CLOSE_BRACKET=16
    BIT_STRING=17
    REGEX_STRING=18
    NUMERIC_LITERAL=19
    INTEGER_LITERAL=20
    HEX_INTEGER_LITERAL=21
    DOT=22
    SINGLEQ_STRING_LITERAL=23
    DOUBLEQ_STRING_LITERAL=24
    IDENTIFIER=25
    IDENTIFIER_UNICODE=26
    AMP=27
    AMP_AMP=28
    AMP_LT=29
    AT_AT=30
    AT_GT=31
    AT_SIGN=32
    BANG=33
    BANG_BANG=34
    BANG_EQUAL=35
    CARET=36
    EQUAL=37
    EQUAL_GT=38
    GT=39
    GTE=40
    GT_GT=41
    HASH=42
    HASH_EQ=43
    HASH_GT=44
    HASH_GT_GT=45
    HASH_HASH=46
    HYPHEN_GT=47
    HYPHEN_GT_GT=48
    HYPHEN_PIPE_HYPHEN=49
    LT=50
    LTE=51
    LT_AT=52
    LT_CARET=53
    LT_GT=54
    LT_HYPHEN_GT=55
    LT_LT=56
    LT_LT_EQ=57
    LT_QMARK_GT=58
    MINUS=59
    PERCENT=60
    PIPE=61
    PIPE_PIPE=62
    PIPE_PIPE_SLASH=63
    PIPE_SLASH=64
    PLUS=65
    QMARK=66
    QMARK_AMP=67
    QMARK_HASH=68
    QMARK_HYPHEN=69
    QMARK_PIPE=70
    SLASH=71
    TIL=72
    TIL_EQ=73
    TIL_GTE_TIL=74
    TIL_GT_TIL=75
    TIL_LTE_TIL=76
    TIL_LT_TIL=77
    TIL_STAR=78
    TIL_TIL=79
    SEMI=80
    ErrorCharacter=81

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
            self.state = 10
            self.expr(0)
            self.state = 11
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


    class FieldReferenceContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BaserowFormula.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def FIELD(self):
            return self.getToken(BaserowFormula.FIELD, 0)
        def OPEN_PAREN(self):
            return self.getToken(BaserowFormula.OPEN_PAREN, 0)
        def field_reference(self):
            return self.getTypedRuleContext(BaserowFormula.Field_referenceContext,0)

        def CLOSE_PAREN(self):
            return self.getToken(BaserowFormula.CLOSE_PAREN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFieldReference" ):
                listener.enterFieldReference(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFieldReference" ):
                listener.exitFieldReference(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFieldReference" ):
                return visitor.visitFieldReference(self)
            else:
                return visitor.visitChildren(self)


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


    class FieldByIdReferenceContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BaserowFormula.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def FIELDBYID(self):
            return self.getToken(BaserowFormula.FIELDBYID, 0)
        def OPEN_PAREN(self):
            return self.getToken(BaserowFormula.OPEN_PAREN, 0)
        def INTEGER_LITERAL(self):
            return self.getToken(BaserowFormula.INTEGER_LITERAL, 0)
        def CLOSE_PAREN(self):
            return self.getToken(BaserowFormula.CLOSE_PAREN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFieldByIdReference" ):
                listener.enterFieldByIdReference(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFieldByIdReference" ):
                listener.exitFieldByIdReference(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFieldByIdReference" ):
                return visitor.visitFieldByIdReference(self)
            else:
                return visitor.visitChildren(self)


    class IntegerLiteralContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BaserowFormula.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INTEGER_LITERAL(self):
            return self.getToken(BaserowFormula.INTEGER_LITERAL, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIntegerLiteral" ):
                listener.enterIntegerLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIntegerLiteral" ):
                listener.exitIntegerLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIntegerLiteral" ):
                return visitor.visitIntegerLiteral(self)
            else:
                return visitor.visitChildren(self)


    class BinaryOpContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BaserowFormula.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BaserowFormula.ExprContext)
            else:
                return self.getTypedRuleContext(BaserowFormula.ExprContext,i)

        def PLUS(self):
            return self.getToken(BaserowFormula.PLUS, 0)
        def MINUS(self):
            return self.getToken(BaserowFormula.MINUS, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBinaryOp" ):
                listener.enterBinaryOp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBinaryOp" ):
                listener.exitBinaryOp(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBinaryOp" ):
                return visitor.visitBinaryOp(self)
            else:
                return visitor.visitChildren(self)



    def expr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = BaserowFormula.ExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 2
        self.enterRecursionRule(localctx, 2, self.RULE_expr, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [BaserowFormula.SINGLEQ_STRING_LITERAL]:
                localctx = BaserowFormula.StringLiteralContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 14
                self.match(BaserowFormula.SINGLEQ_STRING_LITERAL)
                pass
            elif token in [BaserowFormula.DOUBLEQ_STRING_LITERAL]:
                localctx = BaserowFormula.StringLiteralContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 15
                self.match(BaserowFormula.DOUBLEQ_STRING_LITERAL)
                pass
            elif token in [BaserowFormula.INTEGER_LITERAL]:
                localctx = BaserowFormula.IntegerLiteralContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 16
                self.match(BaserowFormula.INTEGER_LITERAL)
                pass
            elif token in [BaserowFormula.FIELD]:
                localctx = BaserowFormula.FieldReferenceContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 17
                self.match(BaserowFormula.FIELD)
                self.state = 18
                self.match(BaserowFormula.OPEN_PAREN)
                self.state = 19
                self.field_reference()
                self.state = 20
                self.match(BaserowFormula.CLOSE_PAREN)
                pass
            elif token in [BaserowFormula.FIELDBYID]:
                localctx = BaserowFormula.FieldByIdReferenceContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 22
                self.match(BaserowFormula.FIELDBYID)
                self.state = 23
                self.match(BaserowFormula.OPEN_PAREN)
                self.state = 24
                self.match(BaserowFormula.INTEGER_LITERAL)
                self.state = 25
                self.match(BaserowFormula.CLOSE_PAREN)
                pass
            elif token in [BaserowFormula.IDENTIFIER, BaserowFormula.IDENTIFIER_UNICODE]:
                localctx = BaserowFormula.FunctionCallContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 26
                self.func_name()
                self.state = 27
                self.match(BaserowFormula.OPEN_PAREN)
                self.state = 36
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << BaserowFormula.FIELD) | (1 << BaserowFormula.FIELDBYID) | (1 << BaserowFormula.INTEGER_LITERAL) | (1 << BaserowFormula.SINGLEQ_STRING_LITERAL) | (1 << BaserowFormula.DOUBLEQ_STRING_LITERAL) | (1 << BaserowFormula.IDENTIFIER) | (1 << BaserowFormula.IDENTIFIER_UNICODE))) != 0):
                    self.state = 28
                    self.expr(0)
                    self.state = 33
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while _la==BaserowFormula.COMMA:
                        self.state = 29
                        self.match(BaserowFormula.COMMA)
                        self.state = 30
                        self.expr(0)
                        self.state = 35
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)



                self.state = 38
                self.match(BaserowFormula.CLOSE_PAREN)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 47
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = BaserowFormula.BinaryOpContext(self, BaserowFormula.ExprContext(self, _parentctx, _parentState))
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                    self.state = 42
                    if not self.precpred(self._ctx, 4):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                    self.state = 43
                    localctx.op = self._input.LT(1)
                    _la = self._input.LA(1)
                    if not(_la==BaserowFormula.MINUS or _la==BaserowFormula.PLUS):
                        localctx.op = self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 44
                    self.expr(5) 
                self.state = 49
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
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
            self.state = 50
            self.identifier()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Field_referenceContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SINGLEQ_STRING_LITERAL(self):
            return self.getToken(BaserowFormula.SINGLEQ_STRING_LITERAL, 0)

        def DOUBLEQ_STRING_LITERAL(self):
            return self.getToken(BaserowFormula.DOUBLEQ_STRING_LITERAL, 0)

        def getRuleIndex(self):
            return BaserowFormula.RULE_field_reference

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterField_reference" ):
                listener.enterField_reference(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitField_reference" ):
                listener.exitField_reference(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitField_reference" ):
                return visitor.visitField_reference(self)
            else:
                return visitor.visitChildren(self)




    def field_reference(self):

        localctx = BaserowFormula.Field_referenceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_field_reference)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            _la = self._input.LA(1)
            if not(_la==BaserowFormula.SINGLEQ_STRING_LITERAL or _la==BaserowFormula.DOUBLEQ_STRING_LITERAL):
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
        self.enterRule(localctx, 8, self.RULE_identifier)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 54
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



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[1] = self.expr_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expr_sempred(self, localctx:ExprContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 4)
         




