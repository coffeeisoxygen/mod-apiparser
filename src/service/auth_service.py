"""Authentication service for user login and token management."""

from src.domain.token.sch_token import TokenResponse
from src.domain.user.sch_user import UserLogin
from src.exceptions.app_exceptions import AppException
from src.mlogger import get_logger
from src.service.token.token_service import TokenService

logger = get_logger(__name__)


class AuthService:
    """Authentication service handling user login and logout operations.

    This service provides high-level authentication operations using the
    modular token service components.
    """

    def __init__(self, token_service: TokenService) -> None:
        """Initialize authentication service.

        Args:
            token_service: Token service for token operations
        """
        self.token_service = token_service
        logger.info("AuthService initialized")

    def login(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return token response.

        Args:
            login_data: User login credentials

        Returns:
            TokenResponse with access and refresh tokens

        Raises:
            AppException.AuthenticationError: If authentication fails
        """
        logger.info(f"Processing login for user: {login_data.username}")

        try:
            # Authenticate user and create tokens
            token_response = self.token_service.authenticate_user(
                username=login_data.username, password=login_data.password
            )

            logger.info(f"Login successful for user: {login_data.username}")
            return token_response

        except AppException.AuthenticationError:
            # Re-raise authentication errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise AppException.AuthenticationError("Login failed") from e

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            TokenResponse with new token pair

        Raises:
            AppException.TokenInvalidError: If refresh token is invalid
            AppException.TokenExpiredError: If refresh token is expired
        """
        logger.debug("Processing token refresh")

        try:
            new_tokens = self.token_service.refresh_tokens(refresh_token)
            logger.info("Token refresh successful")
            return new_tokens

        except (AppException.TokenInvalidError, AppException.TokenExpiredError):
            # Re-raise token-specific errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {e}")
            raise AppException.TokenServiceError("Token refresh failed") from e

    def logout(self, token: str) -> None:
        """Logout user by revoking their token.

        Args:
            token: Token to revoke (access or refresh)
        """
        logger.debug("Processing logout")

        try:
            self.token_service.revoke_token(token, reason="User logout")
            logger.info("Logout successful")

        except Exception as e:
            # Log error but don't raise - logout should always succeed
            logger.error(f"Error during logout (token may already be invalid): {e}")

    def logout_all_sessions(self, user_id: str) -> int:
        """Logout user from all sessions by revoking all their tokens.

        Args:
            user_id: User ID whose tokens to revoke

        Returns:
            Number of tokens revoked
        """
        logger.info(f"Processing logout from all sessions for user: {user_id}")

        try:
            count = self.token_service.revoke_user_tokens(
                user_id=user_id, reason="Logout from all sessions"
            )
            logger.info(f"Logout from all sessions successful, revoked {count} tokens")
            return count

        except Exception as e:
            logger.error(f"Error during logout from all sessions: {e}")
            return 0
