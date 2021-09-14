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
    UnTyped,
    BaserowStringLiteral,
    BaserowExpression,
)
from baserow.contrib.database.formula.ast.type_defs import (
    BaserowFormulaValidType,
    BaserowFormulaType,
    BaserowFormulaTextType,
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

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return check_arg_type(
            expr_being_typed=func_call,
            arg_to_type_check=arg,
            valid_arg_types=[TextField],
            resulting_type_if_valid=BaserowFormulaTextType(),
        )

    def to_django_expression(self, arg: Expression) -> Expression:
        return Upper(arg)


class BaserowLower(OneArgumentBaserowFunction):
    type = "lower"

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        return check_arg_type(
            expr_being_typed=func_call,
            arg_to_type_check=arg,
            valid_arg_types=[TextField],
            resulting_type_if_valid=BaserowFormulaTextType(),
        )

    def to_django_expression(self, arg: Expression) -> Expression:
        return Lower(arg)


class BaserowToChar(TwoArgumentBaserowFunction):
    type = "to_char"

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        checked_arg1 = check_arg_type(
            expr_being_typed=func_call,
            arg_to_type_check=arg1,
            valid_arg_types=[DateField],
            resulting_type_if_valid=arg1.expression_type,
        )
        if isinstance(checked_arg1.expression_type, InvalidType):
            return func_call.with_invalid_type(checked_arg1.expression_type)
        else:
            checked_arg2 = check_arg_type(
                expr_being_typed=func_call,
                arg_to_type_check=arg1,
                valid_arg_types=[TextField],
                resulting_type_if_valid=arg1.expression_type,
            )
            if isinstance(checked_arg2.expression_type, InvalidType):
                return func_call.with_invalid_type(checked_arg2.expression_type)
            else:
                func_call.with_valid_type(TextField())

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

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        if isinstance(arg.expression_type, DateField):
            return BaserowFunctionCall[BaserowFormulaValidType](
                BaserowToChar(),
                [
                    arg,
                    BaserowStringLiteral(
                        arg.expression_type.get_psql_format(), TextField()
                    ),
                ],
                TextField(),
            )
        else:
            return func_call.with_valid_type(TextField())

    def to_django_expression(self, arg: Expression) -> Expression:
        return Cast(arg, output_field=fields.TextField())


class BaserowConcat(BaserowFunctionDefinition):
    type = "concat"

    @property
    def num_args(self) -> ArgCountSpecifier:
        return NumOfArgsGreaterThan(1)

    def type_function_given_valid_args(
        self,
        args: List[BaserowExpression[BaserowFormulaValidType]],
        expression: "BaserowFunctionCall[UnTyped]",
    ) -> BaserowExpression[BaserowFormulaType]:
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
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
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
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
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
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
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
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
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
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
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

    ALLOWED_TYPE_COMPARISONS: Dict[
        Type[BaserowFormulaValidType], List[Type[BaserowFormulaValidType]]
    ] = {
        BooleanField: [BooleanField, TextField],
        NumberField: [TextField, NumberField],
        TextField: [TextField, BooleanField, NumberField, DateField],
        DateField: [TextField, DateField],
    }

    def type_function(
        self,
        func_call: BaserowFunctionCall[UnTyped],
        arg1: BaserowExpression[BaserowFormulaValidType],
        arg2: BaserowExpression[BaserowFormulaValidType],
    ) -> BaserowExpression[BaserowFormulaType]:
        arg1_type = arg1.expression_type
        arg2_type = arg2.expression_type
        can_compare = check_arg_type(
            func_call,
            arg2,
            self.ALLOWED_TYPE_COMPARISONS[type(arg1_type)],
            BooleanField(),
        )
        if isinstance(can_compare.expression_type, InvalidType):
            return can_compare
        else:
            if not (type(arg1_type) is type(arg2_type)):
                args = [
                    BaserowFunctionCall[UnTyped](
                        BaserowToText(), [arg1], None
                    ).type_function_given_valid_args([arg1]),
                    BaserowFunctionCall[UnTyped](
                        BaserowToText(), [arg2], None
                    ).type_function_given_valid_args([arg2]),
                ]
                return BaserowFunctionCall(
                    BaserowEqual(), args, None
                ).type_function_given_valid_args(args)
            else:
                return func_call.with_valid_type(BooleanField())

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
