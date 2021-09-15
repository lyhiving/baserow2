from decimal import Decimal
from typing import Type, List, Dict

from django.db.models import (
    Expression,
    Value,
    Transform,
    Case,
    When,
    fields,
    Func,
)
from django.db.models.functions import Upper, Lower, Concat, Coalesce, Cast, Greatest

from baserow.contrib.database.fields.models import (
    DateField,
    TextField,
    NumberField,
    NUMBER_TYPE_INTEGER,
    NUMBER_TYPE_DECIMAL,
    NUMBER_MAX_DECIMAL_PLACES,
    BooleanField,
)
from baserow.contrib.database.formula.ast.function import (
    BaserowFunctionDefinition,
    ArgCountSpecifier,
    NumOfArgsGreaterThan,
    FixedNumOfArgs,
    OneArgumentBaserowFunction,
    TwoArgumentBaserowFunction,
    check_arg_type,
    check_types,
)
from baserow.contrib.database.formula.ast.tree import (
    BaserowFunctionCall,
    BaserowExpression,
    BaserowArgumentTypeChecker,
)
from baserow.contrib.database.formula.ast.type_defs import (
    BaserowFormulaTextType,
    BaserowFormulaDateType,
    BaserowFormulaNumberType,
    BaserowFormulaBooleanType,
)
from baserow.contrib.database.formula.ast.type_types import (
    BaserowFormulaType,
    BaserowFormulaValidType,
    UnTyped,
)


def register_formula_functions(registry):
    registry.register(BaserowUpper())
    registry.register(BaserowLower())
    registry.register(BaserowConcat())
    registry.register(BaserowAdd())
    registry.register(BaserowMinus())
    registry.register(BaserowDivide())
    registry.register(BaserowEqual())
    registry.register(BaserowIf())
    registry.register(BaserowToText())
    registry.register(BaserowToChar())


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


class BaserowToChar(TwoArgumentBaserowFunction):
    type = "to_char"
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
        return Coalesce(
            Func(
                arg1,
                arg2,
                function="to_char",
                output_field=TextField(),
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


class EqualsExpr(Transform):
    template = "%(expressions)s"
    arg_joiner = "="
    arity = 2


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

    ALLOWED_TYPE_COMPARISONS: Dict[
        Type[BaserowFormulaValidType], List[Type[BaserowFormulaValidType]]
    ] = {
        BooleanField: [BooleanField, TextField],
        NumberField: [TextField, NumberField],
        TextField: [TextField, BooleanField, NumberField, DateField],
        DateField: [TextField, DateField],
    }

    @property
    def arg_types(self) -> BaserowArgumentTypeChecker:
        def type_checker(arg_index: int, arg_types: List[BaserowFormulaValidType]):
            # The valid types for arg1 are the comparable types for arg2 and vice versa.
            other_arg_index = arg_index - 1 % 2
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
            return BaserowEqual().call_and_type_with(
                BaserowToText().call_and_type_with(arg1),
                BaserowToText().call_and_type_with(arg2),
            )
        else:
            return func_call.with_valid_type(BaserowFormulaBooleanType())

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        return EqualsExpr(
            Cast(arg1, output_field=fields.TextField()),
            Cast(arg2, output_field=fields.TextField()),
            output_field=fields.BooleanField(),
        )

    # ALLOWED_TYPE_COMPARISONS: Dict[Type[Field], List[Type[Field]]] = {
    #     BooleanField: [BooleanField],
    #     DecimalField: [TextField, BooleanField],
    #     TextField: [TextField, BooleanField, DecimalField, DateField, DateTimeField],
    #     DateField: [TextField, DateField],
    #     DateTimeField: [TextField, DateTimeField],
    # }

    # def to_django_field_type(self, args: List[BaserowFormulaValidType]) -> Typed:
    #     return check_arg_type(
    #         arg_types[0],
    #         self.ALLOWED_TYPE_COMPARISONS[arg_types[1].__class__],
    #         BooleanField(),
    #     )
    #
    # def to_django_expression(self, args: List[Expression]) -> Expression:
    #     if type(args[0].output_field) != type(args[1].output_field):
    #         return EqualsExpr(
    #             Cast(args[0], output_field=TextField()),
    #             Cast(args[1], output_field=TextField()),
    #             output_field=BooleanField(),
    #         )
    #     else:
    #         return EqualsExpr(
    #             args[0],
    #             args[1],
    #             output_field=BooleanField(),
    #         )


class BaserowIf(BaserowFunctionDefinition):
    type = "if"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return FixedNumOfArgs(3)

    def type_function_given_valid_args(
        self,
        args: List[BaserowExpression[BaserowFormulaValidType]],
        expression: "BaserowFunctionCall[UnTyped]",
    ) -> BaserowExpression[BaserowFormulaType]:
        condition_arg = check_arg_type(
            expression, args[0], [BooleanField], BooleanField()
        )
        if isinstance(condition_arg.expression_type, InvalidType):
            return condition_arg

        arg1_type = args[1].expression_type
        arg2_type = args[2].expression_type
        if not (type(arg1_type) is type(arg2_type)):
            # TODO Casting logic
            return BaserowFunctionCall(
                BaserowIf(),
                [
                    args[0],
                    BaserowFunctionCall(BaserowToText(), [args[1]], TextField()),
                    BaserowFunctionCall(BaserowToText(), [args[2]], TextField()),
                ],
                TextField(),
            )
        elif isinstance(arg1_type, NumberField) and isinstance(arg2_type, NumberField):
            valid_type = _calculate_number_type([arg1_type, arg2_type])
        else:
            valid_type = arg1_type
        return expression.with_valid_type(valid_type)

    def to_django_expression_given_args(self, args: List[Expression]) -> Expression:
        # TODO TYPES
        return Case(When(condition=args[0], then=args[1]), default=args[2])

    # def to_django_field_type(self, args: List[BaserowFormulaValidType]) -> Typed:
    #     when = check_arg_type(args[0], [BooleanField], BooleanField())
    #     if when.is_invalid():
    #         return when
    #     if args[1] != args[2]:
    #         return ValidType(TextField())
    #     elif args[1] == DecimalField:
    #         return _calculate_number_type(arg_types[1:2])
    #     else:
    #         return ValidType(arg_types[1])
    #
    # def to_django_expression(self, args: List[Expression]) -> Expression:
    #     then_output_field = args[1].output_field
    #     else_output_field = args[2].output_field
    #     if type(then_output_field) != type(else_output_field):
    #         output_field = TextField()
    #         args[1] = Cast(args[1], output_field=output_field)
    #         args[2] = Cast(args[2], output_field=output_field)
    #     elif isinstance(then_output_field, DecimalField):
    #         output_field = _calculate_number_type(
    #             [then_output_field, else_output_field]
    #         ).valid_type
    #     else:
    #         output_field = then_output_field
    #
    #     return Case(
    #         When(condition=args[0], then=args[1]),
    #         default=args[2],
    #         output_field=output_field,
    #     )
