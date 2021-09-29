import abc
from typing import Optional, Any, List, Type

from django.db import models
from django.db.models import Q, Func, F, Value
from django.db.models.functions import Coalesce
from rest_framework import serializers
from rest_framework.fields import Field

from baserow.contrib.database.fields.field_filters import contains_filter, AnnotatedQ
from baserow.contrib.database.fields.mixins import DATE_FORMAT, DATE_TIME_FORMAT
from baserow.contrib.database.formula.ast.tree import (
    BaserowExpression,
    BaserowFunctionCall,
    BaserowStringLiteral,
)
from baserow.contrib.database.formula.registries import (
    BaserowFormulaTypeTypeRegistry,
    formula_function_registry,
)
from baserow.contrib.database.formula.types.type_handler import (
    BaserowFormulaTypeType,
)
from baserow.contrib.database.formula.types.type_types import (
    BaserowFormulaInvalidType,
    BaserowFormulaValidType,
    UnTyped,
    BaserowFormulaType,
)


class BaserowFormulaTextType(BaserowFormulaValidType):
    type = "text"

    @property
    def comparable_types(self) -> List[Type["BaserowFormulaValidType"]]:
        return [
            type(self),
            BaserowFormulaDateType,
            BaserowFormulaNumberType,
            BaserowFormulaBooleanType,
        ]

    def cast_to_text(
        self,
        to_text_func_call: "BaserowFunctionCall[UnTyped]",
        arg: "BaserowExpression[BaserowFormulaValidType]",
    ) -> "BaserowExpression[BaserowFormulaType]":
        # Explicitly unwrap the func_call here and just return the arg as it is already
        # in the text type and we don't want to return to_text(arg) but instead just
        # arg.
        return arg

    def contains_query(self, *args):
        return contains_filter(*args)

    def get_model_field(self, **kwargs) -> models.Field:
        return models.TextField(default=None, blank=True, null=True, **kwargs)

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


class BaserowFormulaCharType(BaserowFormulaTextType):
    type = "char"

    def cast_to_text(
        self,
        to_text_func_call: "BaserowFunctionCall[UnTyped]",
        arg: "BaserowExpression[BaserowFormulaValidType]",
    ) -> "BaserowExpression[BaserowFormulaType]":
        # Force char fields to be casted to text so Django does not complain
        return to_text_func_call.with_valid_type(BaserowFormulaTextType())


class BaserowFormulaNumberType(BaserowFormulaValidType):
    type = "number"
    MAX_DIGITS = 50

    def __init__(self, number_decimal_places: int):
        self.number_decimal_places = number_decimal_places

    @property
    def comparable_types(self) -> List[Type["BaserowFormulaValidType"]]:
        return [
            type(self),
            BaserowFormulaTextType,
        ]

    def contains_query(self, *args):
        return contains_filter(*args)

    def get_export_value(self, value) -> Any:
        if value is None:
            return value

        # If the number is an integer we want it to be a literal json number and so
        # don't convert it to a string. However if a decimal to preserve any precision
        # we keep it as a string.
        if self.number_decimal_places == 0:
            return int(value)

        # DRF's Decimal Serializer knows how to quantize and format the decimal
        # correctly so lets use it instead of trying to do it ourselves.
        return self.get_serializer_field().to_representation(value)

    def get_model_field(self, **kwargs) -> models.Field:
        return models.DecimalField(
            max_digits=self.MAX_DIGITS + self.number_decimal_places,
            decimal_places=self.number_decimal_places,
            null=True,
            blank=True,
            **kwargs,
        )

    def get_serializer_field(self, **kwargs) -> Optional[Field]:
        required = kwargs.get("required", False)

        return serializers.DecimalField(
            **{
                "max_digits": self.MAX_DIGITS + self.number_decimal_places,
                "decimal_places": self.number_decimal_places,
                "required": required,
                "allow_null": not required,
                **kwargs,
            }
        )

    def should_recreate_when_old_type_was(self, old_type: "BaserowFormulaType") -> bool:
        if isinstance(old_type, BaserowFormulaNumberType):
            return self.number_decimal_places != old_type.number_decimal_places
        else:
            return True

    def __str__(self) -> str:
        return f"number({self.number_decimal_places})"


class BaserowFormulaBooleanType(BaserowFormulaValidType):
    type = "boolean"

    @property
    def comparable_types(self) -> List[Type["BaserowFormulaValidType"]]:
        return [
            type(self),
            BaserowFormulaTextType,
        ]

    def get_model_field(self, **kwargs) -> models.Field:
        return models.BooleanField(default=False, **kwargs)

    def get_serializer_field(self, **kwargs) -> Optional[Field]:
        return serializers.BooleanField(
            **{"required": False, "default": False, **kwargs}
        )


class BaserowFormulaDateType(BaserowFormulaValidType):
    type = "date"

    def __init__(
        self, date_format: str, date_include_time: bool, date_time_format: str
    ):
        self.date_format = date_format
        self.date_include_time = date_include_time
        self.date_time_format = date_time_format

    @property
    def comparable_types(self) -> List[Type["BaserowFormulaValidType"]]:
        return [
            type(self),
            BaserowFormulaTextType,
        ]

    def should_recreate_when_old_type_was(self, old_type: "BaserowFormulaType") -> bool:
        if isinstance(old_type, BaserowFormulaDateType):
            return self.date_include_time != old_type.date_include_time
        else:
            return True

    def cast_to_text(
        self,
        to_text_func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaValidType]:
        return BaserowFunctionCall[BaserowFormulaValidType](
            formula_function_registry.get("datetime_format"),
            [
                arg,
                BaserowStringLiteral(self.get_psql_format(), BaserowFormulaTextType()),
            ],
            BaserowFormulaTextType(),
        )

    def get_alter_column_prepare_old_value(self):
        """
        If the field type has changed then we want to convert the date or timestamp to
        a human readable text following the old date format.
        """

        sql_format = self.get_psql_format()
        sql_type = self.get_psql_type()
        return f"""p_in = TO_CHAR(p_in::{sql_type}, '{sql_format}');"""

    def contains_query(self, field_name, value, model_field, field):
        value = value.strip()
        # If an empty value has been provided we do not want to filter at all.
        if value == "":
            return Q()
        return AnnotatedQ(
            annotation={
                f"formatted_date_{field_name}": Coalesce(
                    Func(
                        F(field_name),
                        Value(self.get_psql_format()),
                        function="to_char",
                        output_field=models.CharField(),
                    ),
                    Value(""),
                )
            },
            q={f"formatted_date_{field_name}__icontains": value},
        )

    def get_python_format(self):
        """
        Returns the strftime format as a string based on the field's properties. This
        could for example be '%Y-%m-%d %H:%I'.

        :return: The strftime format based on the field's properties.
        :rtype: str
        """

        return self._get_format("format")

    def get_psql_format(self):
        """
        Returns the sql datetime format as a string based on the field's properties.
        This could for example be 'YYYY-MM-DD HH12:MIAM'.

        :return: The sql datetime format based on the field's properties.
        :rtype: str
        """

        return self._get_format("sql")

    def get_psql_type(self):
        """
        Returns the postgresql column type used by this field depending on if it is a
        date or datetime.

        :return: The postgresql column type either 'timestamp' or 'date'
        :rtype: str
        """

        return "timestamp" if self.date_include_time else "date"

    def _get_format(self, format_type):
        date_format = DATE_FORMAT[self.date_format][format_type]
        time_format = DATE_TIME_FORMAT[self.date_time_format][format_type]
        if self.date_include_time:
            return f"{date_format} {time_format}"
        else:
            return date_format

    def get_export_value(self, value) -> Any:
        if value is None:
            return value
        python_format = self.get_python_format()
        return value.strftime(python_format)

    def get_model_field(self, **kwargs) -> models.Field:
        kwargs["null"] = True
        kwargs["blank"] = True
        if self.date_include_time:
            return models.DateTimeField(**kwargs)
        else:
            return models.DateField(**kwargs)

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

    def __str__(self) -> str:
        date_or_datetime = "datetime" if self.date_include_time else "date"
        optional_time_format = (
            f", {self.date_time_format}" if self.date_include_time else ""
        )
        return f"{date_or_datetime}({self.date_format}{optional_time_format})"


class BaserowFormulaInvalidTypeType(BaserowFormulaTypeType[BaserowFormulaInvalidType]):
    cls = BaserowFormulaInvalidType
    internal_fields = ["error"]


class ValidBaserowFormulaTypeType(BaserowFormulaTypeType, abc.ABC):
    pass


class BaserowTextFormulaTypeType(ValidBaserowFormulaTypeType):
    cls = BaserowFormulaTextType


class BaserowCharFormulaTypeType(ValidBaserowFormulaTypeType):
    cls = BaserowFormulaCharType


class BaserowBooleanFormulaTypeType(ValidBaserowFormulaTypeType):
    cls = BaserowFormulaBooleanType


class BaserowDateFormulaTypeType(ValidBaserowFormulaTypeType):
    user_overridable_formatting_option_fields = [
        "date_format",
        "date_include_time",
        "date_time_format",
    ]
    cls = BaserowFormulaDateType


class BaserowNumberFormulaTypeType(ValidBaserowFormulaTypeType):
    user_overridable_formatting_option_fields = ["number_decimal_places"]
    cls = BaserowFormulaNumberType


BASEROW_FORMULA_TYPE_TYPES = [
    BaserowFormulaInvalidTypeType(),
    BaserowTextFormulaTypeType(),
    BaserowBooleanFormulaTypeType(),
    BaserowDateFormulaTypeType(),
    BaserowNumberFormulaTypeType(),
    BaserowCharFormulaTypeType(),
]

BASEROW_FORMULA_TYPE_ALLOWED_FIELDS = [
    name for h in BASEROW_FORMULA_TYPE_TYPES for name in h.all_fields()
]


def register_formula_type_types(registry: BaserowFormulaTypeTypeRegistry):
    for formula_type in BASEROW_FORMULA_TYPE_TYPES:
        registry.register(formula_type)
