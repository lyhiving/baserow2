from typing import List, Type

from baserow.contrib.database.fields.mixins import (
    get_date_time_format,
)
from baserow.contrib.database.fields import models
from baserow.contrib.database.formula.ast.tree import (
    BaserowExpression,
    BaserowFunctionCall,
    BaserowStringLiteral,
)
from baserow.contrib.database.formula.registries import (
    formula_function_registry,
)
from baserow.contrib.database.formula.types.exceptions import UnknownFormulaType
from baserow.contrib.database.formula.types.formula_type import (
    BaserowFormulaValidType,
    UnTyped,
    BaserowFormulaType,
)


class BaserowFormulaTextType(BaserowFormulaValidType):
    type = "text"
    baserow_field_type = "text"

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


class BaserowFormulaCharType(BaserowFormulaTextType):
    type = "char"
    baserow_field_type = "text"

    def cast_to_text(
        self,
        to_text_func_call: "BaserowFunctionCall[UnTyped]",
        arg: "BaserowExpression[BaserowFormulaValidType]",
    ) -> "BaserowExpression[BaserowFormulaType]":
        # Force char fields to be casted to text so Django does not complain
        return to_text_func_call.with_valid_type(BaserowFormulaTextType())


class BaserowFormulaNumberType(BaserowFormulaValidType):
    type = "number"
    baserow_field_type = "number"
    user_overridable_formatting_option_fields = ["number_decimal_places"]

    def __init__(self, number_decimal_places: int):
        self.number_decimal_places = number_decimal_places

    @property
    def comparable_types(self) -> List[Type["BaserowFormulaValidType"]]:
        return [
            type(self),
            BaserowFormulaTextType,
        ]

    def should_recreate_when_old_type_was(self, old_type: "BaserowFormulaType") -> bool:
        if isinstance(old_type, BaserowFormulaNumberType):
            return self.number_decimal_places != old_type.number_decimal_places
        else:
            return True

    def __str__(self) -> str:
        return f"number({self.number_decimal_places})"


class BaserowFormulaBooleanType(BaserowFormulaValidType):
    type = "boolean"
    baserow_field_type = "boolean"

    @property
    def comparable_types(self) -> List[Type["BaserowFormulaValidType"]]:
        return [
            type(self),
            BaserowFormulaTextType,
        ]


class BaserowFormulaDateType(BaserowFormulaValidType):
    type = "date"
    baserow_field_type = "date"
    user_overridable_formatting_option_fields = [
        "date_format",
        "date_include_time",
        "date_time_format",
    ]

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
                BaserowStringLiteral(
                    get_date_time_format(self, "sql"), BaserowFormulaTextType()
                ),
            ],
            BaserowFormulaTextType(),
        )

    def __str__(self) -> str:
        date_or_datetime = "datetime" if self.date_include_time else "date"
        optional_time_format = (
            f", {self.date_time_format}" if self.date_include_time else ""
        )
        return f"{date_or_datetime}({self.date_format}{optional_time_format})"


def construct_type_from_formula_field(
    formula_field: "models.FormulaField",
) -> BaserowFormulaType:
    """
    Gets the BaserowFormulaType the provided formula field currently has. This will
    vary depending on the formula of the field.

    :param formula_field: An instance of a formula field.
    :return: The BaserowFormulaType of the formula field instance.
    """

    for formula_type in BaserowFormulaType.all_types():
        if formula_field.formula_type == formula_type.type:
            return formula_type.construct_type_from_formula_field(formula_field)
    raise UnknownFormulaType(formula_field.formula_type)


BASEROW_FORMULA_TYPE_ALLOWED_FIELDS = [
    allowed_field
    for f in BaserowFormulaType.all_types()
    for allowed_field in f.all_fields()
]

BASEROW_FORMULA_TYPE_CHOICES = [
    (f.type, f.type) for f in BaserowFormulaType.all_types()
]
