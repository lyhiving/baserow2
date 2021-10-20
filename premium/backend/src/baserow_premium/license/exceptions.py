from rest_framework.status import HTTP_402_PAYMENT_REQUIRED
from rest_framework.exceptions import APIException


class NoPremiumLicenseError(APIException):
    """
    Raised when the related user does not have an active license for the premium
    version.
    """

    def __init__(self):
        super().__init__(
            {
                "error": "ERROR_NO_ACTIVE_PREMIUM_LICENSE",
                "detail": "The related user does not have access to the premium "
                "version.",
            },
            code=HTTP_402_PAYMENT_REQUIRED,
        )
        self.status_code = HTTP_402_PAYMENT_REQUIRED
