import abc
from typing import (
    Optional,
    Any,
    List,
    Type,
    Union,
    Callable,
)

from django.db import models
from django.db.models import Q
from rest_framework import serializers

from baserow.contrib.database.formula.ast import tree
from baserow.contrib.database.formula.types.errors import (
    InvalidFormulaType,
)


class BaserowFormulaType(abc.ABC):
    @property
    @abc.abstractmethod
    def type(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def comparable_types(self) -> List[Type["BaserowFormulaValidType"]]:
        pass

    @property
    @abc.abstractmethod
    def is_valid(self) -> bool:
        pass

    def is_invalid(self) -> bool:
        return not self.is_valid

    @abc.abstractmethod
    def get_serializer_field(self, **kwargs) -> Optional[serializers.Field]:
        """
        Should return a serializer field which serializes a single row's value for a
        formula field of this type. If None is returned then nothing we be serialized
        for this row.

        :param kwargs: The kwargs that will be passed to the field.
        :return: The serializer field that represents a cell in this formula type.
        """

        pass

    @abc.abstractmethod
    def get_model_field(self, **kwargs) -> models.Field:
        """
        Should return the django model field which can be used to represent this formula
        type in a Baserow table.

        :param kwargs: The kwargs that will be passed to the field.
        :return: The model field that represents this formula type on a table.
        """

        pass

    def get_export_value(self, value) -> Any:
        """
        Should convert this formula type's internal baserow value to a form suitable
        for exporting to a standalone file.

        :param value: The internal value to convert to a suitable export format
        :return: A value suitable to be serialized and stored in a file format for
            users.
        """

        return value

    def contains_query(self, field_name, value, model_field, field):
        """
        Returns a Q or AnnotatedQ filter which performs a contains filter over the a
        formula field for this specific type of formula.

        :param field_name: The name of the formula field being filtered.
        :type field_name: str
        :param value: The value to check if this formula field contains or not.
        :type value: str
        :param model_field: The field's actual django field model instance.
        :type model_field: models.Field
        :param field: The related field's instance.
        :type field: Field
        :return: A Q or AnnotatedQ filter.
            given value.
        :rtype: OptionallyAnnotatedQ
        """

        return Q()

    def get_alter_column_prepare_old_value(self):
        """
        Can return an SQL statement to convert the `p_in` variable to a readable text
        format for the new field.
        This SQL will not be run when converting between two fields of the same
        baserow type which share the same underlying database column type.
        If you require this then implement force_same_type_alter_column.

        Example: return "p_in = lower(p_in);"

        :return: The SQL statement converting the value to text for the next field. The
            can for example be used to convert a select option to plain text.
        :rtype: None or str
        """

        return None

    def __str__(self) -> str:
        return self.type

    def should_recreate_when_old_type_was(self, old_type: "BaserowFormulaType") -> bool:
        return not isinstance(self, type(old_type))

    @abc.abstractmethod
    def raise_if_invalid(self):
        pass


class BaserowFormulaInvalidType(BaserowFormulaType):
    is_valid = False
    comparable_types = []
    type = "invalid"

    def raise_if_invalid(self):
        raise InvalidFormulaType(self.error)

    def get_export_value(self, value) -> Any:
        return None

    def __init__(self, error: str):
        self.error = error

    def get_model_field(self, **kwargs) -> models.Field:
        return models.CharField(
            default=None,
            blank=True,
            null=True,
            **kwargs,
        )

    def get_serializer_field(self, **kwargs) -> Optional[serializers.Field]:
        required = kwargs.get("required", False)
        return serializers.CharField(
            **{
                "required": required,
                "allow_null": not required,
                "allow_blank": not required,
                "default": None,
                **kwargs,
            }
        )

    def should_recreate_when_old_type_was(self, old_type: "BaserowFormulaType") -> bool:
        return False


class BaserowFormulaValidType(BaserowFormulaType, abc.ABC):
    is_valid = True

    def raise_if_invalid(self):
        pass

    def cast_to_text(
        self,
        func_call: "tree.BaserowFunctionCall[UnTyped]",
        arg: "tree.BaserowExpression[BaserowFormulaValidType]",
    ) -> "tree.BaserowExpression[BaserowFormulaType]":
        # We default to not having to do any extra expression wrapping to convert to
        # the text type by just returning the existing to_text func call which by
        # default just does a Cast(arg, output_field=fields.TextField()).
        from baserow.contrib.database.formula.types.type_defs import (
            BaserowFormulaTextType,
        )

        return func_call.with_valid_type(BaserowFormulaTextType())


UnTyped = type(None)
InvalidType = BaserowFormulaInvalidType
ValidType = BaserowFormulaValidType
Typed = BaserowFormulaType
BaserowListOfValidTypes = List[Type[BaserowFormulaValidType]]
BaserowSingleArgumentTypeChecker = Union[
    Callable[[BaserowFormulaValidType], BaserowListOfValidTypes],
    BaserowListOfValidTypes,
]
BaserowArgumentTypeChecker = Union[
    Callable[[int, List[BaserowFormulaType]], BaserowListOfValidTypes],
    List[BaserowSingleArgumentTypeChecker],
]
