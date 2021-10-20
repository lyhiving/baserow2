from django.contrib.auth.models import User

from .exceptions import NoPremiumLicenseError


# This is a temporary object that contains all the user ids as key and a boolean
# value to indicate if the user as active to the premium version. This part is going
# to be replaced by an actual license model and check in another merge request.
active_premium_user_registry = {}


def has_active_premium_license(user: User) -> bool:
    """
    A temporary placeholder function that should indicate if the provided user has an
    active license for the premium version.

    :param user: The user instance for which must checked if he has access to the
        premium version.
    :return: True if the user has a license to the premium version.
    """

    return active_premium_user_registry.get(user.id, False)


def check_active_premium_license(user):
    if not has_active_premium_license(user):
        raise NoPremiumLicenseError()
