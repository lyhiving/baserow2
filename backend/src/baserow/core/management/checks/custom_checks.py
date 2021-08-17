from django.db import connections
from django.db.utils import OperationalError
from django.core.checks import Error, register, Tags


@register(Tags.compatibility)
def postgres_version_check(app_configs, **kwargs):
    errors = []
    check_failed = False
    try:
        conn = connections["default"]
        cur = conn.cursor()
        cur.execute("show server_version_num;")
        res = cur.fetchone()
        pg_version = int(res[0])

        # server_version_num reports the version number
        # of the server as integer. The first two numbers
        # represent the major version and the last two
        # the patch version. We want to make sure that
        # the server is running at least PG12.
        if pg_version < 120000:
            check_failed = True

    except OperationalError:
        errors.append(
            Error(
                "Cannot establish connection to PostgreSQL.",
                hint="Is the database running?",
            )
        )
    if check_failed:
        errors.append(
            Error(
                "PostgreSQL version is incompatible. Please update.",
                hint="Baserow requires at least version 12 of PostgreSQL.",
                id="Baserow.E001",
            )
        )
    return errors
