class UserNotFound(Exception):
    """Raised when a user with given parameters is not found."""


class UserAlreadyExist(Exception):
    """Raised when a user could not be created because the email already exists."""


class InvalidOldPassword(Exception):
    """Raised when the provided old/current password is incorrect."""


class InvalidPassword(Exception):
    """Raised when the provided password is not a valid password."""


class DisabledSignupError(Exception):
    """
    Raised when a user account is created when the new signup setting is disabled.
    """
