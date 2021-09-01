from typing import Union, Type, List

from django.db.models import Field, TextField, IntegerField

from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.formula.ast.errors import (
    NoSelfReferencesError,
    NoCircularReferencesError,
    UnknownFieldReference,
)
from baserow.contrib.database.formula.ast.tree import (
    BaserowFormulaASTVisitor,
    BaserowStringLiteral,
    BaserowFunctionCall,
    BaserowIntegerLiteral,
    BaserowFieldReference,
    BaserowExpression,
)
from baserow.contrib.database.formula.parser.ast_mapper import raw_formula_to_tree
from baserow.contrib.database.formula.parser.errors import MaximumFormulaDepthError

FIELD_TYPE_LOOKUP = {}


def type_table(fields):
    try:
        formula_fields = []
        field_types = {}
        field_references = {}
        formula_asts = {}
        field_db_names = {f.name: f.db_column for f in fields}
        for field in fields:
            specific_class = field.specific_class
            field_type = field_type_registry.get_by_model(specific_class)
            if field_type.type == "formula":
                formula_fields.append(field.db_column)
                ast = raw_formula_to_tree(field.specific.formula, field_db_names)
                field_references[field.db_column] = ast.accept(
                    FieldReferenceResolvingVisitor()
                )
                formula_asts[field.db_column] = ast
            else:
                field_types[field.db_column] = field_type.get_model_field(
                    field.specific
                )
                field_references[field.db_column] = []

        check_for_self_references(field_references)
        formula_fields_ordered = resolve_formula_field_ordering(
            field_references, formula_fields
        )
        for formula_field in formula_fields_ordered:
            ast = formula_asts[formula_field]
            field_types[formula_field] = ast.accept(TypeResolverASTVisitor(field_types))
            formula_asts[formula_field] = ast.accept(
                UnnestingResolverASTVisitor(formula_asts)
            )

        print(f"Field types are {field_types}")
        print(f"Asts are {formula_asts}:")
        for field, ast in formula_asts.items():
            print(field)
            print(str(ast))
        return field_types, formula_asts
    except RecursionError:
        raise MaximumFormulaDepthError()


def check_for_self_references(all_field_references):
    for field_db_cloumn, field_references in all_field_references.items():
        if field_db_cloumn in field_references:
            raise NoSelfReferencesError()


def resolve_formula_field_ordering(all_field_references, formula_fields):
    ordered_formula_fields = []
    unvisited_formula_fields = formula_fields.copy()
    while len(unvisited_formula_fields) > 0:
        new_starting_formula = unvisited_formula_fields[0]
        build_tree(
            new_starting_formula,
            set(),
            all_field_references,
            formula_fields,
            unvisited_formula_fields,
            ordered_formula_fields,
        )
    return ordered_formula_fields


def build_tree(
    current_field,
    visited_field_names,
    all_field_references,
    formula_fields,
    unvisited_formula_fields,
    ordered_formula_fields,
):
    if current_field in formula_fields:
        if current_field in visited_field_names:
            raise NoCircularReferencesError()
        new_visited_field_names = visited_field_names.copy()
        new_visited_field_names.add(current_field)
        if current_field in unvisited_formula_fields:
            unvisited_formula_fields.remove(current_field)
        for ref in all_field_references[current_field]:
            build_tree(
                ref,
                new_visited_field_names,
                all_field_references,
                formula_fields,
                unvisited_formula_fields,
                ordered_formula_fields,
            )
        if current_field not in ordered_formula_fields:
            ordered_formula_fields.append(current_field)


class FieldReferenceResolvingVisitor(BaserowFormulaASTVisitor[List[str]]):
    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> List[str]:
        return []

    def visit_function_call(self, function_call: BaserowFunctionCall) -> List[str]:
        all_arg_references = [expr.accept(self) for expr in function_call.args]
        combined_references = []
        for arg_references in all_arg_references:
            combined_references += arg_references

        return combined_references

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return []

    def visit_field_reference(self, field_reference: BaserowFieldReference):
        return [field_reference.referenced_field]


class TypeResolverASTVisitor(BaserowFormulaASTVisitor[Field]):
    def __init__(self, field_types):
        self.field_types = field_types

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> Field:
        return TextField()

    def visit_function_call(self, function_call: BaserowFunctionCall) -> Field:
        arg_types = [expr.accept(self) for expr in function_call.args]
        return function_call.function_def.to_django_field_type(arg_types)

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return IntegerField()

    def visit_field_reference(self, field_reference: BaserowFieldReference):
        if field_reference.referenced_field not in self.field_types:
            raise UnknownFieldReference(field_reference.referenced_field)
        return self.field_types[field_reference.referenced_field]


class UnnestingResolverASTVisitor(BaserowFormulaASTVisitor[BaserowExpression]):
    def __init__(self, field_asts):
        self.field_asts = field_asts

    def visit_string_literal(
        self, string_literal: BaserowStringLiteral
    ) -> BaserowExpression:
        return string_literal

    def visit_function_call(
        self, function_call: BaserowFunctionCall
    ) -> BaserowExpression:
        args = [expr.accept(self) for expr in function_call.args]
        return BaserowFunctionCall(function_call.function_def, args)

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return int_literal

    def visit_field_reference(self, field_reference: BaserowFieldReference):
        if field_reference.referenced_field in self.field_asts:
            return self.field_asts[field_reference.referenced_field]
        else:
            return field_reference
