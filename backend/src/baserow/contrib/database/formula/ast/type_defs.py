import abc
from typing import Optional

from rest_framework import serializers
from rest_framework.fields import Field

from baserow.contrib.database.fields.field_types import NumberFieldType
from baserow.contrib.database.fields.models import NUMBER_TYPE_INTEGER
from baserow.contrib.database.formula.ast.type_types import BaserowFormulaTypeHandler
from baserow.contrib.database.formula.registries import (
    BaserowFormulaTypeHandlerRegistry,
)


class BaserowFormulaType(abc.ABC):
    @abc.abstractmethod
    def get_serializer_field(self, **kwargs) -> Optional[Field]:
        """
        Should return a serializer field which serializes a single row's value for a
        formula field of this type. If None is returned then nothing we be serialized
        for this row.

        :param kwargs: The kwargs that will be passed to the field.
        :return: The serializer field that represents a cell in this formula type.
        """


class BaserowFormulaInvalidType(BaserowFormulaType):
    def get_serializer_field(self, **kwargs) -> Optional[Field]:
        return None

    def __init__(self, error: str):
        self.error = error


class BaserowValidFormulaType(BaserowFormulaType, abc.ABC):
    pass


class BaserowFormulaTextType(BaserowValidFormulaType):
    def get_serializer_field(self, **kwargs) -> Optional[Field]:
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


class BaserowFormulaBooleanType(BaserowValidFormulaType):
    def get_serializer_field(self, **kwargs) -> Optional[Field]:
        return serializers.BooleanField(
            **{"required": False, "default": False, **kwargs}
        )


class BaserowFormulaDateType(BaserowValidFormulaType):
    def get_serializer_field(self, **kwargs) -> Optional[Field]:
        required = kwargs.get("required", False)

        if self.date_include_time:
            return serializers.DateTimeField(
                **{"required": required, "allow_null": not required, **kwargs}
            )
        else:
            return serializers.DateField(
                **{"required": required, "allow_null": not required, **kwargs}
            )

    def __init__(
        self, date_format: str, date_include_time: bool, date_time_format: str
    ):
        self.date_format = date_format
        self.date_include_time = date_include_time
        self.date_include_time = date_time_format


class BaserowFormulaNumberType(BaserowValidFormulaType):
    def get_serializer_field(self, **kwargs) -> Optional[Field]:
        required = kwargs.get("required", False)

        kwargs["decimal_places"] = (
            0 if self.number_type == NUMBER_TYPE_INTEGER else self.number_decimal_places
        )

        return serializers.DecimalField(
            **{
                "max_digits": NumberFieldType.MAX_DIGITS + kwargs["decimal_places"],
                "required": required,
                "allow_null": not required,
                **kwargs,
            }
        )

    def __init__(self, number_type: str, number_decimal_places: int):
        self.number_type = number_type
        self.number_decimal_places = number_decimal_places


class BaserowFormulaInvalidTypeHandler(
    BaserowFormulaTypeHandler[BaserowFormulaInvalidType]
):
    type = "invalid"
    model_class = BaserowFormulaInvalidType
    allowed_fields = ["error"]


class ValidBaserowFormulaTypeHandler(BaserowFormulaTypeHandler, abc.ABC):
    pass


class BaserowTextFormulaTypeHandler(ValidBaserowFormulaTypeHandler):
    type = "text"
    allowed_fields = []
    model_class = BaserowFormulaTextType


class BaserowBooleanFormulaTypeHandler(ValidBaserowFormulaTypeHandler):
    type = "boolean"
    allowed_fields = []
    model_class = BaserowFormulaBooleanType


class BaserowDateFormulaTypeHandler(ValidBaserowFormulaTypeHandler):
    type = "date"
    allowed_fields = ["date_format", "date_include_time", "date_time_format"]
    model_class = BaserowFormulaDateType


class BaserowNumericFormulaTypeHandler(ValidBaserowFormulaTypeHandler):
    type = "number"
    allowed_fields = ["number_type", "number_decimal_places"]
    model_class = BaserowFormulaNumberType


BASEROW_FORMULA_TYPES = [
    BaserowFormulaInvalidTypeHandler(),
    BaserowTextFormulaTypeHandler(),
    BaserowBooleanFormulaTypeHandler(),
    BaserowDateFormulaTypeHandler(),
    BaserowNumericFormulaTypeHandler(),
]


def register_formula_types(registry: BaserowFormulaTypeHandlerRegistry):
    for formula_type in BASEROW_FORMULA_TYPES:
        registry.register(formula_type)
