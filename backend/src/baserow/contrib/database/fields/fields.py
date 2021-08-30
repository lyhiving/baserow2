from django.db import models
from django.db.models import Expression
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor


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
        expression: Expression,
        *args,
        **kwargs,
    ):
        """
        :param expression: The Django expression used to calculate this fields value.
        """

        self.expression = expression
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["expression"] = self.expression
        return name, path, args, kwargs

    def get_internal_type(self):
        internal_type = self.expression.output_field.__class__.__name__
        # Expressions will by default set their output type as a CharField, however
        # as we don't want to have to set a varchar length we switch to using the
        # unlimited length text field.
        if internal_type == "CharField":
            internal_type = "TextField"
        return internal_type

    def pre_save(self, model_instance, add):
        # Force the instance to use the expression to calculate its value.
        setattr(model_instance, self.attname, self.expression)
        return self.expression
