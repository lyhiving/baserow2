from typing import Optional

from django.db import models
from django.db.models import Field, Value
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from baserow.contrib.database.formula.ast.tree import BaserowExpression
from baserow.contrib.database.formula.types.type_types import InvalidType
from baserow.contrib.database.formula.expression_generator.generator import (
    tree_to_django_expression,
)


class SingleSelectForwardManyToOneDescriptor(ForwardManyToOneDescriptor):
    def get_queryset(self, **hints):
        """
        We specifically want to return a new query set without the provided hints
        because the related table could be in another database and that could fail
        otherwise.
        """

        return self.field.remote_field.model.objects.all()

    def get_object(self, instance):
        """
        Tries to fetch the reference object, but if it fails because it doesn't exist,
        the value will be set to None instead of failing hard.
        """

        try:
            return super().get_object(instance)
        except self.field.remote_field.model.DoesNotExist:
            setattr(instance, self.field.name, None)
            instance.save()
            return None


class SingleSelectForeignKey(models.ForeignKey):
    forward_related_accessor_class = SingleSelectForwardManyToOneDescriptor


class ExpressionField(models.Field):
    """
    A Custom Django field which is always set to the value of the provided Django
    Expression.
    """

    # Ensure when a model using one of these fields is created that the values of any
    # generated columns are returned using a INSERT ... RETURNING pk, gen_col_1, etc
    # as there is no default and no way of knowing what the expression evaluates to
    db_returning = True

    def __init__(
        self,
        expression: Optional[BaserowExpression],
        expression_field_type: Field,
        *args,
        **kwargs,
    ):
        """
        :param expression: The Django expression used to calculate this fields value.
        """

        self.expression = expression
        self.expression_field_type = expression_field_type
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["expression"] = self.expression
        kwargs["expression_field_type"] = self.expression_field_type
        return name, path, args, kwargs

    def db_type(self, connection):
        if isinstance(self.expression_field_type, InvalidType):
            return "TEXT"
        else:
            db_type = self.expression_field_type.db_type(connection)
            return db_type

    def pre_save(self, model_instance, add):
        print(self.expression)
        return (
            tree_to_django_expression(self.expression, model_instance, False)
            if self.expression is not None
            else Value(None)
        )
