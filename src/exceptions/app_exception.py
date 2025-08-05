class BasExceptionError(Exception):
    """Base class for all application-specific exceptions."""

    def __init__(
        self, status_code: int, message: str | None = None, context: dict | None = None
    ):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.message = message or "An application error occurred."
        self.context = context if context is not None else {}

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            f"status_code={self.status_code} - message={self.message} - context={self.context}>"
        )


class AppException:
    """Collection of application-specific exceptions."""

    class AccountServiceError(BasExceptionError):
        """Exception raised for errors in the account service."""

        def __init__(self, message: str | None = None, context: dict | None = None):
            default_message = "Account service error occurred."
            super().__init__(500, message or default_message, context)
