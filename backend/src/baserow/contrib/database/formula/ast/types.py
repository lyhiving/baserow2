from typing import List, Optional

from django.db.models import TextField, DecimalField, Field

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
    BaserowFieldByIdReference,
    BaserowExpression,
    BaserowFieldReference,
)
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_tree,
    fix_formula,
)
from baserow.contrib.database.formula.parser.errors import MaximumFormulaSizeError

FIELD_TYPE_LOOKUP = {}


class Typer:
    def __init__(
        self,
        table,
        field_override=None,
        new_field=None,
        deleted_field_id_names=None,
        new_field_names_to_id=None,
    ):
        if deleted_field_id_names is None:
            deleted_field_id_names = {}
        self.deleted_field_id_names = deleted_field_id_names
        if new_field_names_to_id is None:
            new_field_names_to_id = {}
        self.new_field_names_to_id = new_field_names_to_id
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
        self.formula_field_ids = []
        self.field_types = {}
        self.field_references = {}
        self.field_parents = {}
        self.formula_asts = {}
        self.field_id_to_field = {f.id: f for f in self.all_fields}
        self.field_ids_requiring_fix = set()

        self.type_table()

    def type_table(self):
        try:
            for field in self.all_fields:
                specific_class = field.specific_class
                field_type = field_type_registry.get_by_model(specific_class)
                if field_type.type == "formula":
                    self.formula_field_ids.append(field.id)
                    if field.trashed or field.id in self.deleted_field_id_names:
                        ast = BaserowFieldReference(field.name)
                        self.deleted_field_id_names[field.id] = field.name
                    else:
                        ast = raw_formula_to_tree(
                            field.specific.formula,
                            self.field_id_to_field,
                            self.new_field_names_to_id,
                        )
                    children = ast.accept(FieldReferenceResolvingVisitor())
                    self.field_references[field.id] = children
                    for child in children:
                        parents = self.field_parents.setdefault(child, set())
                        parents.add(field.id)
                    self.formula_asts[field.id] = ast
                else:
                    if field.trashed or field.id in self.deleted_field_id_names:
                        self.field_types[field.id] = TypeResult.invalid_type(
                            f"Field {field.name} is deleted"
                        )
                        self.deleted_field_id_names[field.id] = field.name
                    else:
                        self.field_types[field.id] = TypeResult.valid_type(
                            field_type.get_model_field(field.specific)
                        )
                    self.field_references[field.id] = []

            check_for_self_references(self.field_references)
            formula_field_ordered_ids = self.resolve_formula_field_ordering()
            for formula_field_id in formula_field_ordered_ids:
                reference_fields_set = set(self.field_references[formula_field_id])
                deleted_fields_set = set(self.deleted_field_id_names.keys())
                new_fields_set = set(self.new_field_names_to_id.values())
                formula_field_references_deleted_field = (
                    len(reference_fields_set.intersection(deleted_fields_set)) > 0
                )
                formula_field_references_new_field = (
                    len(reference_fields_set.intersection(new_fields_set))
                ) > 0
                if (
                    formula_field_references_deleted_field
                    or formula_field_references_new_field
                ):
                    self.field_ids_requiring_fix.add(formula_field_id)
                ast = self.formula_asts[formula_field_id]
                self.field_types[formula_field_id] = ast.accept(
                    TypeResolverASTVisitor(self.field_types)
                )
                self.formula_asts[formula_field_id] = ast.accept(
                    UnnestingResolverASTVisitor(self.formula_asts)
                )

            return self.field_types, self.formula_asts, self.field_references
        except RecursionError:
            raise MaximumFormulaSizeError()

    def calculate_all_child_fields(self, fields):
        fields_to_check = fields.copy()
        extra_fields = []
        extra_field_ids = set()
        current_field_ids = {f.id for f in fields}
        while len(fields_to_check) > 0:
            field = fields_to_check.pop(0)
            references = self.field_references[field.id]
            for ref in references:
                if ref not in current_field_ids and ref not in extra_field_ids:
                    new_field = self.field_id_to_field[ref]
                    extra_fields.append(new_field)
                    extra_field_ids.add(ref)
                    fields_to_check.append(new_field)
        return extra_fields

    def update_fields(self, to_filter=None):
        updated_fields = set()
        for formula_field_id in self.formula_field_ids:
            field_type = self.field_types[formula_field_id]
            formula_field = self.field_id_to_field[formula_field_id]
            if formula_field.trashed:
                continue
            specific_formula_field = self.field_id_to_field[formula_field_id].specific
            previous_error = str(specific_formula_field.error)
            print("FOR ", formula_field_id)
            print("IT WAS ", previous_error)
            previous_formula = str(specific_formula_field.formula)

            if formula_field_id in self.field_ids_requiring_fix:
                specific_formula_field.formula = fix_formula(
                    specific_formula_field.formula,
                    self.deleted_field_id_names,
                    self.new_field_names_to_id,
                )

            if field_type.is_invalid():
                specific_formula_field.error = field_type.error
            else:
                specific_formula_field.error = None

            if not specific_formula_field.trashed and (
                previous_error != str(specific_formula_field.error)
                or previous_formula != str(specific_formula_field.formula)
            ):
                print(
                    "Saving ",
                    specific_formula_field.name,
                    " with ",
                    specific_formula_field.error,
                    " and ",
                    specific_formula_field.formula,
                )
                specific_formula_field.save()
                if to_filter is None or specific_formula_field.id != to_filter.id:
                    updated_fields.add(specific_formula_field)
            else:
                print(
                    "Not Saving ",
                    specific_formula_field.name,
                    " with ",
                    specific_formula_field.error,
                    " and ",
                    specific_formula_field.formula,
                    " as was previously ",
                    previous_error,
                    " and ",
                    previous_formula,
                )
        return updated_fields

    def get_type(self, field):
        return self.field_types[field.id]

    def set_field_type_or_raise(self, field_type, field):
        if field_type.type == "formula":
            new_field_type = self.get_type(field)
            if new_field_type.is_invalid():
                raise InvalidFieldType(new_field_type.error)
            else:
                field.formula_type = (
                    new_field_type.resulting_field_type.__class__.__name__
                )

    def calculate_all_parent_field_ids(self, field_id):
        initial_parents = self.field_parents.get(field_id, [])
        related_field_ids = set(initial_parents)
        parents_to_check = list(initial_parents)
        while len(parents_to_check) > 0:
            parent_id = parents_to_check.pop(0)
            parents = self.field_parents.get(parent_id, [])
            for parent in parents:
                related_field_ids.add(parent)
                related_field_ids.update(self.calculate_all_parent_field_ids(parent))
        return related_field_ids

    def calculate_all_parent_valid_fields(self, field):
        related_field_ids = self.calculate_all_parent_field_ids(field.id)
        return [
            self.field_id_to_field[i]
            for i in related_field_ids
            if self.field_types.get(i, TypeResult.invalid_type("")).is_valid()
        ]

    def resolve_formula_field_ordering(self):
        ordered_formula_fields = []
        unvisited_formula_fields = self.formula_field_ids.copy()
        while len(unvisited_formula_fields) > 0:
            new_starting_formula = unvisited_formula_fields[0]
            self.build_tree(
                new_starting_formula,
                [],
                unvisited_formula_fields,
                ordered_formula_fields,
            )
        return ordered_formula_fields

    def build_tree(
        self,
        current_field,
        visited_field_names,
        unvisited_formula_fields,
        ordered_formula_fields,
    ):
        if current_field in self.formula_field_ids:
            new_visited_field_names = visited_field_names.copy()
            new_visited_field_names.append(current_field)
            if current_field in visited_field_names:
                raise NoCircularReferencesError(
                    [self.field_id_to_field[i].name for i in new_visited_field_names]
                )
            if current_field in unvisited_formula_fields:
                unvisited_formula_fields.remove(current_field)
            for ref in self.field_references[current_field]:
                self.build_tree(
                    ref,
                    new_visited_field_names,
                    unvisited_formula_fields,
                    ordered_formula_fields,
                )
            if current_field not in ordered_formula_fields:
                ordered_formula_fields.append(current_field)


def check_for_self_references(all_field_references):
    for field_db_cloumn, field_references in all_field_references.items():
        if field_db_cloumn in field_references:
            raise NoSelfReferencesError()


class FieldReferenceResolvingVisitor(BaserowFormulaASTVisitor[List[str]]):
    def visit_field_reference(self, field_reference: BaserowFieldReference):
        # The only time when we should encounter a field reference here is when this
        # field is pointing at a trashed or deleted field.
        return []

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

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference
    ):
        return [field_by_id_reference.referenced_field_id]


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
        return not self.is_valid()

    def is_valid(self):
        return self.error is None

    def __str__(self):
        return (
            f"Valid Type({self.resulting_field_type})"
            if self.is_valid()
            else f"Invalid Type({self.error})"
        )


class TypeResolverASTVisitor(BaserowFormulaASTVisitor[TypeResult]):
    def visit_field_reference(self, field_reference: BaserowFieldReference):
        return TypeResult.invalid_type(
            f"Unknown field {field_reference.referenced_field_name}"
        )

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

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference
    ):
        if field_by_id_reference.referenced_field_id not in self.field_types:
            return TypeResult.invalid_type(
                f"Unknown or deleted field referenced: "
                f"{field_by_id_reference.referenced_field_id}"
            )
        return self.field_types[field_by_id_reference.referenced_field_id]


class UnnestingResolverASTVisitor(BaserowFormulaASTVisitor[BaserowExpression]):
    def visit_field_reference(self, field_reference: BaserowFieldReference):
        return field_reference

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

    def visit_field_by_id_reference(
        self, field_by_id_reference: BaserowFieldByIdReference
    ):
        if field_by_id_reference.referenced_field_id in self.field_asts:
            return self.field_asts[field_by_id_reference.referenced_field_id]
        else:
            return field_by_id_reference
