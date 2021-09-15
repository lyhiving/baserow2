from django.db.models import Transform


class EqualsExpr(Transform):
    template = "%(expressions)s"
    arg_joiner = "="
    arity = 2
