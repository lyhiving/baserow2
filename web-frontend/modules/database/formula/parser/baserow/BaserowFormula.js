// Generated from /home/nigel/work/src/baserow/formula_lang/src/BaserowFormula.g4 by ANTLR 4.9.1
// jshint ignore: start
import antlr4 from 'antlr4';
import BaserowFormulaListener from './BaserowFormulaListener.js';
import BaserowFormulaVisitor from './BaserowFormulaVisitor.js';


const serializedATN = ["\u0003\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786",
    "\u5964\u0003Q)\u0004\u0002\t\u0002\u0004\u0003\t\u0003\u0004\u0004\t",
    "\u0004\u0004\u0005\t\u0005\u0004\u0006\t\u0006\u0003\u0002\u0003\u0002",
    "\u0003\u0002\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0007\u0003\u0017\n\u0003\f\u0003\u000e\u0003",
    "\u001a\u000b\u0003\u0005\u0003\u001c\n\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0005\u0003!\n\u0003\u0003\u0004\u0003\u0004\u0003\u0005",
    "\u0003\u0005\u0003\u0006\u0003\u0006\u0003\u0006\u0002\u0002\u0007\u0002",
    "\u0004\u0006\b\n\u0002\u0003\u0003\u0002\u0019\u001a\u0002(\u0002\f",
    "\u0003\u0002\u0002\u0002\u0004 \u0003\u0002\u0002\u0002\u0006\"\u0003",
    "\u0002\u0002\u0002\b$\u0003\u0002\u0002\u0002\n&\u0003\u0002\u0002\u0002",
    "\f\r\u0005\u0004\u0003\u0002\r\u000e\u0007\u0002\u0002\u0003\u000e\u0003",
    "\u0003\u0002\u0002\u0002\u000f!\u0007\u0017\u0002\u0002\u0010!\u0007",
    "\u0018\u0002\u0002\u0011\u0012\u0005\u0006\u0004\u0002\u0012\u001b\u0007",
    "\r\u0002\u0002\u0013\u0018\u0005\u0004\u0003\u0002\u0014\u0015\u0007",
    "\u0007\u0002\u0002\u0015\u0017\u0005\u0004\u0003\u0002\u0016\u0014\u0003",
    "\u0002\u0002\u0002\u0017\u001a\u0003\u0002\u0002\u0002\u0018\u0016\u0003",
    "\u0002\u0002\u0002\u0018\u0019\u0003\u0002\u0002\u0002\u0019\u001c\u0003",
    "\u0002\u0002\u0002\u001a\u0018\u0003\u0002\u0002\u0002\u001b\u0013\u0003",
    "\u0002\u0002\u0002\u001b\u001c\u0003\u0002\u0002\u0002\u001c\u001d\u0003",
    "\u0002\u0002\u0002\u001d\u001e\u0007\u000e\u0002\u0002\u001e!\u0003",
    "\u0002\u0002\u0002\u001f!\u0005\n\u0006\u0002 \u000f\u0003\u0002\u0002",
    "\u0002 \u0010\u0003\u0002\u0002\u0002 \u0011\u0003\u0002\u0002\u0002",
    " \u001f\u0003\u0002\u0002\u0002!\u0005\u0003\u0002\u0002\u0002\"#\u0005",
    "\n\u0006\u0002#\u0007\u0003\u0002\u0002\u0002$%\u0003\u0002\u0002\u0002",
    "%\t\u0003\u0002\u0002\u0002&\'\t\u0002\u0002\u0002\'\u000b\u0003\u0002",
    "\u0002\u0002\u0005\u0018\u001b "].join("");


const atn = new antlr4.atn.ATNDeserializer().deserialize(serializedATN);

const decisionsToDFA = atn.decisionToState.map( (ds, index) => new antlr4.dfa.DFA(ds, index) );

const sharedContextCache = new antlr4.PredictionContextCache();

export default class BaserowFormula extends antlr4.Parser {

    static grammarFileName = "BaserowFormula.g4";
    static literalNames = [ null, null, null, null, null, "','", "':'", 
                            "'::'", "'$'", "'$$'", "'*'", "'('", "')'", 
                            "'['", "']'", null, null, null, null, null, 
                            "'.'", null, null, null, null, "'&'", "'&&'", 
                            "'&<'", "'@@'", "'@>'", "'@'", "'!'", "'!!'", 
                            "'!='", "'^'", "'='", "'=>'", "'>'", "'>='", 
                            "'>>'", "'#'", "'#='", "'#>'", "'#>>'", "'##'", 
                            "'->'", "'->>'", "'-|-'", "'<'", "'<='", "'<@'", 
                            "'<^'", "'<>'", "'<->'", "'<<'", "'<<='", "'<?>'", 
                            "'-'", "'%'", "'|'", "'||'", "'||/'", "'|/'", 
                            "'+'", "'?'", "'?&'", "'?#'", "'?-'", "'?|'", 
                            "'/'", "'~'", "'~='", "'~>=~'", "'~>~'", "'~<=~'", 
                            "'~<~'", "'~*'", "'~~'", "';'" ];
    static symbolicNames = [ null, "WHITESPACE", "BLOCK_COMMENT", "LINE_COMMENT", 
                             "IF", "COMMA", "COLON", "COLON_COLON", "DOLLAR", 
                             "DOLLAR_DOLLAR", "STAR", "OPEN_PAREN", "CLOSE_PAREN", 
                             "OPEN_BRACKET", "CLOSE_BRACKET", "BIT_STRING", 
                             "REGEX_STRING", "NUMERIC_LITERAL", "INTEGER_LITERAL", 
                             "HEX_INTEGER_LITERAL", "DOT", "SINGLEQ_STRING_LITERAL", 
                             "DOUBLEQ_STRING_LITERAL", "IDENTIFIER", "IDENTIFIER_UNICODE", 
                             "AMP", "AMP_AMP", "AMP_LT", "AT_AT", "AT_GT", 
                             "AT_SIGN", "BANG", "BANG_BANG", "BANG_EQUAL", 
                             "CARET", "EQUAL", "EQUAL_GT", "GT", "GTE", 
                             "GT_GT", "HASH", "HASH_EQ", "HASH_GT", "HASH_GT_GT", 
                             "HASH_HASH", "HYPHEN_GT", "HYPHEN_GT_GT", "HYPHEN_PIPE_HYPHEN", 
                             "LT", "LTE", "LT_AT", "LT_CARET", "LT_GT", 
                             "LT_HYPHEN_GT", "LT_LT", "LT_LT_EQ", "LT_QMARK_GT", 
                             "MINUS", "PERCENT", "PIPE", "PIPE_PIPE", "PIPE_PIPE_SLASH", 
                             "PIPE_SLASH", "PLUS", "QMARK", "QMARK_AMP", 
                             "QMARK_HASH", "QMARK_HYPHEN", "QMARK_PIPE", 
                             "SLASH", "TIL", "TIL_EQ", "TIL_GTE_TIL", "TIL_GT_TIL", 
                             "TIL_LTE_TIL", "TIL_LT_TIL", "TIL_STAR", "TIL_TIL", 
                             "SEMI", "ErrorCharacter" ];
    static ruleNames = [ "root", "expr", "func_name", "func_call", "identifier" ];

    constructor(input) {
        super(input);
        this._interp = new antlr4.atn.ParserATNSimulator(this, atn, decisionsToDFA, sharedContextCache);
        this.ruleNames = BaserowFormula.ruleNames;
        this.literalNames = BaserowFormula.literalNames;
        this.symbolicNames = BaserowFormula.symbolicNames;
    }

    get atn() {
        return atn;
    }



	root() {
	    let localctx = new RootContext(this, this._ctx, this.state);
	    this.enterRule(localctx, 0, BaserowFormula.RULE_root);
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 10;
	        this.expr();
	        this.state = 11;
	        this.match(BaserowFormula.EOF);
	    } catch (re) {
	    	if(re instanceof antlr4.error.RecognitionException) {
		        localctx.exception = re;
		        this._errHandler.reportError(this, re);
		        this._errHandler.recover(this, re);
		    } else {
		    	throw re;
		    }
	    } finally {
	        this.exitRule();
	    }
	    return localctx;
	}



	expr() {
	    let localctx = new ExprContext(this, this._ctx, this.state);
	    this.enterRule(localctx, 2, BaserowFormula.RULE_expr);
	    var _la = 0; // Token type
	    try {
	        this.state = 30;
	        this._errHandler.sync(this);
	        var la_ = this._interp.adaptivePredict(this._input,2,this._ctx);
	        switch(la_) {
	        case 1:
	            localctx = new StringLiteralContext(this, localctx);
	            this.enterOuterAlt(localctx, 1);
	            this.state = 13;
	            this.match(BaserowFormula.SINGLEQ_STRING_LITERAL);
	            break;

	        case 2:
	            localctx = new StringLiteralContext(this, localctx);
	            this.enterOuterAlt(localctx, 2);
	            this.state = 14;
	            this.match(BaserowFormula.DOUBLEQ_STRING_LITERAL);
	            break;

	        case 3:
	            localctx = new FunctionCallContext(this, localctx);
	            this.enterOuterAlt(localctx, 3);
	            this.state = 15;
	            this.func_name();
	            this.state = 16;
	            this.match(BaserowFormula.OPEN_PAREN);
	            this.state = 25;
	            this._errHandler.sync(this);
	            _la = this._input.LA(1);
	            if((((_la) & ~0x1f) == 0 && ((1 << _la) & ((1 << BaserowFormula.SINGLEQ_STRING_LITERAL) | (1 << BaserowFormula.DOUBLEQ_STRING_LITERAL) | (1 << BaserowFormula.IDENTIFIER) | (1 << BaserowFormula.IDENTIFIER_UNICODE))) !== 0)) {
	                this.state = 17;
	                this.expr();
	                this.state = 22;
	                this._errHandler.sync(this);
	                _la = this._input.LA(1);
	                while(_la===BaserowFormula.COMMA) {
	                    this.state = 18;
	                    this.match(BaserowFormula.COMMA);
	                    this.state = 19;
	                    this.expr();
	                    this.state = 24;
	                    this._errHandler.sync(this);
	                    _la = this._input.LA(1);
	                }
	            }

	            this.state = 27;
	            this.match(BaserowFormula.CLOSE_PAREN);
	            break;

	        case 4:
	            localctx = new IndentifierContext(this, localctx);
	            this.enterOuterAlt(localctx, 4);
	            this.state = 29;
	            this.identifier();
	            break;

	        }
	    } catch (re) {
	    	if(re instanceof antlr4.error.RecognitionException) {
		        localctx.exception = re;
		        this._errHandler.reportError(this, re);
		        this._errHandler.recover(this, re);
		    } else {
		    	throw re;
		    }
	    } finally {
	        this.exitRule();
	    }
	    return localctx;
	}



	func_name() {
	    let localctx = new Func_nameContext(this, this._ctx, this.state);
	    this.enterRule(localctx, 4, BaserowFormula.RULE_func_name);
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 32;
	        this.identifier();
	    } catch (re) {
	    	if(re instanceof antlr4.error.RecognitionException) {
		        localctx.exception = re;
		        this._errHandler.reportError(this, re);
		        this._errHandler.recover(this, re);
		    } else {
		    	throw re;
		    }
	    } finally {
	        this.exitRule();
	    }
	    return localctx;
	}



	func_call() {
	    let localctx = new Func_callContext(this, this._ctx, this.state);
	    this.enterRule(localctx, 6, BaserowFormula.RULE_func_call);
	    try {
	        this.enterOuterAlt(localctx, 1);

	    } catch (re) {
	    	if(re instanceof antlr4.error.RecognitionException) {
		        localctx.exception = re;
		        this._errHandler.reportError(this, re);
		        this._errHandler.recover(this, re);
		    } else {
		    	throw re;
		    }
	    } finally {
	        this.exitRule();
	    }
	    return localctx;
	}



	identifier() {
	    let localctx = new IdentifierContext(this, this._ctx, this.state);
	    this.enterRule(localctx, 8, BaserowFormula.RULE_identifier);
	    var _la = 0; // Token type
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 36;
	        _la = this._input.LA(1);
	        if(!(_la===BaserowFormula.IDENTIFIER || _la===BaserowFormula.IDENTIFIER_UNICODE)) {
	        this._errHandler.recoverInline(this);
	        }
	        else {
	        	this._errHandler.reportMatch(this);
	            this.consume();
	        }
	    } catch (re) {
	    	if(re instanceof antlr4.error.RecognitionException) {
		        localctx.exception = re;
		        this._errHandler.reportError(this, re);
		        this._errHandler.recover(this, re);
		    } else {
		    	throw re;
		    }
	    } finally {
	        this.exitRule();
	    }
	    return localctx;
	}


}

BaserowFormula.EOF = antlr4.Token.EOF;
BaserowFormula.WHITESPACE = 1;
BaserowFormula.BLOCK_COMMENT = 2;
BaserowFormula.LINE_COMMENT = 3;
BaserowFormula.IF = 4;
BaserowFormula.COMMA = 5;
BaserowFormula.COLON = 6;
BaserowFormula.COLON_COLON = 7;
BaserowFormula.DOLLAR = 8;
BaserowFormula.DOLLAR_DOLLAR = 9;
BaserowFormula.STAR = 10;
BaserowFormula.OPEN_PAREN = 11;
BaserowFormula.CLOSE_PAREN = 12;
BaserowFormula.OPEN_BRACKET = 13;
BaserowFormula.CLOSE_BRACKET = 14;
BaserowFormula.BIT_STRING = 15;
BaserowFormula.REGEX_STRING = 16;
BaserowFormula.NUMERIC_LITERAL = 17;
BaserowFormula.INTEGER_LITERAL = 18;
BaserowFormula.HEX_INTEGER_LITERAL = 19;
BaserowFormula.DOT = 20;
BaserowFormula.SINGLEQ_STRING_LITERAL = 21;
BaserowFormula.DOUBLEQ_STRING_LITERAL = 22;
BaserowFormula.IDENTIFIER = 23;
BaserowFormula.IDENTIFIER_UNICODE = 24;
BaserowFormula.AMP = 25;
BaserowFormula.AMP_AMP = 26;
BaserowFormula.AMP_LT = 27;
BaserowFormula.AT_AT = 28;
BaserowFormula.AT_GT = 29;
BaserowFormula.AT_SIGN = 30;
BaserowFormula.BANG = 31;
BaserowFormula.BANG_BANG = 32;
BaserowFormula.BANG_EQUAL = 33;
BaserowFormula.CARET = 34;
BaserowFormula.EQUAL = 35;
BaserowFormula.EQUAL_GT = 36;
BaserowFormula.GT = 37;
BaserowFormula.GTE = 38;
BaserowFormula.GT_GT = 39;
BaserowFormula.HASH = 40;
BaserowFormula.HASH_EQ = 41;
BaserowFormula.HASH_GT = 42;
BaserowFormula.HASH_GT_GT = 43;
BaserowFormula.HASH_HASH = 44;
BaserowFormula.HYPHEN_GT = 45;
BaserowFormula.HYPHEN_GT_GT = 46;
BaserowFormula.HYPHEN_PIPE_HYPHEN = 47;
BaserowFormula.LT = 48;
BaserowFormula.LTE = 49;
BaserowFormula.LT_AT = 50;
BaserowFormula.LT_CARET = 51;
BaserowFormula.LT_GT = 52;
BaserowFormula.LT_HYPHEN_GT = 53;
BaserowFormula.LT_LT = 54;
BaserowFormula.LT_LT_EQ = 55;
BaserowFormula.LT_QMARK_GT = 56;
BaserowFormula.MINUS = 57;
BaserowFormula.PERCENT = 58;
BaserowFormula.PIPE = 59;
BaserowFormula.PIPE_PIPE = 60;
BaserowFormula.PIPE_PIPE_SLASH = 61;
BaserowFormula.PIPE_SLASH = 62;
BaserowFormula.PLUS = 63;
BaserowFormula.QMARK = 64;
BaserowFormula.QMARK_AMP = 65;
BaserowFormula.QMARK_HASH = 66;
BaserowFormula.QMARK_HYPHEN = 67;
BaserowFormula.QMARK_PIPE = 68;
BaserowFormula.SLASH = 69;
BaserowFormula.TIL = 70;
BaserowFormula.TIL_EQ = 71;
BaserowFormula.TIL_GTE_TIL = 72;
BaserowFormula.TIL_GT_TIL = 73;
BaserowFormula.TIL_LTE_TIL = 74;
BaserowFormula.TIL_LT_TIL = 75;
BaserowFormula.TIL_STAR = 76;
BaserowFormula.TIL_TIL = 77;
BaserowFormula.SEMI = 78;
BaserowFormula.ErrorCharacter = 79;

BaserowFormula.RULE_root = 0;
BaserowFormula.RULE_expr = 1;
BaserowFormula.RULE_func_name = 2;
BaserowFormula.RULE_func_call = 3;
BaserowFormula.RULE_identifier = 4;

class RootContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_root;
    }

	expr() {
	    return this.getTypedRuleContext(ExprContext,0);
	};

	EOF() {
	    return this.getToken(BaserowFormula.EOF, 0);
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterRoot(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitRoot(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitRoot(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}



class ExprContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_expr;
    }


	 
		copyFrom(ctx) {
			super.copyFrom(ctx);
		}

}


class IndentifierContext extends ExprContext {

    constructor(parser, ctx) {
        super(parser);
        super.copyFrom(ctx);
    }

	identifier() {
	    return this.getTypedRuleContext(IdentifierContext,0);
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterIndentifier(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitIndentifier(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitIndentifier(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}

BaserowFormula.IndentifierContext = IndentifierContext;

class StringLiteralContext extends ExprContext {

    constructor(parser, ctx) {
        super(parser);
        super.copyFrom(ctx);
    }

	SINGLEQ_STRING_LITERAL() {
	    return this.getToken(BaserowFormula.SINGLEQ_STRING_LITERAL, 0);
	};

	DOUBLEQ_STRING_LITERAL() {
	    return this.getToken(BaserowFormula.DOUBLEQ_STRING_LITERAL, 0);
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterStringLiteral(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitStringLiteral(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitStringLiteral(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}

BaserowFormula.StringLiteralContext = StringLiteralContext;

class FunctionCallContext extends ExprContext {

    constructor(parser, ctx) {
        super(parser);
        super.copyFrom(ctx);
    }

	func_name() {
	    return this.getTypedRuleContext(Func_nameContext,0);
	};

	OPEN_PAREN() {
	    return this.getToken(BaserowFormula.OPEN_PAREN, 0);
	};

	CLOSE_PAREN() {
	    return this.getToken(BaserowFormula.CLOSE_PAREN, 0);
	};

	expr = function(i) {
	    if(i===undefined) {
	        i = null;
	    }
	    if(i===null) {
	        return this.getTypedRuleContexts(ExprContext);
	    } else {
	        return this.getTypedRuleContext(ExprContext,i);
	    }
	};

	COMMA = function(i) {
		if(i===undefined) {
			i = null;
		}
	    if(i===null) {
	        return this.getTokens(BaserowFormula.COMMA);
	    } else {
	        return this.getToken(BaserowFormula.COMMA, i);
	    }
	};


	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterFunctionCall(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitFunctionCall(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitFunctionCall(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}

BaserowFormula.FunctionCallContext = FunctionCallContext;

class Func_nameContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_func_name;
    }

	identifier() {
	    return this.getTypedRuleContext(IdentifierContext,0);
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterFunc_name(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitFunc_name(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitFunc_name(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}



class Func_callContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_func_call;
    }


	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterFunc_call(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitFunc_call(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitFunc_call(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}



class IdentifierContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_identifier;
    }

	IDENTIFIER() {
	    return this.getToken(BaserowFormula.IDENTIFIER, 0);
	};

	IDENTIFIER_UNICODE() {
	    return this.getToken(BaserowFormula.IDENTIFIER_UNICODE, 0);
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterIdentifier(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitIdentifier(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitIdentifier(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}




BaserowFormula.RootContext = RootContext; 
BaserowFormula.ExprContext = ExprContext; 
BaserowFormula.Func_nameContext = Func_nameContext; 
BaserowFormula.Func_callContext = Func_callContext; 
BaserowFormula.IdentifierContext = IdentifierContext; 
