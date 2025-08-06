from src.exceptions.exc_base import BasExceptionError


class AppException:
    """Collection of application-specific exceptions."""

    class UserActionError(BasExceptionError):
        """Exception raised for errors in the account service."""

        def __init__(self, message: str | None = None, context: dict | None = None):
            default_message = "Account service error occurred."
            super().__init__(500, message or default_message, context)

    class PathResolverError(BasExceptionError):
        """Exception raised for errors in path resolution."""

        def __init__(self, message: str | None = None, context: dict | None = None):
            default_message = "Path resolution error occurred."
            super().__init__(500, message or default_message, context)

    class FileNotFoundError(BasExceptionError):
        """Exception raised when a required file is not found."""

        def __init__(self, message: str | None = None, context: dict | None = None):
            default_message = "Required file not found."
            super().__init__(404, message or default_message, context)
