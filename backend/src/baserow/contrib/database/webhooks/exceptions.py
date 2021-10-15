class TableWebhookCannotBeCalled(Exception):
    """
    Raised when a webhook cannot be called
    """


class TableWebhookAlreadyExists(Exception):
    """
    Raised when trying to create a webhook that already exists
    """


class TableWebhookDoesNotExist(Exception):
    """
    Raised when trying to update a webhook that does not exist
    """


class TableWebhookMaxAllowedCountExceeded(Exception):
    """
    Raised when trying to create more webhooks for a table than allowed
    """
