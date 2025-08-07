"""Main token service orchestrating all token operations."""

from uuid import UUID

from src.config.settings import JWTConfig
from src.domain.token.sch_token import (
    TokenCreate,
    TokenData,
    TokenIntrospection,
    TokenResponse,
)
from src.domain.user.sch_user import UserInDB
from src.exceptions.app_exceptions import AppException
from src.mlogger import get_logger
from src.repos.rep_user import UserRepository
from src.service.hasher_service import HasherService
from src.service.token.jwt_handler import JWTHandler
from src.service.token.token_blacklist import TokenBlacklistManager
from src.service.token.token_validator import TokenValidator

logger = get_logger(__name__)


class TokenService:
    """Main token service orchestrating all token operations.

    This service coordinates between JWT handling, validation, blacklisting,
    and user management to provide high-level token operations.
    """

    def __init__(
        self,
        jwt_handler: JWTHandler,
        validator: TokenValidator,
        blacklist_manager: TokenBlacklistManager,
        user_repo: UserRepository,
        jwt_config: JWTConfig,
    ) -> None:
        """Initialize token service.

        Args:
            jwt_handler: JWT handler for token operations
            validator: Token validator for business rules
            blacklist_manager: Blacklist manager for security
            user_repo: User repository for user operations
            jwt_config: JWT configuration from settings
        """
        self.jwt_handler = jwt_handler
        self.validator = validator
        self.blacklist_manager = blacklist_manager
        self.user_repo = user_repo
        self.config = jwt_config
        self.hasher = HasherService()

        logger.info("TokenService initialized")

    def authenticate_user(self, username: str, password: str) -> TokenResponse:
        """Authenticate user and create token pair.

        Args:
            username: Username for authentication
            password: Password for authentication

        Returns:
            TokenResponse with access and refresh tokens

        Raises:
            AppException.AuthenticationError: If authentication fails
        """
        logger.info(f"Authenticating user: {username}")

        # Get user from repository
        user = self.user_repo.get_user_by_username(username)
        if not user:
            logger.warning(f"User not found: {username}")
            raise AppException.AuthenticationError("Invalid credentials")

        # Verify password
        if not self.hasher.verify_password(password, user.password):
            logger.warning(f"Invalid password for user: {username}")
            raise AppException.AuthenticationError("Invalid credentials")

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {username}")
            raise AppException.AuthenticationError("Account is inactive")

        # Create token pair
        token_response = self.create_token_pair(user)

        logger.info(f"User authenticated successfully: {username}")
        return token_response

    def create_token_pair(self, user: UserInDB) -> TokenResponse:
        """Create access and refresh token pair for user.

        Args:
            user: User to create tokens for

        Returns:
            TokenResponse with token pair
        """
        logger.debug(f"Creating token pair for user: {user.username}")

        # Prepare extra claims for tokens
        extra_claims = {
            "user_id": str(user.id),
            "username": user.username,
            "is_superuser": user.is_superuser,
        }

        # Create tokens
        access_token = self.jwt_handler.create_access_token(
            subject=str(user.id),
            extra_claims=extra_claims,
        )

        refresh_token = self.jwt_handler.create_refresh_token(
            subject=str(user.id),
            extra_claims=extra_claims,
        )

        # Calculate expires_in for access token
        expires_in = self.config.access_token_expire_minutes * 60

        response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
        )

        logger.info(f"Token pair created for user: {user.username}")
        return response

    def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Create new token pair from valid refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            TokenResponse with new token pair

        Raises:
            AppException.TokenInvalidError: If refresh token is invalid
            AppException.TokenExpiredError: If refresh token is expired
        """
        logger.debug("Refreshing tokens")

        # Validate refresh token
        token_data = self.validator.validate_refresh_token(refresh_token)

        # Get user to ensure they still exist and are active
        user = self.user_repo.get_user_by_username(token_data.username)
        if not user:
            logger.warning(
                f"User not found during token refresh: {token_data.username}"
            )
            raise AppException.TokenInvalidError("User not found")

        if not user.is_active:
            logger.warning(
                f"Inactive user attempted token refresh: {token_data.username}"
            )
            raise AppException.TokenInvalidError("Account is inactive")

        # Blacklist old refresh token
        jti = self.validator.get_token_jti(refresh_token)
        if jti:
            self.blacklist_manager.blacklist_token(
                jti=jti,
                user_id=token_data.user_id,
                token_type="refresh",
                reason="Token refreshed",
            )

        # Create new token pair
        new_response = self.create_token_pair(user)

        logger.info(f"Tokens refreshed for user: {user.username}")
        return new_response

    def revoke_token(self, token: str, reason: str | None = None) -> None:
        """Revoke (blacklist) a token.

        Args:
            token: Token to revoke
            reason: Optional reason for revocation
        """
        logger.debug("Revoking token")

        try:
            # Get token information
            jti = self.validator.get_token_jti(token)
            subject = self.validator.get_token_subject(token)

            if jti and subject:
                # Try to get token type from claims
                try:
                    claims = self.jwt_handler.get_unverified_claims(token)
                    token_type = claims.get("token_type", "unknown")
                except Exception:
                    token_type = "unknown"

                self.blacklist_manager.blacklist_token(
                    jti=jti,
                    user_id=subject,
                    token_type=token_type,
                    reason=reason or "Token revoked",
                )

                logger.info(f"Token revoked: {jti}")
            else:
                logger.warning("Could not extract token information for revocation")

        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            # Don't raise exception for revocation failures
            # as the token might already be invalid

    def revoke_user_tokens(self, user_id: str | UUID, reason: str | None = None) -> int:
        """Revoke all tokens for a user.

        Args:
            user_id: User ID whose tokens to revoke
            reason: Optional reason for revocation

        Returns:
            Number of tokens revoked
        """
        logger.info(f"Revoking all tokens for user: {user_id}")

        count = self.blacklist_manager.blacklist_user_tokens(
            user_id=user_id,
            reason=reason or f"All tokens revoked for user: {user_id}",
        )

        logger.info(f"Revoked {count} tokens for user: {user_id}")
        return count

    def introspect_token(self, token: str) -> TokenIntrospection:
        """Perform token introspection.

        Args:
            token: Token to introspect

        Returns:
            TokenIntrospection with token details
        """
        return self.validator.introspect_token(token)

    def validate_access_token(self, token: str) -> TokenData:
        """Validate an access token.

        Args:
            token: Access token to validate

        Returns:
            TokenData with validated information

        Raises:
            AppException.TokenInvalidError: If token is invalid
            AppException.TokenExpiredError: If token is expired
        """
        return self.validator.validate_access_token(token)

    def validate_refresh_token(self, token: str) -> TokenData:
        """Validate a refresh token.

        Args:
            token: Refresh token to validate

        Returns:
            TokenData with validated information

        Raises:
            AppException.TokenInvalidError: If token is invalid
            AppException.TokenExpiredError: If token is expired
        """
        return self.validator.validate_refresh_token(token)

    def create_token_for_user(self, token_create: TokenCreate) -> str:
        """Create a single token for a user (for testing/admin purposes).

        Args:
            token_create: Token creation parameters

        Returns:
            Created token string
        """
        logger.debug(
            f"Creating {token_create.token_type} token for user: {token_create.username}"
        )

        extra_claims = {
            "user_id": str(token_create.user_id),
            "username": token_create.username,
            "is_superuser": token_create.is_superuser,
        }

        if token_create.token_type == "access":
            token = self.jwt_handler.create_access_token(
                subject=str(token_create.user_id),
                extra_claims=extra_claims,
            )
        elif token_create.token_type == "refresh":
            token = self.jwt_handler.create_refresh_token(
                subject=str(token_create.user_id),
                extra_claims=extra_claims,
            )
        else:
            raise AppException.TokenServiceError(
                f"Unsupported token type: {token_create.token_type}"
            )

        logger.info(f"Token created for user: {token_create.username}")
        return token

    def get_blacklist_stats(self) -> dict[str, int]:
        """Get blacklist statistics.

        Returns:
            Dictionary with blacklist statistics
        """
        return self.blacklist_manager.get_blacklist_stats()

    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens from blacklist.

        Returns:
            Number of tokens cleaned up
        """
        return self.blacklist_manager.cleanup_expired_tokens()
