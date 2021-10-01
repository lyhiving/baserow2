import abc
from typing import (
    List,
    Type,
    Union,
    Callable,
    TypeVar,
)

from django.utils.functional import classproperty

from baserow.contrib.database.fields import models
from baserow.contrib.database.formula.ast import tree
from baserow.contrib.database.formula.types.exceptions import (
    InvalidFormulaType,
)

T = TypeVar("T", bound="BaserowFormulaType")


class BaserowFormulaType(abc.ABC):
    @property
    @abc.abstractmethod
    def type(self) -> str:
        """
        Should be a unique lowercase string used to identify this type.
        """

        pass

    @property
    @abc.abstractmethod
    def baserow_field_type(self) -> str:
        """
        The Baserow field type that corresponds to this formula type and should be
        used to do various Baserow operations for a formula field of this type.
        """

        pass

    @classproperty
    def user_overridable_formatting_option_fields(self) -> List[str]:
        """
        :return: The list of FormulaField model field names which control
        formatting for a formula field of this type and should be allowed to be
        controlled and set by a user.
        """

        return []

    @classproperty
    def internal_fields(self) -> List[str]:
        """
        :return: The list of FormulaField model field names which store internal
        information required for a formula of this type.
        """

        return []

    @classmethod
    def all_fields(cls) -> List[str]:
        """
        :returns All FormulaField model field names required for a formula field of
        this type.
        """

        return cls.user_overridable_formatting_option_fields + cls.internal_fields

    @property
    @abc.abstractmethod
    def comparable_types(self) -> List[Type["BaserowFormulaValidType"]]:
        """
        A list of valid types that this type can be compared with in a formula.
        """

        pass

    @property
    @abc.abstractmethod
    def is_valid(self) -> bool:
        pass

    def is_invalid(self) -> bool:
        return not self.is_valid

    @abc.abstractmethod
    def raise_if_invalid(self):
        pass

    @classmethod
    def all_types(cls) -> List[Type["BaserowFormulaType"]]:
        invalid_type: List[Type["BaserowFormulaType"]] = [BaserowFormulaInvalidType]
        return invalid_type + BaserowFormulaValidType.__subclasses__()

    @classmethod
    def construct_type_from_formula_field(
        cls: Type[T], formula_field: "models.FormulaField"
    ) -> T:
        """
        Creates a BaserowFormulaType instance based on what is set on the formula field.
        :param formula_field: The formula field to get type info from.
        :return: A new BaserowFormulaType.
        """

        kwargs = {}
        for field_name in cls.all_fields():
            kwargs[field_name] = getattr(formula_field, field_name)
        return cls(**kwargs)

    def new_type_with_user_and_calculated_options_merged(
        self: T, formula_field: "models.FormulaField"
    ):
        """
        Generates a new merged BaserowFormulaType instance from what has been set on the
        formula field and this instance of the type. Fields which are set on
        this types user_overridable_formatting_option_fields will be taken from the
        FormulaField instance if set there, otherwise the values from the type instance
        will be used.

        :param formula_field: The formula field to get any type option overrides set by
            the user from.
        :return: A new merged object of the formula type using values from both the
            instance and if set values also from the formula field.
        """

        kwargs = {}
        for field_name in self.user_overridable_formatting_option_fields:
            override_set_by_user = getattr(formula_field, field_name)
            if override_set_by_user is not None:
                kwargs[field_name] = override_set_by_user
            else:
                kwargs[field_name] = getattr(self, field_name)
        for field_name in self.internal_fields:
            kwargs[field_name] = getattr(self, field_name)
        return self.__class__(**kwargs)

    def persist_onto_formula_field(self, formula_field: "models.FormulaField"):
        """
        Saves this type onto the provided formula_field instance for later retrieval.
        Sets the attributes on the formula_field required
        for this formula type and unsets all other formula types attributes. Does not
        save the formula_field.

        :param formula_field: The formula field to store the type information onto.
        """

        formula_field.formula_type = self.type
        for field_name in self.user_overridable_formatting_option_fields:
            # Only set the calculated type formatting options if the user has not
            # already set them.
            if getattr(formula_field, field_name) is None:
                setattr(formula_field, field_name, getattr(self, field_name))

        for field_name in self.internal_fields:
            setattr(formula_field, field_name, getattr(self, field_name))

    def should_recreate_when_old_type_was(self, old_type: "BaserowFormulaType") -> bool:
        """
        :param old_type: The previous type of a formula field.
        :return: True if the formula field should have it's database column recreated
            given it's old_type.
        """

        return not isinstance(self, type(old_type))

    def __str__(self) -> str:
        return self.type


class BaserowFormulaInvalidType(BaserowFormulaType):
    is_valid = False
    comparable_types = []
    type = "invalid"
    baserow_field_type = "text"
    internal_fields = ["error"]

    text_default = ""

    def raise_if_invalid(self):
        raise InvalidFormulaType(self.error)

    def __init__(self, error: str):
        self.error = error


class BaserowFormulaValidType(BaserowFormulaType, abc.ABC):
    is_valid = True

    def raise_if_invalid(self):
        pass

    def cast_to_text(
        self,
        to_text_func_call: "tree.BaserowFunctionCall[UnTyped]",
        arg: "tree.BaserowExpression[BaserowFormulaValidType]",
    ) -> "tree.BaserowExpression[BaserowFormulaType]":
        """
        Given a expression which is an untyped BaserowToText function call this function
        should return an expression which results in this type being turning into a
        BaserowFormulaTextType.

        :param to_text_func_call: A BaserowToText function call expression where the
            argument is of this type and is required to be turned into a text type.
        :param arg: The typed argument that needs to be turned into a text type.
        :return: A typed BaserowExpression which results in arg turning into a text
            type.
        """

        # We default to not having to do any extra expression wrapping to convert to
        # the text type by just returning the existing to_text func call which by
        # default just does a Cast(arg, output_field=fields.TextField()).
        from baserow.contrib.database.formula.types.formula_types import (
            BaserowFormulaTextType,
        )

        return to_text_func_call.with_valid_type(BaserowFormulaTextType())


UnTyped = type(None)
BaserowListOfValidTypes = List[Type[BaserowFormulaValidType]]

BaserowSingleArgumentTypeChecker = BaserowListOfValidTypes
"""
Defines a way of checking a single provided argument has a valid type or not.
"""

BaserowArgumentTypeChecker = Union[
    Callable[[int, List[BaserowFormulaType]], BaserowListOfValidTypes],
    List[BaserowSingleArgumentTypeChecker],
]
"""
Defines a way of checking if all the arguments for a function.
Either a callable which is given the argument index to check and the list of argument
types and should return a list of valid types for that argument. Or instead can just be
a list of single arg type checkers where the Nth position in the list is the type
checker for the Nth argument.
"""
