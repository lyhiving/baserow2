from typing import List, Optional

from django.db.models import Field, TextField, DecimalField

from baserow.contrib.database.fields.models import FormulaField
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.formula.ast.errors import (
    NoSelfReferencesError,
    NoCircularReferencesError,
    InvalidFieldType,
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


class Typer:
    def __init__(self, table, field_override=None, new_field=None):
        self.all_fields = [
            f for f in table.field_set(manager="objects_and_trash").all()
        ]
        if field_override:
            new_all_fields = []
            for field in self.all_fields:
                if field.id == field_override.id:
                    new_all_fields.append(field_override)
                else:
                    new_all_fields.append(field)
            self.all_fields = new_all_fields
        if new_field is not None:
            self.all_fields.append(new_field)
        self.formula_fields = []
        self.field_types = {}
        self.field_references = {}
        self.formula_asts = {}
        self.field_db_names = {f.name: f.db_column for f in self.all_fields}
        self.dbname_to_field = {f.db_column: f for f in self.all_fields}

        self.type_table()

    def calculate_all_depended_on_fields(self, fields):
        fields_to_check = fields.copy()
        extra_fields = []
        extra_field_names = set()
        current_field_db_names = {f.db_column for f in fields}
        while len(fields_to_check) > 0:
            field = fields_to_check.pop(0)
            references = self.field_references[field.db_column]
            for ref in references:
                if ref not in current_field_db_names and ref not in extra_field_names:
                    new_field = self.dbname_to_field[ref]
                    extra_fields.append(new_field)
                    extra_field_names.add(ref)
                    fields_to_check.append(new_field)
        return extra_fields

    def update_fields(self):
        updated_fields = []
        for formula_field in self.formula_fields:
            field_type = self.field_types[formula_field]
            formula_field = self.dbname_to_field[formula_field].specific
            previous_error = formula_field.error
            if field_type.is_invalid():
                formula_field.error = field_type.error
            else:
                formula_field.error = None
            if previous_error != formula_field.error:
                formula_field.save()
                updated_fields.append(formula_field)
        return updated_fields

    def type_table(self):
        try:
            for field in self.all_fields:
                specific_class = field.specific_class
                field_type = field_type_registry.get_by_model(specific_class)
                if field_type.type == "formula":
                    self.formula_fields.append(field.db_column)
                    ast = raw_formula_to_tree(
                        field.specific.formula, self.field_db_names
                    )
                    self.field_references[field.db_column] = ast.accept(
                        FieldReferenceResolvingVisitor()
                    )
                    self.formula_asts[field.db_column] = ast
                else:
                    self.field_types[field.db_column] = TypeResult.valid_type(
                        field_type.get_model_field(field.specific)
                    )
                    self.field_references[field.db_column] = []

            check_for_self_references(self.field_references)
            formula_fields_ordered = resolve_formula_field_ordering(
                self.field_references, self.formula_fields
            )
            for formula_field in formula_fields_ordered:
                ast = self.formula_asts[formula_field]
                self.field_types[formula_field] = ast.accept(
                    TypeResolverASTVisitor(self.field_types)
                )
                self.formula_asts[formula_field] = ast.accept(
                    UnnestingResolverASTVisitor(self.formula_asts)
                )

            return (self.field_types), (self.formula_asts), (self.field_references)
        except RecursionError:
            raise MaximumFormulaDepthError()

    def get_type(self, field):
        return self.field_types[field.db_column]

    def set_field_type_or_raise(self, field_type, field):
        if field_type.type == "formula":
            new_field_type = self.get_type(field)
            if new_field_type.is_invalid():
                raise InvalidFieldType(new_field_type.error)
            else:
                field.formula_type = (
                    new_field_type.resulting_field_type.__class__.__name__
                )

    def update_pk(self, pk):
        self._fix_dict(pk, self.field_references)
        self._fix_dict(pk, self.field_types)
        self._fix_dict(pk, self.formula_asts)
        self._fix_dict(pk, self.dbname_to_field)
        for name, db_name in self.field_db_names.items():
            if db_name == "field_None":
                self.field_db_names[db_name] = f"field_{pk}"
                return

    def _fix_dict(self, pk, dict_to_fix):
        if "field_None" in dict_to_fix:
            dict_to_fix[f"field_{pk}"] = dict_to_fix["field_None"]
            del dict_to_fix["field_None"]


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


class TypeResult:
    def __init__(self, resulting_field_type: Optional[Field], error: Optional[str]):
        self.resulting_field_type = resulting_field_type
        self.error = error

    @classmethod
    def valid_type(cls, resulting_field_type: Field):
        return cls(resulting_field_type, None)

    @classmethod
    def invalid_type(cls, error: str):
        return cls(None, error)

    def is_invalid(self):
        return self.error is not None


class TypeResolverASTVisitor(BaserowFormulaASTVisitor[TypeResult]):
    def __init__(self, field_types):
        self.field_types = field_types

    def visit_string_literal(self, string_literal: BaserowStringLiteral) -> TypeResult:
        return TypeResult.valid_type(TextField())

    def visit_function_call(self, function_call: BaserowFunctionCall) -> TypeResult:
        arg_types = []
        invalid_results = []
        for i, expr in enumerate(function_call.args):
            arg_type_result = expr.accept(self)
            if arg_type_result.is_invalid():
                invalid_results.append((i, arg_type_result))
            else:
                arg_types.append(arg_type_result.resulting_field_type)
        if len(invalid_results) > 0:
            message = ", ".join(
                [f"argument {i} invalid because {msg}" for i, msg in invalid_results]
            )
            return TypeResult.invalid_type(
                f"Failed to type arguments for call "
                f"{function_call.function_def} because {message}"
            )
        else:
            return function_call.function_def.to_django_field_type(arg_types)

    def visit_int_literal(self, int_literal: BaserowIntegerLiteral):
        return TypeResult.valid_type(DecimalField(max_digits=50, decimal_places=0))

    def visit_field_reference(self, field_reference: BaserowFieldReference):
        if field_reference.referenced_field not in self.field_types:
            return TypeResult.invalid_type(
                f"Unknown or deleted field referenced: "
                f"{field_reference.referenced_field}"
            )
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
