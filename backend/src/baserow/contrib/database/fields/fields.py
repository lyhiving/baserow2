from typing import Optional

from django.db import models
from django.db.models import Field, Value
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from baserow.contrib.database.formula.ast.tree import BaserowExpression
from baserow.contrib.database.formula.types.type_types import InvalidType
from baserow.contrib.database.formula.expression_generator.generator import (
    baserow_expression_to_django_expression,
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


class BaserowExpressionField(models.Field):
    """
    A Custom Django field which is always set to the value of the provided Baserow
    Expression.
    """

    # Ensure when a model using one of these fields is created that the values of any
    # generated columns are returned using a INSERT ... RETURNING pk, gen_col_1, etc
    # as there is no default and no way of knowing what the expression evaluates to
    db_returning = True

    def __init__(
        self,
        expression: Optional[BaserowExpression],
        expression_field: Field,
        *args,
        **kwargs,
    ):
        """
        :param expression: The Baserow expression used to calculate this fields value.
        :param expression_field: An instance of a Django field that should be used to
            store the result of the expression in the database.
        """

        self.expression = expression
        self.expression_field = expression_field
        for name, lookup in self.expression_field.get_lookups().items():
            self.register_lookup(lookup, lookup_name=name)
        super().__init__(*args, **kwargs)

    @property
    def __class__(self):
        return self.expression_field.__class__

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["expression"] = self.expression
        kwargs["expression_field"] = self.expression_field
        return name, path, args, kwargs

    def db_type(self, connection):
        if isinstance(self.expression_field, InvalidType):
            return "TEXT"
        else:
            return self.expression_field.db_type(connection)

    def get_prep_value(self, value):
        return self.expression_field.get_prep_value(value)

    def pre_save(self, model_instance, add):
        if self.expression is None:
            return Value(None)
        else:
            return baserow_expression_to_django_expression(
                self.expression, model_instance
            )
