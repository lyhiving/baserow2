from django.db.models import Transform


# noinspection PyAbstractClass
# Django provides no way of doing a SQL equals expression with an arbitrary Django
# expression on both the LHS and RHS. Instead we have to define our own simple transform
# which joins two expressions together with a single =.
class EqualsExpr(Transform):
    template = "%(expressions)s"
    arg_joiner = "="
    arity = 2


class NotEqualsExpr(Transform):
    template = "%(expressions)s"
    arg_joiner = "!="
    arity = 2


class NotExpr(Transform):
    template = "not %(expressions)s"
    arity = 1
