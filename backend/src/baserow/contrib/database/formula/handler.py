from typing import Type, Dict, Set, Optional

from django.db.models import Model, Expression, Q

from baserow.contrib.database.fields.dependencies.types import FieldDependencies
from baserow.contrib.database.fields.field_cache import FieldCache
from baserow.contrib.database.formula.ast.tree import (
    BaserowExpression,
    BaserowFieldReference,
    BaserowFunctionDefinition,
)
from baserow.contrib.database.formula.expression_generator.generator import (
    baserow_expression_to_update_django_expression,
    baserow_expression_to_insert_django_expression,
)
from baserow.contrib.database.formula.parser.ast_mapper import (
    raw_formula_to_untyped_expression,
)
from baserow.contrib.database.formula.parser.parser import get_parse_tree_for_formula
from baserow.contrib.database.formula.parser.update_field_names import (
    update_field_names,
)
from baserow.contrib.database.formula.types.exceptions import UnknownFormulaType
from baserow.contrib.database.formula.types.formula_type import BaserowFormulaType
from baserow.contrib.database.formula.types.formula_types import BASEROW_FORMULA_TYPES
from baserow.contrib.database.formula.types.typer import (
    calculate_typed_expression,
    recreate_formula_field_if_needed,
)
from baserow.contrib.database.formula.types.visitors import (
    FunctionsUsedVisitor,
    FieldReferenceExtractingVisitor,
)
from baserow.core.db import LockedAtomicTransaction


def _expression_requires_refresh_after_insert(expression: BaserowExpression):
    """
    WARNING: This function is directly used by migration code. Please ensure
    backwards compatability when adding fields etc.

    Some baserow expressions cannot be computed in a single INSERT xx INTO yy statement.
    For example expressions which reference the rows id. This function calculates if
    the provided expression is one such expression.

    :param expression: The expression to check to see if it needs a database refresh
        after an insert.
    :return: True if after executing this expression the row should be selected again
        from the database with the expression as second time to get its correct value.
    """

    functions_used: Set[BaserowFunctionDefinition] = expression.accept(
        FunctionsUsedVisitor()
    )
    return any(f.requires_refresh_after_insert for f in functions_used)


def _lookup_formula_type_from_string(formula_type_string):
    for possible_type in BASEROW_FORMULA_TYPES:
        if formula_type_string == possible_type.type:
            return possible_type
    raise UnknownFormulaType(formula_type_string)


class FormulaHandler:
    """
    Contains all the methods used to interact with formulas and formula fields in
    Baserow.
    """

    BASEROW_FORMULA_VERSION = 2

    @classmethod
    def baserow_expression_to_update_django_expression(
        cls, expression: BaserowExpression, model: Type[Model]
    ) -> Expression:
        """
        Converts the provided baserow expression to a django expression that can be
        used in an update statement. Compared to the django expression from the
        alternate insert method below this expression will contain column references
        to other tables/non formula columns instead of directly subsituted values.

        :param expression: A fully typed internal Baserow expression.
        :param model: The model class (database table) that the expression will be run
            for a column in.
        :return: A Django Expression for use in an update statement.
        """

        return baserow_expression_to_update_django_expression(expression, model)

    @classmethod
    def baserow_expression_to_insert_django_expression(
        cls,
        expression: BaserowExpression,
        model_instance: Model,
    ) -> Expression:
        """
        Converts the provided baserow expression to a django expression that can be
        used in an insert statement. Compared to the django expression from the
        alternate update method above this expression will contain the values
        taken directly from the provided model instance (row) and use those in place
        of field references.

        :param expression: A fully typed internal Baserow expression.
        :param model_instance: The instance of the row that is about to be inserted.
        :return: A Django Expression for use in an insert statement.
        """

        return baserow_expression_to_insert_django_expression(
            expression, model_instance
        )

    @classmethod
    def get_normal_field_reference_expression(
        cls, field, formula_type: BaserowFormulaType
    ) -> BaserowExpression:
        """
        Returns the Baserow Expression that represents internally a normal Baserow
        field in a formula. Non normal fields are link row fields and any field type
        derived from a formula type and should not use this representation but their
        own.

        :param field: The field instance that is being referenced.
        :param formula_type: The formula type of said instance.
        :return: A Baserow Expression that can be used in internal formulas to represent
            a reference to field.
        """

        return BaserowFieldReference[BaserowFormulaType](field.db_column, formula_type)

    @classmethod
    def rename_field_references_in_formula_string(
        cls,
        formula_to_update: str,
        field_renames: Dict[str, str],
        via_field: Optional[str] = None,
        field_ids_to_replace_with_name_refs: Optional[Dict[int, str]] = None,
        field_names_to_replace_with_id_refs: Optional[Dict[str, int]] = None,
    ) -> str:
        """
        Given a dictionary of renames and an optional via field renames all direct
        references in the raw formula string to use the renamed versions. Preserves
        whitespace, comments and everything else in the formula string.

        :param formula_to_update: A string containing a baserow formula expression to
            rename all field('xxx') references which match a key:value in field_names.
        :param field_renames: A dictionary of field names to rename references for. The
            key is the existing name used by the formula and the value is the new name
            to use instead.
        :param via_field: If provided this indicates only field references which go via
            this field name should have their target field names renamed.
        :param field_names_to_replace_with_id_refs: DEPRECATED - An optional dict of
            field names that any references to should be replaced with the old
            field_by_id references.
        :param field_ids_to_replace_with_name_refs: DEPRECATED - An optional dict of
            field ids that any references to should be replaced with a
            normal field reference.
        """

        return update_field_names(
            formula_to_update,
            field_renames,
            via_field=via_field,
            field_ids_to_replace_with_name_refs=field_ids_to_replace_with_name_refs,
            field_names_to_replace_with_id_refs=field_names_to_replace_with_id_refs,
        )

    @classmethod
    def get_field_dependencies_from_expression(cls, expression) -> FieldDependencies:
        """
        Helper method that returns a the field dependencies of a given expression.

        :param expression: The expression to calculate field dependencies for.
        """

        return expression.accept(FieldReferenceExtractingVisitor())

    @classmethod
    def get_field_dependencies(cls, formula_field, field_lookup_cache):
        """
        Returns all the field dependencies for the provided formula field.

        :param formula_field: A formula field instance to lookup its dependencies for.
        :param field_lookup_cache: An optional field lookup cache that can be used
            when calculating dependencies.
        """

        # Importantly we use the untyped basic expression which will still contain
        # field(..) references. After typing these will have been replaced and so we
        # can't get dependencies out of the internal formula.
        return cls.get_field_dependencies_from_expression(
            formula_field.cached_untyped_expression
        )

    @classmethod
    def raw_formula_to_untyped_expression(cls, formula_string):
        """
        Converts the provided formula string to an untyped BaserowExpression which is
        an intermediate representation of the formula consisting of a tree of python
        objects. This form is much easier to inspect, transform and perform calculations
        on compared to the raw string.

        :param formula_string: A string containing a formula in the Baserow Formula
            expression language.
        """
        return raw_formula_to_untyped_expression(formula_string)

    @classmethod
    def get_formula_type_from_field(cls, formula_field) -> BaserowFormulaType:
        """
        Looks up the formula type stored in the database for the provided formula field
        and returns it.

        :param formula_field: An instance of a formula field whose type stored in the
            database should be looked up and returned.
        :return: Returns a populated instance of a BaserowFormulaType object which
            represents the stored type for the formula field.
        """

        formula_type = _lookup_formula_type_from_string(formula_field.formula_type)
        return formula_type.construct_type_from_formula_field(formula_field)

    @classmethod
    def get_typed_internal_expression_from_field(
        cls, formula_field, used_cached_attrs=True
    ) -> BaserowExpression[BaserowFormulaType]:
        """
        Returns a typed expression which can be directly translated to a Django
        Expression using the two baserow_expression_to_{update,insert}_django_expression
        methods above.

        The internal typed expression differs from formula_field.formula in a number of
        ways:
            - Any field references to formulas in the same table have been substituted
              with that formulas internal expression directly.
            - Any field references to other tables columns or non formula columns in the
              same column are in the form `field('field_XX')` where the references
              value is the actual database column name and not the name of the field
              set by the user.
            - All transformations of the formula that occur during the typing process
              have been applied. For instance if you have the formula
              `concat(1, 'a', field('a date field'))` during the typing process the
              concat function will wrap all of its arguments in the appropriate to_text
              function if they are of different types. This internal formula will
              then look something like `concat(totext(1), 'a', datetime_format(field(
              'field_NN', 'YYYY-MM-DD'))`

        You can think of the internal formula as the actual formula that will correctly
        calculate the desired result of formula_field.formula.

        :param formula_field: The formula field instance to get the internal
            expression for.
        :param used_cached_attrs: If False no cached formula_field attributes will be
            used. Useful for migrations when model functions cannot be used.
        :return: A typed internal Baserow Expression.
        """

        untyped_internal_expr = FormulaHandler.raw_formula_to_untyped_expression(
            formula_field.internal_formula
        )
        if used_cached_attrs:
            return untyped_internal_expr.with_type(formula_field.cached_formula_type)
        else:
            return untyped_internal_expr.with_type(
                cls.get_formula_type_from_field(formula_field)
            )

    @classmethod
    def recalculate_internal_formula_fields(cls, formula_field, field_lookup_cache):
        """
        WARNING: This function is directly used by migration code. Please ensure
        backwards compatability when adding fields etc.

        For the provided formula field this function recalculates all of the required
        internal attributes given the user supplied ones have already been set on
        the instance.

        :param formula_field: The formula instance to update its internal fields for.
        :param field_lookup_cache: A field cache that will be used to lookup fields
            during any recalculations.
        :return: The typed internal expression which results after the recalculation.
        """

        if field_lookup_cache is None:
            field_lookup_cache = FieldCache()

        expression = calculate_typed_expression(formula_field, field_lookup_cache)
        expression_type = expression.expression_type

        formula_field.internal_formula = str(expression)
        formula_field.version = cls.BASEROW_FORMULA_VERSION
        expression_type.persist_onto_formula_field(formula_field)
        formula_field.requires_refresh_after_insert = (
            _expression_requires_refresh_after_insert(expression)
        )
        return expression

    @classmethod
    def get_parse_tree_for_formula(cls, formula: str):
        """
        WARNING: This function is directly used by migration code. Please ensure
        backwards compatability .

        Returns the raw antlr parse tree for a formula string in the baserow formula
        language.

        :param formula: A string possibly in the baserow formula language.
        :return: An Antlr parse tree for the formula.
        """

        return get_parse_tree_for_formula(formula)

    @classmethod
    def recalculate_formulas_according_to_version(cls):
        from baserow.contrib.database.fields.models import FormulaField

        field_lookup_cache = FieldCache()
        already_recalculated = set()

        def _recalculate_depth_first(f):
            recalculated_dependant = False
            if f in already_recalculated:
                return True
            for dep in f.field_dependencies.all():
                recalculated_dependant = (
                    recalculated_dependant or _recalculate_depth_first(dep)
                )

            f = f.specific

            if isinstance(f, FormulaField) and (
                f.version != cls.BASEROW_FORMULA_VERSION or recalculated_dependant
            ):
                field.save(
                    field_lookup_cache=field_lookup_cache, raise_if_invalid=False
                )
                recalculated_dependant = True
                already_recalculated.add(f)
            return recalculated_dependant

        with LockedAtomicTransaction(FormulaField):
            if FormulaField.objects.filter(
                ~Q(version=cls.BASEROW_FORMULA_VERSION)
            ).exists():
                for field in FormulaField.objects.all():
                    _recalculate_depth_first(field)

                FormulaField.objects.update(
                    version=cls.BASEROW_FORMULA_VERSION,
                )

    @classmethod
    def recalculate_formula_and_get_update_expression(
        cls, field, old_field, field_cache
    ):
        from baserow.contrib.database.views.handler import ViewHandler

        field.save(field_lookup_cache=field_cache)
        recreate_formula_field_if_needed(field, old_field)
        ViewHandler().field_type_changed(field)
        return FormulaHandler.baserow_expression_to_update_django_expression(
            field.cached_typed_internal_expression,
            field_cache.get_model(field.table),
        )
