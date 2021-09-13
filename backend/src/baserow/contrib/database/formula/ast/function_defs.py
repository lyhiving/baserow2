from decimal import Decimal
from typing import Type, List, Dict, Callable, Union, Any

from django.db.models import (
    Expression,
    Value,
    Transform,
    Case,
    When,
    fields,
    Max,
)
from django.db.models.functions import Upper, Lower, Concat, Coalesce, Cast, Greatest

from baserow.contrib.database.fields.models import (
    DateField,
    Field,
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
)
from baserow.contrib.database.formula.ast.tree import (
    BaserowExpression,
    BaserowFunctionCall,
    UnTyped,
)
from baserow.contrib.database.formula.ast.type_types import (
    ValidType,
    Typed,
    InvalidType,
)


def check_arg_type(
    func_being_typed: BaserowFunctionCall[UnTyped],
    arg_to_type_check: BaserowExpression[ValidType],
    valid_arg_types: List[Type[Field]],
    resulting_func_type_if_valid: ValidType,
) -> BaserowExpression[Typed]:
    for valid_arg_type in valid_arg_types:
        arg_type = arg_to_type_check.expression_type
        if isinstance(arg_type, valid_arg_type):
            return func_being_typed.with_valid_type(resulting_func_type_if_valid)
    valid_types_str = ",".join([str(t) for t in valid_arg_types])
    return func_being_typed.with_invalid_type(
        f"must be one of {valid_types_str} but was instead {type(arg_to_type_check)}"
    )


def check_types(
    func_being_typed: BaserowFunctionCall[UnTyped],
    args_to_type_check: List[BaserowExpression[ValidType]],
    valid_arg_types: List[Type[ValidType]],
    resulting_func_type_if_valid: Union[ValidType, Callable[[List[Any]], ValidType]],
) -> BaserowExpression[Typed]:
    invalid_types = []
    valid_types = []
    for i, arg_to_type_check in enumerate(args_to_type_check):
        matching_type_found = False
        arg_type = arg_to_type_check.expression_type
        for valid_arg_type in valid_arg_types:
            if isinstance(arg_type, valid_arg_type):
                matching_type_found = True
                break
        if matching_type_found:
            valid_types.append(arg_type)
        else:
            invalid_types.append((i, arg_type))
    if len(invalid_types) > 0:
        error = ",".join(
            [f"argument {i} invalid as it was a {type(r)}" for i, r in invalid_types]
        )
        return func_being_typed.with_invalid_type(error)
    else:
        if callable(resulting_func_type_if_valid):
            resulting_func_type_if_valid = resulting_func_type_if_valid(valid_types)
        return func_being_typed.with_valid_type(resulting_func_type_if_valid)


def register_functions(registry):
    registry.register(BaserowUpper())
    registry.register(BaserowLower())
    registry.register(BaserowConcat())
    registry.register(BaserowAdd())
    registry.register(BaserowMinus())
    registry.register(BaserowDivide())
    registry.register(BaserowEqual())
    registry.register(BaserowIf())


class BaserowUpper(OneArgumentBaserowFunction):
    type = "upper"

    def type_function(
        self, func_call: BaserowFunctionCall[UnTyped], arg: BaserowExpression[ValidType]
    ) -> BaserowExpression[Typed]:
        return check_arg_type(
            func_being_typed=func_call,
            arg_to_type_check=arg,
            valid_arg_types=[TextField],
            resulting_func_type_if_valid=TextField(),
        )

    def to_django_expression(self, arg: Expression) -> Expression:
        return Upper(arg)


class BaserowLower(OneArgumentBaserowFunction):
    type = "lower"

    def type_function(
        self, func_call: BaserowFunctionCall[UnTyped], arg: BaserowExpression[ValidType]
    ) -> BaserowExpression[Typed]:
        return check_arg_type(
            func_being_typed=func_call,
            arg_to_type_check=arg,
            valid_arg_types=[TextField],
            resulting_func_type_if_valid=TextField(),
        )

    def to_django_expression(self, arg: Expression) -> Expression:
        return Lower(arg)


class BaserowConcat(BaserowFunctionDefinition):
    type = "concat"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return NumOfArgsGreaterThan(1)

    def type_function_given_valid_args(
        self,
        args: List[BaserowExpression[ValidType]],
        expression: "BaserowFunctionCall[UnTyped]",
    ) -> BaserowExpression[Typed]:
        return check_types(
            expression,
            args,
            [TextField, NumberField],
            TextField(),
        )

    def to_django_expression_given_args(self, args: List[Expression]) -> Expression:
        return Concat(*args, output_field=fields.TextField())


class BaserowAdd(TwoArgumentBaserowFunction):
    type = "add"

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[ValidType],
        arg2: BaserowExpression[ValidType],
    ) -> BaserowExpression[Typed]:
        return check_types(
            func_being_typed=func_call,
            args_to_type_check=[arg1, arg2],
            valid_arg_types=[NumberField],
            resulting_func_type_if_valid=_calculate_number_type,
        )

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        return arg1 + arg2


def _calculate_number_type(arg_types: List[NumberField], min_decimal_places=0):
    number_type = NUMBER_TYPE_INTEGER
    max_number_decimal_places = min_decimal_places
    for a in arg_types:
        max_number_decimal_places = max(
            max_number_decimal_places, a.number_decimal_places
        )
        if a.number_type == NUMBER_TYPE_DECIMAL:
            number_type = NUMBER_TYPE_DECIMAL

    return NumberField(
        number_type=number_type,
        number_decimal_places=max_number_decimal_places,
        number_negative=True,
    )


class BaserowMinus(TwoArgumentBaserowFunction):
    type = "minus"

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[ValidType],
        arg2: BaserowExpression[ValidType],
    ) -> BaserowExpression[Typed]:
        return check_types(
            func_being_typed=func_call,
            args_to_type_check=[arg1, arg2],
            valid_arg_types=[NumberField],
            resulting_func_type_if_valid=_calculate_number_type,
        )

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        return arg1 - arg2


class EqualsExpr(Transform):
    template = "%(expressions)s"
    arg_joiner = "="
    arity = 2


class BaserowMax(TwoArgumentBaserowFunction):
    type = "Max"

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[ValidType],
        arg2: BaserowExpression[ValidType],
    ) -> BaserowExpression[Typed]:
        return check_types(
            func_being_typed=func_call,
            args_to_type_check=[arg1, arg2],
            valid_arg_types=[NumberField],
            resulting_func_type_if_valid=_calculate_number_type,
        )

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        return Greatest(arg1, arg2)


class BaserowTextDefault(TwoArgumentBaserowFunction):
    type = "text_default"

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[ValidType],
        arg2: BaserowExpression[ValidType],
    ) -> BaserowExpression[Typed]:
        return check_types(
            func_being_typed=func_call,
            args_to_type_check=[arg1, arg2],
            valid_arg_types=[TextField],
            resulting_func_type_if_valid=TextField(),
        )

    def to_django_expression(self, arg1: Expression, arg2: Expression) -> Expression:
        return Case(
            When(
                EqualsExpr(
                    Coalesce(arg1, Value("")),
                    Value(""),
                    output_field=fields.BooleanField(),
                ),
                then=arg2,
            ),
            default=arg1,
        )


class BaserowDivide(TwoArgumentBaserowFunction):
    type = "divide"

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[ValidType],
        arg2: BaserowExpression[ValidType],
    ) -> BaserowExpression[Typed]:
        return check_types(
            func_being_typed=func_call,
            args_to_type_check=[arg1, arg2],
            valid_arg_types=[NumberField],
            # Show all the decimal places we can by default if the user makes a formula
            # with a division to prevent weird results like `1/3=0`
            resulting_func_type_if_valid=NumberField(
                number_type=NUMBER_TYPE_DECIMAL,
                number_decimal_places=NUMBER_MAX_DECIMAL_PLACES,
                number_negative=True,
            ),
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

    ALLOWED_TYPE_COMPARISONS: Dict[Type[ValidType], List[Type[ValidType]]] = {
        BooleanField: [BooleanField],
        NumberField: [TextField, NumberField],
        TextField: [TextField, BooleanField, NumberField, DateField],
        DateField: [TextField, DateField],
    }

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[ValidType],
        arg2: BaserowExpression[ValidType],
    ) -> BaserowExpression[Typed]:
        # TODO Handle type casting
        return check_types(
            func_being_typed=func_call,
            args_to_type_check=[arg1, arg2],
            valid_arg_types=self.ALLOWED_TYPE_COMPARISONS[type(arg1.expression_type)],
            resulting_func_type_if_valid=BooleanField(),
        )

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

    # def to_django_field_type(self, args: List[ValidType]) -> Typed:
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
        args: List[BaserowExpression[ValidType]],
        expression: "BaserowFunctionCall[UnTyped]",
    ) -> BaserowExpression[Typed]:
        condition_arg = check_arg_type(
            expression, args[0], [BooleanField], BooleanField()
        )
        if isinstance(condition_arg.expression_type, InvalidType):
            return condition_arg

        arg1_type = args[1].expression_type
        arg2_type = args[2].expression_type
        if not (type(arg1_type) is type(arg2_type)):
            # TODO Casting logic
            valid_type = TextField()
        elif isinstance(arg1_type, NumberField) and isinstance(arg2_type, NumberField):
            valid_type = _calculate_number_type([arg1_type, arg2_type])
        else:
            valid_type = arg1_type
        return expression.with_valid_type(valid_type)

    def to_django_expression_given_args(self, args: List[Expression]) -> Expression:
        # TODO TYPES
        return Case(When(condition=args[0], then=args[1]), default=args[2])

    # def to_django_field_type(self, args: List[ValidType]) -> Typed:
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
