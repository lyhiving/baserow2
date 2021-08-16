// Generated from /home/nigel/work/src/baserow/formula_lang/src/BaserowFormula.g4 by ANTLR 4.9.1
// jshint ignore: start
import antlr4 from 'antlr4';
import BaserowFormulaListener from './BaserowFormulaListener.js';
import BaserowFormulaVisitor from './BaserowFormulaVisitor.js';


const serializedATN = ["\u0003\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786",
    "\u5964\u0003\u0344\u014a\u0004\u0002\t\u0002\u0004\u0003\t\u0003\u0004",
    "\u0004\t\u0004\u0004\u0005\t\u0005\u0004\u0006\t\u0006\u0004\u0007\t",
    "\u0007\u0004\b\t\b\u0004\t\t\t\u0004\n\t\n\u0004\u000b\t\u000b\u0004",
    "\f\t\f\u0004\r\t\r\u0003\u0002\u0003\u0002\u0003\u0002\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0006",
    "\u0003+\n\u0003\r\u0003\u000e\u0003,\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0006\u00033\n\u0003\r\u0003\u000e\u00034\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0005\u0003Z\n\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0005\u0003l\n\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0005\u0003q\n\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0005\u0003\u0081\n\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0005\u0003\u0093\n\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0005\u0003\u0098\n\u0003\u0003\u0003\u0003\u0003\u0005\u0003",
    "\u009c\n\u0003\u0003\u0003\u0006\u0003\u009f\n\u0003\r\u0003\u000e\u0003",
    "\u00a0\u0003\u0003\u0003\u0003\u0003\u0003\u0006\u0003\u00a6\n\u0003",
    "\r\u0003\u000e\u0003\u00a7\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0005\u0003\u00b5\n\u0003\u0003\u0003\u0003\u0003",
    "\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0003\u0007\u0003\u00bd\n",
    "\u0003\f\u0003\u000e\u0003\u00c0\u000b\u0003\u0003\u0004\u0003\u0004",
    "\u0003\u0004\u0003\u0004\u0003\u0004\u0005\u0004\u00c7\n\u0004\u0003",
    "\u0004\u0003\u0004\u0003\u0004\u0003\u0004\u0003\u0004\u0003\u0004\u0007",
    "\u0004\u00cf\n\u0004\f\u0004\u000e\u0004\u00d2\u000b\u0004\u0003\u0005",
    "\u0003\u0005\u0003\u0005\u0003\u0005\u0003\u0005\u0003\u0005\u0003\u0005",
    "\u0006\u0005\u00db\n\u0005\r\u0005\u000e\u0005\u00dc\u0003\u0005\u0003",
    "\u0005\u0005\u0005\u00e1\n\u0005\u0003\u0005\u0003\u0005\u0003\u0005",
    "\u0003\u0005\u0003\u0005\u0003\u0005\u0003\u0005\u0003\u0005\u0006\u0005",
    "\u00eb\n\u0005\r\u0005\u000e\u0005\u00ec\u0003\u0005\u0003\u0005\u0005",
    "\u0005\u00f1\n\u0005\u0003\u0005\u0003\u0005\u0005\u0005\u00f5\n\u0005",
    "\u0003\u0006\u0003\u0006\u0003\u0006\u0003\u0006\u0007\u0006\u00fb\n",
    "\u0006\f\u0006\u000e\u0006\u00fe\u000b\u0006\u0003\u0006\u0003\u0006",
    "\u0003\u0007\u0003\u0007\u0003\b\u0003\b\u0003\t\u0003\t\u0003\n\u0003",
    "\n\u0003\n\u0003\n\u0003\n\u0003\n\u0003\n\u0003\n\u0003\n\u0003\n\u0003",
    "\n\u0007\n\u0113\n\n\f\n\u000e\n\u0116\u000b\n\u0003\n\u0003\n\u0003",
    "\n\u0005\n\u011b\n\n\u0005\n\u011d\n\n\u0003\n\u0003\n\u0005\n\u0121",
    "\n\n\u0003\u000b\u0003\u000b\u0003\u000b\u0003\u000b\u0003\u000b\u0003",
    "\u000b\u0003\u000b\u0003\u000b\u0005\u000b\u012b\n\u000b\u0003\u000b",
    "\u0003\u000b\u0003\u000b\u0003\u000b\u0003\u000b\u0003\u000b\u0007\u000b",
    "\u0133\n\u000b\f\u000b\u000e\u000b\u0136\u000b\u000b\u0003\f\u0003\f",
    "\u0003\r\u0003\r\u0003\r\u0003\r\u0003\r\u0003\r\u0005\r\u0140\n\r\u0003",
    "\r\u0003\r\u0003\r\u0007\r\u0145\n\r\f\r\u000e\r\u0148\u000b\r\u0003",
    "\r\u0002\u0006\u0004\u0006\u0014\u0018\u000e\u0002\u0004\u0006\b\n\f",
    "\u000e\u0010\u0012\u0014\u0016\u0018\u0002\f\u0003\u0002\u02fd\u02fd",
    "\u0006\u0002\u0314\u0314\u0316\u0316\u032f\u032f\u0335\u0335\u0004\u0002",
    "\u0339\u0339\u033c\u033c\u0004\u0002\u0012\u0012\u016f\u016f\u0004\u0002",
    "\u0318\u0318\u0333\u0334\u0005\u0002\u02ff\u02ff\u0330\u0330\u033b\u033b",
    "\u0004\u0002\u032f\u032f\u0335\u0335\u000e\u0002\u0019\u0019\u016f\u016f",
    "\u0189\u0189\u030f\u0313\u031a\u031a\u031d\u0325\u0328\u0329\u032b\u032e",
    "\u0331\u0332\u0336\u0338\u033a\u033a\u033c\u0343\u0007\u0002\u0317\u0317",
    "\u0319\u0319\u031b\u031c\u0326\u0327\u032a\u032a\u0004\u0002\u0143\u0143",
    "\u026c\u026c\u0002\u018a\u0002\u001a\u0003\u0002\u0002\u0002\u0004Y",
    "\u0003\u0002\u0002\u0002\u0006\u00c6\u0003\u0002\u0002\u0002\b\u00f4",
    "\u0003\u0002\u0002\u0002\n\u00f6\u0003\u0002\u0002\u0002\f\u0101\u0003",
    "\u0002\u0002\u0002\u000e\u0103\u0003\u0002\u0002\u0002\u0010\u0105\u0003",
    "\u0002\u0002\u0002\u0012\u0120\u0003\u0002\u0002\u0002\u0014\u012a\u0003",
    "\u0002\u0002\u0002\u0016\u0137\u0003\u0002\u0002\u0002\u0018\u013f\u0003",
    "\u0002\u0002\u0002\u001a\u001b\u0005\u0004\u0003\u0002\u001b\u001c\u0007",
    "\u0002\u0002\u0003\u001c\u0003\u0003\u0002\u0002\u0002\u001d\u001e\b",
    "\u0003\u0001\u0002\u001eZ\u0007\u0174\u0002\u0002\u001fZ\u0007\u0088",
    "\u0002\u0002 Z\u0007\u008c\u0002\u0002!Z\u0007\u008d\u0002\u0002\"Z",
    "\u0007\u0307\u0002\u0002#Z\u0007\u0308\u0002\u0002$Z\u0007\u0306\u0002",
    "\u0002%Z\u0007\u030a\u0002\u0002&Z\u0007\u0304\u0002\u0002\'Z\u0007",
    "\u0305\u0002\u0002(*\u0007\u02fe\u0002\u0002)+\n\u0002\u0002\u0002*",
    ")\u0003\u0002\u0002\u0002+,\u0003\u0002\u0002\u0002,*\u0003\u0002\u0002",
    "\u0002,-\u0003\u0002\u0002\u0002-.\u0003\u0002\u0002\u0002.Z\u0007\u02fe",
    "\u0002\u0002/0\u0007\u02fd\u0002\u000202\u0005\u0018\r\u000213\n\u0002",
    "\u0002\u000221\u0003\u0002\u0002\u000234\u0003\u0002\u0002\u000242\u0003",
    "\u0002\u0002\u000245\u0003\u0002\u0002\u000256\u0003\u0002\u0002\u0002",
    "67\u0007\u02fd\u0002\u000278\u0005\u0018\r\u000289\u0007\u02fd\u0002",
    "\u00029Z\u0003\u0002\u0002\u0002:Z\u0005\u0006\u0004\u0002;Z\u0005\n",
    "\u0006\u0002<=\u0007\u0300\u0002\u0002=>\u0005\u0004\u0003\u0002>?\u0007",
    "\u0301\u0002\u0002?Z\u0003\u0002\u0002\u0002@A\u0005\f\u0007\u0002A",
    "B\u0007\u030a\u0002\u0002BZ\u0003\u0002\u0002\u0002CD\t\u0003\u0002",
    "\u0002DZ\u0005\u0004\u0003\u001cEF\t\u0004\u0002\u0002FZ\u0005\u0004",
    "\u0003\u001bGH\t\u0005\u0002\u0002HZ\u0005\u0004\u0003\u000fIZ\u0005",
    "\u0012\n\u0002JZ\u0005\u0018\r\u0002KL\u0007A\u0002\u0002LM\u0007\u0300",
    "\u0002\u0002MN\u0005\u0004\u0003\u0002NO\u0007\u001d\u0002\u0002OP\u0005",
    "\u000e\b\u0002PQ\u0007\u0301\u0002\u0002QZ\u0003\u0002\u0002\u0002R",
    "Z\u0005\b\u0005\u0002ST\u0005\u000e\b\u0002TU\u0005\u0004\u0003\bUZ",
    "\u0003\u0002\u0002\u0002VW\u0007\u00d5\u0002\u0002WZ\u0005\u0004\u0003",
    "\u0004XZ\u0007\u030d\u0002\u0002Y\u001d\u0003\u0002\u0002\u0002Y\u001f",
    "\u0003\u0002\u0002\u0002Y \u0003\u0002\u0002\u0002Y!\u0003\u0002\u0002",
    "\u0002Y\"\u0003\u0002\u0002\u0002Y#\u0003\u0002\u0002\u0002Y$\u0003",
    "\u0002\u0002\u0002Y%\u0003\u0002\u0002\u0002Y&\u0003\u0002\u0002\u0002",
    "Y\'\u0003\u0002\u0002\u0002Y(\u0003\u0002\u0002\u0002Y/\u0003\u0002",
    "\u0002\u0002Y:\u0003\u0002\u0002\u0002Y;\u0003\u0002\u0002\u0002Y<\u0003",
    "\u0002\u0002\u0002Y@\u0003\u0002\u0002\u0002YC\u0003\u0002\u0002\u0002",
    "YE\u0003\u0002\u0002\u0002YG\u0003\u0002\u0002\u0002YI\u0003\u0002\u0002",
    "\u0002YJ\u0003\u0002\u0002\u0002YK\u0003\u0002\u0002\u0002YR\u0003\u0002",
    "\u0002\u0002YS\u0003\u0002\u0002\u0002YV\u0003\u0002\u0002\u0002YX\u0003",
    "\u0002\u0002\u0002Z\u00be\u0003\u0002\u0002\u0002[\\\f\u0019\u0002\u0002",
    "\\]\t\u0006\u0002\u0002]\u00bd\u0005\u0004\u0003\u001a^_\f\u0018\u0002",
    "\u0002_`\t\u0007\u0002\u0002`\u00bd\u0005\u0004\u0003\u0019ab\f\u0017",
    "\u0002\u0002bc\t\b\u0002\u0002c\u00bd\u0005\u0004\u0003\u0018de\f\u0016",
    "\u0002\u0002ef\t\t\u0002\u0002f\u00bd\u0005\u0004\u0003\u0017gk\f\u0015",
    "\u0002\u0002hi\u0007\u016f\u0002\u0002il\u0007\u0137\u0002\u0002jl\u0007",
    "\u0137\u0002\u0002kh\u0003\u0002\u0002\u0002kj\u0003\u0002\u0002\u0002",
    "lm\u0003\u0002\u0002\u0002m\u00bd\u0005\u0004\u0003\u0016np\f\u0014",
    "\u0002\u0002oq\u0007\u016f\u0002\u0002po\u0003\u0002\u0002\u0002pq\u0003",
    "\u0002\u0002\u0002qr\u0003\u0002\u0002\u0002rs\u0007-\u0002\u0002st",
    "\u0005\u0004\u0003\u0002tu\u0007\u0019\u0002\u0002uv\u0005\u0004\u0003",
    "\u0015v\u00bd\u0003\u0002\u0002\u0002wx\f\u0013\u0002\u0002xy\u0007",
    "\u010b\u0002\u0002y\u00bd\u0005\u0004\u0003\u0014z{\f\u0012\u0002\u0002",
    "{|\t\n\u0002\u0002|\u00bd\u0005\u0004\u0003\u0013}~\f\u0010\u0002\u0002",
    "~\u0080\u0007\u0123\u0002\u0002\u007f\u0081\u0007\u016f\u0002\u0002",
    "\u0080\u007f\u0003\u0002\u0002\u0002\u0080\u0081\u0003\u0002\u0002\u0002",
    "\u0081\u0082\u0003\u0002\u0002\u0002\u0082\u0083\u0007\u00ba\u0002\u0002",
    "\u0083\u0084\u0007\u00ee\u0002\u0002\u0084\u00bd\u0005\u0004\u0003\u0011",
    "\u0085\u0086\f\u001f\u0002\u0002\u0086\u0087\u0007\u0302\u0002\u0002",
    "\u0087\u0088\u0005\u0004\u0003\u0002\u0088\u0089\u0007\u0303\u0002\u0002",
    "\u0089\u00bd\u0003\u0002\u0002\u0002\u008a\u008b\f\u001a\u0002\u0002",
    "\u008b\u00bd\u0007\u0315\u0002\u0002\u008c\u008d\f\u0011\u0002\u0002",
    "\u008d\u0092\u0007\u0123\u0002\u0002\u008e\u0093\u0005\u0006\u0004\u0002",
    "\u008f\u0093\u0007\u0174\u0002\u0002\u0090\u0091\u0007\u016f\u0002\u0002",
    "\u0091\u0093\u0007\u0174\u0002\u0002\u0092\u008e\u0003\u0002\u0002\u0002",
    "\u0092\u008f\u0003\u0002\u0002\u0002\u0092\u0090\u0003\u0002\u0002\u0002",
    "\u0093\u00bd\u0003\u0002\u0002\u0002\u0094\u009e\f\n\u0002\u0002\u0095",
    "\u0097\u0007\u0302\u0002\u0002\u0096\u0098\u0005\u0004\u0003\u0002\u0097",
    "\u0096\u0003\u0002\u0002\u0002\u0097\u0098\u0003\u0002\u0002\u0002\u0098",
    "\u0099\u0003\u0002\u0002\u0002\u0099\u009b\u0007\u02fb\u0002\u0002\u009a",
    "\u009c\u0005\u0004\u0003\u0002\u009b\u009a\u0003\u0002\u0002\u0002\u009b",
    "\u009c\u0003\u0002\u0002\u0002\u009c\u009d\u0003\u0002\u0002\u0002\u009d",
    "\u009f\u0007\u0303\u0002\u0002\u009e\u0095\u0003\u0002\u0002\u0002\u009f",
    "\u00a0\u0003\u0002\u0002\u0002\u00a0\u009e\u0003\u0002\u0002\u0002\u00a0",
    "\u00a1\u0003\u0002\u0002\u0002\u00a1\u00bd\u0003\u0002\u0002\u0002\u00a2",
    "\u00a5\f\t\u0002\u0002\u00a3\u00a4\u0007\u02fc\u0002\u0002\u00a4\u00a6",
    "\u0005\u000e\b\u0002\u00a5\u00a3\u0003\u0002\u0002\u0002\u00a6\u00a7",
    "\u0003\u0002\u0002\u0002\u00a7\u00a5\u0003\u0002\u0002\u0002\u00a7\u00a8",
    "\u0003\u0002\u0002\u0002\u00a8\u00bd\u0003\u0002\u0002\u0002\u00a9\u00aa",
    "\f\u0007\u0002\u0002\u00aa\u00ab\u0007\u0123\u0002\u0002\u00ab\u00ac",
    "\u0007\u017d\u0002\u0002\u00ac\u00ad\u0007\u0300\u0002\u0002\u00ad\u00ae",
    "\u0005\u000e\b\u0002\u00ae\u00af\u0007\u0301\u0002\u0002\u00af\u00bd",
    "\u0003\u0002\u0002\u0002\u00b0\u00b1\f\u0006\u0002\u0002\u00b1\u00b4",
    "\u0007\u0309\u0002\u0002\u00b2\u00b5\u0005\u0018\r\u0002\u00b3\u00b5",
    "\u0007\u02ff\u0002\u0002\u00b4\u00b2\u0003\u0002\u0002\u0002\u00b4\u00b3",
    "\u0003\u0002\u0002\u0002\u00b5\u00bd\u0003\u0002\u0002\u0002\u00b6\u00b7",
    "\f\u0005\u0002\u0002\u00b7\u00b8\u0007#\u0002\u0002\u00b8\u00b9\u0007",
    "\u0244\u0002\u0002\u00b9\u00ba\u0007\u0290\u0002\u0002\u00ba\u00bb\u0003",
    "\u0002\u0002\u0002\u00bb\u00bd\u0007\u030a\u0002\u0002\u00bc[\u0003",
    "\u0002\u0002\u0002\u00bc^\u0003\u0002\u0002\u0002\u00bca\u0003\u0002",
    "\u0002\u0002\u00bcd\u0003\u0002\u0002\u0002\u00bcg\u0003\u0002\u0002",
    "\u0002\u00bcn\u0003\u0002\u0002\u0002\u00bcw\u0003\u0002\u0002\u0002",
    "\u00bcz\u0003\u0002\u0002\u0002\u00bc}\u0003\u0002\u0002\u0002\u00bc",
    "\u0085\u0003\u0002\u0002\u0002\u00bc\u008a\u0003\u0002\u0002\u0002\u00bc",
    "\u008c\u0003\u0002\u0002\u0002\u00bc\u0094\u0003\u0002\u0002\u0002\u00bc",
    "\u00a2\u0003\u0002\u0002\u0002\u00bc\u00a9\u0003\u0002\u0002\u0002\u00bc",
    "\u00b0\u0003\u0002\u0002\u0002\u00bc\u00b6\u0003\u0002\u0002\u0002\u00bd",
    "\u00c0\u0003\u0002\u0002\u0002\u00be\u00bc\u0003\u0002\u0002\u0002\u00be",
    "\u00bf\u0003\u0002\u0002\u0002\u00bf\u0005\u0003\u0002\u0002\u0002\u00c0",
    "\u00be\u0003\u0002\u0002\u0002\u00c1\u00c2\b\u0004\u0001\u0002\u00c2",
    "\u00c7\u0007\u025b\u0002\u0002\u00c3\u00c7\u0007\u00dc\u0002\u0002\u00c4",
    "\u00c5\u0007\u016f\u0002\u0002\u00c5\u00c7\u0005\u0006\u0004\u0005\u00c6",
    "\u00c1\u0003\u0002\u0002\u0002\u00c6\u00c3\u0003\u0002\u0002\u0002\u00c6",
    "\u00c4\u0003\u0002\u0002\u0002\u00c7\u00d0\u0003\u0002\u0002\u0002\u00c8",
    "\u00c9\f\u0004\u0002\u0002\u00c9\u00ca\u0007\u0019\u0002\u0002\u00ca",
    "\u00cf\u0005\u0006\u0004\u0005\u00cb\u00cc\f\u0003\u0002\u0002\u00cc",
    "\u00cd\u0007\u0189\u0002\u0002\u00cd\u00cf\u0005\u0006\u0004\u0004\u00ce",
    "\u00c8\u0003\u0002\u0002\u0002\u00ce\u00cb\u0003\u0002\u0002\u0002\u00cf",
    "\u00d2\u0003\u0002\u0002\u0002\u00d0\u00ce\u0003\u0002\u0002\u0002\u00d0",
    "\u00d1\u0003\u0002\u0002\u0002\u00d1\u0007\u0003\u0002\u0002\u0002\u00d2",
    "\u00d0\u0003\u0002\u0002\u0002\u00d3\u00d4\u0007@\u0002\u0002\u00d4",
    "\u00da\u0005\u0004\u0003\u0002\u00d5\u00d6\u0007\u0283\u0002\u0002\u00d6",
    "\u00d7\u0005\u0004\u0003\u0002\u00d7\u00d8\u0007\u0242\u0002\u0002\u00d8",
    "\u00d9\u0005\u0004\u0003\u0002\u00d9\u00db\u0003\u0002\u0002\u0002\u00da",
    "\u00d5\u0003\u0002\u0002\u0002\u00db\u00dc\u0003\u0002\u0002\u0002\u00dc",
    "\u00da\u0003\u0002\u0002\u0002\u00dc\u00dd\u0003\u0002\u0002\u0002\u00dd",
    "\u00e0\u0003\u0002\u0002\u0002\u00de\u00df\u0007\u00c4\u0002\u0002\u00df",
    "\u00e1\u0005\u0004\u0003\u0002\u00e0\u00de\u0003\u0002\u0002\u0002\u00e0",
    "\u00e1\u0003\u0002\u0002\u0002\u00e1\u00e2\u0003\u0002\u0002\u0002\u00e2",
    "\u00e3\u0007\u00c8\u0002\u0002\u00e3\u00f5\u0003\u0002\u0002\u0002\u00e4",
    "\u00ea\u0007@\u0002\u0002\u00e5\u00e6\u0007\u0283\u0002\u0002\u00e6",
    "\u00e7\u0005\u0014\u000b\u0002\u00e7\u00e8\u0007\u0242\u0002\u0002\u00e8",
    "\u00e9\u0005\u0004\u0003\u0002\u00e9\u00eb\u0003\u0002\u0002\u0002\u00ea",
    "\u00e5\u0003\u0002\u0002\u0002\u00eb\u00ec\u0003\u0002\u0002\u0002\u00ec",
    "\u00ea\u0003\u0002\u0002\u0002\u00ec\u00ed\u0003\u0002\u0002\u0002\u00ed",
    "\u00f0\u0003\u0002\u0002\u0002\u00ee\u00ef\u0007\u00c4\u0002\u0002\u00ef",
    "\u00f1\u0005\u0004\u0003\u0002\u00f0\u00ee\u0003\u0002\u0002\u0002\u00f0",
    "\u00f1\u0003\u0002\u0002\u0002\u00f1\u00f2\u0003\u0002\u0002\u0002\u00f2",
    "\u00f3\u0007\u00c8\u0002\u0002\u00f3\u00f5\u0003\u0002\u0002\u0002\u00f4",
    "\u00d3\u0003\u0002\u0002\u0002\u00f4\u00e4\u0003\u0002\u0002\u0002\u00f5",
    "\t\u0003\u0002\u0002\u0002\u00f6\u00f7\u0007\u0300\u0002\u0002\u00f7",
    "\u00fc\u0005\u0004\u0003\u0002\u00f8\u00f9\u0007\u02fa\u0002\u0002\u00f9",
    "\u00fb\u0005\u0004\u0003\u0002\u00fa\u00f8\u0003\u0002\u0002\u0002\u00fb",
    "\u00fe\u0003\u0002\u0002\u0002\u00fc\u00fa\u0003\u0002\u0002\u0002\u00fc",
    "\u00fd\u0003\u0002\u0002\u0002\u00fd\u00ff\u0003\u0002\u0002\u0002\u00fe",
    "\u00fc\u0003\u0002\u0002\u0002\u00ff\u0100\u0007\u0301\u0002\u0002\u0100",
    "\u000b\u0003\u0002\u0002\u0002\u0101\u0102\u0007\u02f1\u0002\u0002\u0102",
    "\r\u0003\u0002\u0002\u0002\u0103\u0104\u0005\f\u0007\u0002\u0104\u000f",
    "\u0003\u0002\u0002\u0002\u0105\u0106\u0005\u0018\r\u0002\u0106\u0011",
    "\u0003\u0002\u0002\u0002\u0107\u0108\u0005\u0010\t\u0002\u0108\u0109",
    "\u0007\u0300\u0002\u0002\u0109\u010a\u0007\u027e\u0002\u0002\u010a\u010b",
    "\u0005\u0004\u0003\u0002\u010b\u010c\u0007\u0301\u0002\u0002\u010c\u0121",
    "\u0003\u0002\u0002\u0002\u010d\u010e\u0005\u0010\t\u0002\u010e\u011c",
    "\u0007\u0300\u0002\u0002\u010f\u0114\u0005\u0004\u0003\u0002\u0110\u0111",
    "\u0007\u02fa\u0002\u0002\u0111\u0113\u0005\u0004\u0003\u0002\u0112\u0110",
    "\u0003\u0002\u0002\u0002\u0113\u0116\u0003\u0002\u0002\u0002\u0114\u0112",
    "\u0003\u0002\u0002\u0002\u0114\u0115\u0003\u0002\u0002\u0002\u0115\u011a",
    "\u0003\u0002\u0002\u0002\u0116\u0114\u0003\u0002\u0002\u0002\u0117\u0118",
    "\u0007\u02fa\u0002\u0002\u0118\u0119\u0007\u027e\u0002\u0002\u0119\u011b",
    "\u0005\u0004\u0003\u0002\u011a\u0117\u0003\u0002\u0002\u0002\u011a\u011b",
    "\u0003\u0002\u0002\u0002\u011b\u011d\u0003\u0002\u0002\u0002\u011c\u010f",
    "\u0003\u0002\u0002\u0002\u011c\u011d\u0003\u0002\u0002\u0002\u011d\u011e",
    "\u0003\u0002\u0002\u0002\u011e\u011f\u0007\u0301\u0002\u0002\u011f\u0121",
    "\u0003\u0002\u0002\u0002\u0120\u0107\u0003\u0002\u0002\u0002\u0120\u010d",
    "\u0003\u0002\u0002\u0002\u0121\u0013\u0003\u0002\u0002\u0002\u0122\u0123",
    "\b\u000b\u0001\u0002\u0123\u012b\u0005\u0004\u0003\u0002\u0124\u0125",
    "\u0007\u0300\u0002\u0002\u0125\u0126\u0005\u0014\u000b\u0002\u0126\u0127",
    "\u0007\u0301\u0002\u0002\u0127\u012b\u0003\u0002\u0002\u0002\u0128\u0129",
    "\u0007\u016f\u0002\u0002\u0129\u012b\u0005\u0014\u000b\u0003\u012a\u0122",
    "\u0003\u0002\u0002\u0002\u012a\u0124\u0003\u0002\u0002\u0002\u012a\u0128",
    "\u0003\u0002\u0002\u0002\u012b\u0134\u0003\u0002\u0002\u0002\u012c\u012d",
    "\f\u0005\u0002\u0002\u012d\u012e\u0007\u0019\u0002\u0002\u012e\u0133",
    "\u0005\u0014\u000b\u0006\u012f\u0130\f\u0004\u0002\u0002\u0130\u0131",
    "\u0007\u0189\u0002\u0002\u0131\u0133\u0005\u0014\u000b\u0005\u0132\u012c",
    "\u0003\u0002\u0002\u0002\u0132\u012f\u0003\u0002\u0002\u0002\u0133\u0136",
    "\u0003\u0002\u0002\u0002\u0134\u0132\u0003\u0002\u0002\u0002\u0134\u0135",
    "\u0003\u0002\u0002\u0002\u0135\u0015\u0003\u0002\u0002\u0002\u0136\u0134",
    "\u0003\u0002\u0002\u0002\u0137\u0138\t\u000b\u0002\u0002\u0138\u0017",
    "\u0003\u0002\u0002\u0002\u0139\u013a\b\r\u0001\u0002\u013a\u0140\u0005",
    "\u0016\f\u0002\u013b\u0140\u0007\u030b\u0002\u0002\u013c\u0140\u0007",
    "\u030c\u0002\u0002\u013d\u0140\u0005\f\u0007\u0002\u013e\u0140\u0007",
    "\u030e\u0002\u0002\u013f\u0139\u0003\u0002\u0002\u0002\u013f\u013b\u0003",
    "\u0002\u0002\u0002\u013f\u013c\u0003\u0002\u0002\u0002\u013f\u013d\u0003",
    "\u0002\u0002\u0002\u013f\u013e\u0003\u0002\u0002\u0002\u0140\u0146\u0003",
    "\u0002\u0002\u0002\u0141\u0142\f\u0005\u0002\u0002\u0142\u0143\u0007",
    "\u0309\u0002\u0002\u0143\u0145\u0005\u0018\r\u0006\u0144\u0141\u0003",
    "\u0002\u0002\u0002\u0145\u0148\u0003\u0002\u0002\u0002\u0146\u0144\u0003",
    "\u0002\u0002\u0002\u0146\u0147\u0003\u0002\u0002\u0002\u0147\u0019\u0003",
    "\u0002\u0002\u0002\u0148\u0146\u0003\u0002\u0002\u0002\",4Ykp\u0080",
    "\u0092\u0097\u009b\u00a0\u00a7\u00b4\u00bc\u00be\u00c6\u00ce\u00d0\u00dc",
    "\u00e0\u00ec\u00f0\u00f4\u00fc\u0114\u011a\u011c\u0120\u012a\u0132\u0134",
    "\u013f\u0146"].join("");


const atn = new antlr4.atn.ATNDeserializer().deserialize(serializedATN);

const decisionsToDFA = atn.decisionToState.map( (ds, index) => new antlr4.dfa.DFA(ds, index) );

const sharedContextCache = new antlr4.PredictionContextCache();

export default class BaserowFormula extends antlr4.Parser {

    static grammarFileName = "BaserowFormula.g4";
    static literalNames = [ null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, 
                            "','", "':'", "'::'", "'$'", "'$$'", "'*'", 
                            "'('", "')'", "'['", "']'", null, null, null, 
                            null, null, "'.'", null, null, null, null, null, 
                            "'&'", "'&&'", "'&<'", "'@@'", "'@>'", "'@'", 
                            "'!'", "'!!'", "'!='", "'^'", "'='", "'=>'", 
                            "'>'", "'>='", "'>>'", "'#'", "'#='", "'#>'", 
                            "'#>>'", "'##'", "'->'", "'->>'", "'-|-'", "'<'", 
                            "'<='", "'<@'", "'<^'", "'<>'", "'<->'", "'<<'", 
                            "'<<='", "'<?>'", "'-'", "'%'", "'|'", "'||'", 
                            "'||/'", "'|/'", "'+'", "'?'", "'?&'", "'?#'", 
                            "'?-'", "'?|'", "'/'", "'~'", "'~='", "'~>=~'", 
                            "'~>~'", "'~<=~'", "'~<~'", "'~*'", "'~~'", 
                            "';'" ];
    static symbolicNames = [ null, "WHITESPACE", "BLOCK_COMMENT", "LINE_COMMENT", 
                             "A_", "ABORT", "ABS", "ABSOLUTE", "ACCESS", 
                             "ACTION", "ADA", "ADD", "ADMIN", "AFTER", "AGGREGATE", 
                             "ALIAS", "ALL", "ALLOCATE", "ALSO", "ALTER", 
                             "ALWAYS", "ANALYSE", "ANALYZE", "AND", "ANY", 
                             "ARE", "ARRAY", "AS", "ASC", "ASENSITIVE", 
                             "ASSERTION", "ASSIGNMENT", "ASYMMETRIC", "AT", 
                             "ATOMIC", "ATTRIBUTE", "ATTRIBUTES", "AUTHORIZATION", 
                             "AVG", "BACKWARD", "BEFORE", "BEGIN", "BERNOULLI", 
                             "BETWEEN", "BIGINT", "BINARY", "BIT", "BIT_LENGTH", 
                             "BITVAR", "BLOB", "BOOLEAN", "BOTH", "BREADTH", 
                             "BUFFERS", "BY", "C_", "CACHE", "CALL", "CALLED", 
                             "CARDINALITY", "CASCADE", "CASCADED", "CASE", 
                             "CAST", "CATALOG", "CATALOG_NAME", "CEIL", 
                             "CEILING", "CHAIN", "CHAR", "CHAR_LENGTH", 
                             "CHARACTER", "CHARACTER_LENGTH", "CHARACTER_SET_CATALOG", 
                             "CHARACTER_SET_NAME", "CHARACTER_SET_SCHEMA", 
                             "CHARACTERISTICS", "CHARACTERS", "CHECK", "CHECKED", 
                             "CHECKPOINT", "CLASS", "CLASS_ORIGIN", "CLOB", 
                             "CLOSE", "CLUSTER", "COALESCE", "COBOL", "COLLATE", 
                             "COLLATION", "COLLATION_CATALOG", "COLLATION_NAME", 
                             "COLLATION_SCHEMA", "COLLECT", "COLUMN", "COLUMN_NAME", 
                             "COMMAND_FUNCTION", "COMMAND_FUNCTION_CODE", 
                             "COMMENT", "COMMIT", "COMMITTED", "COMPLETION", 
                             "CONDITION", "CONDITION_NUMBER", "CONFIGURATION", 
                             "CONFLICT", "CONNECT", "CONNECTION", "CONNECTION_NAME", 
                             "CONSTRAINT", "CONSTRAINT_CATALOG", "CONSTRAINT_NAME", 
                             "CONSTRAINT_SCHEMA", "CONSTRAINTS", "CONSTRUCTOR", 
                             "CONTAINS", "CONTINUE", "CONVERSION", "CONVERT", 
                             "COPY", "CORR", "CORRESPONDING", "COSTS", "COUNT", 
                             "COVAR_POP", "COVAR_SAMP", "CREATE", "CREATEDB", 
                             "CREATEUSER", "CROSS", "CSV", "CUBE", "CUME_DIST", 
                             "CURRENT", "CURRENT_DATE", "CURRENT_DEFAULT_TRANSFORM_GROUP", 
                             "CURRENT_PATH", "CURRENT_ROLE", "CURRENT_TIME", 
                             "CURRENT_TIMESTAMP", "CURRENT_TRANSFORM_GROUP_FOR_TYPE", 
                             "CURRENT_USER", "CURSOR", "CURSOR_NAME", "CYCLE", 
                             "DATA", "DATABASE", "DATE", "DATETIME_INTERVAL_CODE", 
                             "DATETIME_INTERVAL_PRECISION", "DAY", "DEALLOCATE", 
                             "DEC", "DECIMAL", "DECLARE", "DEFAULT", "DEFAULTS", 
                             "DEFERABLE", "DEFERRABLE", "DEFERRED", "DEFINED", 
                             "DEFINER", "DEGREE", "DELETE", "DELIMITER", 
                             "DELIMITERS", "DENSE_RANK", "DEPENDS", "DEPTH", 
                             "DEREF", "DERIVED", "DESC", "DESCRIBE", "DESCRIPTOR", 
                             "DESTROY", "DESTRUCTOR", "DETERMINISTIC", "DIAGNOSTICS", 
                             "DICTIONARY", "DISABLE", "DISABLE_PAGE_SKIPPING", 
                             "DISCARD", "DISCONNECT", "DISPATCH", "DISTINCT", 
                             "DO", "DOMAIN", "DOUBLE", "DROP", "DYNAMIC", 
                             "DYNAMIC_FUNCTION", "DYNAMIC_FUNCTION_CODE", 
                             "EACH", "ELEMENT", "ELSE", "ENABLE", "ENCODING", 
                             "ENCRYPTED", "END", "END_EXEC", "EQUALS", "ESCAPE", 
                             "EVERY", "EXCEPT", "EXCEPTION", "EXCLUDE", 
                             "EXCLUDING", "EXCLUSIVE", "EXEC", "EXECUTE", 
                             "EXISTING", "EXISTS", "EXP", "EXPLAIN", "EXTENDED", 
                             "EXTENSION", "EXTERNAL", "EXTRACT", "FALSE", 
                             "FETCH", "FIELDS", "FILTER", "FINAL", "FIRST", 
                             "FLOAT", "FLOOR", "FOLLOWING", "FOR", "FORCE", 
                             "FOREIGN", "FORMAT", "FORTRAN", "FORWARD", 
                             "FOUND", "FREE", "FREEZE", "FROM", "FULL", 
                             "FUNCTION", "FUSION", "G_", "GENERAL", "GENERATED", 
                             "GET", "GLOBAL", "GO", "GOTO", "GRANT", "GRANTED", 
                             "GREATEST", "GROUP", "GROUPING", "HANDLER", 
                             "HAVING", "HIERARCHY", "HOLD", "HOST", "HOUR", 
                             "IDENTITY", "IGNORE", "ILIKE", "IMMEDIATE", 
                             "IMMUTABLE", "IMPLEMENTATION", "IMPLICIT", 
                             "IN", "INCLUDING", "INCREMENT", "INDEX", "INDICATOR", 
                             "INFIX", "INHERITS", "INITIALIZE", "INITIALLY", 
                             "INNER", "INOUT", "INPUT", "INSENSITIVE", "INSERT", 
                             "INSTANCE", "INSTANTIABLE", "INSTEAD", "INT", 
                             "INTEGER", "INTERSECT", "INTERSECTION", "INTERVAL", 
                             "INTO", "INVOKER", "IS", "ISOLATION", "ITERATE", 
                             "JOIN", "K_", "KEY", "KEY_MEMBER", "KEY_TYPE", 
                             "LABEL", "LANCOMPILER", "LANGUAGE", "LARGE", 
                             "LAST", "LATERAL", "LEADING", "LEAST", "LEFT", 
                             "LENGTH", "LESS", "LEVEL", "LIKE", "LIMIT", 
                             "LISTEN", "LN", "LOAD", "LOCAL", "LOCALTIME", 
                             "LOCALTIMESTAMP", "LOCATION", "LOCATOR", "LOCK", 
                             "LOCKED", "LOWER", "M_", "MAIN", "MAP", "MAPPING", 
                             "MATCH", "MATCH_SIMPLE", "MATCHED", "MAX", 
                             "MAXVALUE", "MEMBER", "MERGE", "MESSAGE_LENGTH", 
                             "MESSAGE_OCTET_LENGTH", "MESSAGE_TEXT", "METHOD", 
                             "MIN", "MINUTE", "MINVALUE", "MOD", "MODE", 
                             "MODIFIES", "MODIFY", "MODULE", "MONTH", "MORE_", 
                             "MOVE", "MULTISET", "MUMPS", "NAME", "NAMES", 
                             "NATIONAL", "NATURAL", "NCHAR", "NCLOB", "NESTING", 
                             "NEW", "NEXT", "NO", "NOCREATEDB", "NOCREATEUSER", 
                             "NONE", "NORMALIZE", "NORMALIZED", "NOT", "NOTHING", 
                             "NOTIFY", "NOTNULL", "NOWAIT", "NULL", "NULLABLE", 
                             "NULLIF", "NULLS", "NUMBER", "NUMERIC", "OBJECT", 
                             "OCTET_LENGTH", "OCTETS", "OF", "OFF", "OFFSET", 
                             "OIDS", "OLD", "ON", "ONLY", "OPEN", "OPERATION", 
                             "OPERATOR", "OPTION", "OPTIONS", "OR", "ORDER", 
                             "ORDERING", "ORDINALITY", "OTHERS", "OUT", 
                             "OUTER", "OUTPUT", "OVER", "OVERLAPS", "OVERLAY", 
                             "OVERRIDING", "OWNER", "PAD", "PARAMETER", 
                             "PARAMETER_MODE", "PARAMETER_NAME", "PARAMETER_ORDINAL_POSITION", 
                             "PARAMETER_SPECIFIC_CATALOG", "PARAMETER_SPECIFIC_NAME", 
                             "PARAMETER_SPECIFIC_SCHEMA", "PARAMETERS", 
                             "PARSER", "PARTIAL", "PARTITION", "PASCAL", 
                             "PASSWORD", "PATH", "PERCENT_RANK", "PERCENTILE_CONT", 
                             "PERCENTILE_DISC", "PLACING", "PLAIN", "PLANS", 
                             "PLI", "POSITION", "POSTFIX", "POWER", "PRECEDING", 
                             "PRECISION", "PREFIX", "PREORDER", "PREPARE", 
                             "PREPARED", "PRESERVE", "PRIMARY", "PRIOR", 
                             "PRIVILEGES", "PROCEDURAL", "PROCEDURE", "PUBLIC", 
                             "PUBLICATION", "QUOTE", "RANGE", "RANK", "READ", 
                             "READS", "REAL", "REASSIGN", "RECHECK", "RECURSIVE", 
                             "REF", "REFERENCES", "REFERENCING", "REFRESH", 
                             "REGR_AVGX", "REGR_AVGY", "REGR_COUNT", "REGR_INTERCEPT", 
                             "REGR_R2", "REGR_SLOPE", "REGR_SXX", "REGR_SXY", 
                             "REGR_SYY", "REINDEX", "RELATIVE", "RELEASE", 
                             "RENAME", "REPEATABLE", "REPLACE", "REPLICA", 
                             "RESET", "RESTART", "RESTRICT", "RESULT", "RETURN", 
                             "RETURNED_CARDINALITY", "RETURNED_LENGTH", 
                             "RETURNED_OCTET_LENGTH", "RETURNED_SQLSTATE", 
                             "RETURNING", "RETURNS", "REVOKE", "RIGHT", 
                             "ROLE", "ROLLBACK", "ROLLUP", "ROUTINE", "ROUTINE_CATALOG", 
                             "ROUTINE_NAME", "ROUTINE_SCHEMA", "ROW", "ROW_COUNT", 
                             "ROW_NUMBER", "ROWS", "RULE", "SAVEPOINT", 
                             "SCALE", "SCHEMA", "SCHEMA_NAME", "SCOPE", 
                             "SCOPE_CATALOG", "SCOPE_NAME", "SCOPE_SCHEMA", 
                             "SCROLL", "SEARCH", "SECOND", "SECTION", "SECURITY", 
                             "SELECT", "SELF", "SENSITIVE", "SEQUENCE", 
                             "SEQUENCES", "SERIALIZABLE", "SERVER_NAME", 
                             "SESSION", "SESSION_USER", "SET", "SETOF", 
                             "SETS", "SHARE", "SHOW", "SIMILAR", "SIMPLE", 
                             "SIZE", "SKIP_", "SMALLINT", "SNAPSHOT", "SOME", 
                             "SOURCE", "SPACE", "SPECIFIC", "SPECIFIC_NAME", 
                             "SPECIFICTYPE", "SQL", "SQLCODE", "SQLERROR", 
                             "SQLEXCEPTION", "SQLSTATE", "SQLWARNING", "SQRT", 
                             "STABLE", "START", "STATE", "STATEMENT", "STATIC", 
                             "STATISTICS", "STDDEV_POP", "STDDEV_SAMP", 
                             "STDIN", "STDOUT", "STORAGE", "STRICT", "STRUCTURE", 
                             "STYLE", "SUBCLASS_ORIGIN", "SUBLIST", "SUBMULTISET", 
                             "SUBSCRIPTION", "SUBSTRING", "SUM", "SYMMETRIC", 
                             "SYSID", "SYSTEM", "SYSTEM_USER", "TABLE", 
                             "TABLE_NAME", "TABLESAMPLE", "TABLESPACE", 
                             "TEMP", "TEMPLATE", "TEMPORARY", "TERMINATE", 
                             "THAN", "THEN", "TIES", "TIME", "TIMESTAMP", 
                             "TIMEZONE_HOUR", "TIMEZONE_MINUTE", "TIMING", 
                             "TO", "TOAST", "TOP_LEVEL_COUNT", "TRAILING", 
                             "TRANSACTION", "TRANSACTION_ACTIVE", "TRANSACTIONS_COMMITTED", 
                             "TRANSACTIONS_ROLLED_BACK", "TRANSFORM", "TRANSFORMS", 
                             "TRANSLATE", "TRANSLATION", "TREAT", "TRIGGER", 
                             "TRIGGER_CATALOG", "TRIGGER_NAME", "TRIGGER_SCHEMA", 
                             "TRIM", "TRUE", "TRUNCATE", "TRUSTED", "TYPE", 
                             "UESCAPE", "UNBOUNDED", "UNCOMMITTED", "UNDER", 
                             "UNENCRYPTED", "UNION", "UNIQUE", "UNKNOWN", 
                             "UNLISTEN", "UNNAMED", "UNNEST", "UNTIL", "UPDATE", 
                             "UPPER", "USAGE", "USER", "USER_DEFINED_TYPE_CATALOG", 
                             "USER_DEFINED_TYPE_CODE", "USER_DEFINED_TYPE_NAME", 
                             "USER_DEFINED_TYPE_SCHEMA", "USING", "VACUUM", 
                             "VALID", "VALIDATE", "VALIDATOR", "VALUE", 
                             "VALUES", "VAR_POP", "VAR_SAMP", "VARCHAR", 
                             "VARIABLE", "VARIADIC", "VARYING", "VERBOSE", 
                             "VIEW", "VOLATILE", "WHEN", "WHENEVER", "WHERE", 
                             "WIDTH_BUCKET", "WINDOW", "WITH", "WITHIN", 
                             "WITHOUT", "WORK", "WRITE", "YAML", "YEAR", 
                             "YES", "ZONE", "SUPERUSER", "NOSUPERUSER", 
                             "CREATEROLE", "NOCREATEROLE", "INHERIT", "NOINHERIT", 
                             "LOGIN", "NOLOGIN", "REPLICATION", "NOREPLICATION", 
                             "BYPASSRLS", "NOBYPASSRLS", "SFUNC", "STYPE", 
                             "SSPACE", "FINALFUNC", "FINALFUNC_EXTRA", "COMBINEFUNC", 
                             "SERIALFUNC", "DESERIALFUNC", "INITCOND", "MSFUNC", 
                             "MINVFUNC", "MSTYPE", "MSSPACE", "MFINALFUNC", 
                             "MFINALFUNC_EXTRA", "MINITCOND", "SORTOP", 
                             "PARALLEL", "HYPOTHETICAL", "SAFE", "RESTRICTED", 
                             "UNSAFE", "BASETYPE", "IF", "LOCALE", "LC_COLLATE", 
                             "LC_CTYPE", "PROVIDER", "VERSION", "ALLOW_CONNECTIONS", 
                             "IS_TEMPLATE", "EVENT", "WRAPPER", "SERVER", 
                             "BTREE", "HASH_", "GIST", "SPGIST", "GIN", 
                             "BRIN", "CONCURRENTLY", "INLINE", "MATERIALIZED", 
                             "LEFTARG", "RIGHTARG", "COMMUTATOR", "NEGATOR", 
                             "HASHES", "MERGES", "FAMILY", "POLICY", "OWNED", 
                             "ABSTIME", "BIGSERIAL", "BIT_VARYING", "BOOL", 
                             "BOX", "BYTEA", "CHARACTER_VARYING", "CIDR", 
                             "CIRCLE", "FLOAT4", "FLOAT8", "INET", "INT2", 
                             "INT4", "INT8", "JSON", "JSONB", "LINE", "LSEG", 
                             "MACADDR", "MACADDR8", "MONEY", "PG_LSN", "POINT", 
                             "POLYGON", "RELTIME", "SERIAL", "SERIAL2", 
                             "SERIAL4", "SERIAL8", "SMALLSERIAL", "STSTEM", 
                             "TEXT", "TIMESTAMPTZ", "TIMETZ", "TSQUERY", 
                             "TSVECTOR", "TXID_SNAPSHOT", "UUID", "VARBIT", 
                             "XML", "COMMA", "COLON", "COLON_COLON", "DOLLAR", 
                             "DOLLAR_DOLLAR", "STAR", "OPEN_PAREN", "CLOSE_PAREN", 
                             "OPEN_BRACKET", "CLOSE_BRACKET", "BIT_STRING", 
                             "REGEX_STRING", "NUMERIC_LITERAL", "INTEGER_LITERAL", 
                             "HEX_INTEGER_LITERAL", "DOT", "SINGLEQ_STRING_LITERAL", 
                             "DOUBLEQ_STRING_LITERAL", "IDENTIFIER", "DOLLAR_DEC", 
                             "IDENTIFIER_UNICODE", "AMP", "AMP_AMP", "AMP_LT", 
                             "AT_AT", "AT_GT", "AT_SIGN", "BANG", "BANG_BANG", 
                             "BANG_EQUAL", "CARET", "EQUAL", "EQUAL_GT", 
                             "GT", "GTE", "GT_GT", "HASH", "HASH_EQ", "HASH_GT", 
                             "HASH_GT_GT", "HASH_HASH", "HYPHEN_GT", "HYPHEN_GT_GT", 
                             "HYPHEN_PIPE_HYPHEN", "LT", "LTE", "LT_AT", 
                             "LT_CARET", "LT_GT", "LT_HYPHEN_GT", "LT_LT", 
                             "LT_LT_EQ", "LT_QMARK_GT", "MINUS", "PERCENT", 
                             "PIPE", "PIPE_PIPE", "PIPE_PIPE_SLASH", "PIPE_SLASH", 
                             "PLUS", "QMARK", "QMARK_AMP", "QMARK_HASH", 
                             "QMARK_HYPHEN", "QMARK_PIPE", "SLASH", "TIL", 
                             "TIL_EQ", "TIL_GTE_TIL", "TIL_GT_TIL", "TIL_LTE_TIL", 
                             "TIL_LT_TIL", "TIL_STAR", "TIL_TIL", "SEMI" ];
    static ruleNames = [ "root", "expr", "bool_expr", "case_expr", "expr_list", 
                         "type_name", "data_type", "func_name", "func_call", 
                         "predicate", "non_reserved_keyword", "identifier" ];

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

    sempred(localctx, ruleIndex, predIndex) {
    	switch(ruleIndex) {
    	case 1:
    	    		return this.expr_sempred(localctx, predIndex);
    	case 2:
    	    		return this.bool_expr_sempred(localctx, predIndex);
    	case 9:
    	    		return this.predicate_sempred(localctx, predIndex);
    	case 11:
    	    		return this.identifier_sempred(localctx, predIndex);
        default:
            throw "No predicate with index:" + ruleIndex;
       }
    }

    expr_sempred(localctx, predIndex) {
    	switch(predIndex) {
    		case 0:
    			return this.precpred(this._ctx, 23);
    		case 1:
    			return this.precpred(this._ctx, 22);
    		case 2:
    			return this.precpred(this._ctx, 21);
    		case 3:
    			return this.precpred(this._ctx, 20);
    		case 4:
    			return this.precpred(this._ctx, 19);
    		case 5:
    			return this.precpred(this._ctx, 18);
    		case 6:
    			return this.precpred(this._ctx, 17);
    		case 7:
    			return this.precpred(this._ctx, 16);
    		case 8:
    			return this.precpred(this._ctx, 14);
    		case 9:
    			return this.precpred(this._ctx, 29);
    		case 10:
    			return this.precpred(this._ctx, 24);
    		case 11:
    			return this.precpred(this._ctx, 15);
    		case 12:
    			return this.precpred(this._ctx, 8);
    		case 13:
    			return this.precpred(this._ctx, 7);
    		case 14:
    			return this.precpred(this._ctx, 5);
    		case 15:
    			return this.precpred(this._ctx, 4);
    		case 16:
    			return this.precpred(this._ctx, 3);
    		default:
    			throw "No predicate with index:" + predIndex;
    	}
    };

    bool_expr_sempred(localctx, predIndex) {
    	switch(predIndex) {
    		case 17:
    			return this.precpred(this._ctx, 2);
    		case 18:
    			return this.precpred(this._ctx, 1);
    		default:
    			throw "No predicate with index:" + predIndex;
    	}
    };

    predicate_sempred(localctx, predIndex) {
    	switch(predIndex) {
    		case 19:
    			return this.precpred(this._ctx, 3);
    		case 20:
    			return this.precpred(this._ctx, 2);
    		default:
    			throw "No predicate with index:" + predIndex;
    	}
    };

    identifier_sempred(localctx, predIndex) {
    	switch(predIndex) {
    		case 21:
    			return this.precpred(this._ctx, 3);
    		default:
    			throw "No predicate with index:" + predIndex;
    	}
    };




	root() {
	    let localctx = new RootContext(this, this._ctx, this.state);
	    this.enterRule(localctx, 0, BaserowFormula.RULE_root);
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 24;
	        this.expr(0);
	        this.state = 25;
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


	expr(_p) {
		if(_p===undefined) {
		    _p = 0;
		}
	    const _parentctx = this._ctx;
	    const _parentState = this.state;
	    let localctx = new ExprContext(this, this._ctx, _parentState);
	    let _prevctx = localctx;
	    const _startState = 2;
	    this.enterRecursionRule(localctx, 2, BaserowFormula.RULE_expr, _p);
	    var _la = 0; // Token type
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 87;
	        this._errHandler.sync(this);
	        var la_ = this._interp.adaptivePredict(this._input,2,this._ctx);
	        switch(la_) {
	        case 1:
	            this.state = 28;
	            this.match(BaserowFormula.NULL);
	            break;

	        case 2:
	            this.state = 29;
	            this.match(BaserowFormula.CURRENT_DATE);
	            break;

	        case 3:
	            this.state = 30;
	            this.match(BaserowFormula.CURRENT_TIME);
	            break;

	        case 4:
	            this.state = 31;
	            this.match(BaserowFormula.CURRENT_TIMESTAMP);
	            break;

	        case 5:
	            this.state = 32;
	            this.match(BaserowFormula.INTEGER_LITERAL);
	            break;

	        case 6:
	            this.state = 33;
	            this.match(BaserowFormula.HEX_INTEGER_LITERAL);
	            break;

	        case 7:
	            this.state = 34;
	            this.match(BaserowFormula.NUMERIC_LITERAL);
	            break;

	        case 8:
	            this.state = 35;
	            this.match(BaserowFormula.SINGLEQ_STRING_LITERAL);
	            break;

	        case 9:
	            this.state = 36;
	            this.match(BaserowFormula.BIT_STRING);
	            break;

	        case 10:
	            this.state = 37;
	            this.match(BaserowFormula.REGEX_STRING);
	            break;

	        case 11:
	            this.state = 38;
	            this.match(BaserowFormula.DOLLAR_DOLLAR);
	            this.state = 40; 
	            this._errHandler.sync(this);
	            var _alt = 1;
	            do {
	            	switch (_alt) {
	            	case 1:
	            		this.state = 39;
	            		_la = this._input.LA(1);
	            		if(_la<=0 || _la===BaserowFormula.DOLLAR) {
	            		this._errHandler.recoverInline(this);
	            		}
	            		else {
	            			this._errHandler.reportMatch(this);
	            		    this.consume();
	            		}
	            		break;
	            	default:
	            		throw new antlr4.error.NoViableAltException(this);
	            	}
	            	this.state = 42; 
	            	this._errHandler.sync(this);
	            	_alt = this._interp.adaptivePredict(this._input,0, this._ctx);
	            } while ( _alt!=2 && _alt!=antlr4.atn.ATN.INVALID_ALT_NUMBER );
	            this.state = 44;
	            this.match(BaserowFormula.DOLLAR_DOLLAR);
	            break;

	        case 12:
	            this.state = 45;
	            this.match(BaserowFormula.DOLLAR);
	            this.state = 46;
	            this.identifier(0);
	            this.state = 48; 
	            this._errHandler.sync(this);
	            _la = this._input.LA(1);
	            do {
	                this.state = 47;
	                _la = this._input.LA(1);
	                if(_la<=0 || _la===BaserowFormula.DOLLAR) {
	                this._errHandler.recoverInline(this);
	                }
	                else {
	                	this._errHandler.reportMatch(this);
	                    this.consume();
	                }
	                this.state = 50; 
	                this._errHandler.sync(this);
	                _la = this._input.LA(1);
	            } while((((_la) & ~0x1f) == 0 && ((1 << _la) & ((1 << BaserowFormula.WHITESPACE) | (1 << BaserowFormula.BLOCK_COMMENT) | (1 << BaserowFormula.LINE_COMMENT) | (1 << BaserowFormula.A_) | (1 << BaserowFormula.ABORT) | (1 << BaserowFormula.ABS) | (1 << BaserowFormula.ABSOLUTE) | (1 << BaserowFormula.ACCESS) | (1 << BaserowFormula.ACTION) | (1 << BaserowFormula.ADA) | (1 << BaserowFormula.ADD) | (1 << BaserowFormula.ADMIN) | (1 << BaserowFormula.AFTER) | (1 << BaserowFormula.AGGREGATE) | (1 << BaserowFormula.ALIAS) | (1 << BaserowFormula.ALL) | (1 << BaserowFormula.ALLOCATE) | (1 << BaserowFormula.ALSO) | (1 << BaserowFormula.ALTER) | (1 << BaserowFormula.ALWAYS) | (1 << BaserowFormula.ANALYSE) | (1 << BaserowFormula.ANALYZE) | (1 << BaserowFormula.AND) | (1 << BaserowFormula.ANY) | (1 << BaserowFormula.ARE) | (1 << BaserowFormula.ARRAY) | (1 << BaserowFormula.AS) | (1 << BaserowFormula.ASC) | (1 << BaserowFormula.ASENSITIVE) | (1 << BaserowFormula.ASSERTION) | (1 << BaserowFormula.ASSIGNMENT))) !== 0) || ((((_la - 32)) & ~0x1f) == 0 && ((1 << (_la - 32)) & ((1 << (BaserowFormula.ASYMMETRIC - 32)) | (1 << (BaserowFormula.AT - 32)) | (1 << (BaserowFormula.ATOMIC - 32)) | (1 << (BaserowFormula.ATTRIBUTE - 32)) | (1 << (BaserowFormula.ATTRIBUTES - 32)) | (1 << (BaserowFormula.AUTHORIZATION - 32)) | (1 << (BaserowFormula.AVG - 32)) | (1 << (BaserowFormula.BACKWARD - 32)) | (1 << (BaserowFormula.BEFORE - 32)) | (1 << (BaserowFormula.BEGIN - 32)) | (1 << (BaserowFormula.BERNOULLI - 32)) | (1 << (BaserowFormula.BETWEEN - 32)) | (1 << (BaserowFormula.BIGINT - 32)) | (1 << (BaserowFormula.BINARY - 32)) | (1 << (BaserowFormula.BIT - 32)) | (1 << (BaserowFormula.BIT_LENGTH - 32)) | (1 << (BaserowFormula.BITVAR - 32)) | (1 << (BaserowFormula.BLOB - 32)) | (1 << (BaserowFormula.BOOLEAN - 32)) | (1 << (BaserowFormula.BOTH - 32)) | (1 << (BaserowFormula.BREADTH - 32)) | (1 << (BaserowFormula.BUFFERS - 32)) | (1 << (BaserowFormula.BY - 32)) | (1 << (BaserowFormula.C_ - 32)) | (1 << (BaserowFormula.CACHE - 32)) | (1 << (BaserowFormula.CALL - 32)) | (1 << (BaserowFormula.CALLED - 32)) | (1 << (BaserowFormula.CARDINALITY - 32)) | (1 << (BaserowFormula.CASCADE - 32)) | (1 << (BaserowFormula.CASCADED - 32)) | (1 << (BaserowFormula.CASE - 32)) | (1 << (BaserowFormula.CAST - 32)))) !== 0) || ((((_la - 64)) & ~0x1f) == 0 && ((1 << (_la - 64)) & ((1 << (BaserowFormula.CATALOG - 64)) | (1 << (BaserowFormula.CATALOG_NAME - 64)) | (1 << (BaserowFormula.CEIL - 64)) | (1 << (BaserowFormula.CEILING - 64)) | (1 << (BaserowFormula.CHAIN - 64)) | (1 << (BaserowFormula.CHAR - 64)) | (1 << (BaserowFormula.CHAR_LENGTH - 64)) | (1 << (BaserowFormula.CHARACTER - 64)) | (1 << (BaserowFormula.CHARACTER_LENGTH - 64)) | (1 << (BaserowFormula.CHARACTER_SET_CATALOG - 64)) | (1 << (BaserowFormula.CHARACTER_SET_NAME - 64)) | (1 << (BaserowFormula.CHARACTER_SET_SCHEMA - 64)) | (1 << (BaserowFormula.CHARACTERISTICS - 64)) | (1 << (BaserowFormula.CHARACTERS - 64)) | (1 << (BaserowFormula.CHECK - 64)) | (1 << (BaserowFormula.CHECKED - 64)) | (1 << (BaserowFormula.CHECKPOINT - 64)) | (1 << (BaserowFormula.CLASS - 64)) | (1 << (BaserowFormula.CLASS_ORIGIN - 64)) | (1 << (BaserowFormula.CLOB - 64)) | (1 << (BaserowFormula.CLOSE - 64)) | (1 << (BaserowFormula.CLUSTER - 64)) | (1 << (BaserowFormula.COALESCE - 64)) | (1 << (BaserowFormula.COBOL - 64)) | (1 << (BaserowFormula.COLLATE - 64)) | (1 << (BaserowFormula.COLLATION - 64)) | (1 << (BaserowFormula.COLLATION_CATALOG - 64)) | (1 << (BaserowFormula.COLLATION_NAME - 64)) | (1 << (BaserowFormula.COLLATION_SCHEMA - 64)) | (1 << (BaserowFormula.COLLECT - 64)) | (1 << (BaserowFormula.COLUMN - 64)) | (1 << (BaserowFormula.COLUMN_NAME - 64)))) !== 0) || ((((_la - 96)) & ~0x1f) == 0 && ((1 << (_la - 96)) & ((1 << (BaserowFormula.COMMAND_FUNCTION - 96)) | (1 << (BaserowFormula.COMMAND_FUNCTION_CODE - 96)) | (1 << (BaserowFormula.COMMENT - 96)) | (1 << (BaserowFormula.COMMIT - 96)) | (1 << (BaserowFormula.COMMITTED - 96)) | (1 << (BaserowFormula.COMPLETION - 96)) | (1 << (BaserowFormula.CONDITION - 96)) | (1 << (BaserowFormula.CONDITION_NUMBER - 96)) | (1 << (BaserowFormula.CONFIGURATION - 96)) | (1 << (BaserowFormula.CONFLICT - 96)) | (1 << (BaserowFormula.CONNECT - 96)) | (1 << (BaserowFormula.CONNECTION - 96)) | (1 << (BaserowFormula.CONNECTION_NAME - 96)) | (1 << (BaserowFormula.CONSTRAINT - 96)) | (1 << (BaserowFormula.CONSTRAINT_CATALOG - 96)) | (1 << (BaserowFormula.CONSTRAINT_NAME - 96)) | (1 << (BaserowFormula.CONSTRAINT_SCHEMA - 96)) | (1 << (BaserowFormula.CONSTRAINTS - 96)) | (1 << (BaserowFormula.CONSTRUCTOR - 96)) | (1 << (BaserowFormula.CONTAINS - 96)) | (1 << (BaserowFormula.CONTINUE - 96)) | (1 << (BaserowFormula.CONVERSION - 96)) | (1 << (BaserowFormula.CONVERT - 96)) | (1 << (BaserowFormula.COPY - 96)) | (1 << (BaserowFormula.CORR - 96)) | (1 << (BaserowFormula.CORRESPONDING - 96)) | (1 << (BaserowFormula.COSTS - 96)) | (1 << (BaserowFormula.COUNT - 96)) | (1 << (BaserowFormula.COVAR_POP - 96)) | (1 << (BaserowFormula.COVAR_SAMP - 96)) | (1 << (BaserowFormula.CREATE - 96)) | (1 << (BaserowFormula.CREATEDB - 96)))) !== 0) || ((((_la - 128)) & ~0x1f) == 0 && ((1 << (_la - 128)) & ((1 << (BaserowFormula.CREATEUSER - 128)) | (1 << (BaserowFormula.CROSS - 128)) | (1 << (BaserowFormula.CSV - 128)) | (1 << (BaserowFormula.CUBE - 128)) | (1 << (BaserowFormula.CUME_DIST - 128)) | (1 << (BaserowFormula.CURRENT - 128)) | (1 << (BaserowFormula.CURRENT_DATE - 128)) | (1 << (BaserowFormula.CURRENT_DEFAULT_TRANSFORM_GROUP - 128)) | (1 << (BaserowFormula.CURRENT_PATH - 128)) | (1 << (BaserowFormula.CURRENT_ROLE - 128)) | (1 << (BaserowFormula.CURRENT_TIME - 128)) | (1 << (BaserowFormula.CURRENT_TIMESTAMP - 128)) | (1 << (BaserowFormula.CURRENT_TRANSFORM_GROUP_FOR_TYPE - 128)) | (1 << (BaserowFormula.CURRENT_USER - 128)) | (1 << (BaserowFormula.CURSOR - 128)) | (1 << (BaserowFormula.CURSOR_NAME - 128)) | (1 << (BaserowFormula.CYCLE - 128)) | (1 << (BaserowFormula.DATA - 128)) | (1 << (BaserowFormula.DATABASE - 128)) | (1 << (BaserowFormula.DATE - 128)) | (1 << (BaserowFormula.DATETIME_INTERVAL_CODE - 128)) | (1 << (BaserowFormula.DATETIME_INTERVAL_PRECISION - 128)) | (1 << (BaserowFormula.DAY - 128)) | (1 << (BaserowFormula.DEALLOCATE - 128)) | (1 << (BaserowFormula.DEC - 128)) | (1 << (BaserowFormula.DECIMAL - 128)) | (1 << (BaserowFormula.DECLARE - 128)) | (1 << (BaserowFormula.DEFAULT - 128)) | (1 << (BaserowFormula.DEFAULTS - 128)) | (1 << (BaserowFormula.DEFERABLE - 128)) | (1 << (BaserowFormula.DEFERRABLE - 128)) | (1 << (BaserowFormula.DEFERRED - 128)))) !== 0) || ((((_la - 160)) & ~0x1f) == 0 && ((1 << (_la - 160)) & ((1 << (BaserowFormula.DEFINED - 160)) | (1 << (BaserowFormula.DEFINER - 160)) | (1 << (BaserowFormula.DEGREE - 160)) | (1 << (BaserowFormula.DELETE - 160)) | (1 << (BaserowFormula.DELIMITER - 160)) | (1 << (BaserowFormula.DELIMITERS - 160)) | (1 << (BaserowFormula.DENSE_RANK - 160)) | (1 << (BaserowFormula.DEPENDS - 160)) | (1 << (BaserowFormula.DEPTH - 160)) | (1 << (BaserowFormula.DEREF - 160)) | (1 << (BaserowFormula.DERIVED - 160)) | (1 << (BaserowFormula.DESC - 160)) | (1 << (BaserowFormula.DESCRIBE - 160)) | (1 << (BaserowFormula.DESCRIPTOR - 160)) | (1 << (BaserowFormula.DESTROY - 160)) | (1 << (BaserowFormula.DESTRUCTOR - 160)) | (1 << (BaserowFormula.DETERMINISTIC - 160)) | (1 << (BaserowFormula.DIAGNOSTICS - 160)) | (1 << (BaserowFormula.DICTIONARY - 160)) | (1 << (BaserowFormula.DISABLE - 160)) | (1 << (BaserowFormula.DISABLE_PAGE_SKIPPING - 160)) | (1 << (BaserowFormula.DISCARD - 160)) | (1 << (BaserowFormula.DISCONNECT - 160)) | (1 << (BaserowFormula.DISPATCH - 160)) | (1 << (BaserowFormula.DISTINCT - 160)) | (1 << (BaserowFormula.DO - 160)) | (1 << (BaserowFormula.DOMAIN - 160)) | (1 << (BaserowFormula.DOUBLE - 160)) | (1 << (BaserowFormula.DROP - 160)) | (1 << (BaserowFormula.DYNAMIC - 160)) | (1 << (BaserowFormula.DYNAMIC_FUNCTION - 160)) | (1 << (BaserowFormula.DYNAMIC_FUNCTION_CODE - 160)))) !== 0) || ((((_la - 192)) & ~0x1f) == 0 && ((1 << (_la - 192)) & ((1 << (BaserowFormula.EACH - 192)) | (1 << (BaserowFormula.ELEMENT - 192)) | (1 << (BaserowFormula.ELSE - 192)) | (1 << (BaserowFormula.ENABLE - 192)) | (1 << (BaserowFormula.ENCODING - 192)) | (1 << (BaserowFormula.ENCRYPTED - 192)) | (1 << (BaserowFormula.END - 192)) | (1 << (BaserowFormula.END_EXEC - 192)) | (1 << (BaserowFormula.EQUALS - 192)) | (1 << (BaserowFormula.ESCAPE - 192)) | (1 << (BaserowFormula.EVERY - 192)) | (1 << (BaserowFormula.EXCEPT - 192)) | (1 << (BaserowFormula.EXCEPTION - 192)) | (1 << (BaserowFormula.EXCLUDE - 192)) | (1 << (BaserowFormula.EXCLUDING - 192)) | (1 << (BaserowFormula.EXCLUSIVE - 192)) | (1 << (BaserowFormula.EXEC - 192)) | (1 << (BaserowFormula.EXECUTE - 192)) | (1 << (BaserowFormula.EXISTING - 192)) | (1 << (BaserowFormula.EXISTS - 192)) | (1 << (BaserowFormula.EXP - 192)) | (1 << (BaserowFormula.EXPLAIN - 192)) | (1 << (BaserowFormula.EXTENDED - 192)) | (1 << (BaserowFormula.EXTENSION - 192)) | (1 << (BaserowFormula.EXTERNAL - 192)) | (1 << (BaserowFormula.EXTRACT - 192)) | (1 << (BaserowFormula.FALSE - 192)) | (1 << (BaserowFormula.FETCH - 192)) | (1 << (BaserowFormula.FIELDS - 192)) | (1 << (BaserowFormula.FILTER - 192)) | (1 << (BaserowFormula.FINAL - 192)) | (1 << (BaserowFormula.FIRST - 192)))) !== 0) || ((((_la - 224)) & ~0x1f) == 0 && ((1 << (_la - 224)) & ((1 << (BaserowFormula.FLOAT - 224)) | (1 << (BaserowFormula.FLOOR - 224)) | (1 << (BaserowFormula.FOLLOWING - 224)) | (1 << (BaserowFormula.FOR - 224)) | (1 << (BaserowFormula.FORCE - 224)) | (1 << (BaserowFormula.FOREIGN - 224)) | (1 << (BaserowFormula.FORMAT - 224)) | (1 << (BaserowFormula.FORTRAN - 224)) | (1 << (BaserowFormula.FORWARD - 224)) | (1 << (BaserowFormula.FOUND - 224)) | (1 << (BaserowFormula.FREE - 224)) | (1 << (BaserowFormula.FREEZE - 224)) | (1 << (BaserowFormula.FROM - 224)) | (1 << (BaserowFormula.FULL - 224)) | (1 << (BaserowFormula.FUNCTION - 224)) | (1 << (BaserowFormula.FUSION - 224)) | (1 << (BaserowFormula.G_ - 224)) | (1 << (BaserowFormula.GENERAL - 224)) | (1 << (BaserowFormula.GENERATED - 224)) | (1 << (BaserowFormula.GET - 224)) | (1 << (BaserowFormula.GLOBAL - 224)) | (1 << (BaserowFormula.GO - 224)) | (1 << (BaserowFormula.GOTO - 224)) | (1 << (BaserowFormula.GRANT - 224)) | (1 << (BaserowFormula.GRANTED - 224)) | (1 << (BaserowFormula.GREATEST - 224)) | (1 << (BaserowFormula.GROUP - 224)) | (1 << (BaserowFormula.GROUPING - 224)) | (1 << (BaserowFormula.HANDLER - 224)) | (1 << (BaserowFormula.HAVING - 224)) | (1 << (BaserowFormula.HIERARCHY - 224)) | (1 << (BaserowFormula.HOLD - 224)))) !== 0) || ((((_la - 256)) & ~0x1f) == 0 && ((1 << (_la - 256)) & ((1 << (BaserowFormula.HOST - 256)) | (1 << (BaserowFormula.HOUR - 256)) | (1 << (BaserowFormula.IDENTITY - 256)) | (1 << (BaserowFormula.IGNORE - 256)) | (1 << (BaserowFormula.ILIKE - 256)) | (1 << (BaserowFormula.IMMEDIATE - 256)) | (1 << (BaserowFormula.IMMUTABLE - 256)) | (1 << (BaserowFormula.IMPLEMENTATION - 256)) | (1 << (BaserowFormula.IMPLICIT - 256)) | (1 << (BaserowFormula.IN - 256)) | (1 << (BaserowFormula.INCLUDING - 256)) | (1 << (BaserowFormula.INCREMENT - 256)) | (1 << (BaserowFormula.INDEX - 256)) | (1 << (BaserowFormula.INDICATOR - 256)) | (1 << (BaserowFormula.INFIX - 256)) | (1 << (BaserowFormula.INHERITS - 256)) | (1 << (BaserowFormula.INITIALIZE - 256)) | (1 << (BaserowFormula.INITIALLY - 256)) | (1 << (BaserowFormula.INNER - 256)) | (1 << (BaserowFormula.INOUT - 256)) | (1 << (BaserowFormula.INPUT - 256)) | (1 << (BaserowFormula.INSENSITIVE - 256)) | (1 << (BaserowFormula.INSERT - 256)) | (1 << (BaserowFormula.INSTANCE - 256)) | (1 << (BaserowFormula.INSTANTIABLE - 256)) | (1 << (BaserowFormula.INSTEAD - 256)) | (1 << (BaserowFormula.INT - 256)) | (1 << (BaserowFormula.INTEGER - 256)) | (1 << (BaserowFormula.INTERSECT - 256)) | (1 << (BaserowFormula.INTERSECTION - 256)) | (1 << (BaserowFormula.INTERVAL - 256)) | (1 << (BaserowFormula.INTO - 256)))) !== 0) || ((((_la - 288)) & ~0x1f) == 0 && ((1 << (_la - 288)) & ((1 << (BaserowFormula.INVOKER - 288)) | (1 << (BaserowFormula.IS - 288)) | (1 << (BaserowFormula.ISOLATION - 288)) | (1 << (BaserowFormula.ITERATE - 288)) | (1 << (BaserowFormula.JOIN - 288)) | (1 << (BaserowFormula.K_ - 288)) | (1 << (BaserowFormula.KEY - 288)) | (1 << (BaserowFormula.KEY_MEMBER - 288)) | (1 << (BaserowFormula.KEY_TYPE - 288)) | (1 << (BaserowFormula.LABEL - 288)) | (1 << (BaserowFormula.LANCOMPILER - 288)) | (1 << (BaserowFormula.LANGUAGE - 288)) | (1 << (BaserowFormula.LARGE - 288)) | (1 << (BaserowFormula.LAST - 288)) | (1 << (BaserowFormula.LATERAL - 288)) | (1 << (BaserowFormula.LEADING - 288)) | (1 << (BaserowFormula.LEAST - 288)) | (1 << (BaserowFormula.LEFT - 288)) | (1 << (BaserowFormula.LENGTH - 288)) | (1 << (BaserowFormula.LESS - 288)) | (1 << (BaserowFormula.LEVEL - 288)) | (1 << (BaserowFormula.LIKE - 288)) | (1 << (BaserowFormula.LIMIT - 288)) | (1 << (BaserowFormula.LISTEN - 288)) | (1 << (BaserowFormula.LN - 288)) | (1 << (BaserowFormula.LOAD - 288)) | (1 << (BaserowFormula.LOCAL - 288)) | (1 << (BaserowFormula.LOCALTIME - 288)) | (1 << (BaserowFormula.LOCALTIMESTAMP - 288)) | (1 << (BaserowFormula.LOCATION - 288)) | (1 << (BaserowFormula.LOCATOR - 288)) | (1 << (BaserowFormula.LOCK - 288)))) !== 0) || ((((_la - 320)) & ~0x1f) == 0 && ((1 << (_la - 320)) & ((1 << (BaserowFormula.LOCKED - 320)) | (1 << (BaserowFormula.LOWER - 320)) | (1 << (BaserowFormula.M_ - 320)) | (1 << (BaserowFormula.MAIN - 320)) | (1 << (BaserowFormula.MAP - 320)) | (1 << (BaserowFormula.MAPPING - 320)) | (1 << (BaserowFormula.MATCH - 320)) | (1 << (BaserowFormula.MATCH_SIMPLE - 320)) | (1 << (BaserowFormula.MATCHED - 320)) | (1 << (BaserowFormula.MAX - 320)) | (1 << (BaserowFormula.MAXVALUE - 320)) | (1 << (BaserowFormula.MEMBER - 320)) | (1 << (BaserowFormula.MERGE - 320)) | (1 << (BaserowFormula.MESSAGE_LENGTH - 320)) | (1 << (BaserowFormula.MESSAGE_OCTET_LENGTH - 320)) | (1 << (BaserowFormula.MESSAGE_TEXT - 320)) | (1 << (BaserowFormula.METHOD - 320)) | (1 << (BaserowFormula.MIN - 320)) | (1 << (BaserowFormula.MINUTE - 320)) | (1 << (BaserowFormula.MINVALUE - 320)) | (1 << (BaserowFormula.MOD - 320)) | (1 << (BaserowFormula.MODE - 320)) | (1 << (BaserowFormula.MODIFIES - 320)) | (1 << (BaserowFormula.MODIFY - 320)) | (1 << (BaserowFormula.MODULE - 320)) | (1 << (BaserowFormula.MONTH - 320)) | (1 << (BaserowFormula.MORE_ - 320)) | (1 << (BaserowFormula.MOVE - 320)) | (1 << (BaserowFormula.MULTISET - 320)) | (1 << (BaserowFormula.MUMPS - 320)) | (1 << (BaserowFormula.NAME - 320)) | (1 << (BaserowFormula.NAMES - 320)))) !== 0) || ((((_la - 352)) & ~0x1f) == 0 && ((1 << (_la - 352)) & ((1 << (BaserowFormula.NATIONAL - 352)) | (1 << (BaserowFormula.NATURAL - 352)) | (1 << (BaserowFormula.NCHAR - 352)) | (1 << (BaserowFormula.NCLOB - 352)) | (1 << (BaserowFormula.NESTING - 352)) | (1 << (BaserowFormula.NEW - 352)) | (1 << (BaserowFormula.NEXT - 352)) | (1 << (BaserowFormula.NO - 352)) | (1 << (BaserowFormula.NOCREATEDB - 352)) | (1 << (BaserowFormula.NOCREATEUSER - 352)) | (1 << (BaserowFormula.NONE - 352)) | (1 << (BaserowFormula.NORMALIZE - 352)) | (1 << (BaserowFormula.NORMALIZED - 352)) | (1 << (BaserowFormula.NOT - 352)) | (1 << (BaserowFormula.NOTHING - 352)) | (1 << (BaserowFormula.NOTIFY - 352)) | (1 << (BaserowFormula.NOTNULL - 352)) | (1 << (BaserowFormula.NOWAIT - 352)) | (1 << (BaserowFormula.NULL - 352)) | (1 << (BaserowFormula.NULLABLE - 352)) | (1 << (BaserowFormula.NULLIF - 352)) | (1 << (BaserowFormula.NULLS - 352)) | (1 << (BaserowFormula.NUMBER - 352)) | (1 << (BaserowFormula.NUMERIC - 352)) | (1 << (BaserowFormula.OBJECT - 352)) | (1 << (BaserowFormula.OCTET_LENGTH - 352)) | (1 << (BaserowFormula.OCTETS - 352)) | (1 << (BaserowFormula.OF - 352)) | (1 << (BaserowFormula.OFF - 352)) | (1 << (BaserowFormula.OFFSET - 352)) | (1 << (BaserowFormula.OIDS - 352)) | (1 << (BaserowFormula.OLD - 352)))) !== 0) || ((((_la - 384)) & ~0x1f) == 0 && ((1 << (_la - 384)) & ((1 << (BaserowFormula.ON - 384)) | (1 << (BaserowFormula.ONLY - 384)) | (1 << (BaserowFormula.OPEN - 384)) | (1 << (BaserowFormula.OPERATION - 384)) | (1 << (BaserowFormula.OPERATOR - 384)) | (1 << (BaserowFormula.OPTION - 384)) | (1 << (BaserowFormula.OPTIONS - 384)) | (1 << (BaserowFormula.OR - 384)) | (1 << (BaserowFormula.ORDER - 384)) | (1 << (BaserowFormula.ORDERING - 384)) | (1 << (BaserowFormula.ORDINALITY - 384)) | (1 << (BaserowFormula.OTHERS - 384)) | (1 << (BaserowFormula.OUT - 384)) | (1 << (BaserowFormula.OUTER - 384)) | (1 << (BaserowFormula.OUTPUT - 384)) | (1 << (BaserowFormula.OVER - 384)) | (1 << (BaserowFormula.OVERLAPS - 384)) | (1 << (BaserowFormula.OVERLAY - 384)) | (1 << (BaserowFormula.OVERRIDING - 384)) | (1 << (BaserowFormula.OWNER - 384)) | (1 << (BaserowFormula.PAD - 384)) | (1 << (BaserowFormula.PARAMETER - 384)) | (1 << (BaserowFormula.PARAMETER_MODE - 384)) | (1 << (BaserowFormula.PARAMETER_NAME - 384)) | (1 << (BaserowFormula.PARAMETER_ORDINAL_POSITION - 384)) | (1 << (BaserowFormula.PARAMETER_SPECIFIC_CATALOG - 384)) | (1 << (BaserowFormula.PARAMETER_SPECIFIC_NAME - 384)) | (1 << (BaserowFormula.PARAMETER_SPECIFIC_SCHEMA - 384)) | (1 << (BaserowFormula.PARAMETERS - 384)) | (1 << (BaserowFormula.PARSER - 384)) | (1 << (BaserowFormula.PARTIAL - 384)) | (1 << (BaserowFormula.PARTITION - 384)))) !== 0) || ((((_la - 416)) & ~0x1f) == 0 && ((1 << (_la - 416)) & ((1 << (BaserowFormula.PASCAL - 416)) | (1 << (BaserowFormula.PASSWORD - 416)) | (1 << (BaserowFormula.PATH - 416)) | (1 << (BaserowFormula.PERCENT_RANK - 416)) | (1 << (BaserowFormula.PERCENTILE_CONT - 416)) | (1 << (BaserowFormula.PERCENTILE_DISC - 416)) | (1 << (BaserowFormula.PLACING - 416)) | (1 << (BaserowFormula.PLAIN - 416)) | (1 << (BaserowFormula.PLANS - 416)) | (1 << (BaserowFormula.PLI - 416)) | (1 << (BaserowFormula.POSITION - 416)) | (1 << (BaserowFormula.POSTFIX - 416)) | (1 << (BaserowFormula.POWER - 416)) | (1 << (BaserowFormula.PRECEDING - 416)) | (1 << (BaserowFormula.PRECISION - 416)) | (1 << (BaserowFormula.PREFIX - 416)) | (1 << (BaserowFormula.PREORDER - 416)) | (1 << (BaserowFormula.PREPARE - 416)) | (1 << (BaserowFormula.PREPARED - 416)) | (1 << (BaserowFormula.PRESERVE - 416)) | (1 << (BaserowFormula.PRIMARY - 416)) | (1 << (BaserowFormula.PRIOR - 416)) | (1 << (BaserowFormula.PRIVILEGES - 416)) | (1 << (BaserowFormula.PROCEDURAL - 416)) | (1 << (BaserowFormula.PROCEDURE - 416)) | (1 << (BaserowFormula.PUBLIC - 416)) | (1 << (BaserowFormula.PUBLICATION - 416)) | (1 << (BaserowFormula.QUOTE - 416)) | (1 << (BaserowFormula.RANGE - 416)) | (1 << (BaserowFormula.RANK - 416)) | (1 << (BaserowFormula.READ - 416)) | (1 << (BaserowFormula.READS - 416)))) !== 0) || ((((_la - 448)) & ~0x1f) == 0 && ((1 << (_la - 448)) & ((1 << (BaserowFormula.REAL - 448)) | (1 << (BaserowFormula.REASSIGN - 448)) | (1 << (BaserowFormula.RECHECK - 448)) | (1 << (BaserowFormula.RECURSIVE - 448)) | (1 << (BaserowFormula.REF - 448)) | (1 << (BaserowFormula.REFERENCES - 448)) | (1 << (BaserowFormula.REFERENCING - 448)) | (1 << (BaserowFormula.REFRESH - 448)) | (1 << (BaserowFormula.REGR_AVGX - 448)) | (1 << (BaserowFormula.REGR_AVGY - 448)) | (1 << (BaserowFormula.REGR_COUNT - 448)) | (1 << (BaserowFormula.REGR_INTERCEPT - 448)) | (1 << (BaserowFormula.REGR_R2 - 448)) | (1 << (BaserowFormula.REGR_SLOPE - 448)) | (1 << (BaserowFormula.REGR_SXX - 448)) | (1 << (BaserowFormula.REGR_SXY - 448)) | (1 << (BaserowFormula.REGR_SYY - 448)) | (1 << (BaserowFormula.REINDEX - 448)) | (1 << (BaserowFormula.RELATIVE - 448)) | (1 << (BaserowFormula.RELEASE - 448)) | (1 << (BaserowFormula.RENAME - 448)) | (1 << (BaserowFormula.REPEATABLE - 448)) | (1 << (BaserowFormula.REPLACE - 448)) | (1 << (BaserowFormula.REPLICA - 448)) | (1 << (BaserowFormula.RESET - 448)) | (1 << (BaserowFormula.RESTART - 448)) | (1 << (BaserowFormula.RESTRICT - 448)) | (1 << (BaserowFormula.RESULT - 448)) | (1 << (BaserowFormula.RETURN - 448)) | (1 << (BaserowFormula.RETURNED_CARDINALITY - 448)) | (1 << (BaserowFormula.RETURNED_LENGTH - 448)) | (1 << (BaserowFormula.RETURNED_OCTET_LENGTH - 448)))) !== 0) || ((((_la - 480)) & ~0x1f) == 0 && ((1 << (_la - 480)) & ((1 << (BaserowFormula.RETURNED_SQLSTATE - 480)) | (1 << (BaserowFormula.RETURNING - 480)) | (1 << (BaserowFormula.RETURNS - 480)) | (1 << (BaserowFormula.REVOKE - 480)) | (1 << (BaserowFormula.RIGHT - 480)) | (1 << (BaserowFormula.ROLE - 480)) | (1 << (BaserowFormula.ROLLBACK - 480)) | (1 << (BaserowFormula.ROLLUP - 480)) | (1 << (BaserowFormula.ROUTINE - 480)) | (1 << (BaserowFormula.ROUTINE_CATALOG - 480)) | (1 << (BaserowFormula.ROUTINE_NAME - 480)) | (1 << (BaserowFormula.ROUTINE_SCHEMA - 480)) | (1 << (BaserowFormula.ROW - 480)) | (1 << (BaserowFormula.ROW_COUNT - 480)) | (1 << (BaserowFormula.ROW_NUMBER - 480)) | (1 << (BaserowFormula.ROWS - 480)) | (1 << (BaserowFormula.RULE - 480)) | (1 << (BaserowFormula.SAVEPOINT - 480)) | (1 << (BaserowFormula.SCALE - 480)) | (1 << (BaserowFormula.SCHEMA - 480)) | (1 << (BaserowFormula.SCHEMA_NAME - 480)) | (1 << (BaserowFormula.SCOPE - 480)) | (1 << (BaserowFormula.SCOPE_CATALOG - 480)) | (1 << (BaserowFormula.SCOPE_NAME - 480)) | (1 << (BaserowFormula.SCOPE_SCHEMA - 480)) | (1 << (BaserowFormula.SCROLL - 480)) | (1 << (BaserowFormula.SEARCH - 480)) | (1 << (BaserowFormula.SECOND - 480)) | (1 << (BaserowFormula.SECTION - 480)) | (1 << (BaserowFormula.SECURITY - 480)) | (1 << (BaserowFormula.SELECT - 480)) | (1 << (BaserowFormula.SELF - 480)))) !== 0) || ((((_la - 512)) & ~0x1f) == 0 && ((1 << (_la - 512)) & ((1 << (BaserowFormula.SENSITIVE - 512)) | (1 << (BaserowFormula.SEQUENCE - 512)) | (1 << (BaserowFormula.SEQUENCES - 512)) | (1 << (BaserowFormula.SERIALIZABLE - 512)) | (1 << (BaserowFormula.SERVER_NAME - 512)) | (1 << (BaserowFormula.SESSION - 512)) | (1 << (BaserowFormula.SESSION_USER - 512)) | (1 << (BaserowFormula.SET - 512)) | (1 << (BaserowFormula.SETOF - 512)) | (1 << (BaserowFormula.SETS - 512)) | (1 << (BaserowFormula.SHARE - 512)) | (1 << (BaserowFormula.SHOW - 512)) | (1 << (BaserowFormula.SIMILAR - 512)) | (1 << (BaserowFormula.SIMPLE - 512)) | (1 << (BaserowFormula.SIZE - 512)) | (1 << (BaserowFormula.SKIP_ - 512)) | (1 << (BaserowFormula.SMALLINT - 512)) | (1 << (BaserowFormula.SNAPSHOT - 512)) | (1 << (BaserowFormula.SOME - 512)) | (1 << (BaserowFormula.SOURCE - 512)) | (1 << (BaserowFormula.SPACE - 512)) | (1 << (BaserowFormula.SPECIFIC - 512)) | (1 << (BaserowFormula.SPECIFIC_NAME - 512)) | (1 << (BaserowFormula.SPECIFICTYPE - 512)) | (1 << (BaserowFormula.SQL - 512)) | (1 << (BaserowFormula.SQLCODE - 512)) | (1 << (BaserowFormula.SQLERROR - 512)) | (1 << (BaserowFormula.SQLEXCEPTION - 512)) | (1 << (BaserowFormula.SQLSTATE - 512)) | (1 << (BaserowFormula.SQLWARNING - 512)) | (1 << (BaserowFormula.SQRT - 512)) | (1 << (BaserowFormula.STABLE - 512)))) !== 0) || ((((_la - 544)) & ~0x1f) == 0 && ((1 << (_la - 544)) & ((1 << (BaserowFormula.START - 544)) | (1 << (BaserowFormula.STATE - 544)) | (1 << (BaserowFormula.STATEMENT - 544)) | (1 << (BaserowFormula.STATIC - 544)) | (1 << (BaserowFormula.STATISTICS - 544)) | (1 << (BaserowFormula.STDDEV_POP - 544)) | (1 << (BaserowFormula.STDDEV_SAMP - 544)) | (1 << (BaserowFormula.STDIN - 544)) | (1 << (BaserowFormula.STDOUT - 544)) | (1 << (BaserowFormula.STORAGE - 544)) | (1 << (BaserowFormula.STRICT - 544)) | (1 << (BaserowFormula.STRUCTURE - 544)) | (1 << (BaserowFormula.STYLE - 544)) | (1 << (BaserowFormula.SUBCLASS_ORIGIN - 544)) | (1 << (BaserowFormula.SUBLIST - 544)) | (1 << (BaserowFormula.SUBMULTISET - 544)) | (1 << (BaserowFormula.SUBSCRIPTION - 544)) | (1 << (BaserowFormula.SUBSTRING - 544)) | (1 << (BaserowFormula.SUM - 544)) | (1 << (BaserowFormula.SYMMETRIC - 544)) | (1 << (BaserowFormula.SYSID - 544)) | (1 << (BaserowFormula.SYSTEM - 544)) | (1 << (BaserowFormula.SYSTEM_USER - 544)) | (1 << (BaserowFormula.TABLE - 544)) | (1 << (BaserowFormula.TABLE_NAME - 544)) | (1 << (BaserowFormula.TABLESAMPLE - 544)) | (1 << (BaserowFormula.TABLESPACE - 544)) | (1 << (BaserowFormula.TEMP - 544)) | (1 << (BaserowFormula.TEMPLATE - 544)) | (1 << (BaserowFormula.TEMPORARY - 544)) | (1 << (BaserowFormula.TERMINATE - 544)) | (1 << (BaserowFormula.THAN - 544)))) !== 0) || ((((_la - 576)) & ~0x1f) == 0 && ((1 << (_la - 576)) & ((1 << (BaserowFormula.THEN - 576)) | (1 << (BaserowFormula.TIES - 576)) | (1 << (BaserowFormula.TIME - 576)) | (1 << (BaserowFormula.TIMESTAMP - 576)) | (1 << (BaserowFormula.TIMEZONE_HOUR - 576)) | (1 << (BaserowFormula.TIMEZONE_MINUTE - 576)) | (1 << (BaserowFormula.TIMING - 576)) | (1 << (BaserowFormula.TO - 576)) | (1 << (BaserowFormula.TOAST - 576)) | (1 << (BaserowFormula.TOP_LEVEL_COUNT - 576)) | (1 << (BaserowFormula.TRAILING - 576)) | (1 << (BaserowFormula.TRANSACTION - 576)) | (1 << (BaserowFormula.TRANSACTION_ACTIVE - 576)) | (1 << (BaserowFormula.TRANSACTIONS_COMMITTED - 576)) | (1 << (BaserowFormula.TRANSACTIONS_ROLLED_BACK - 576)) | (1 << (BaserowFormula.TRANSFORM - 576)) | (1 << (BaserowFormula.TRANSFORMS - 576)) | (1 << (BaserowFormula.TRANSLATE - 576)) | (1 << (BaserowFormula.TRANSLATION - 576)) | (1 << (BaserowFormula.TREAT - 576)) | (1 << (BaserowFormula.TRIGGER - 576)) | (1 << (BaserowFormula.TRIGGER_CATALOG - 576)) | (1 << (BaserowFormula.TRIGGER_NAME - 576)) | (1 << (BaserowFormula.TRIGGER_SCHEMA - 576)) | (1 << (BaserowFormula.TRIM - 576)) | (1 << (BaserowFormula.TRUE - 576)) | (1 << (BaserowFormula.TRUNCATE - 576)) | (1 << (BaserowFormula.TRUSTED - 576)) | (1 << (BaserowFormula.TYPE - 576)) | (1 << (BaserowFormula.UESCAPE - 576)) | (1 << (BaserowFormula.UNBOUNDED - 576)) | (1 << (BaserowFormula.UNCOMMITTED - 576)))) !== 0) || ((((_la - 608)) & ~0x1f) == 0 && ((1 << (_la - 608)) & ((1 << (BaserowFormula.UNDER - 608)) | (1 << (BaserowFormula.UNENCRYPTED - 608)) | (1 << (BaserowFormula.UNION - 608)) | (1 << (BaserowFormula.UNIQUE - 608)) | (1 << (BaserowFormula.UNKNOWN - 608)) | (1 << (BaserowFormula.UNLISTEN - 608)) | (1 << (BaserowFormula.UNNAMED - 608)) | (1 << (BaserowFormula.UNNEST - 608)) | (1 << (BaserowFormula.UNTIL - 608)) | (1 << (BaserowFormula.UPDATE - 608)) | (1 << (BaserowFormula.UPPER - 608)) | (1 << (BaserowFormula.USAGE - 608)) | (1 << (BaserowFormula.USER - 608)) | (1 << (BaserowFormula.USER_DEFINED_TYPE_CATALOG - 608)) | (1 << (BaserowFormula.USER_DEFINED_TYPE_CODE - 608)) | (1 << (BaserowFormula.USER_DEFINED_TYPE_NAME - 608)) | (1 << (BaserowFormula.USER_DEFINED_TYPE_SCHEMA - 608)) | (1 << (BaserowFormula.USING - 608)) | (1 << (BaserowFormula.VACUUM - 608)) | (1 << (BaserowFormula.VALID - 608)) | (1 << (BaserowFormula.VALIDATE - 608)) | (1 << (BaserowFormula.VALIDATOR - 608)) | (1 << (BaserowFormula.VALUE - 608)) | (1 << (BaserowFormula.VALUES - 608)) | (1 << (BaserowFormula.VAR_POP - 608)) | (1 << (BaserowFormula.VAR_SAMP - 608)) | (1 << (BaserowFormula.VARCHAR - 608)) | (1 << (BaserowFormula.VARIABLE - 608)) | (1 << (BaserowFormula.VARIADIC - 608)) | (1 << (BaserowFormula.VARYING - 608)) | (1 << (BaserowFormula.VERBOSE - 608)) | (1 << (BaserowFormula.VIEW - 608)))) !== 0) || ((((_la - 640)) & ~0x1f) == 0 && ((1 << (_la - 640)) & ((1 << (BaserowFormula.VOLATILE - 640)) | (1 << (BaserowFormula.WHEN - 640)) | (1 << (BaserowFormula.WHENEVER - 640)) | (1 << (BaserowFormula.WHERE - 640)) | (1 << (BaserowFormula.WIDTH_BUCKET - 640)) | (1 << (BaserowFormula.WINDOW - 640)) | (1 << (BaserowFormula.WITH - 640)) | (1 << (BaserowFormula.WITHIN - 640)) | (1 << (BaserowFormula.WITHOUT - 640)) | (1 << (BaserowFormula.WORK - 640)) | (1 << (BaserowFormula.WRITE - 640)) | (1 << (BaserowFormula.YAML - 640)) | (1 << (BaserowFormula.YEAR - 640)) | (1 << (BaserowFormula.YES - 640)) | (1 << (BaserowFormula.ZONE - 640)) | (1 << (BaserowFormula.SUPERUSER - 640)) | (1 << (BaserowFormula.NOSUPERUSER - 640)) | (1 << (BaserowFormula.CREATEROLE - 640)) | (1 << (BaserowFormula.NOCREATEROLE - 640)) | (1 << (BaserowFormula.INHERIT - 640)) | (1 << (BaserowFormula.NOINHERIT - 640)) | (1 << (BaserowFormula.LOGIN - 640)) | (1 << (BaserowFormula.NOLOGIN - 640)) | (1 << (BaserowFormula.REPLICATION - 640)) | (1 << (BaserowFormula.NOREPLICATION - 640)) | (1 << (BaserowFormula.BYPASSRLS - 640)) | (1 << (BaserowFormula.NOBYPASSRLS - 640)) | (1 << (BaserowFormula.SFUNC - 640)) | (1 << (BaserowFormula.STYPE - 640)) | (1 << (BaserowFormula.SSPACE - 640)) | (1 << (BaserowFormula.FINALFUNC - 640)) | (1 << (BaserowFormula.FINALFUNC_EXTRA - 640)))) !== 0) || ((((_la - 672)) & ~0x1f) == 0 && ((1 << (_la - 672)) & ((1 << (BaserowFormula.COMBINEFUNC - 672)) | (1 << (BaserowFormula.SERIALFUNC - 672)) | (1 << (BaserowFormula.DESERIALFUNC - 672)) | (1 << (BaserowFormula.INITCOND - 672)) | (1 << (BaserowFormula.MSFUNC - 672)) | (1 << (BaserowFormula.MINVFUNC - 672)) | (1 << (BaserowFormula.MSTYPE - 672)) | (1 << (BaserowFormula.MSSPACE - 672)) | (1 << (BaserowFormula.MFINALFUNC - 672)) | (1 << (BaserowFormula.MFINALFUNC_EXTRA - 672)) | (1 << (BaserowFormula.MINITCOND - 672)) | (1 << (BaserowFormula.SORTOP - 672)) | (1 << (BaserowFormula.PARALLEL - 672)) | (1 << (BaserowFormula.HYPOTHETICAL - 672)) | (1 << (BaserowFormula.SAFE - 672)) | (1 << (BaserowFormula.RESTRICTED - 672)) | (1 << (BaserowFormula.UNSAFE - 672)) | (1 << (BaserowFormula.BASETYPE - 672)) | (1 << (BaserowFormula.IF - 672)) | (1 << (BaserowFormula.LOCALE - 672)) | (1 << (BaserowFormula.LC_COLLATE - 672)) | (1 << (BaserowFormula.LC_CTYPE - 672)) | (1 << (BaserowFormula.PROVIDER - 672)) | (1 << (BaserowFormula.VERSION - 672)) | (1 << (BaserowFormula.ALLOW_CONNECTIONS - 672)) | (1 << (BaserowFormula.IS_TEMPLATE - 672)) | (1 << (BaserowFormula.EVENT - 672)) | (1 << (BaserowFormula.WRAPPER - 672)) | (1 << (BaserowFormula.SERVER - 672)) | (1 << (BaserowFormula.BTREE - 672)) | (1 << (BaserowFormula.HASH_ - 672)) | (1 << (BaserowFormula.GIST - 672)))) !== 0) || ((((_la - 704)) & ~0x1f) == 0 && ((1 << (_la - 704)) & ((1 << (BaserowFormula.SPGIST - 704)) | (1 << (BaserowFormula.GIN - 704)) | (1 << (BaserowFormula.BRIN - 704)) | (1 << (BaserowFormula.CONCURRENTLY - 704)) | (1 << (BaserowFormula.INLINE - 704)) | (1 << (BaserowFormula.MATERIALIZED - 704)) | (1 << (BaserowFormula.LEFTARG - 704)) | (1 << (BaserowFormula.RIGHTARG - 704)) | (1 << (BaserowFormula.COMMUTATOR - 704)) | (1 << (BaserowFormula.NEGATOR - 704)) | (1 << (BaserowFormula.HASHES - 704)) | (1 << (BaserowFormula.MERGES - 704)) | (1 << (BaserowFormula.FAMILY - 704)) | (1 << (BaserowFormula.POLICY - 704)) | (1 << (BaserowFormula.OWNED - 704)) | (1 << (BaserowFormula.ABSTIME - 704)) | (1 << (BaserowFormula.BIGSERIAL - 704)) | (1 << (BaserowFormula.BIT_VARYING - 704)) | (1 << (BaserowFormula.BOOL - 704)) | (1 << (BaserowFormula.BOX - 704)) | (1 << (BaserowFormula.BYTEA - 704)) | (1 << (BaserowFormula.CHARACTER_VARYING - 704)) | (1 << (BaserowFormula.CIDR - 704)) | (1 << (BaserowFormula.CIRCLE - 704)) | (1 << (BaserowFormula.FLOAT4 - 704)) | (1 << (BaserowFormula.FLOAT8 - 704)) | (1 << (BaserowFormula.INET - 704)) | (1 << (BaserowFormula.INT2 - 704)) | (1 << (BaserowFormula.INT4 - 704)) | (1 << (BaserowFormula.INT8 - 704)) | (1 << (BaserowFormula.JSON - 704)) | (1 << (BaserowFormula.JSONB - 704)))) !== 0) || ((((_la - 736)) & ~0x1f) == 0 && ((1 << (_la - 736)) & ((1 << (BaserowFormula.LINE - 736)) | (1 << (BaserowFormula.LSEG - 736)) | (1 << (BaserowFormula.MACADDR - 736)) | (1 << (BaserowFormula.MACADDR8 - 736)) | (1 << (BaserowFormula.MONEY - 736)) | (1 << (BaserowFormula.PG_LSN - 736)) | (1 << (BaserowFormula.POINT - 736)) | (1 << (BaserowFormula.POLYGON - 736)) | (1 << (BaserowFormula.RELTIME - 736)) | (1 << (BaserowFormula.SERIAL - 736)) | (1 << (BaserowFormula.SERIAL2 - 736)) | (1 << (BaserowFormula.SERIAL4 - 736)) | (1 << (BaserowFormula.SERIAL8 - 736)) | (1 << (BaserowFormula.SMALLSERIAL - 736)) | (1 << (BaserowFormula.STSTEM - 736)) | (1 << (BaserowFormula.TEXT - 736)) | (1 << (BaserowFormula.TIMESTAMPTZ - 736)) | (1 << (BaserowFormula.TIMETZ - 736)) | (1 << (BaserowFormula.TSQUERY - 736)) | (1 << (BaserowFormula.TSVECTOR - 736)) | (1 << (BaserowFormula.TXID_SNAPSHOT - 736)) | (1 << (BaserowFormula.UUID - 736)) | (1 << (BaserowFormula.VARBIT - 736)) | (1 << (BaserowFormula.XML - 736)) | (1 << (BaserowFormula.COMMA - 736)) | (1 << (BaserowFormula.COLON - 736)) | (1 << (BaserowFormula.COLON_COLON - 736)) | (1 << (BaserowFormula.DOLLAR_DOLLAR - 736)) | (1 << (BaserowFormula.STAR - 736)) | (1 << (BaserowFormula.OPEN_PAREN - 736)) | (1 << (BaserowFormula.CLOSE_PAREN - 736)))) !== 0) || ((((_la - 768)) & ~0x1f) == 0 && ((1 << (_la - 768)) & ((1 << (BaserowFormula.OPEN_BRACKET - 768)) | (1 << (BaserowFormula.CLOSE_BRACKET - 768)) | (1 << (BaserowFormula.BIT_STRING - 768)) | (1 << (BaserowFormula.REGEX_STRING - 768)) | (1 << (BaserowFormula.NUMERIC_LITERAL - 768)) | (1 << (BaserowFormula.INTEGER_LITERAL - 768)) | (1 << (BaserowFormula.HEX_INTEGER_LITERAL - 768)) | (1 << (BaserowFormula.DOT - 768)) | (1 << (BaserowFormula.SINGLEQ_STRING_LITERAL - 768)) | (1 << (BaserowFormula.DOUBLEQ_STRING_LITERAL - 768)) | (1 << (BaserowFormula.IDENTIFIER - 768)) | (1 << (BaserowFormula.DOLLAR_DEC - 768)) | (1 << (BaserowFormula.IDENTIFIER_UNICODE - 768)) | (1 << (BaserowFormula.AMP - 768)) | (1 << (BaserowFormula.AMP_AMP - 768)) | (1 << (BaserowFormula.AMP_LT - 768)) | (1 << (BaserowFormula.AT_AT - 768)) | (1 << (BaserowFormula.AT_GT - 768)) | (1 << (BaserowFormula.AT_SIGN - 768)) | (1 << (BaserowFormula.BANG - 768)) | (1 << (BaserowFormula.BANG_BANG - 768)) | (1 << (BaserowFormula.BANG_EQUAL - 768)) | (1 << (BaserowFormula.CARET - 768)) | (1 << (BaserowFormula.EQUAL - 768)) | (1 << (BaserowFormula.EQUAL_GT - 768)) | (1 << (BaserowFormula.GT - 768)) | (1 << (BaserowFormula.GTE - 768)) | (1 << (BaserowFormula.GT_GT - 768)) | (1 << (BaserowFormula.HASH - 768)) | (1 << (BaserowFormula.HASH_EQ - 768)) | (1 << (BaserowFormula.HASH_GT - 768)) | (1 << (BaserowFormula.HASH_GT_GT - 768)))) !== 0) || ((((_la - 800)) & ~0x1f) == 0 && ((1 << (_la - 800)) & ((1 << (BaserowFormula.HASH_HASH - 800)) | (1 << (BaserowFormula.HYPHEN_GT - 800)) | (1 << (BaserowFormula.HYPHEN_GT_GT - 800)) | (1 << (BaserowFormula.HYPHEN_PIPE_HYPHEN - 800)) | (1 << (BaserowFormula.LT - 800)) | (1 << (BaserowFormula.LTE - 800)) | (1 << (BaserowFormula.LT_AT - 800)) | (1 << (BaserowFormula.LT_CARET - 800)) | (1 << (BaserowFormula.LT_GT - 800)) | (1 << (BaserowFormula.LT_HYPHEN_GT - 800)) | (1 << (BaserowFormula.LT_LT - 800)) | (1 << (BaserowFormula.LT_LT_EQ - 800)) | (1 << (BaserowFormula.LT_QMARK_GT - 800)) | (1 << (BaserowFormula.MINUS - 800)) | (1 << (BaserowFormula.PERCENT - 800)) | (1 << (BaserowFormula.PIPE - 800)) | (1 << (BaserowFormula.PIPE_PIPE - 800)) | (1 << (BaserowFormula.PIPE_PIPE_SLASH - 800)) | (1 << (BaserowFormula.PIPE_SLASH - 800)) | (1 << (BaserowFormula.PLUS - 800)) | (1 << (BaserowFormula.QMARK - 800)) | (1 << (BaserowFormula.QMARK_AMP - 800)) | (1 << (BaserowFormula.QMARK_HASH - 800)) | (1 << (BaserowFormula.QMARK_HYPHEN - 800)) | (1 << (BaserowFormula.QMARK_PIPE - 800)) | (1 << (BaserowFormula.SLASH - 800)) | (1 << (BaserowFormula.TIL - 800)) | (1 << (BaserowFormula.TIL_EQ - 800)) | (1 << (BaserowFormula.TIL_GTE_TIL - 800)) | (1 << (BaserowFormula.TIL_GT_TIL - 800)) | (1 << (BaserowFormula.TIL_LTE_TIL - 800)) | (1 << (BaserowFormula.TIL_LT_TIL - 800)))) !== 0) || ((((_la - 832)) & ~0x1f) == 0 && ((1 << (_la - 832)) & ((1 << (BaserowFormula.TIL_STAR - 832)) | (1 << (BaserowFormula.TIL_TIL - 832)) | (1 << (BaserowFormula.SEMI - 832)))) !== 0));
	            this.state = 52;
	            this.match(BaserowFormula.DOLLAR);
	            this.state = 53;
	            this.identifier(0);
	            this.state = 54;
	            this.match(BaserowFormula.DOLLAR);
	            break;

	        case 13:
	            this.state = 56;
	            this.bool_expr(0);
	            break;

	        case 14:
	            this.state = 57;
	            this.expr_list();
	            break;

	        case 15:
	            this.state = 58;
	            this.match(BaserowFormula.OPEN_PAREN);
	            this.state = 59;
	            this.expr(0);
	            this.state = 60;
	            this.match(BaserowFormula.CLOSE_PAREN);
	            break;

	        case 16:
	            this.state = 62;
	            this.type_name();
	            this.state = 63;
	            this.match(BaserowFormula.SINGLEQ_STRING_LITERAL);
	            break;

	        case 17:
	            this.state = 65;
	            localctx.op = this._input.LT(1);
	            _la = this._input.LA(1);
	            if(!(((((_la - 786)) & ~0x1f) == 0 && ((1 << (_la - 786)) & ((1 << (BaserowFormula.AT_SIGN - 786)) | (1 << (BaserowFormula.BANG_BANG - 786)) | (1 << (BaserowFormula.MINUS - 786)))) !== 0) || _la===BaserowFormula.PLUS)) {
	                localctx.op = this._errHandler.recoverInline(this);
	            }
	            else {
	            	this._errHandler.reportMatch(this);
	                this.consume();
	            }
	            this.state = 66;
	            this.expr(26);
	            break;

	        case 18:
	            this.state = 67;
	            localctx.op = this._input.LT(1);
	            _la = this._input.LA(1);
	            if(!(_la===BaserowFormula.QMARK_HYPHEN || _la===BaserowFormula.TIL)) {
	                localctx.op = this._errHandler.recoverInline(this);
	            }
	            else {
	            	this._errHandler.reportMatch(this);
	                this.consume();
	            }
	            this.state = 68;
	            this.expr(25);
	            break;

	        case 19:
	            this.state = 69;
	            localctx.op = this._input.LT(1);
	            _la = this._input.LA(1);
	            if(!(_la===BaserowFormula.ALL || _la===BaserowFormula.NOT)) {
	                localctx.op = this._errHandler.recoverInline(this);
	            }
	            else {
	            	this._errHandler.reportMatch(this);
	                this.consume();
	            }
	            this.state = 70;
	            this.expr(13);
	            break;

	        case 20:
	            this.state = 71;
	            this.func_call();
	            break;

	        case 21:
	            this.state = 72;
	            this.identifier(0);
	            break;

	        case 22:
	            this.state = 73;
	            this.match(BaserowFormula.CAST);
	            this.state = 74;
	            this.match(BaserowFormula.OPEN_PAREN);
	            this.state = 75;
	            this.expr(0);
	            this.state = 76;
	            this.match(BaserowFormula.AS);
	            this.state = 77;
	            this.data_type();
	            this.state = 78;
	            this.match(BaserowFormula.CLOSE_PAREN);
	            break;

	        case 23:
	            this.state = 80;
	            this.case_expr();
	            break;

	        case 24:
	            this.state = 81;
	            this.data_type();
	            this.state = 82;
	            this.expr(6);
	            break;

	        case 25:
	            this.state = 84;
	            this.match(BaserowFormula.EXISTS);
	            this.state = 85;
	            this.expr(2);
	            break;

	        case 26:
	            this.state = 86;
	            this.match(BaserowFormula.DOLLAR_DEC);
	            break;

	        }
	        this._ctx.stop = this._input.LT(-1);
	        this.state = 188;
	        this._errHandler.sync(this);
	        var _alt = this._interp.adaptivePredict(this._input,13,this._ctx)
	        while(_alt!=2 && _alt!=antlr4.atn.ATN.INVALID_ALT_NUMBER) {
	            if(_alt===1) {
	                if(this._parseListeners!==null) {
	                    this.triggerExitRuleEvent();
	                }
	                _prevctx = localctx;
	                this.state = 186;
	                this._errHandler.sync(this);
	                var la_ = this._interp.adaptivePredict(this._input,12,this._ctx);
	                switch(la_) {
	                case 1:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 89;
	                    if (!( this.precpred(this._ctx, 23))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 23)");
	                    }
	                    this.state = 90;
	                    localctx.op = this._input.LT(1);
	                    _la = this._input.LA(1);
	                    if(!(((((_la - 790)) & ~0x1f) == 0 && ((1 << (_la - 790)) & ((1 << (BaserowFormula.CARET - 790)) | (1 << (BaserowFormula.PIPE_PIPE_SLASH - 790)) | (1 << (BaserowFormula.PIPE_SLASH - 790)))) !== 0))) {
	                        localctx.op = this._errHandler.recoverInline(this);
	                    }
	                    else {
	                    	this._errHandler.reportMatch(this);
	                        this.consume();
	                    }
	                    this.state = 91;
	                    this.expr(24);
	                    break;

	                case 2:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 92;
	                    if (!( this.precpred(this._ctx, 22))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 22)");
	                    }
	                    this.state = 93;
	                    localctx.op = this._input.LT(1);
	                    _la = this._input.LA(1);
	                    if(!(_la===BaserowFormula.STAR || _la===BaserowFormula.PERCENT || _la===BaserowFormula.SLASH)) {
	                        localctx.op = this._errHandler.recoverInline(this);
	                    }
	                    else {
	                    	this._errHandler.reportMatch(this);
	                        this.consume();
	                    }
	                    this.state = 94;
	                    this.expr(23);
	                    break;

	                case 3:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 95;
	                    if (!( this.precpred(this._ctx, 21))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 21)");
	                    }
	                    this.state = 96;
	                    localctx.op = this._input.LT(1);
	                    _la = this._input.LA(1);
	                    if(!(_la===BaserowFormula.MINUS || _la===BaserowFormula.PLUS)) {
	                        localctx.op = this._errHandler.recoverInline(this);
	                    }
	                    else {
	                    	this._errHandler.reportMatch(this);
	                        this.consume();
	                    }
	                    this.state = 97;
	                    this.expr(22);
	                    break;

	                case 4:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 98;
	                    if (!( this.precpred(this._ctx, 20))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 20)");
	                    }
	                    this.state = 99;
	                    localctx.op = this._input.LT(1);
	                    _la = this._input.LA(1);
	                    if(!(_la===BaserowFormula.AND || _la===BaserowFormula.NOT || _la===BaserowFormula.OR || ((((_la - 781)) & ~0x1f) == 0 && ((1 << (_la - 781)) & ((1 << (BaserowFormula.AMP - 781)) | (1 << (BaserowFormula.AMP_AMP - 781)) | (1 << (BaserowFormula.AMP_LT - 781)) | (1 << (BaserowFormula.AT_AT - 781)) | (1 << (BaserowFormula.AT_GT - 781)) | (1 << (BaserowFormula.EQUAL_GT - 781)) | (1 << (BaserowFormula.GT_GT - 781)) | (1 << (BaserowFormula.HASH - 781)) | (1 << (BaserowFormula.HASH_EQ - 781)) | (1 << (BaserowFormula.HASH_GT - 781)) | (1 << (BaserowFormula.HASH_GT_GT - 781)) | (1 << (BaserowFormula.HASH_HASH - 781)) | (1 << (BaserowFormula.HYPHEN_GT - 781)) | (1 << (BaserowFormula.HYPHEN_GT_GT - 781)) | (1 << (BaserowFormula.HYPHEN_PIPE_HYPHEN - 781)) | (1 << (BaserowFormula.LT_AT - 781)) | (1 << (BaserowFormula.LT_CARET - 781)) | (1 << (BaserowFormula.LT_HYPHEN_GT - 781)) | (1 << (BaserowFormula.LT_LT - 781)) | (1 << (BaserowFormula.LT_LT_EQ - 781)) | (1 << (BaserowFormula.LT_QMARK_GT - 781)))) !== 0) || ((((_la - 815)) & ~0x1f) == 0 && ((1 << (_la - 815)) & ((1 << (BaserowFormula.PIPE - 815)) | (1 << (BaserowFormula.PIPE_PIPE - 815)) | (1 << (BaserowFormula.QMARK - 815)) | (1 << (BaserowFormula.QMARK_AMP - 815)) | (1 << (BaserowFormula.QMARK_HASH - 815)) | (1 << (BaserowFormula.QMARK_PIPE - 815)) | (1 << (BaserowFormula.TIL - 815)) | (1 << (BaserowFormula.TIL_EQ - 815)) | (1 << (BaserowFormula.TIL_GTE_TIL - 815)) | (1 << (BaserowFormula.TIL_GT_TIL - 815)) | (1 << (BaserowFormula.TIL_LTE_TIL - 815)) | (1 << (BaserowFormula.TIL_LT_TIL - 815)) | (1 << (BaserowFormula.TIL_STAR - 815)) | (1 << (BaserowFormula.TIL_TIL - 815)))) !== 0))) {
	                        localctx.op = this._errHandler.recoverInline(this);
	                    }
	                    else {
	                    	this._errHandler.reportMatch(this);
	                        this.consume();
	                    }
	                    this.state = 100;
	                    this.expr(21);
	                    break;

	                case 5:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 101;
	                    if (!( this.precpred(this._ctx, 19))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 19)");
	                    }
	                    this.state = 105;
	                    this._errHandler.sync(this);
	                    switch(this._input.LA(1)) {
	                    case BaserowFormula.NOT:
	                        this.state = 102;
	                        this.match(BaserowFormula.NOT);
	                        this.state = 103;
	                        this.match(BaserowFormula.LIKE);
	                        break;
	                    case BaserowFormula.LIKE:
	                        this.state = 104;
	                        this.match(BaserowFormula.LIKE);
	                        break;
	                    default:
	                        throw new antlr4.error.NoViableAltException(this);
	                    }
	                    this.state = 107;
	                    this.expr(20);
	                    break;

	                case 6:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 108;
	                    if (!( this.precpred(this._ctx, 18))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 18)");
	                    }
	                    this.state = 110;
	                    this._errHandler.sync(this);
	                    _la = this._input.LA(1);
	                    if(_la===BaserowFormula.NOT) {
	                        this.state = 109;
	                        this.match(BaserowFormula.NOT);
	                    }

	                    this.state = 112;
	                    this.match(BaserowFormula.BETWEEN);
	                    this.state = 113;
	                    this.expr(0);
	                    this.state = 114;
	                    this.match(BaserowFormula.AND);
	                    this.state = 115;
	                    this.expr(19);
	                    break;

	                case 7:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 117;
	                    if (!( this.precpred(this._ctx, 17))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 17)");
	                    }
	                    this.state = 118;
	                    this.match(BaserowFormula.IN);
	                    this.state = 119;
	                    this.expr(18);
	                    break;

	                case 8:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 120;
	                    if (!( this.precpred(this._ctx, 16))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 16)");
	                    }
	                    this.state = 121;
	                    localctx.op = this._input.LT(1);
	                    _la = this._input.LA(1);
	                    if(!(((((_la - 789)) & ~0x1f) == 0 && ((1 << (_la - 789)) & ((1 << (BaserowFormula.BANG_EQUAL - 789)) | (1 << (BaserowFormula.EQUAL - 789)) | (1 << (BaserowFormula.GT - 789)) | (1 << (BaserowFormula.GTE - 789)) | (1 << (BaserowFormula.LT - 789)) | (1 << (BaserowFormula.LTE - 789)) | (1 << (BaserowFormula.LT_GT - 789)))) !== 0))) {
	                        localctx.op = this._errHandler.recoverInline(this);
	                    }
	                    else {
	                    	this._errHandler.reportMatch(this);
	                        this.consume();
	                    }
	                    this.state = 122;
	                    this.expr(17);
	                    break;

	                case 9:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 123;
	                    if (!( this.precpred(this._ctx, 14))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 14)");
	                    }
	                    this.state = 124;
	                    this.match(BaserowFormula.IS);
	                    this.state = 126;
	                    this._errHandler.sync(this);
	                    _la = this._input.LA(1);
	                    if(_la===BaserowFormula.NOT) {
	                        this.state = 125;
	                        this.match(BaserowFormula.NOT);
	                    }

	                    this.state = 128;
	                    this.match(BaserowFormula.DISTINCT);
	                    this.state = 129;
	                    this.match(BaserowFormula.FROM);
	                    this.state = 130;
	                    this.expr(15);
	                    break;

	                case 10:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 131;
	                    if (!( this.precpred(this._ctx, 29))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 29)");
	                    }
	                    this.state = 132;
	                    this.match(BaserowFormula.OPEN_BRACKET);
	                    this.state = 133;
	                    this.expr(0);
	                    this.state = 134;
	                    this.match(BaserowFormula.CLOSE_BRACKET);
	                    break;

	                case 11:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 136;
	                    if (!( this.precpred(this._ctx, 24))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 24)");
	                    }
	                    this.state = 137;
	                    localctx.op = this.match(BaserowFormula.BANG);
	                    break;

	                case 12:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 138;
	                    if (!( this.precpred(this._ctx, 15))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 15)");
	                    }
	                    this.state = 139;
	                    localctx.op = this.match(BaserowFormula.IS);
	                    this.state = 144;
	                    this._errHandler.sync(this);
	                    var la_ = this._interp.adaptivePredict(this._input,6,this._ctx);
	                    switch(la_) {
	                    case 1:
	                        this.state = 140;
	                        this.bool_expr(0);
	                        break;

	                    case 2:
	                        this.state = 141;
	                        this.match(BaserowFormula.NULL);
	                        break;

	                    case 3:
	                        this.state = 142;
	                        this.match(BaserowFormula.NOT);
	                        this.state = 143;
	                        this.match(BaserowFormula.NULL);
	                        break;

	                    }
	                    break;

	                case 13:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 146;
	                    if (!( this.precpred(this._ctx, 8))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 8)");
	                    }
	                    this.state = 156; 
	                    this._errHandler.sync(this);
	                    var _alt = 1;
	                    do {
	                    	switch (_alt) {
	                    	case 1:
	                    		this.state = 147;
	                    		this.match(BaserowFormula.OPEN_BRACKET);
	                    		this.state = 149;
	                    		this._errHandler.sync(this);
	                    		_la = this._input.LA(1);
	                    		if(_la===BaserowFormula.ALL || _la===BaserowFormula.CASE || _la===BaserowFormula.CAST || ((((_la - 134)) & ~0x1f) == 0 && ((1 << (_la - 134)) & ((1 << (BaserowFormula.CURRENT_DATE - 134)) | (1 << (BaserowFormula.CURRENT_TIME - 134)) | (1 << (BaserowFormula.CURRENT_TIMESTAMP - 134)))) !== 0) || _la===BaserowFormula.EXISTS || _la===BaserowFormula.FALSE || _la===BaserowFormula.LOWER || _la===BaserowFormula.NOT || _la===BaserowFormula.NULL || _la===BaserowFormula.TRUE || _la===BaserowFormula.UPPER || ((((_la - 751)) & ~0x1f) == 0 && ((1 << (_la - 751)) & ((1 << (BaserowFormula.TEXT - 751)) | (1 << (BaserowFormula.DOLLAR - 751)) | (1 << (BaserowFormula.DOLLAR_DOLLAR - 751)) | (1 << (BaserowFormula.OPEN_PAREN - 751)) | (1 << (BaserowFormula.BIT_STRING - 751)) | (1 << (BaserowFormula.REGEX_STRING - 751)) | (1 << (BaserowFormula.NUMERIC_LITERAL - 751)) | (1 << (BaserowFormula.INTEGER_LITERAL - 751)) | (1 << (BaserowFormula.HEX_INTEGER_LITERAL - 751)) | (1 << (BaserowFormula.SINGLEQ_STRING_LITERAL - 751)) | (1 << (BaserowFormula.DOUBLEQ_STRING_LITERAL - 751)) | (1 << (BaserowFormula.IDENTIFIER - 751)) | (1 << (BaserowFormula.DOLLAR_DEC - 751)) | (1 << (BaserowFormula.IDENTIFIER_UNICODE - 751)))) !== 0) || ((((_la - 786)) & ~0x1f) == 0 && ((1 << (_la - 786)) & ((1 << (BaserowFormula.AT_SIGN - 786)) | (1 << (BaserowFormula.BANG_BANG - 786)) | (1 << (BaserowFormula.MINUS - 786)))) !== 0) || ((((_la - 819)) & ~0x1f) == 0 && ((1 << (_la - 819)) & ((1 << (BaserowFormula.PLUS - 819)) | (1 << (BaserowFormula.QMARK_HYPHEN - 819)) | (1 << (BaserowFormula.TIL - 819)))) !== 0)) {
	                    		    this.state = 148;
	                    		    this.expr(0);
	                    		}

	                    		this.state = 151;
	                    		this.match(BaserowFormula.COLON);
	                    		this.state = 153;
	                    		this._errHandler.sync(this);
	                    		_la = this._input.LA(1);
	                    		if(_la===BaserowFormula.ALL || _la===BaserowFormula.CASE || _la===BaserowFormula.CAST || ((((_la - 134)) & ~0x1f) == 0 && ((1 << (_la - 134)) & ((1 << (BaserowFormula.CURRENT_DATE - 134)) | (1 << (BaserowFormula.CURRENT_TIME - 134)) | (1 << (BaserowFormula.CURRENT_TIMESTAMP - 134)))) !== 0) || _la===BaserowFormula.EXISTS || _la===BaserowFormula.FALSE || _la===BaserowFormula.LOWER || _la===BaserowFormula.NOT || _la===BaserowFormula.NULL || _la===BaserowFormula.TRUE || _la===BaserowFormula.UPPER || ((((_la - 751)) & ~0x1f) == 0 && ((1 << (_la - 751)) & ((1 << (BaserowFormula.TEXT - 751)) | (1 << (BaserowFormula.DOLLAR - 751)) | (1 << (BaserowFormula.DOLLAR_DOLLAR - 751)) | (1 << (BaserowFormula.OPEN_PAREN - 751)) | (1 << (BaserowFormula.BIT_STRING - 751)) | (1 << (BaserowFormula.REGEX_STRING - 751)) | (1 << (BaserowFormula.NUMERIC_LITERAL - 751)) | (1 << (BaserowFormula.INTEGER_LITERAL - 751)) | (1 << (BaserowFormula.HEX_INTEGER_LITERAL - 751)) | (1 << (BaserowFormula.SINGLEQ_STRING_LITERAL - 751)) | (1 << (BaserowFormula.DOUBLEQ_STRING_LITERAL - 751)) | (1 << (BaserowFormula.IDENTIFIER - 751)) | (1 << (BaserowFormula.DOLLAR_DEC - 751)) | (1 << (BaserowFormula.IDENTIFIER_UNICODE - 751)))) !== 0) || ((((_la - 786)) & ~0x1f) == 0 && ((1 << (_la - 786)) & ((1 << (BaserowFormula.AT_SIGN - 786)) | (1 << (BaserowFormula.BANG_BANG - 786)) | (1 << (BaserowFormula.MINUS - 786)))) !== 0) || ((((_la - 819)) & ~0x1f) == 0 && ((1 << (_la - 819)) & ((1 << (BaserowFormula.PLUS - 819)) | (1 << (BaserowFormula.QMARK_HYPHEN - 819)) | (1 << (BaserowFormula.TIL - 819)))) !== 0)) {
	                    		    this.state = 152;
	                    		    this.expr(0);
	                    		}

	                    		this.state = 155;
	                    		this.match(BaserowFormula.CLOSE_BRACKET);
	                    		break;
	                    	default:
	                    		throw new antlr4.error.NoViableAltException(this);
	                    	}
	                    	this.state = 158; 
	                    	this._errHandler.sync(this);
	                    	_alt = this._interp.adaptivePredict(this._input,9, this._ctx);
	                    } while ( _alt!=2 && _alt!=antlr4.atn.ATN.INVALID_ALT_NUMBER );
	                    break;

	                case 14:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 160;
	                    if (!( this.precpred(this._ctx, 7))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 7)");
	                    }
	                    this.state = 163; 
	                    this._errHandler.sync(this);
	                    var _alt = 1;
	                    do {
	                    	switch (_alt) {
	                    	case 1:
	                    		this.state = 161;
	                    		this.match(BaserowFormula.COLON_COLON);
	                    		this.state = 162;
	                    		this.data_type();
	                    		break;
	                    	default:
	                    		throw new antlr4.error.NoViableAltException(this);
	                    	}
	                    	this.state = 165; 
	                    	this._errHandler.sync(this);
	                    	_alt = this._interp.adaptivePredict(this._input,10, this._ctx);
	                    } while ( _alt!=2 && _alt!=antlr4.atn.ATN.INVALID_ALT_NUMBER );
	                    break;

	                case 15:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 167;
	                    if (!( this.precpred(this._ctx, 5))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 5)");
	                    }
	                    this.state = 168;
	                    this.match(BaserowFormula.IS);
	                    this.state = 169;
	                    this.match(BaserowFormula.OF);
	                    this.state = 170;
	                    this.match(BaserowFormula.OPEN_PAREN);
	                    this.state = 171;
	                    this.data_type();
	                    this.state = 172;
	                    this.match(BaserowFormula.CLOSE_PAREN);
	                    break;

	                case 16:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 174;
	                    if (!( this.precpred(this._ctx, 4))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 4)");
	                    }
	                    this.state = 175;
	                    this.match(BaserowFormula.DOT);
	                    this.state = 178;
	                    this._errHandler.sync(this);
	                    switch(this._input.LA(1)) {
	                    case BaserowFormula.LOWER:
	                    case BaserowFormula.UPPER:
	                    case BaserowFormula.TEXT:
	                    case BaserowFormula.DOUBLEQ_STRING_LITERAL:
	                    case BaserowFormula.IDENTIFIER:
	                    case BaserowFormula.IDENTIFIER_UNICODE:
	                        this.state = 176;
	                        this.identifier(0);
	                        break;
	                    case BaserowFormula.STAR:
	                        this.state = 177;
	                        this.match(BaserowFormula.STAR);
	                        break;
	                    default:
	                        throw new antlr4.error.NoViableAltException(this);
	                    }
	                    break;

	                case 17:
	                    localctx = new ExprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_expr);
	                    this.state = 180;
	                    if (!( this.precpred(this._ctx, 3))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 3)");
	                    }

	                    this.state = 181;
	                    this.match(BaserowFormula.AT);
	                    this.state = 182;
	                    this.match(BaserowFormula.TIME);
	                    this.state = 183;
	                    this.match(BaserowFormula.ZONE);
	                    this.state = 185;
	                    this.match(BaserowFormula.SINGLEQ_STRING_LITERAL);
	                    break;

	                } 
	            }
	            this.state = 190;
	            this._errHandler.sync(this);
	            _alt = this._interp.adaptivePredict(this._input,13,this._ctx);
	        }

	    } catch( error) {
	        if(error instanceof antlr4.error.RecognitionException) {
		        localctx.exception = error;
		        this._errHandler.reportError(this, error);
		        this._errHandler.recover(this, error);
		    } else {
		    	throw error;
		    }
	    } finally {
	        this.unrollRecursionContexts(_parentctx)
	    }
	    return localctx;
	}


	bool_expr(_p) {
		if(_p===undefined) {
		    _p = 0;
		}
	    const _parentctx = this._ctx;
	    const _parentState = this.state;
	    let localctx = new Bool_exprContext(this, this._ctx, _parentState);
	    let _prevctx = localctx;
	    const _startState = 4;
	    this.enterRecursionRule(localctx, 4, BaserowFormula.RULE_bool_expr, _p);
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 196;
	        this._errHandler.sync(this);
	        switch(this._input.LA(1)) {
	        case BaserowFormula.TRUE:
	            this.state = 192;
	            this.match(BaserowFormula.TRUE);
	            break;
	        case BaserowFormula.FALSE:
	            this.state = 193;
	            this.match(BaserowFormula.FALSE);
	            break;
	        case BaserowFormula.NOT:
	            this.state = 194;
	            this.match(BaserowFormula.NOT);
	            this.state = 195;
	            this.bool_expr(3);
	            break;
	        default:
	            throw new antlr4.error.NoViableAltException(this);
	        }
	        this._ctx.stop = this._input.LT(-1);
	        this.state = 206;
	        this._errHandler.sync(this);
	        var _alt = this._interp.adaptivePredict(this._input,16,this._ctx)
	        while(_alt!=2 && _alt!=antlr4.atn.ATN.INVALID_ALT_NUMBER) {
	            if(_alt===1) {
	                if(this._parseListeners!==null) {
	                    this.triggerExitRuleEvent();
	                }
	                _prevctx = localctx;
	                this.state = 204;
	                this._errHandler.sync(this);
	                var la_ = this._interp.adaptivePredict(this._input,15,this._ctx);
	                switch(la_) {
	                case 1:
	                    localctx = new Bool_exprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_bool_expr);
	                    this.state = 198;
	                    if (!( this.precpred(this._ctx, 2))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 2)");
	                    }
	                    this.state = 199;
	                    this.match(BaserowFormula.AND);
	                    this.state = 200;
	                    this.bool_expr(3);
	                    break;

	                case 2:
	                    localctx = new Bool_exprContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_bool_expr);
	                    this.state = 201;
	                    if (!( this.precpred(this._ctx, 1))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 1)");
	                    }
	                    this.state = 202;
	                    this.match(BaserowFormula.OR);
	                    this.state = 203;
	                    this.bool_expr(2);
	                    break;

	                } 
	            }
	            this.state = 208;
	            this._errHandler.sync(this);
	            _alt = this._interp.adaptivePredict(this._input,16,this._ctx);
	        }

	    } catch( error) {
	        if(error instanceof antlr4.error.RecognitionException) {
		        localctx.exception = error;
		        this._errHandler.reportError(this, error);
		        this._errHandler.recover(this, error);
		    } else {
		    	throw error;
		    }
	    } finally {
	        this.unrollRecursionContexts(_parentctx)
	    }
	    return localctx;
	}



	case_expr() {
	    let localctx = new Case_exprContext(this, this._ctx, this.state);
	    this.enterRule(localctx, 6, BaserowFormula.RULE_case_expr);
	    var _la = 0; // Token type
	    try {
	        this.state = 242;
	        this._errHandler.sync(this);
	        var la_ = this._interp.adaptivePredict(this._input,21,this._ctx);
	        switch(la_) {
	        case 1:
	            this.enterOuterAlt(localctx, 1);
	            this.state = 209;
	            this.match(BaserowFormula.CASE);
	            this.state = 210;
	            this.expr(0);
	            this.state = 216; 
	            this._errHandler.sync(this);
	            _la = this._input.LA(1);
	            do {
	                this.state = 211;
	                this.match(BaserowFormula.WHEN);
	                this.state = 212;
	                this.expr(0);
	                this.state = 213;
	                this.match(BaserowFormula.THEN);
	                this.state = 214;
	                this.expr(0);
	                this.state = 218; 
	                this._errHandler.sync(this);
	                _la = this._input.LA(1);
	            } while(_la===BaserowFormula.WHEN);
	            this.state = 222;
	            this._errHandler.sync(this);
	            _la = this._input.LA(1);
	            if(_la===BaserowFormula.ELSE) {
	                this.state = 220;
	                this.match(BaserowFormula.ELSE);
	                this.state = 221;
	                this.expr(0);
	            }

	            this.state = 224;
	            this.match(BaserowFormula.END);
	            break;

	        case 2:
	            this.enterOuterAlt(localctx, 2);
	            this.state = 226;
	            this.match(BaserowFormula.CASE);
	            this.state = 232; 
	            this._errHandler.sync(this);
	            _la = this._input.LA(1);
	            do {
	                this.state = 227;
	                this.match(BaserowFormula.WHEN);
	                this.state = 228;
	                this.predicate(0);
	                this.state = 229;
	                this.match(BaserowFormula.THEN);
	                this.state = 230;
	                this.expr(0);
	                this.state = 234; 
	                this._errHandler.sync(this);
	                _la = this._input.LA(1);
	            } while(_la===BaserowFormula.WHEN);
	            this.state = 238;
	            this._errHandler.sync(this);
	            _la = this._input.LA(1);
	            if(_la===BaserowFormula.ELSE) {
	                this.state = 236;
	                this.match(BaserowFormula.ELSE);
	                this.state = 237;
	                this.expr(0);
	            }

	            this.state = 240;
	            this.match(BaserowFormula.END);
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



	expr_list() {
	    let localctx = new Expr_listContext(this, this._ctx, this.state);
	    this.enterRule(localctx, 8, BaserowFormula.RULE_expr_list);
	    var _la = 0; // Token type
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 244;
	        this.match(BaserowFormula.OPEN_PAREN);
	        this.state = 245;
	        this.expr(0);
	        this.state = 250;
	        this._errHandler.sync(this);
	        _la = this._input.LA(1);
	        while(_la===BaserowFormula.COMMA) {
	            this.state = 246;
	            this.match(BaserowFormula.COMMA);
	            this.state = 247;
	            this.expr(0);
	            this.state = 252;
	            this._errHandler.sync(this);
	            _la = this._input.LA(1);
	        }
	        this.state = 253;
	        this.match(BaserowFormula.CLOSE_PAREN);
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



	type_name() {
	    let localctx = new Type_nameContext(this, this._ctx, this.state);
	    this.enterRule(localctx, 10, BaserowFormula.RULE_type_name);
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 255;
	        this.match(BaserowFormula.TEXT);
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



	data_type() {
	    let localctx = new Data_typeContext(this, this._ctx, this.state);
	    this.enterRule(localctx, 12, BaserowFormula.RULE_data_type);
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 257;
	        this.type_name();
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
	    this.enterRule(localctx, 14, BaserowFormula.RULE_func_name);
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 259;
	        this.identifier(0);
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
	    this.enterRule(localctx, 16, BaserowFormula.RULE_func_call);
	    var _la = 0; // Token type
	    try {
	        this.state = 286;
	        this._errHandler.sync(this);
	        var la_ = this._interp.adaptivePredict(this._input,26,this._ctx);
	        switch(la_) {
	        case 1:
	            this.enterOuterAlt(localctx, 1);
	            this.state = 261;
	            this.func_name();
	            this.state = 262;
	            this.match(BaserowFormula.OPEN_PAREN);
	            this.state = 263;
	            this.match(BaserowFormula.VARIADIC);
	            this.state = 264;
	            this.expr(0);
	            this.state = 265;
	            this.match(BaserowFormula.CLOSE_PAREN);
	            break;

	        case 2:
	            this.enterOuterAlt(localctx, 2);
	            this.state = 267;
	            this.func_name();
	            this.state = 268;
	            this.match(BaserowFormula.OPEN_PAREN);
	            this.state = 282;
	            this._errHandler.sync(this);
	            _la = this._input.LA(1);
	            if(_la===BaserowFormula.ALL || _la===BaserowFormula.CASE || _la===BaserowFormula.CAST || ((((_la - 134)) & ~0x1f) == 0 && ((1 << (_la - 134)) & ((1 << (BaserowFormula.CURRENT_DATE - 134)) | (1 << (BaserowFormula.CURRENT_TIME - 134)) | (1 << (BaserowFormula.CURRENT_TIMESTAMP - 134)))) !== 0) || _la===BaserowFormula.EXISTS || _la===BaserowFormula.FALSE || _la===BaserowFormula.LOWER || _la===BaserowFormula.NOT || _la===BaserowFormula.NULL || _la===BaserowFormula.TRUE || _la===BaserowFormula.UPPER || ((((_la - 751)) & ~0x1f) == 0 && ((1 << (_la - 751)) & ((1 << (BaserowFormula.TEXT - 751)) | (1 << (BaserowFormula.DOLLAR - 751)) | (1 << (BaserowFormula.DOLLAR_DOLLAR - 751)) | (1 << (BaserowFormula.OPEN_PAREN - 751)) | (1 << (BaserowFormula.BIT_STRING - 751)) | (1 << (BaserowFormula.REGEX_STRING - 751)) | (1 << (BaserowFormula.NUMERIC_LITERAL - 751)) | (1 << (BaserowFormula.INTEGER_LITERAL - 751)) | (1 << (BaserowFormula.HEX_INTEGER_LITERAL - 751)) | (1 << (BaserowFormula.SINGLEQ_STRING_LITERAL - 751)) | (1 << (BaserowFormula.DOUBLEQ_STRING_LITERAL - 751)) | (1 << (BaserowFormula.IDENTIFIER - 751)) | (1 << (BaserowFormula.DOLLAR_DEC - 751)) | (1 << (BaserowFormula.IDENTIFIER_UNICODE - 751)))) !== 0) || ((((_la - 786)) & ~0x1f) == 0 && ((1 << (_la - 786)) & ((1 << (BaserowFormula.AT_SIGN - 786)) | (1 << (BaserowFormula.BANG_BANG - 786)) | (1 << (BaserowFormula.MINUS - 786)))) !== 0) || ((((_la - 819)) & ~0x1f) == 0 && ((1 << (_la - 819)) & ((1 << (BaserowFormula.PLUS - 819)) | (1 << (BaserowFormula.QMARK_HYPHEN - 819)) | (1 << (BaserowFormula.TIL - 819)))) !== 0)) {
	                this.state = 269;
	                this.expr(0);
	                this.state = 274;
	                this._errHandler.sync(this);
	                var _alt = this._interp.adaptivePredict(this._input,23,this._ctx)
	                while(_alt!=2 && _alt!=antlr4.atn.ATN.INVALID_ALT_NUMBER) {
	                    if(_alt===1) {
	                        this.state = 270;
	                        this.match(BaserowFormula.COMMA);
	                        this.state = 271;
	                        this.expr(0); 
	                    }
	                    this.state = 276;
	                    this._errHandler.sync(this);
	                    _alt = this._interp.adaptivePredict(this._input,23,this._ctx);
	                }

	                this.state = 280;
	                this._errHandler.sync(this);
	                _la = this._input.LA(1);
	                if(_la===BaserowFormula.COMMA) {
	                    this.state = 277;
	                    this.match(BaserowFormula.COMMA);
	                    this.state = 278;
	                    this.match(BaserowFormula.VARIADIC);
	                    this.state = 279;
	                    this.expr(0);
	                }

	            }

	            this.state = 284;
	            this.match(BaserowFormula.CLOSE_PAREN);
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


	predicate(_p) {
		if(_p===undefined) {
		    _p = 0;
		}
	    const _parentctx = this._ctx;
	    const _parentState = this.state;
	    let localctx = new PredicateContext(this, this._ctx, _parentState);
	    let _prevctx = localctx;
	    const _startState = 18;
	    this.enterRecursionRule(localctx, 18, BaserowFormula.RULE_predicate, _p);
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 296;
	        this._errHandler.sync(this);
	        var la_ = this._interp.adaptivePredict(this._input,27,this._ctx);
	        switch(la_) {
	        case 1:
	            this.state = 289;
	            this.expr(0);
	            break;

	        case 2:
	            this.state = 290;
	            this.match(BaserowFormula.OPEN_PAREN);
	            this.state = 291;
	            this.predicate(0);
	            this.state = 292;
	            this.match(BaserowFormula.CLOSE_PAREN);
	            break;

	        case 3:
	            this.state = 294;
	            this.match(BaserowFormula.NOT);
	            this.state = 295;
	            this.predicate(1);
	            break;

	        }
	        this._ctx.stop = this._input.LT(-1);
	        this.state = 306;
	        this._errHandler.sync(this);
	        var _alt = this._interp.adaptivePredict(this._input,29,this._ctx)
	        while(_alt!=2 && _alt!=antlr4.atn.ATN.INVALID_ALT_NUMBER) {
	            if(_alt===1) {
	                if(this._parseListeners!==null) {
	                    this.triggerExitRuleEvent();
	                }
	                _prevctx = localctx;
	                this.state = 304;
	                this._errHandler.sync(this);
	                var la_ = this._interp.adaptivePredict(this._input,28,this._ctx);
	                switch(la_) {
	                case 1:
	                    localctx = new PredicateContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_predicate);
	                    this.state = 298;
	                    if (!( this.precpred(this._ctx, 3))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 3)");
	                    }
	                    this.state = 299;
	                    this.match(BaserowFormula.AND);
	                    this.state = 300;
	                    this.predicate(4);
	                    break;

	                case 2:
	                    localctx = new PredicateContext(this, _parentctx, _parentState);
	                    this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_predicate);
	                    this.state = 301;
	                    if (!( this.precpred(this._ctx, 2))) {
	                        throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 2)");
	                    }
	                    this.state = 302;
	                    this.match(BaserowFormula.OR);
	                    this.state = 303;
	                    this.predicate(3);
	                    break;

	                } 
	            }
	            this.state = 308;
	            this._errHandler.sync(this);
	            _alt = this._interp.adaptivePredict(this._input,29,this._ctx);
	        }

	    } catch( error) {
	        if(error instanceof antlr4.error.RecognitionException) {
		        localctx.exception = error;
		        this._errHandler.reportError(this, error);
		        this._errHandler.recover(this, error);
		    } else {
		    	throw error;
		    }
	    } finally {
	        this.unrollRecursionContexts(_parentctx)
	    }
	    return localctx;
	}



	non_reserved_keyword() {
	    let localctx = new Non_reserved_keywordContext(this, this._ctx, this.state);
	    this.enterRule(localctx, 20, BaserowFormula.RULE_non_reserved_keyword);
	    var _la = 0; // Token type
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 309;
	        _la = this._input.LA(1);
	        if(!(_la===BaserowFormula.LOWER || _la===BaserowFormula.UPPER)) {
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


	identifier(_p) {
		if(_p===undefined) {
		    _p = 0;
		}
	    const _parentctx = this._ctx;
	    const _parentState = this.state;
	    let localctx = new IdentifierContext(this, this._ctx, _parentState);
	    let _prevctx = localctx;
	    const _startState = 22;
	    this.enterRecursionRule(localctx, 22, BaserowFormula.RULE_identifier, _p);
	    try {
	        this.enterOuterAlt(localctx, 1);
	        this.state = 317;
	        this._errHandler.sync(this);
	        switch(this._input.LA(1)) {
	        case BaserowFormula.LOWER:
	        case BaserowFormula.UPPER:
	            this.state = 312;
	            this.non_reserved_keyword();
	            break;
	        case BaserowFormula.DOUBLEQ_STRING_LITERAL:
	            this.state = 313;
	            this.match(BaserowFormula.DOUBLEQ_STRING_LITERAL);
	            break;
	        case BaserowFormula.IDENTIFIER:
	            this.state = 314;
	            this.match(BaserowFormula.IDENTIFIER);
	            break;
	        case BaserowFormula.TEXT:
	            this.state = 315;
	            this.type_name();
	            break;
	        case BaserowFormula.IDENTIFIER_UNICODE:
	            this.state = 316;
	            this.match(BaserowFormula.IDENTIFIER_UNICODE);
	            break;
	        default:
	            throw new antlr4.error.NoViableAltException(this);
	        }
	        this._ctx.stop = this._input.LT(-1);
	        this.state = 324;
	        this._errHandler.sync(this);
	        var _alt = this._interp.adaptivePredict(this._input,31,this._ctx)
	        while(_alt!=2 && _alt!=antlr4.atn.ATN.INVALID_ALT_NUMBER) {
	            if(_alt===1) {
	                if(this._parseListeners!==null) {
	                    this.triggerExitRuleEvent();
	                }
	                _prevctx = localctx;
	                localctx = new IdentifierContext(this, _parentctx, _parentState);
	                this.pushNewRecursionContext(localctx, _startState, BaserowFormula.RULE_identifier);
	                this.state = 319;
	                if (!( this.precpred(this._ctx, 3))) {
	                    throw new antlr4.error.FailedPredicateException(this, "this.precpred(this._ctx, 3)");
	                }
	                this.state = 320;
	                this.match(BaserowFormula.DOT);
	                this.state = 321;
	                this.identifier(4); 
	            }
	            this.state = 326;
	            this._errHandler.sync(this);
	            _alt = this._interp.adaptivePredict(this._input,31,this._ctx);
	        }

	    } catch( error) {
	        if(error instanceof antlr4.error.RecognitionException) {
		        localctx.exception = error;
		        this._errHandler.reportError(this, error);
		        this._errHandler.recover(this, error);
		    } else {
		    	throw error;
		    }
	    } finally {
	        this.unrollRecursionContexts(_parentctx)
	    }
	    return localctx;
	}


}

BaserowFormula.EOF = antlr4.Token.EOF;
BaserowFormula.WHITESPACE = 1;
BaserowFormula.BLOCK_COMMENT = 2;
BaserowFormula.LINE_COMMENT = 3;
BaserowFormula.A_ = 4;
BaserowFormula.ABORT = 5;
BaserowFormula.ABS = 6;
BaserowFormula.ABSOLUTE = 7;
BaserowFormula.ACCESS = 8;
BaserowFormula.ACTION = 9;
BaserowFormula.ADA = 10;
BaserowFormula.ADD = 11;
BaserowFormula.ADMIN = 12;
BaserowFormula.AFTER = 13;
BaserowFormula.AGGREGATE = 14;
BaserowFormula.ALIAS = 15;
BaserowFormula.ALL = 16;
BaserowFormula.ALLOCATE = 17;
BaserowFormula.ALSO = 18;
BaserowFormula.ALTER = 19;
BaserowFormula.ALWAYS = 20;
BaserowFormula.ANALYSE = 21;
BaserowFormula.ANALYZE = 22;
BaserowFormula.AND = 23;
BaserowFormula.ANY = 24;
BaserowFormula.ARE = 25;
BaserowFormula.ARRAY = 26;
BaserowFormula.AS = 27;
BaserowFormula.ASC = 28;
BaserowFormula.ASENSITIVE = 29;
BaserowFormula.ASSERTION = 30;
BaserowFormula.ASSIGNMENT = 31;
BaserowFormula.ASYMMETRIC = 32;
BaserowFormula.AT = 33;
BaserowFormula.ATOMIC = 34;
BaserowFormula.ATTRIBUTE = 35;
BaserowFormula.ATTRIBUTES = 36;
BaserowFormula.AUTHORIZATION = 37;
BaserowFormula.AVG = 38;
BaserowFormula.BACKWARD = 39;
BaserowFormula.BEFORE = 40;
BaserowFormula.BEGIN = 41;
BaserowFormula.BERNOULLI = 42;
BaserowFormula.BETWEEN = 43;
BaserowFormula.BIGINT = 44;
BaserowFormula.BINARY = 45;
BaserowFormula.BIT = 46;
BaserowFormula.BIT_LENGTH = 47;
BaserowFormula.BITVAR = 48;
BaserowFormula.BLOB = 49;
BaserowFormula.BOOLEAN = 50;
BaserowFormula.BOTH = 51;
BaserowFormula.BREADTH = 52;
BaserowFormula.BUFFERS = 53;
BaserowFormula.BY = 54;
BaserowFormula.C_ = 55;
BaserowFormula.CACHE = 56;
BaserowFormula.CALL = 57;
BaserowFormula.CALLED = 58;
BaserowFormula.CARDINALITY = 59;
BaserowFormula.CASCADE = 60;
BaserowFormula.CASCADED = 61;
BaserowFormula.CASE = 62;
BaserowFormula.CAST = 63;
BaserowFormula.CATALOG = 64;
BaserowFormula.CATALOG_NAME = 65;
BaserowFormula.CEIL = 66;
BaserowFormula.CEILING = 67;
BaserowFormula.CHAIN = 68;
BaserowFormula.CHAR = 69;
BaserowFormula.CHAR_LENGTH = 70;
BaserowFormula.CHARACTER = 71;
BaserowFormula.CHARACTER_LENGTH = 72;
BaserowFormula.CHARACTER_SET_CATALOG = 73;
BaserowFormula.CHARACTER_SET_NAME = 74;
BaserowFormula.CHARACTER_SET_SCHEMA = 75;
BaserowFormula.CHARACTERISTICS = 76;
BaserowFormula.CHARACTERS = 77;
BaserowFormula.CHECK = 78;
BaserowFormula.CHECKED = 79;
BaserowFormula.CHECKPOINT = 80;
BaserowFormula.CLASS = 81;
BaserowFormula.CLASS_ORIGIN = 82;
BaserowFormula.CLOB = 83;
BaserowFormula.CLOSE = 84;
BaserowFormula.CLUSTER = 85;
BaserowFormula.COALESCE = 86;
BaserowFormula.COBOL = 87;
BaserowFormula.COLLATE = 88;
BaserowFormula.COLLATION = 89;
BaserowFormula.COLLATION_CATALOG = 90;
BaserowFormula.COLLATION_NAME = 91;
BaserowFormula.COLLATION_SCHEMA = 92;
BaserowFormula.COLLECT = 93;
BaserowFormula.COLUMN = 94;
BaserowFormula.COLUMN_NAME = 95;
BaserowFormula.COMMAND_FUNCTION = 96;
BaserowFormula.COMMAND_FUNCTION_CODE = 97;
BaserowFormula.COMMENT = 98;
BaserowFormula.COMMIT = 99;
BaserowFormula.COMMITTED = 100;
BaserowFormula.COMPLETION = 101;
BaserowFormula.CONDITION = 102;
BaserowFormula.CONDITION_NUMBER = 103;
BaserowFormula.CONFIGURATION = 104;
BaserowFormula.CONFLICT = 105;
BaserowFormula.CONNECT = 106;
BaserowFormula.CONNECTION = 107;
BaserowFormula.CONNECTION_NAME = 108;
BaserowFormula.CONSTRAINT = 109;
BaserowFormula.CONSTRAINT_CATALOG = 110;
BaserowFormula.CONSTRAINT_NAME = 111;
BaserowFormula.CONSTRAINT_SCHEMA = 112;
BaserowFormula.CONSTRAINTS = 113;
BaserowFormula.CONSTRUCTOR = 114;
BaserowFormula.CONTAINS = 115;
BaserowFormula.CONTINUE = 116;
BaserowFormula.CONVERSION = 117;
BaserowFormula.CONVERT = 118;
BaserowFormula.COPY = 119;
BaserowFormula.CORR = 120;
BaserowFormula.CORRESPONDING = 121;
BaserowFormula.COSTS = 122;
BaserowFormula.COUNT = 123;
BaserowFormula.COVAR_POP = 124;
BaserowFormula.COVAR_SAMP = 125;
BaserowFormula.CREATE = 126;
BaserowFormula.CREATEDB = 127;
BaserowFormula.CREATEUSER = 128;
BaserowFormula.CROSS = 129;
BaserowFormula.CSV = 130;
BaserowFormula.CUBE = 131;
BaserowFormula.CUME_DIST = 132;
BaserowFormula.CURRENT = 133;
BaserowFormula.CURRENT_DATE = 134;
BaserowFormula.CURRENT_DEFAULT_TRANSFORM_GROUP = 135;
BaserowFormula.CURRENT_PATH = 136;
BaserowFormula.CURRENT_ROLE = 137;
BaserowFormula.CURRENT_TIME = 138;
BaserowFormula.CURRENT_TIMESTAMP = 139;
BaserowFormula.CURRENT_TRANSFORM_GROUP_FOR_TYPE = 140;
BaserowFormula.CURRENT_USER = 141;
BaserowFormula.CURSOR = 142;
BaserowFormula.CURSOR_NAME = 143;
BaserowFormula.CYCLE = 144;
BaserowFormula.DATA = 145;
BaserowFormula.DATABASE = 146;
BaserowFormula.DATE = 147;
BaserowFormula.DATETIME_INTERVAL_CODE = 148;
BaserowFormula.DATETIME_INTERVAL_PRECISION = 149;
BaserowFormula.DAY = 150;
BaserowFormula.DEALLOCATE = 151;
BaserowFormula.DEC = 152;
BaserowFormula.DECIMAL = 153;
BaserowFormula.DECLARE = 154;
BaserowFormula.DEFAULT = 155;
BaserowFormula.DEFAULTS = 156;
BaserowFormula.DEFERABLE = 157;
BaserowFormula.DEFERRABLE = 158;
BaserowFormula.DEFERRED = 159;
BaserowFormula.DEFINED = 160;
BaserowFormula.DEFINER = 161;
BaserowFormula.DEGREE = 162;
BaserowFormula.DELETE = 163;
BaserowFormula.DELIMITER = 164;
BaserowFormula.DELIMITERS = 165;
BaserowFormula.DENSE_RANK = 166;
BaserowFormula.DEPENDS = 167;
BaserowFormula.DEPTH = 168;
BaserowFormula.DEREF = 169;
BaserowFormula.DERIVED = 170;
BaserowFormula.DESC = 171;
BaserowFormula.DESCRIBE = 172;
BaserowFormula.DESCRIPTOR = 173;
BaserowFormula.DESTROY = 174;
BaserowFormula.DESTRUCTOR = 175;
BaserowFormula.DETERMINISTIC = 176;
BaserowFormula.DIAGNOSTICS = 177;
BaserowFormula.DICTIONARY = 178;
BaserowFormula.DISABLE = 179;
BaserowFormula.DISABLE_PAGE_SKIPPING = 180;
BaserowFormula.DISCARD = 181;
BaserowFormula.DISCONNECT = 182;
BaserowFormula.DISPATCH = 183;
BaserowFormula.DISTINCT = 184;
BaserowFormula.DO = 185;
BaserowFormula.DOMAIN = 186;
BaserowFormula.DOUBLE = 187;
BaserowFormula.DROP = 188;
BaserowFormula.DYNAMIC = 189;
BaserowFormula.DYNAMIC_FUNCTION = 190;
BaserowFormula.DYNAMIC_FUNCTION_CODE = 191;
BaserowFormula.EACH = 192;
BaserowFormula.ELEMENT = 193;
BaserowFormula.ELSE = 194;
BaserowFormula.ENABLE = 195;
BaserowFormula.ENCODING = 196;
BaserowFormula.ENCRYPTED = 197;
BaserowFormula.END = 198;
BaserowFormula.END_EXEC = 199;
BaserowFormula.EQUALS = 200;
BaserowFormula.ESCAPE = 201;
BaserowFormula.EVERY = 202;
BaserowFormula.EXCEPT = 203;
BaserowFormula.EXCEPTION = 204;
BaserowFormula.EXCLUDE = 205;
BaserowFormula.EXCLUDING = 206;
BaserowFormula.EXCLUSIVE = 207;
BaserowFormula.EXEC = 208;
BaserowFormula.EXECUTE = 209;
BaserowFormula.EXISTING = 210;
BaserowFormula.EXISTS = 211;
BaserowFormula.EXP = 212;
BaserowFormula.EXPLAIN = 213;
BaserowFormula.EXTENDED = 214;
BaserowFormula.EXTENSION = 215;
BaserowFormula.EXTERNAL = 216;
BaserowFormula.EXTRACT = 217;
BaserowFormula.FALSE = 218;
BaserowFormula.FETCH = 219;
BaserowFormula.FIELDS = 220;
BaserowFormula.FILTER = 221;
BaserowFormula.FINAL = 222;
BaserowFormula.FIRST = 223;
BaserowFormula.FLOAT = 224;
BaserowFormula.FLOOR = 225;
BaserowFormula.FOLLOWING = 226;
BaserowFormula.FOR = 227;
BaserowFormula.FORCE = 228;
BaserowFormula.FOREIGN = 229;
BaserowFormula.FORMAT = 230;
BaserowFormula.FORTRAN = 231;
BaserowFormula.FORWARD = 232;
BaserowFormula.FOUND = 233;
BaserowFormula.FREE = 234;
BaserowFormula.FREEZE = 235;
BaserowFormula.FROM = 236;
BaserowFormula.FULL = 237;
BaserowFormula.FUNCTION = 238;
BaserowFormula.FUSION = 239;
BaserowFormula.G_ = 240;
BaserowFormula.GENERAL = 241;
BaserowFormula.GENERATED = 242;
BaserowFormula.GET = 243;
BaserowFormula.GLOBAL = 244;
BaserowFormula.GO = 245;
BaserowFormula.GOTO = 246;
BaserowFormula.GRANT = 247;
BaserowFormula.GRANTED = 248;
BaserowFormula.GREATEST = 249;
BaserowFormula.GROUP = 250;
BaserowFormula.GROUPING = 251;
BaserowFormula.HANDLER = 252;
BaserowFormula.HAVING = 253;
BaserowFormula.HIERARCHY = 254;
BaserowFormula.HOLD = 255;
BaserowFormula.HOST = 256;
BaserowFormula.HOUR = 257;
BaserowFormula.IDENTITY = 258;
BaserowFormula.IGNORE = 259;
BaserowFormula.ILIKE = 260;
BaserowFormula.IMMEDIATE = 261;
BaserowFormula.IMMUTABLE = 262;
BaserowFormula.IMPLEMENTATION = 263;
BaserowFormula.IMPLICIT = 264;
BaserowFormula.IN = 265;
BaserowFormula.INCLUDING = 266;
BaserowFormula.INCREMENT = 267;
BaserowFormula.INDEX = 268;
BaserowFormula.INDICATOR = 269;
BaserowFormula.INFIX = 270;
BaserowFormula.INHERITS = 271;
BaserowFormula.INITIALIZE = 272;
BaserowFormula.INITIALLY = 273;
BaserowFormula.INNER = 274;
BaserowFormula.INOUT = 275;
BaserowFormula.INPUT = 276;
BaserowFormula.INSENSITIVE = 277;
BaserowFormula.INSERT = 278;
BaserowFormula.INSTANCE = 279;
BaserowFormula.INSTANTIABLE = 280;
BaserowFormula.INSTEAD = 281;
BaserowFormula.INT = 282;
BaserowFormula.INTEGER = 283;
BaserowFormula.INTERSECT = 284;
BaserowFormula.INTERSECTION = 285;
BaserowFormula.INTERVAL = 286;
BaserowFormula.INTO = 287;
BaserowFormula.INVOKER = 288;
BaserowFormula.IS = 289;
BaserowFormula.ISOLATION = 290;
BaserowFormula.ITERATE = 291;
BaserowFormula.JOIN = 292;
BaserowFormula.K_ = 293;
BaserowFormula.KEY = 294;
BaserowFormula.KEY_MEMBER = 295;
BaserowFormula.KEY_TYPE = 296;
BaserowFormula.LABEL = 297;
BaserowFormula.LANCOMPILER = 298;
BaserowFormula.LANGUAGE = 299;
BaserowFormula.LARGE = 300;
BaserowFormula.LAST = 301;
BaserowFormula.LATERAL = 302;
BaserowFormula.LEADING = 303;
BaserowFormula.LEAST = 304;
BaserowFormula.LEFT = 305;
BaserowFormula.LENGTH = 306;
BaserowFormula.LESS = 307;
BaserowFormula.LEVEL = 308;
BaserowFormula.LIKE = 309;
BaserowFormula.LIMIT = 310;
BaserowFormula.LISTEN = 311;
BaserowFormula.LN = 312;
BaserowFormula.LOAD = 313;
BaserowFormula.LOCAL = 314;
BaserowFormula.LOCALTIME = 315;
BaserowFormula.LOCALTIMESTAMP = 316;
BaserowFormula.LOCATION = 317;
BaserowFormula.LOCATOR = 318;
BaserowFormula.LOCK = 319;
BaserowFormula.LOCKED = 320;
BaserowFormula.LOWER = 321;
BaserowFormula.M_ = 322;
BaserowFormula.MAIN = 323;
BaserowFormula.MAP = 324;
BaserowFormula.MAPPING = 325;
BaserowFormula.MATCH = 326;
BaserowFormula.MATCH_SIMPLE = 327;
BaserowFormula.MATCHED = 328;
BaserowFormula.MAX = 329;
BaserowFormula.MAXVALUE = 330;
BaserowFormula.MEMBER = 331;
BaserowFormula.MERGE = 332;
BaserowFormula.MESSAGE_LENGTH = 333;
BaserowFormula.MESSAGE_OCTET_LENGTH = 334;
BaserowFormula.MESSAGE_TEXT = 335;
BaserowFormula.METHOD = 336;
BaserowFormula.MIN = 337;
BaserowFormula.MINUTE = 338;
BaserowFormula.MINVALUE = 339;
BaserowFormula.MOD = 340;
BaserowFormula.MODE = 341;
BaserowFormula.MODIFIES = 342;
BaserowFormula.MODIFY = 343;
BaserowFormula.MODULE = 344;
BaserowFormula.MONTH = 345;
BaserowFormula.MORE_ = 346;
BaserowFormula.MOVE = 347;
BaserowFormula.MULTISET = 348;
BaserowFormula.MUMPS = 349;
BaserowFormula.NAME = 350;
BaserowFormula.NAMES = 351;
BaserowFormula.NATIONAL = 352;
BaserowFormula.NATURAL = 353;
BaserowFormula.NCHAR = 354;
BaserowFormula.NCLOB = 355;
BaserowFormula.NESTING = 356;
BaserowFormula.NEW = 357;
BaserowFormula.NEXT = 358;
BaserowFormula.NO = 359;
BaserowFormula.NOCREATEDB = 360;
BaserowFormula.NOCREATEUSER = 361;
BaserowFormula.NONE = 362;
BaserowFormula.NORMALIZE = 363;
BaserowFormula.NORMALIZED = 364;
BaserowFormula.NOT = 365;
BaserowFormula.NOTHING = 366;
BaserowFormula.NOTIFY = 367;
BaserowFormula.NOTNULL = 368;
BaserowFormula.NOWAIT = 369;
BaserowFormula.NULL = 370;
BaserowFormula.NULLABLE = 371;
BaserowFormula.NULLIF = 372;
BaserowFormula.NULLS = 373;
BaserowFormula.NUMBER = 374;
BaserowFormula.NUMERIC = 375;
BaserowFormula.OBJECT = 376;
BaserowFormula.OCTET_LENGTH = 377;
BaserowFormula.OCTETS = 378;
BaserowFormula.OF = 379;
BaserowFormula.OFF = 380;
BaserowFormula.OFFSET = 381;
BaserowFormula.OIDS = 382;
BaserowFormula.OLD = 383;
BaserowFormula.ON = 384;
BaserowFormula.ONLY = 385;
BaserowFormula.OPEN = 386;
BaserowFormula.OPERATION = 387;
BaserowFormula.OPERATOR = 388;
BaserowFormula.OPTION = 389;
BaserowFormula.OPTIONS = 390;
BaserowFormula.OR = 391;
BaserowFormula.ORDER = 392;
BaserowFormula.ORDERING = 393;
BaserowFormula.ORDINALITY = 394;
BaserowFormula.OTHERS = 395;
BaserowFormula.OUT = 396;
BaserowFormula.OUTER = 397;
BaserowFormula.OUTPUT = 398;
BaserowFormula.OVER = 399;
BaserowFormula.OVERLAPS = 400;
BaserowFormula.OVERLAY = 401;
BaserowFormula.OVERRIDING = 402;
BaserowFormula.OWNER = 403;
BaserowFormula.PAD = 404;
BaserowFormula.PARAMETER = 405;
BaserowFormula.PARAMETER_MODE = 406;
BaserowFormula.PARAMETER_NAME = 407;
BaserowFormula.PARAMETER_ORDINAL_POSITION = 408;
BaserowFormula.PARAMETER_SPECIFIC_CATALOG = 409;
BaserowFormula.PARAMETER_SPECIFIC_NAME = 410;
BaserowFormula.PARAMETER_SPECIFIC_SCHEMA = 411;
BaserowFormula.PARAMETERS = 412;
BaserowFormula.PARSER = 413;
BaserowFormula.PARTIAL = 414;
BaserowFormula.PARTITION = 415;
BaserowFormula.PASCAL = 416;
BaserowFormula.PASSWORD = 417;
BaserowFormula.PATH = 418;
BaserowFormula.PERCENT_RANK = 419;
BaserowFormula.PERCENTILE_CONT = 420;
BaserowFormula.PERCENTILE_DISC = 421;
BaserowFormula.PLACING = 422;
BaserowFormula.PLAIN = 423;
BaserowFormula.PLANS = 424;
BaserowFormula.PLI = 425;
BaserowFormula.POSITION = 426;
BaserowFormula.POSTFIX = 427;
BaserowFormula.POWER = 428;
BaserowFormula.PRECEDING = 429;
BaserowFormula.PRECISION = 430;
BaserowFormula.PREFIX = 431;
BaserowFormula.PREORDER = 432;
BaserowFormula.PREPARE = 433;
BaserowFormula.PREPARED = 434;
BaserowFormula.PRESERVE = 435;
BaserowFormula.PRIMARY = 436;
BaserowFormula.PRIOR = 437;
BaserowFormula.PRIVILEGES = 438;
BaserowFormula.PROCEDURAL = 439;
BaserowFormula.PROCEDURE = 440;
BaserowFormula.PUBLIC = 441;
BaserowFormula.PUBLICATION = 442;
BaserowFormula.QUOTE = 443;
BaserowFormula.RANGE = 444;
BaserowFormula.RANK = 445;
BaserowFormula.READ = 446;
BaserowFormula.READS = 447;
BaserowFormula.REAL = 448;
BaserowFormula.REASSIGN = 449;
BaserowFormula.RECHECK = 450;
BaserowFormula.RECURSIVE = 451;
BaserowFormula.REF = 452;
BaserowFormula.REFERENCES = 453;
BaserowFormula.REFERENCING = 454;
BaserowFormula.REFRESH = 455;
BaserowFormula.REGR_AVGX = 456;
BaserowFormula.REGR_AVGY = 457;
BaserowFormula.REGR_COUNT = 458;
BaserowFormula.REGR_INTERCEPT = 459;
BaserowFormula.REGR_R2 = 460;
BaserowFormula.REGR_SLOPE = 461;
BaserowFormula.REGR_SXX = 462;
BaserowFormula.REGR_SXY = 463;
BaserowFormula.REGR_SYY = 464;
BaserowFormula.REINDEX = 465;
BaserowFormula.RELATIVE = 466;
BaserowFormula.RELEASE = 467;
BaserowFormula.RENAME = 468;
BaserowFormula.REPEATABLE = 469;
BaserowFormula.REPLACE = 470;
BaserowFormula.REPLICA = 471;
BaserowFormula.RESET = 472;
BaserowFormula.RESTART = 473;
BaserowFormula.RESTRICT = 474;
BaserowFormula.RESULT = 475;
BaserowFormula.RETURN = 476;
BaserowFormula.RETURNED_CARDINALITY = 477;
BaserowFormula.RETURNED_LENGTH = 478;
BaserowFormula.RETURNED_OCTET_LENGTH = 479;
BaserowFormula.RETURNED_SQLSTATE = 480;
BaserowFormula.RETURNING = 481;
BaserowFormula.RETURNS = 482;
BaserowFormula.REVOKE = 483;
BaserowFormula.RIGHT = 484;
BaserowFormula.ROLE = 485;
BaserowFormula.ROLLBACK = 486;
BaserowFormula.ROLLUP = 487;
BaserowFormula.ROUTINE = 488;
BaserowFormula.ROUTINE_CATALOG = 489;
BaserowFormula.ROUTINE_NAME = 490;
BaserowFormula.ROUTINE_SCHEMA = 491;
BaserowFormula.ROW = 492;
BaserowFormula.ROW_COUNT = 493;
BaserowFormula.ROW_NUMBER = 494;
BaserowFormula.ROWS = 495;
BaserowFormula.RULE = 496;
BaserowFormula.SAVEPOINT = 497;
BaserowFormula.SCALE = 498;
BaserowFormula.SCHEMA = 499;
BaserowFormula.SCHEMA_NAME = 500;
BaserowFormula.SCOPE = 501;
BaserowFormula.SCOPE_CATALOG = 502;
BaserowFormula.SCOPE_NAME = 503;
BaserowFormula.SCOPE_SCHEMA = 504;
BaserowFormula.SCROLL = 505;
BaserowFormula.SEARCH = 506;
BaserowFormula.SECOND = 507;
BaserowFormula.SECTION = 508;
BaserowFormula.SECURITY = 509;
BaserowFormula.SELECT = 510;
BaserowFormula.SELF = 511;
BaserowFormula.SENSITIVE = 512;
BaserowFormula.SEQUENCE = 513;
BaserowFormula.SEQUENCES = 514;
BaserowFormula.SERIALIZABLE = 515;
BaserowFormula.SERVER_NAME = 516;
BaserowFormula.SESSION = 517;
BaserowFormula.SESSION_USER = 518;
BaserowFormula.SET = 519;
BaserowFormula.SETOF = 520;
BaserowFormula.SETS = 521;
BaserowFormula.SHARE = 522;
BaserowFormula.SHOW = 523;
BaserowFormula.SIMILAR = 524;
BaserowFormula.SIMPLE = 525;
BaserowFormula.SIZE = 526;
BaserowFormula.SKIP_ = 527;
BaserowFormula.SMALLINT = 528;
BaserowFormula.SNAPSHOT = 529;
BaserowFormula.SOME = 530;
BaserowFormula.SOURCE = 531;
BaserowFormula.SPACE = 532;
BaserowFormula.SPECIFIC = 533;
BaserowFormula.SPECIFIC_NAME = 534;
BaserowFormula.SPECIFICTYPE = 535;
BaserowFormula.SQL = 536;
BaserowFormula.SQLCODE = 537;
BaserowFormula.SQLERROR = 538;
BaserowFormula.SQLEXCEPTION = 539;
BaserowFormula.SQLSTATE = 540;
BaserowFormula.SQLWARNING = 541;
BaserowFormula.SQRT = 542;
BaserowFormula.STABLE = 543;
BaserowFormula.START = 544;
BaserowFormula.STATE = 545;
BaserowFormula.STATEMENT = 546;
BaserowFormula.STATIC = 547;
BaserowFormula.STATISTICS = 548;
BaserowFormula.STDDEV_POP = 549;
BaserowFormula.STDDEV_SAMP = 550;
BaserowFormula.STDIN = 551;
BaserowFormula.STDOUT = 552;
BaserowFormula.STORAGE = 553;
BaserowFormula.STRICT = 554;
BaserowFormula.STRUCTURE = 555;
BaserowFormula.STYLE = 556;
BaserowFormula.SUBCLASS_ORIGIN = 557;
BaserowFormula.SUBLIST = 558;
BaserowFormula.SUBMULTISET = 559;
BaserowFormula.SUBSCRIPTION = 560;
BaserowFormula.SUBSTRING = 561;
BaserowFormula.SUM = 562;
BaserowFormula.SYMMETRIC = 563;
BaserowFormula.SYSID = 564;
BaserowFormula.SYSTEM = 565;
BaserowFormula.SYSTEM_USER = 566;
BaserowFormula.TABLE = 567;
BaserowFormula.TABLE_NAME = 568;
BaserowFormula.TABLESAMPLE = 569;
BaserowFormula.TABLESPACE = 570;
BaserowFormula.TEMP = 571;
BaserowFormula.TEMPLATE = 572;
BaserowFormula.TEMPORARY = 573;
BaserowFormula.TERMINATE = 574;
BaserowFormula.THAN = 575;
BaserowFormula.THEN = 576;
BaserowFormula.TIES = 577;
BaserowFormula.TIME = 578;
BaserowFormula.TIMESTAMP = 579;
BaserowFormula.TIMEZONE_HOUR = 580;
BaserowFormula.TIMEZONE_MINUTE = 581;
BaserowFormula.TIMING = 582;
BaserowFormula.TO = 583;
BaserowFormula.TOAST = 584;
BaserowFormula.TOP_LEVEL_COUNT = 585;
BaserowFormula.TRAILING = 586;
BaserowFormula.TRANSACTION = 587;
BaserowFormula.TRANSACTION_ACTIVE = 588;
BaserowFormula.TRANSACTIONS_COMMITTED = 589;
BaserowFormula.TRANSACTIONS_ROLLED_BACK = 590;
BaserowFormula.TRANSFORM = 591;
BaserowFormula.TRANSFORMS = 592;
BaserowFormula.TRANSLATE = 593;
BaserowFormula.TRANSLATION = 594;
BaserowFormula.TREAT = 595;
BaserowFormula.TRIGGER = 596;
BaserowFormula.TRIGGER_CATALOG = 597;
BaserowFormula.TRIGGER_NAME = 598;
BaserowFormula.TRIGGER_SCHEMA = 599;
BaserowFormula.TRIM = 600;
BaserowFormula.TRUE = 601;
BaserowFormula.TRUNCATE = 602;
BaserowFormula.TRUSTED = 603;
BaserowFormula.TYPE = 604;
BaserowFormula.UESCAPE = 605;
BaserowFormula.UNBOUNDED = 606;
BaserowFormula.UNCOMMITTED = 607;
BaserowFormula.UNDER = 608;
BaserowFormula.UNENCRYPTED = 609;
BaserowFormula.UNION = 610;
BaserowFormula.UNIQUE = 611;
BaserowFormula.UNKNOWN = 612;
BaserowFormula.UNLISTEN = 613;
BaserowFormula.UNNAMED = 614;
BaserowFormula.UNNEST = 615;
BaserowFormula.UNTIL = 616;
BaserowFormula.UPDATE = 617;
BaserowFormula.UPPER = 618;
BaserowFormula.USAGE = 619;
BaserowFormula.USER = 620;
BaserowFormula.USER_DEFINED_TYPE_CATALOG = 621;
BaserowFormula.USER_DEFINED_TYPE_CODE = 622;
BaserowFormula.USER_DEFINED_TYPE_NAME = 623;
BaserowFormula.USER_DEFINED_TYPE_SCHEMA = 624;
BaserowFormula.USING = 625;
BaserowFormula.VACUUM = 626;
BaserowFormula.VALID = 627;
BaserowFormula.VALIDATE = 628;
BaserowFormula.VALIDATOR = 629;
BaserowFormula.VALUE = 630;
BaserowFormula.VALUES = 631;
BaserowFormula.VAR_POP = 632;
BaserowFormula.VAR_SAMP = 633;
BaserowFormula.VARCHAR = 634;
BaserowFormula.VARIABLE = 635;
BaserowFormula.VARIADIC = 636;
BaserowFormula.VARYING = 637;
BaserowFormula.VERBOSE = 638;
BaserowFormula.VIEW = 639;
BaserowFormula.VOLATILE = 640;
BaserowFormula.WHEN = 641;
BaserowFormula.WHENEVER = 642;
BaserowFormula.WHERE = 643;
BaserowFormula.WIDTH_BUCKET = 644;
BaserowFormula.WINDOW = 645;
BaserowFormula.WITH = 646;
BaserowFormula.WITHIN = 647;
BaserowFormula.WITHOUT = 648;
BaserowFormula.WORK = 649;
BaserowFormula.WRITE = 650;
BaserowFormula.YAML = 651;
BaserowFormula.YEAR = 652;
BaserowFormula.YES = 653;
BaserowFormula.ZONE = 654;
BaserowFormula.SUPERUSER = 655;
BaserowFormula.NOSUPERUSER = 656;
BaserowFormula.CREATEROLE = 657;
BaserowFormula.NOCREATEROLE = 658;
BaserowFormula.INHERIT = 659;
BaserowFormula.NOINHERIT = 660;
BaserowFormula.LOGIN = 661;
BaserowFormula.NOLOGIN = 662;
BaserowFormula.REPLICATION = 663;
BaserowFormula.NOREPLICATION = 664;
BaserowFormula.BYPASSRLS = 665;
BaserowFormula.NOBYPASSRLS = 666;
BaserowFormula.SFUNC = 667;
BaserowFormula.STYPE = 668;
BaserowFormula.SSPACE = 669;
BaserowFormula.FINALFUNC = 670;
BaserowFormula.FINALFUNC_EXTRA = 671;
BaserowFormula.COMBINEFUNC = 672;
BaserowFormula.SERIALFUNC = 673;
BaserowFormula.DESERIALFUNC = 674;
BaserowFormula.INITCOND = 675;
BaserowFormula.MSFUNC = 676;
BaserowFormula.MINVFUNC = 677;
BaserowFormula.MSTYPE = 678;
BaserowFormula.MSSPACE = 679;
BaserowFormula.MFINALFUNC = 680;
BaserowFormula.MFINALFUNC_EXTRA = 681;
BaserowFormula.MINITCOND = 682;
BaserowFormula.SORTOP = 683;
BaserowFormula.PARALLEL = 684;
BaserowFormula.HYPOTHETICAL = 685;
BaserowFormula.SAFE = 686;
BaserowFormula.RESTRICTED = 687;
BaserowFormula.UNSAFE = 688;
BaserowFormula.BASETYPE = 689;
BaserowFormula.IF = 690;
BaserowFormula.LOCALE = 691;
BaserowFormula.LC_COLLATE = 692;
BaserowFormula.LC_CTYPE = 693;
BaserowFormula.PROVIDER = 694;
BaserowFormula.VERSION = 695;
BaserowFormula.ALLOW_CONNECTIONS = 696;
BaserowFormula.IS_TEMPLATE = 697;
BaserowFormula.EVENT = 698;
BaserowFormula.WRAPPER = 699;
BaserowFormula.SERVER = 700;
BaserowFormula.BTREE = 701;
BaserowFormula.HASH_ = 702;
BaserowFormula.GIST = 703;
BaserowFormula.SPGIST = 704;
BaserowFormula.GIN = 705;
BaserowFormula.BRIN = 706;
BaserowFormula.CONCURRENTLY = 707;
BaserowFormula.INLINE = 708;
BaserowFormula.MATERIALIZED = 709;
BaserowFormula.LEFTARG = 710;
BaserowFormula.RIGHTARG = 711;
BaserowFormula.COMMUTATOR = 712;
BaserowFormula.NEGATOR = 713;
BaserowFormula.HASHES = 714;
BaserowFormula.MERGES = 715;
BaserowFormula.FAMILY = 716;
BaserowFormula.POLICY = 717;
BaserowFormula.OWNED = 718;
BaserowFormula.ABSTIME = 719;
BaserowFormula.BIGSERIAL = 720;
BaserowFormula.BIT_VARYING = 721;
BaserowFormula.BOOL = 722;
BaserowFormula.BOX = 723;
BaserowFormula.BYTEA = 724;
BaserowFormula.CHARACTER_VARYING = 725;
BaserowFormula.CIDR = 726;
BaserowFormula.CIRCLE = 727;
BaserowFormula.FLOAT4 = 728;
BaserowFormula.FLOAT8 = 729;
BaserowFormula.INET = 730;
BaserowFormula.INT2 = 731;
BaserowFormula.INT4 = 732;
BaserowFormula.INT8 = 733;
BaserowFormula.JSON = 734;
BaserowFormula.JSONB = 735;
BaserowFormula.LINE = 736;
BaserowFormula.LSEG = 737;
BaserowFormula.MACADDR = 738;
BaserowFormula.MACADDR8 = 739;
BaserowFormula.MONEY = 740;
BaserowFormula.PG_LSN = 741;
BaserowFormula.POINT = 742;
BaserowFormula.POLYGON = 743;
BaserowFormula.RELTIME = 744;
BaserowFormula.SERIAL = 745;
BaserowFormula.SERIAL2 = 746;
BaserowFormula.SERIAL4 = 747;
BaserowFormula.SERIAL8 = 748;
BaserowFormula.SMALLSERIAL = 749;
BaserowFormula.STSTEM = 750;
BaserowFormula.TEXT = 751;
BaserowFormula.TIMESTAMPTZ = 752;
BaserowFormula.TIMETZ = 753;
BaserowFormula.TSQUERY = 754;
BaserowFormula.TSVECTOR = 755;
BaserowFormula.TXID_SNAPSHOT = 756;
BaserowFormula.UUID = 757;
BaserowFormula.VARBIT = 758;
BaserowFormula.XML = 759;
BaserowFormula.COMMA = 760;
BaserowFormula.COLON = 761;
BaserowFormula.COLON_COLON = 762;
BaserowFormula.DOLLAR = 763;
BaserowFormula.DOLLAR_DOLLAR = 764;
BaserowFormula.STAR = 765;
BaserowFormula.OPEN_PAREN = 766;
BaserowFormula.CLOSE_PAREN = 767;
BaserowFormula.OPEN_BRACKET = 768;
BaserowFormula.CLOSE_BRACKET = 769;
BaserowFormula.BIT_STRING = 770;
BaserowFormula.REGEX_STRING = 771;
BaserowFormula.NUMERIC_LITERAL = 772;
BaserowFormula.INTEGER_LITERAL = 773;
BaserowFormula.HEX_INTEGER_LITERAL = 774;
BaserowFormula.DOT = 775;
BaserowFormula.SINGLEQ_STRING_LITERAL = 776;
BaserowFormula.DOUBLEQ_STRING_LITERAL = 777;
BaserowFormula.IDENTIFIER = 778;
BaserowFormula.DOLLAR_DEC = 779;
BaserowFormula.IDENTIFIER_UNICODE = 780;
BaserowFormula.AMP = 781;
BaserowFormula.AMP_AMP = 782;
BaserowFormula.AMP_LT = 783;
BaserowFormula.AT_AT = 784;
BaserowFormula.AT_GT = 785;
BaserowFormula.AT_SIGN = 786;
BaserowFormula.BANG = 787;
BaserowFormula.BANG_BANG = 788;
BaserowFormula.BANG_EQUAL = 789;
BaserowFormula.CARET = 790;
BaserowFormula.EQUAL = 791;
BaserowFormula.EQUAL_GT = 792;
BaserowFormula.GT = 793;
BaserowFormula.GTE = 794;
BaserowFormula.GT_GT = 795;
BaserowFormula.HASH = 796;
BaserowFormula.HASH_EQ = 797;
BaserowFormula.HASH_GT = 798;
BaserowFormula.HASH_GT_GT = 799;
BaserowFormula.HASH_HASH = 800;
BaserowFormula.HYPHEN_GT = 801;
BaserowFormula.HYPHEN_GT_GT = 802;
BaserowFormula.HYPHEN_PIPE_HYPHEN = 803;
BaserowFormula.LT = 804;
BaserowFormula.LTE = 805;
BaserowFormula.LT_AT = 806;
BaserowFormula.LT_CARET = 807;
BaserowFormula.LT_GT = 808;
BaserowFormula.LT_HYPHEN_GT = 809;
BaserowFormula.LT_LT = 810;
BaserowFormula.LT_LT_EQ = 811;
BaserowFormula.LT_QMARK_GT = 812;
BaserowFormula.MINUS = 813;
BaserowFormula.PERCENT = 814;
BaserowFormula.PIPE = 815;
BaserowFormula.PIPE_PIPE = 816;
BaserowFormula.PIPE_PIPE_SLASH = 817;
BaserowFormula.PIPE_SLASH = 818;
BaserowFormula.PLUS = 819;
BaserowFormula.QMARK = 820;
BaserowFormula.QMARK_AMP = 821;
BaserowFormula.QMARK_HASH = 822;
BaserowFormula.QMARK_HYPHEN = 823;
BaserowFormula.QMARK_PIPE = 824;
BaserowFormula.SLASH = 825;
BaserowFormula.TIL = 826;
BaserowFormula.TIL_EQ = 827;
BaserowFormula.TIL_GTE_TIL = 828;
BaserowFormula.TIL_GT_TIL = 829;
BaserowFormula.TIL_LTE_TIL = 830;
BaserowFormula.TIL_LT_TIL = 831;
BaserowFormula.TIL_STAR = 832;
BaserowFormula.TIL_TIL = 833;
BaserowFormula.SEMI = 834;

BaserowFormula.RULE_root = 0;
BaserowFormula.RULE_expr = 1;
BaserowFormula.RULE_bool_expr = 2;
BaserowFormula.RULE_case_expr = 3;
BaserowFormula.RULE_expr_list = 4;
BaserowFormula.RULE_type_name = 5;
BaserowFormula.RULE_data_type = 6;
BaserowFormula.RULE_func_name = 7;
BaserowFormula.RULE_func_call = 8;
BaserowFormula.RULE_predicate = 9;
BaserowFormula.RULE_non_reserved_keyword = 10;
BaserowFormula.RULE_identifier = 11;

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
        this.op = null; // Token
    }

	NULL() {
	    return this.getToken(BaserowFormula.NULL, 0);
	};

	CURRENT_DATE() {
	    return this.getToken(BaserowFormula.CURRENT_DATE, 0);
	};

	CURRENT_TIME() {
	    return this.getToken(BaserowFormula.CURRENT_TIME, 0);
	};

	CURRENT_TIMESTAMP() {
	    return this.getToken(BaserowFormula.CURRENT_TIMESTAMP, 0);
	};

	INTEGER_LITERAL() {
	    return this.getToken(BaserowFormula.INTEGER_LITERAL, 0);
	};

	HEX_INTEGER_LITERAL() {
	    return this.getToken(BaserowFormula.HEX_INTEGER_LITERAL, 0);
	};

	NUMERIC_LITERAL() {
	    return this.getToken(BaserowFormula.NUMERIC_LITERAL, 0);
	};

	SINGLEQ_STRING_LITERAL() {
	    return this.getToken(BaserowFormula.SINGLEQ_STRING_LITERAL, 0);
	};

	BIT_STRING() {
	    return this.getToken(BaserowFormula.BIT_STRING, 0);
	};

	REGEX_STRING() {
	    return this.getToken(BaserowFormula.REGEX_STRING, 0);
	};

	DOLLAR_DOLLAR = function(i) {
		if(i===undefined) {
			i = null;
		}
	    if(i===null) {
	        return this.getTokens(BaserowFormula.DOLLAR_DOLLAR);
	    } else {
	        return this.getToken(BaserowFormula.DOLLAR_DOLLAR, i);
	    }
	};


	DOLLAR = function(i) {
		if(i===undefined) {
			i = null;
		}
	    if(i===null) {
	        return this.getTokens(BaserowFormula.DOLLAR);
	    } else {
	        return this.getToken(BaserowFormula.DOLLAR, i);
	    }
	};


	identifier = function(i) {
	    if(i===undefined) {
	        i = null;
	    }
	    if(i===null) {
	        return this.getTypedRuleContexts(IdentifierContext);
	    } else {
	        return this.getTypedRuleContext(IdentifierContext,i);
	    }
	};

	bool_expr() {
	    return this.getTypedRuleContext(Bool_exprContext,0);
	};

	expr_list() {
	    return this.getTypedRuleContext(Expr_listContext,0);
	};

	OPEN_PAREN() {
	    return this.getToken(BaserowFormula.OPEN_PAREN, 0);
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

	CLOSE_PAREN() {
	    return this.getToken(BaserowFormula.CLOSE_PAREN, 0);
	};

	type_name() {
	    return this.getTypedRuleContext(Type_nameContext,0);
	};

	BANG_BANG() {
	    return this.getToken(BaserowFormula.BANG_BANG, 0);
	};

	AT_SIGN() {
	    return this.getToken(BaserowFormula.AT_SIGN, 0);
	};

	PLUS() {
	    return this.getToken(BaserowFormula.PLUS, 0);
	};

	MINUS() {
	    return this.getToken(BaserowFormula.MINUS, 0);
	};

	TIL() {
	    return this.getToken(BaserowFormula.TIL, 0);
	};

	QMARK_HYPHEN() {
	    return this.getToken(BaserowFormula.QMARK_HYPHEN, 0);
	};

	NOT() {
	    return this.getToken(BaserowFormula.NOT, 0);
	};

	ALL() {
	    return this.getToken(BaserowFormula.ALL, 0);
	};

	func_call() {
	    return this.getTypedRuleContext(Func_callContext,0);
	};

	CAST() {
	    return this.getToken(BaserowFormula.CAST, 0);
	};

	AS() {
	    return this.getToken(BaserowFormula.AS, 0);
	};

	data_type = function(i) {
	    if(i===undefined) {
	        i = null;
	    }
	    if(i===null) {
	        return this.getTypedRuleContexts(Data_typeContext);
	    } else {
	        return this.getTypedRuleContext(Data_typeContext,i);
	    }
	};

	case_expr() {
	    return this.getTypedRuleContext(Case_exprContext,0);
	};

	EXISTS() {
	    return this.getToken(BaserowFormula.EXISTS, 0);
	};

	DOLLAR_DEC() {
	    return this.getToken(BaserowFormula.DOLLAR_DEC, 0);
	};

	CARET() {
	    return this.getToken(BaserowFormula.CARET, 0);
	};

	PIPE_SLASH() {
	    return this.getToken(BaserowFormula.PIPE_SLASH, 0);
	};

	PIPE_PIPE_SLASH() {
	    return this.getToken(BaserowFormula.PIPE_PIPE_SLASH, 0);
	};

	STAR() {
	    return this.getToken(BaserowFormula.STAR, 0);
	};

	SLASH() {
	    return this.getToken(BaserowFormula.SLASH, 0);
	};

	PERCENT() {
	    return this.getToken(BaserowFormula.PERCENT, 0);
	};

	AMP() {
	    return this.getToken(BaserowFormula.AMP, 0);
	};

	PIPE() {
	    return this.getToken(BaserowFormula.PIPE, 0);
	};

	HASH() {
	    return this.getToken(BaserowFormula.HASH, 0);
	};

	LT_LT() {
	    return this.getToken(BaserowFormula.LT_LT, 0);
	};

	LT_LT_EQ() {
	    return this.getToken(BaserowFormula.LT_LT_EQ, 0);
	};

	GT_GT() {
	    return this.getToken(BaserowFormula.GT_GT, 0);
	};

	AT_AT() {
	    return this.getToken(BaserowFormula.AT_AT, 0);
	};

	LT_HYPHEN_GT() {
	    return this.getToken(BaserowFormula.LT_HYPHEN_GT, 0);
	};

	AT_GT() {
	    return this.getToken(BaserowFormula.AT_GT, 0);
	};

	LT_AT() {
	    return this.getToken(BaserowFormula.LT_AT, 0);
	};

	TIL_EQ() {
	    return this.getToken(BaserowFormula.TIL_EQ, 0);
	};

	TIL_STAR() {
	    return this.getToken(BaserowFormula.TIL_STAR, 0);
	};

	TIL_TIL() {
	    return this.getToken(BaserowFormula.TIL_TIL, 0);
	};

	TIL_LT_TIL() {
	    return this.getToken(BaserowFormula.TIL_LT_TIL, 0);
	};

	TIL_GT_TIL() {
	    return this.getToken(BaserowFormula.TIL_GT_TIL, 0);
	};

	TIL_LTE_TIL() {
	    return this.getToken(BaserowFormula.TIL_LTE_TIL, 0);
	};

	TIL_GTE_TIL() {
	    return this.getToken(BaserowFormula.TIL_GTE_TIL, 0);
	};

	LT_QMARK_GT() {
	    return this.getToken(BaserowFormula.LT_QMARK_GT, 0);
	};

	HYPHEN_GT() {
	    return this.getToken(BaserowFormula.HYPHEN_GT, 0);
	};

	HYPHEN_GT_GT() {
	    return this.getToken(BaserowFormula.HYPHEN_GT_GT, 0);
	};

	HASH_HASH() {
	    return this.getToken(BaserowFormula.HASH_HASH, 0);
	};

	HASH_GT() {
	    return this.getToken(BaserowFormula.HASH_GT, 0);
	};

	HASH_GT_GT() {
	    return this.getToken(BaserowFormula.HASH_GT_GT, 0);
	};

	QMARK() {
	    return this.getToken(BaserowFormula.QMARK, 0);
	};

	QMARK_PIPE() {
	    return this.getToken(BaserowFormula.QMARK_PIPE, 0);
	};

	QMARK_AMP() {
	    return this.getToken(BaserowFormula.QMARK_AMP, 0);
	};

	QMARK_HASH() {
	    return this.getToken(BaserowFormula.QMARK_HASH, 0);
	};

	LT_CARET() {
	    return this.getToken(BaserowFormula.LT_CARET, 0);
	};

	AMP_LT() {
	    return this.getToken(BaserowFormula.AMP_LT, 0);
	};

	HYPHEN_PIPE_HYPHEN() {
	    return this.getToken(BaserowFormula.HYPHEN_PIPE_HYPHEN, 0);
	};

	HASH_EQ() {
	    return this.getToken(BaserowFormula.HASH_EQ, 0);
	};

	AMP_AMP() {
	    return this.getToken(BaserowFormula.AMP_AMP, 0);
	};

	PIPE_PIPE() {
	    return this.getToken(BaserowFormula.PIPE_PIPE, 0);
	};

	EQUAL_GT() {
	    return this.getToken(BaserowFormula.EQUAL_GT, 0);
	};

	AND() {
	    return this.getToken(BaserowFormula.AND, 0);
	};

	OR() {
	    return this.getToken(BaserowFormula.OR, 0);
	};

	LIKE() {
	    return this.getToken(BaserowFormula.LIKE, 0);
	};

	BETWEEN() {
	    return this.getToken(BaserowFormula.BETWEEN, 0);
	};

	IN() {
	    return this.getToken(BaserowFormula.IN, 0);
	};

	LT() {
	    return this.getToken(BaserowFormula.LT, 0);
	};

	GT() {
	    return this.getToken(BaserowFormula.GT, 0);
	};

	EQUAL() {
	    return this.getToken(BaserowFormula.EQUAL, 0);
	};

	LTE() {
	    return this.getToken(BaserowFormula.LTE, 0);
	};

	GTE() {
	    return this.getToken(BaserowFormula.GTE, 0);
	};

	LT_GT() {
	    return this.getToken(BaserowFormula.LT_GT, 0);
	};

	BANG_EQUAL() {
	    return this.getToken(BaserowFormula.BANG_EQUAL, 0);
	};

	IS() {
	    return this.getToken(BaserowFormula.IS, 0);
	};

	DISTINCT() {
	    return this.getToken(BaserowFormula.DISTINCT, 0);
	};

	FROM() {
	    return this.getToken(BaserowFormula.FROM, 0);
	};

	OPEN_BRACKET = function(i) {
		if(i===undefined) {
			i = null;
		}
	    if(i===null) {
	        return this.getTokens(BaserowFormula.OPEN_BRACKET);
	    } else {
	        return this.getToken(BaserowFormula.OPEN_BRACKET, i);
	    }
	};


	CLOSE_BRACKET = function(i) {
		if(i===undefined) {
			i = null;
		}
	    if(i===null) {
	        return this.getTokens(BaserowFormula.CLOSE_BRACKET);
	    } else {
	        return this.getToken(BaserowFormula.CLOSE_BRACKET, i);
	    }
	};


	BANG() {
	    return this.getToken(BaserowFormula.BANG, 0);
	};

	COLON = function(i) {
		if(i===undefined) {
			i = null;
		}
	    if(i===null) {
	        return this.getTokens(BaserowFormula.COLON);
	    } else {
	        return this.getToken(BaserowFormula.COLON, i);
	    }
	};


	COLON_COLON = function(i) {
		if(i===undefined) {
			i = null;
		}
	    if(i===null) {
	        return this.getTokens(BaserowFormula.COLON_COLON);
	    } else {
	        return this.getToken(BaserowFormula.COLON_COLON, i);
	    }
	};


	OF() {
	    return this.getToken(BaserowFormula.OF, 0);
	};

	DOT() {
	    return this.getToken(BaserowFormula.DOT, 0);
	};

	AT() {
	    return this.getToken(BaserowFormula.AT, 0);
	};

	TIME() {
	    return this.getToken(BaserowFormula.TIME, 0);
	};

	ZONE() {
	    return this.getToken(BaserowFormula.ZONE, 0);
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterExpr(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitExpr(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitExpr(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}



class Bool_exprContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_bool_expr;
    }

	TRUE() {
	    return this.getToken(BaserowFormula.TRUE, 0);
	};

	FALSE() {
	    return this.getToken(BaserowFormula.FALSE, 0);
	};

	NOT() {
	    return this.getToken(BaserowFormula.NOT, 0);
	};

	bool_expr = function(i) {
	    if(i===undefined) {
	        i = null;
	    }
	    if(i===null) {
	        return this.getTypedRuleContexts(Bool_exprContext);
	    } else {
	        return this.getTypedRuleContext(Bool_exprContext,i);
	    }
	};

	AND() {
	    return this.getToken(BaserowFormula.AND, 0);
	};

	OR() {
	    return this.getToken(BaserowFormula.OR, 0);
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterBool_expr(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitBool_expr(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitBool_expr(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}



class Case_exprContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_case_expr;
    }

	CASE() {
	    return this.getToken(BaserowFormula.CASE, 0);
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

	END() {
	    return this.getToken(BaserowFormula.END, 0);
	};

	WHEN = function(i) {
		if(i===undefined) {
			i = null;
		}
	    if(i===null) {
	        return this.getTokens(BaserowFormula.WHEN);
	    } else {
	        return this.getToken(BaserowFormula.WHEN, i);
	    }
	};


	THEN = function(i) {
		if(i===undefined) {
			i = null;
		}
	    if(i===null) {
	        return this.getTokens(BaserowFormula.THEN);
	    } else {
	        return this.getToken(BaserowFormula.THEN, i);
	    }
	};


	ELSE() {
	    return this.getToken(BaserowFormula.ELSE, 0);
	};

	predicate = function(i) {
	    if(i===undefined) {
	        i = null;
	    }
	    if(i===null) {
	        return this.getTypedRuleContexts(PredicateContext);
	    } else {
	        return this.getTypedRuleContext(PredicateContext,i);
	    }
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterCase_expr(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitCase_expr(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitCase_expr(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}



class Expr_listContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_expr_list;
    }

	OPEN_PAREN() {
	    return this.getToken(BaserowFormula.OPEN_PAREN, 0);
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

	CLOSE_PAREN() {
	    return this.getToken(BaserowFormula.CLOSE_PAREN, 0);
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
	        listener.enterExpr_list(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitExpr_list(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitExpr_list(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}



class Type_nameContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_type_name;
    }

	TEXT() {
	    return this.getToken(BaserowFormula.TEXT, 0);
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterType_name(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitType_name(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitType_name(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}



class Data_typeContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_data_type;
    }

	type_name() {
	    return this.getTypedRuleContext(Type_nameContext,0);
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterData_type(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitData_type(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitData_type(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}



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

	func_name() {
	    return this.getTypedRuleContext(Func_nameContext,0);
	};

	OPEN_PAREN() {
	    return this.getToken(BaserowFormula.OPEN_PAREN, 0);
	};

	VARIADIC() {
	    return this.getToken(BaserowFormula.VARIADIC, 0);
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

	CLOSE_PAREN() {
	    return this.getToken(BaserowFormula.CLOSE_PAREN, 0);
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



class PredicateContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_predicate;
    }

	expr() {
	    return this.getTypedRuleContext(ExprContext,0);
	};

	OPEN_PAREN() {
	    return this.getToken(BaserowFormula.OPEN_PAREN, 0);
	};

	predicate = function(i) {
	    if(i===undefined) {
	        i = null;
	    }
	    if(i===null) {
	        return this.getTypedRuleContexts(PredicateContext);
	    } else {
	        return this.getTypedRuleContext(PredicateContext,i);
	    }
	};

	CLOSE_PAREN() {
	    return this.getToken(BaserowFormula.CLOSE_PAREN, 0);
	};

	NOT() {
	    return this.getToken(BaserowFormula.NOT, 0);
	};

	AND() {
	    return this.getToken(BaserowFormula.AND, 0);
	};

	OR() {
	    return this.getToken(BaserowFormula.OR, 0);
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterPredicate(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitPredicate(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitPredicate(this);
	    } else {
	        return visitor.visitChildren(this);
	    }
	}


}



class Non_reserved_keywordContext extends antlr4.ParserRuleContext {

    constructor(parser, parent, invokingState) {
        if(parent===undefined) {
            parent = null;
        }
        if(invokingState===undefined || invokingState===null) {
            invokingState = -1;
        }
        super(parent, invokingState);
        this.parser = parser;
        this.ruleIndex = BaserowFormula.RULE_non_reserved_keyword;
    }

	UPPER() {
	    return this.getToken(BaserowFormula.UPPER, 0);
	};

	LOWER() {
	    return this.getToken(BaserowFormula.LOWER, 0);
	};

	enterRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.enterNon_reserved_keyword(this);
		}
	}

	exitRule(listener) {
	    if(listener instanceof BaserowFormulaListener ) {
	        listener.exitNon_reserved_keyword(this);
		}
	}

	accept(visitor) {
	    if ( visitor instanceof BaserowFormulaVisitor ) {
	        return visitor.visitNon_reserved_keyword(this);
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

	non_reserved_keyword() {
	    return this.getTypedRuleContext(Non_reserved_keywordContext,0);
	};

	DOUBLEQ_STRING_LITERAL() {
	    return this.getToken(BaserowFormula.DOUBLEQ_STRING_LITERAL, 0);
	};

	IDENTIFIER() {
	    return this.getToken(BaserowFormula.IDENTIFIER, 0);
	};

	type_name() {
	    return this.getTypedRuleContext(Type_nameContext,0);
	};

	IDENTIFIER_UNICODE() {
	    return this.getToken(BaserowFormula.IDENTIFIER_UNICODE, 0);
	};

	identifier = function(i) {
	    if(i===undefined) {
	        i = null;
	    }
	    if(i===null) {
	        return this.getTypedRuleContexts(IdentifierContext);
	    } else {
	        return this.getTypedRuleContext(IdentifierContext,i);
	    }
	};

	DOT() {
	    return this.getToken(BaserowFormula.DOT, 0);
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
BaserowFormula.Bool_exprContext = Bool_exprContext; 
BaserowFormula.Case_exprContext = Case_exprContext; 
BaserowFormula.Expr_listContext = Expr_listContext; 
BaserowFormula.Type_nameContext = Type_nameContext; 
BaserowFormula.Data_typeContext = Data_typeContext; 
BaserowFormula.Func_nameContext = Func_nameContext; 
BaserowFormula.Func_callContext = Func_callContext; 
BaserowFormula.PredicateContext = PredicateContext; 
BaserowFormula.Non_reserved_keywordContext = Non_reserved_keywordContext; 
BaserowFormula.IdentifierContext = IdentifierContext; 
