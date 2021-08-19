parser grammar BaserowFormula;

options { tokenVocab=BaserowFormulaLexer; }

root
    : expr EOF
    ;

expr
    :
    SINGLEQ_STRING_LITERAL # StringLiteral
    | DOUBLEQ_STRING_LITERAL #  StringLiteral
    | func_name OPEN_PAREN (expr (COMMA expr)*)? CLOSE_PAREN # FunctionCall
    | identifier # Indentifier
    ;

func_name
    : identifier
    ;

func_call
    :
    ;

identifier
    : IDENTIFIER
    | IDENTIFIER_UNICODE
    ;

