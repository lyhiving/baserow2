from decimal import Decimal
from typing import List

from django.db.models import (
    Expression,
    Value,
    Case,
    When,
    fields,
    Func,
)
from django.db.models.functions import (
    Upper,
    Lower,
    Concat,
    Coalesce,
    Cast,
    Greatest,
)

from baserow.contrib.database.fields.models import (
    NUMBER_MAX_DECIMAL_PLACES,
)
from baserow.contrib.database.formula.ast.function import (
    BaserowFunctionDefinition,
    NumOfArgsGreaterThan,
    OneArgumentBaserowFunction,
    TwoArgumentBaserowFunction,
    ThreeArgumentBaserowFunction,
)
from baserow.contrib.database.formula.ast.tree import (
    BaserowFunctionCall,
    BaserowExpression,
)
from baserow.contrib.database.formula.expression_generator.django_expressions import (
    EqualsExpr,
    NotExpr,
    NotEqualsExpr,
)
from baserow.contrib.database.formula.types.type_defs import (
    BaserowFormulaTextType,
    BaserowFormulaDateType,
    BaserowFormulaNumberType,
    BaserowFormulaBooleanType,
)
from baserow.contrib.database.formula.types.type_types import (
    BaserowFormulaType,
    BaserowFormulaValidType,
    UnTyped,
    BaserowArgumentTypeChecker,
)


def register_formula_functions(registry):
    # Text functions
    registry.register(BaserowUpper())
    registry.register(BaserowLower())
    registry.register(BaserowConcat())
    registry.register(BaserowToText())
    registry.register(BaserowT())
    # Number functions
    registry.register(BaserowAdd())
    registry.register(BaserowMultiply())
    registry.register(BaserowMinus())
    registry.register(BaserowDivide())
    registry.register(BaserowToNumber())
    # Boolean functions
    registry.register(BaserowIf())
    registry.register(BaserowEqual())
    registry.register(BaserowIsBlank())
    registry.register(BaserowNot())
    registry.register(BaserowNotEqual())
    # Date functions
    registry.register(BaserowDatetimeFormat())


class BaserowUpper(OneArgumentBaserowFunction):

    type = "upper"
    arg_type = [BaserowFormulaTextType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return func_call.with_valid_type(BaserowFormulaTextType())

    def to_django_expression(self, arg: Expression) -> Expression:
        return Upper(arg)


class BaserowLower(OneArgumentBaserowFunction):
    type = "lower"
    arg_type = [BaserowFormulaTextType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return func_call.with_valid_type(BaserowFormulaTextType())

    def to_django_expression(self, arg: Expression) -> Expression:
        return Lower(arg)


class BaserowDatetimeFormat(TwoArgumentBaserowFunction):
    type = "datetime_format"
    arg1_type = [BaserowFormulaDateType]
    arg2_type = [BaserowFormulaTextType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return func_call.with_valid_type(BaserowFormulaTextType())

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        if isinstance(arg1, Value) and arg1.value is None:
            return Value("")
        return Coalesce(
            Func(
                arg1,
                arg2,
                function="to_char",
                output_field=fields.TextField(),
            ),
            Value(""),
        )


class BaserowToText(OneArgumentBaserowFunction):
    type = "totext"
    arg_type = [BaserowFormulaValidType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return arg.expression_type.cast_to_text(func_call, arg)

    def to_django_expression(self, arg: Expression) -> Expression:
        return Cast(arg, output_field=fields.TextField())


class BaserowT(OneArgumentBaserowFunction):
    type = "t"
    arg_type = [BaserowFormulaValidType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        if isinstance(arg.expression_type, BaserowFormulaTextType):
            return arg
        else:
            return func_call.with_valid_type(BaserowFormulaTextType())

    def to_django_expression(self, arg: Expression) -> Expression:
        return Value("")


class BaserowConcat(BaserowFunctionDefinition):
    type = "concat"
    num_args = NumOfArgsGreaterThan(1)

    @property
    def arg_types(self) -> BaserowArgumentTypeChecker:
        return lambda _, _2: [BaserowFormulaValidType]

    def type_function_given_valid_args(
        self,
        args: List[BaserowExpression[BaserowFormulaValidType]],
        expression: "BaserowFunctionCall[UnTyped]",
    ) -> BaserowExpression[BaserowFormulaType]:
        return expression.with_args(
            [BaserowToText().call_and_type_with(a) for a in args]
        ).with_valid_type(BaserowFormulaTextType())

    def to_django_expression_given_args(self, args: List[Expression]) -> Expression:
        return Concat(*args, output_field=fields.TextField())


def _calculate_number_type(
    arg_types: List[BaserowFormulaNumberType], min_decimal_places=0
):
    max_number_decimal_places = min_decimal_places
    for a in arg_types:
        max_number_decimal_places = max(
            max_number_decimal_places, a.number_decimal_places
        )

    return BaserowFormulaNumberType(
        number_decimal_places=max_number_decimal_places,
    )


class BaserowAdd(TwoArgumentBaserowFunction):
    type = "add"
    arg1_type = [BaserowFormulaNumberType]
    arg2_type = [BaserowFormulaNumberType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaNumberType],
        arg2: BaserowExpression[BaserowFormulaNumberType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return func_call.with_valid_type(
            _calculate_number_type([arg1.expression_type, arg2.expression_type])
        )

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        return arg1 + arg2


class BaserowMultiply(TwoArgumentBaserowFunction):
    type = "multiply"
    arg1_type = [BaserowFormulaNumberType]
    arg2_type = [BaserowFormulaNumberType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaNumberType],
        arg2: BaserowExpression[BaserowFormulaNumberType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return func_call.with_valid_type(
            _calculate_number_type([arg1.expression_type, arg2.expression_type])
        )

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        return arg1 * arg2


class BaserowMinus(TwoArgumentBaserowFunction):
    type = "minus"
    arg1_type = [BaserowFormulaNumberType]
    arg2_type = [BaserowFormulaNumberType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaNumberType],
        arg2: BaserowExpression[BaserowFormulaNumberType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return func_call.with_valid_type(
            _calculate_number_type([arg1.expression_type, arg2.expression_type])
        )

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        return arg1 - arg2


class BaserowMax(TwoArgumentBaserowFunction):
    type = "max"
    arg1_type = [BaserowFormulaNumberType]
    arg2_type = [BaserowFormulaNumberType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaNumberType],
        arg2: BaserowExpression[BaserowFormulaNumberType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return func_call.with_valid_type(
            _calculate_number_type([arg1.expression_type, arg2.expression_type])
        )

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        return Greatest(arg1, arg2)


class BaserowDivide(TwoArgumentBaserowFunction):
    type = "divide"

    arg1_type = [BaserowFormulaNumberType]
    arg2_type = [BaserowFormulaNumberType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaNumberType],
        arg2: BaserowExpression[BaserowFormulaNumberType],
    ) -> BaserowExpression[BaserowFormulaType]:
        # Show all the decimal places we can by default if the user makes a formula
        # with a division to prevent weird results like `1/3=0`
        return func_call.with_valid_type(
            BaserowFormulaNumberType(NUMBER_MAX_DECIMAL_PLACES)
        )

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        # Prevent divide by zero's by swapping 0 for NaN causing the entire expression
        # to evaluate to NaN. The front-end then treats NaN values as a per cell error
        # to display to the user.
        return arg1 / Case(
            When(
                condition=(EqualsExpr(arg2, 0, output_field=fields.BooleanField())),
                then=Value(Decimal("NaN")),
            ),
            default=arg2,
        )


class BaserowEqual(TwoArgumentBaserowFunction):
    type = "equal"

    @property
    def arg_types(self) -> BaserowArgumentTypeChecker:
        def type_checker(arg_index: int, arg_types: List[BaserowFormulaType]):
            # The valid types for arg1 are the comparable types for arg2 and vice versa.
            # For example, if arg1 is a boolean then arg2 must be of type text or
            # boolean for the two arguments to be comparable.
            other_arg_index = 1 if arg_index == 0 else 1
            return arg_types[other_arg_index].comparable_types

        return type_checker

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        arg1_type = arg1.expression_type
        arg2_type = arg2.expression_type
        if not (type(arg1_type) is type(arg2_type)):
            # If trying to compare two types which can be compared, but are of different
            # types, then first cast them to text and then compare.
            # We to ourselves via the __class__ property here so subtypes of this type
            # use themselves here instead of us!
            return self.__class__().call_and_type_with(
                BaserowToText().call_and_type_with(arg1),
                BaserowToText().call_and_type_with(arg2),
            )
        else:
            return func_call.with_valid_type(BaserowFormulaBooleanType())

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        return EqualsExpr(
            arg1,
            arg2,
            output_field=fields.BooleanField(),
        )


class BaserowIf(ThreeArgumentBaserowFunction):
    type = "if"

    arg1_type = [BaserowFormulaBooleanType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
        arg3: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        arg2_type = arg2.expression_type
        arg3_type = arg3.expression_type
        if not (type(arg2_type) is type(arg3_type)):
            # Replace the current if func_call with one which casts both args to text
            # if they are of different types as PostgreSQL requires all cases of a case
            # statement to be of the same type.
            return BaserowIf().call_and_type_with(
                arg1,
                BaserowToText().call_and_type_with(arg2),
                BaserowToText().call_and_type_with(arg3),
            )
        else:
            if isinstance(arg2_type, BaserowFormulaNumberType) and isinstance(
                arg3_type, BaserowFormulaNumberType
            ):
                resulting_type = _calculate_number_type([arg2_type, arg3_type])
            else:
                resulting_type = arg2_type

            return func_call.with_valid_type(resulting_type)

    def to_django_expression(
        self, arg1: Expression, arg2: Expression, arg3: Expression
    ) -> Expression:
        return Case(When(condition=arg1, then=arg2), default=arg3)


class BaserowToNumber(OneArgumentBaserowFunction):
    type = "tonumber"
    arg_type = [BaserowFormulaTextType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return func_call.with_valid_type(
            BaserowFormulaNumberType(number_decimal_places=5)
        )

    def to_django_expression(self, arg: Expression) -> Expression:
        return Func(
            arg,
            function="try_cast_to_numeric",
            output_field=fields.DecimalField(),
        )


class BaserowIsBlank(OneArgumentBaserowFunction):
    type = "isblank"
    arg_type = [BaserowFormulaValidType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return func_call.with_args(
            [BaserowToText().call_and_type_with(arg)]
        ).with_valid_type(BaserowFormulaBooleanType())

    def to_django_expression(self, arg: Expression) -> Expression:
        return EqualsExpr(
            Coalesce(
                arg,
                Value(""),
            ),
            Value(""),
            output_field=fields.BooleanField(),
        )


class BaserowNot(OneArgumentBaserowFunction):
    type = "not"
    arg_type = [BaserowFormulaBooleanType]

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaBooleanType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return func_call.with_valid_type(BaserowFormulaBooleanType())

    def to_django_expression(self, arg: Expression) -> Expression:
        return NotExpr(arg)


class BaserowNotEqual(BaserowEqual):
    type = "not_equal"

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        return NotEqualsExpr(
            arg1,
            arg2,
            output_field=fields.BooleanField(),
        )
