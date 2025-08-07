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

    class YamlReloadExceptionError(BasExceptionError):
        """Exception raised for errors during YAML file reload and validation."""

        def __init__(self, message: str | None = None, context: dict | None = None):
            default_message = "YAML reload or validation failed."
            super().__init__(500, message or default_message, context)

    class TokenServiceError(BasExceptionError):
        """Base exception for token service errors."""

        def __init__(self, message: str | None = None, context: dict | None = None):
            default_message = "Token service error occurred."
            super().__init__(500, message or default_message, context)

    class TokenExpiredError(BasExceptionError):
        """Token has expired."""

        def __init__(self, message: str | None = None, context: dict | None = None):
            default_message = "Token has expired."
            super().__init__(401, message or default_message, context)

    class TokenInvalidError(BasExceptionError):
        """Token is invalid."""

        def __init__(self, message: str | None = None, context: dict | None = None):
            default_message = "Token is invalid."
            super().__init__(401, message or default_message, context)

    class AuthenticationError(BasExceptionError):
        """Authentication failed."""

        def __init__(self, message: str | None = None, context: dict | None = None):
            default_message = "Authentication failed."
            super().__init__(401, message or default_message, context)
