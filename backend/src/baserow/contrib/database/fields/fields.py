from django.db import models
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


class GeneratedColumnField(models.Field):
    _baserow_read_only_field = True

    def __init__(
        self, generated_column_sql, generated_column_sql_type, *args, **kwargs
    ):
        self.generated_column_sql = generated_column_sql
        self.generated_column_sql_type = generated_column_sql_type
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["generated_column_sql"] = self.generated_column_sql
        return name, path, args, kwargs

    def db_type(self, connection):
        return (
            f"{self.generated_column_sql_type} GENERATED ALWAYS AS "
            f"({self.generated_column_sql}) STORED"
        )
