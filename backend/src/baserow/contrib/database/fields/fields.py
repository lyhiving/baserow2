from typing import Type

from django.db import models
from django.db.models import Field
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from baserow.contrib.database.formula.ast.tree import BaserowExpression
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
        ast: BaserowExpression,
        expression_type: Field,
        field_types,
        *args,
        **kwargs,
    ):
        """
        :param expression: The Django expression used to calculate this fields value.
        """

        self.ast = ast
        self.expression_type = expression_type
        self.field_types = field_types
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["ast"] = self.ast
        kwargs["expression_type"] = self.expression_type
        kwargs["field_types"] = self.field_types
        return name, path, args, kwargs

    def get_internal_type(self):
        return self.expression_type.__class__.__name__

    def pre_save(self, model_instance, add):
        # Force the instance to use the expression to calculate its value.
        expression = tree_to_django_expression(
            self.ast, self.field_types, model_instance, False
        )
        setattr(model_instance, self.attname, expression)
        return expression
