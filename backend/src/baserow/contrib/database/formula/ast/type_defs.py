import abc
from typing import Optional, Any

from django.db import models
from django.db.models import Q, Func, F, Value
from django.db.models.functions import Coalesce
from rest_framework import serializers
from rest_framework.fields import Field, CharField

from baserow.contrib.database.fields.field_filters import contains_filter, AnnotatedQ
from baserow.contrib.database.fields.mixins import DATE_FORMAT, DATE_TIME_FORMAT
from baserow.contrib.database.formula.ast.type_handler import BaserowFormulaTypeHandler
from baserow.contrib.database.formula.registries import (
    BaserowFormulaTypeHandlerRegistry,
)


class BaserowFormulaType(abc.ABC):
    @property
    @abc.abstractmethod
    def is_valid(self) -> bool:
        pass

    def is_invalid(self) -> bool:
        return not self.is_valid

    @abc.abstractmethod
    def get_serializer_field(self, **kwargs) -> Optional[Field]:
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

    def contains_query(self, field_name, value):
        """
        Returns a Q or AnnotatedQ filter which performs a contains filter over the a
        formula field for this specific type of formula.

        :param field_name: The name of the formula field being filtered.
        :type field_name: str
        :param value: The value to check if this formula field contains or not.
        :type value: str
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


class BaserowFormulaInvalidType(BaserowFormulaType):
    is_valid = False

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

    def get_serializer_field(self, **kwargs) -> Optional[Field]:
        return None


class BaserowFormulaValidType(BaserowFormulaType, abc.ABC):
    is_valid = True


class BaserowFormulaTextType(BaserowFormulaValidType):
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


class BaserowFormulaNumberType(BaserowFormulaValidType):
    MAX_DIGITS = 50

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
            max_digits=self.MAX_DIGITS + kwargs["decimal_places"],
            null=True,
            blank=True,
            **kwargs,
        )

    def get_serializer_field(self, **kwargs) -> Optional[Field]:
        required = kwargs.get("required", False)

        return serializers.DecimalField(
            **{
                "max_digits": self.MAX_DIGITS + kwargs["decimal_places"],
                "required": required,
                "allow_null": not required,
                **kwargs,
            }
        )

    def __init__(self, number_decimal_places: int):
        self.number_decimal_places = number_decimal_places


class BaserowFormulaBooleanType(BaserowFormulaValidType):
    def get_model_field(self, **kwargs) -> models.Field:
        return models.BooleanField(default=False, **kwargs)

    def get_serializer_field(self, **kwargs) -> Optional[Field]:
        return serializers.BooleanField(
            **{"required": False, "default": False, **kwargs}
        )


class BaserowFormulaDateType(BaserowFormulaValidType):
    def get_alter_column_prepare_old_value(self):
        """
        If the field type has changed then we want to convert the date or timestamp to
        a human readable text following the old date format.
        """

        sql_format = self.get_psql_format()
        sql_type = self.get_psql_type()
        return f"""p_in = TO_CHAR(p_in::{sql_type}, '{sql_format}');"""

    def contains_query(self, field_name, value):
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
                        output_field=CharField(),
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

    def __init__(
        self, date_format: str, date_include_time: bool, date_time_format: str
    ):
        self.date_format = date_format
        self.date_include_time = date_include_time
        self.date_time_format = date_time_format


class BaserowFormulaInvalidTypeHandler(
    BaserowFormulaTypeHandler[BaserowFormulaInvalidType]
):
    type = "invalid"
    model_class = BaserowFormulaInvalidType
    internal_fields = ["error"]


class ValidBaserowFormulaTypeHandler(BaserowFormulaTypeHandler, abc.ABC):
    pass


class BaserowTextFormulaTypeHandler(ValidBaserowFormulaTypeHandler):
    type = "text"
    model_class = BaserowFormulaTextType


class BaserowBooleanFormulaTypeHandler(ValidBaserowFormulaTypeHandler):
    type = "boolean"
    model_class = BaserowFormulaBooleanType


class BaserowDateFormulaTypeHandler(ValidBaserowFormulaTypeHandler):
    type = "date"
    user_overridable_formatting_option_fields = [
        "date_format",
        "date_include_time",
        "date_time_format",
    ]
    model_class = BaserowFormulaDateType


class BaserowNumericFormulaTypeHandler(ValidBaserowFormulaTypeHandler):
    type = "number"
    user_overridable_formatting_option_fields = ["number_type", "number_decimal_places"]
    model_class = BaserowFormulaNumberType


BASEROW_FORMULA_TYPE_HANDLER = [
    BaserowFormulaInvalidTypeHandler(),
    BaserowTextFormulaTypeHandler(),
    BaserowBooleanFormulaTypeHandler(),
    BaserowDateFormulaTypeHandler(),
    BaserowNumericFormulaTypeHandler(),
]


def register_formula_types(registry: BaserowFormulaTypeHandlerRegistry):
    for formula_type in BASEROW_FORMULA_TYPE_HANDLER:
        registry.register(formula_type)


UnTyped = type(None)

InvalidType = BaserowFormulaInvalidType
ValidType = BaserowFormulaValidType
Typed = BaserowFormulaType
