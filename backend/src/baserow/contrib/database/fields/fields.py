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
    """
    A PostgreSQL stored generated column field, provide a SQL expression and the type
    of the expression and every row of this field will be the evaluated upto date
    result of that expression. Please see the following documentation for more details:
    https://www.postgresql.org/docs/12/ddl-generated-columns.html
    """

    # Ensure that Django never tries to INSERT or UPDATE a generated column field
    # as it is not allowed by Postgres (and makes no sense) and will cause database
    # error.
    _baserow_read_only_field = True
    # Ensure when a model using one of these fields is created that the values of any
    # generated columns are returned using a INSERT ... RETURNING pk, gen_col_1, etc
    # as there is no default and no way of knowing what the e
    db_returning = True

    def __init__(
        self,
        generated_column_expression: str,
        generated_column_expression_type: str,
        *args,
        **kwargs,
    ):
        """
        :param generated_column_expression: A PostgreSQL expression valid for use
            when defining a generated column.
        :param generated_column_expression_type: The PostgreSQL type of the expression
            provided above.
        """

        self.generated_column_sql = generated_column_expression
        self.generated_column_sql_type = generated_column_expression_type
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["generated_column_expression"] = self.generated_column_sql
        kwargs["generated_column_expression_type"] = self.generated_column_sql_type
        return name, path, args, kwargs

    def db_type(self, connection):
        return (
            f"{self.generated_column_sql_type} GENERATED ALWAYS AS "
            f"({self.generated_column_sql}) STORED"
        )
