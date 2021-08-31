parser grammar BaserowFormula;

options { tokenVocab=BaserowFormulaLexer; }

root
    : expr EOF
    ;

expr
    :
    SINGLEQ_STRING_LITERAL # StringLiteral
    | DOUBLEQ_STRING_LITERAL #  StringLiteral
    | INTEGER_LITERAL # IntegerLiteral
    | expr op=(PLUS | MINUS) expr # BinaryOp
    | func_name OPEN_PAREN (expr (COMMA expr)*)? CLOSE_PAREN # FunctionCall
    ;

func_name
    : identifier
    ;

identifier
    : IDENTIFIER
    | IDENTIFIER_UNICODE
    ;

