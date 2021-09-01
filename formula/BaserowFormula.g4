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
    | FIELD OPEN_PAREN field_reference CLOSE_PAREN # FieldReference
    | func_name OPEN_PAREN (expr (COMMA expr)*)? CLOSE_PAREN # FunctionCall
    ;

func_name
    : identifier
    ;

field_reference
    : SINGLEQ_STRING_LITERAL
    | DOUBLEQ_STRING_LITERAL
    ;

identifier
    : IDENTIFIER
    | IDENTIFIER_UNICODE
    ;

