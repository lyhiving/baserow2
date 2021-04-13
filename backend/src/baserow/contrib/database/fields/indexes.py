from django.contrib.postgres.indexes import GinIndex


class BaseIndex(GinIndex):
    columns_sql = "%(columns)s"

    def create_sql(self, *args, **kwargs):
        statement = super().create_sql(*args, **kwargs)
        statement.template = f"""
            CREATE INDEX %(name)s ON %(table)s%(using)s
            ({self.columns_sql} gin_trgm_ops)%(extra)s
        """
        print(statement)
        return statement


class AsTextIndex(BaseIndex):
    columns_sql = "CAST(%(columns)s as TEXT)"


class ContainsIndex(BaseIndex):
    columns_sql = "UPPER(%(columns)s)"


class ContainsAsTextIndex(BaseIndex):
    columns_sql = "UPPER(CAST(%(columns)s as TEXT))"


class DateContainsAsTextIndex(BaseIndex):
    def __init__(self, *args, **kwargs):
        self.date_format = kwargs.pop("date_format")
        self.columns_sql = f"""
            Upper(
                COALESCE(
                    my_to_char(%(columns)s),
                    ''
                )::text
            )
        """
        super().__init__(*args, **kwargs)

    def create_sql(self, model, schema_editor, using=""):
        statement = super().create_sql(model, schema_editor, using)
        statement.template = f"""
            CREATE OR REPLACE FUNCTION my_to_char(some_time date)
              RETURNS text
            AS
            $BODY$
                select to_char($1, '{self.date_format}');
            $BODY$
            LANGUAGE sql
            IMMUTABLE;
            {statement.template}
        """
        return statement
