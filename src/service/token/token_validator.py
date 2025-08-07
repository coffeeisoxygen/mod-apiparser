"""Token validation business logic."""

from datetime import datetime

from src.config.settings import JWTConfig
from src.domain.token.sch_token import TokenData, TokenIntrospection
from src.exceptions.app_exceptions import AppException
from src.mlogger import get_logger
from src.service.token.jwt_handler import JWTHandler
from src.service.token.token_blacklist import TokenBlacklistManager

logger = get_logger(__name__)


class TokenValidator:
    """Handles token validation business rules.

    This class implements the business logic for validating tokens,
    including format validation, blacklist checking, and claim verification.
    """

    def __init__(
        self,
        jwt_handler: JWTHandler,
        blacklist_manager: TokenBlacklistManager,
        jwt_config: JWTConfig,
    ) -> None:
        """Initialize token validator.

        Args:
            jwt_handler: JWT handler for token operations
            blacklist_manager: Blacklist manager for security checks
            jwt_config: JWT configuration from settings
        """
        self.jwt_handler = jwt_handler
        self.blacklist_manager = blacklist_manager
        self.config = jwt_config
        logger.info("TokenValidator initialized")

    def validate_access_token(self, token: str) -> TokenData:
        """Validate an access token and return token data.

        Args:
            token: Access token to validate

        Returns:
            TokenData with validated token information

        Raises:
            AppException.TokenInvalidError: If token is invalid
            AppException.TokenExpiredError: If token is expired
        """
        return self._validate_token(token, expected_type="access")

    def validate_refresh_token(self, token: str) -> TokenData:
        """Validate a refresh token and return token data.

        Args:
            token: Refresh token to validate

        Returns:
            TokenData with validated token information

        Raises:
            AppException.TokenInvalidError: If token is invalid
            AppException.TokenExpiredError: If token is expired
        """
        return self._validate_token(token, expected_type="refresh")

    def _validate_token(self, token: str, expected_type: str) -> TokenData:
        """Internal method to validate tokens.

        Args:
            token: Token to validate
            expected_type: Expected token type (access, refresh)

        Returns:
            TokenData with validated token information

        Raises:
            AppException.TokenInvalidError: If token is invalid
            AppException.TokenExpiredError: If token is expired
        """
        if not token:
            raise AppException.TokenInvalidError("Token is required")

        # Decode and verify token
        try:
            payload = self.jwt_handler.decode_token(token, verify=True)
        except (AppException.TokenExpiredError, AppException.TokenInvalidError):
            # Re-raise token-specific exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {e}")
            raise AppException.TokenInvalidError(f"Token validation failed: {e}") from e

        # Validate token type
        token_type = payload.get("token_type")
        if token_type != expected_type:
            raise AppException.TokenInvalidError(
                f"Expected {expected_type} token, got {token_type}"
            )

        # Check blacklist
        jti = payload.get("jti")
        if jti and self.blacklist_manager.is_blacklisted(jti):
            raise AppException.TokenInvalidError("Token has been revoked")

        # Convert to TokenData
        try:
            token_data = TokenData(
                user_id=payload["user_id"],
                username=payload["username"],
                is_superuser=payload.get("is_superuser", False),
                token_type=payload["token_type"],
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"]),
            )

            logger.debug(
                "Token validated successfully",
                user_id=token_data.user_id,
                username=token_data.username,
                token_type=token_data.token_type,
            )

            return token_data

        except KeyError as e:
            logger.error(f"Missing required claim in token: {e}", payload=payload)
            raise AppException.TokenInvalidError(
                f"Invalid token: missing claim {e}"
            ) from e
        except Exception as e:
            logger.error(
                f"Failed to create TokenData from payload: {e}", payload=payload
            )
            raise AppException.TokenInvalidError(f"Invalid token payload: {e}") from e

    def introspect_token(self, token: str) -> TokenIntrospection:
        """Perform token introspection (RFC 7662).

        Returns detailed information about the token without throwing exceptions
        for expired or invalid tokens.

        Args:
            token: Token to introspect

        Returns:
            TokenIntrospection with token details
        """
        try:
            # Try to get unverified claims first
            claims = self.jwt_handler.get_unverified_claims(token)

            # Check if token is active (not expired and not blacklisted)
            active = True

            # Check expiration
            exp = claims.get("exp")
            if exp:
                exp_datetime = datetime.fromtimestamp(exp)
                if datetime.utcnow() > exp_datetime:
                    active = False

            # Check blacklist
            jti = claims.get("jti")
            if jti and self.blacklist_manager.is_blacklisted(jti):
                active = False

            # Try to verify signature if active
            if active:
                try:
                    self.jwt_handler.decode_token(token, verify=True)
                except Exception:
                    active = False

            return TokenIntrospection(
                active=active,
                scope=claims.get("scope"),
                client_id=claims.get("client_id"),
                username=claims.get("username"),
                token_type=claims.get("token_type"),
                exp=claims.get("exp"),
                iat=claims.get("iat"),
                nbf=claims.get("nbf"),
                sub=claims.get("sub"),
                aud=claims.get("aud"),
                iss=claims.get("iss"),
                jti=claims.get("jti"),
            )

        except Exception as e:
            logger.debug(f"Token introspection failed: {e}")
            # Return inactive token introspection
            return TokenIntrospection(
                active=False,
                scope=None,
                client_id=None,
                username=None,
                token_type=None,
                exp=None,
                iat=None,
                nbf=None,
                sub=None,
                aud=None,
                iss=None,
                jti=None,
            )

    def validate_token_format(self, token: str) -> bool:
        """Validate token format without full verification.

        Args:
            token: Token to check format

        Returns:
            True if token format is valid, False otherwise
        """
        if not token:
            return False

        try:
            # Check if token has valid JWT format (3 parts separated by dots)
            parts = token.split(".")
            if len(parts) != 3:
                return False

            # Try to get unverified claims
            self.jwt_handler.get_unverified_claims(token)
            return True

        except Exception:
            return False

    def get_token_subject(self, token: str) -> str | None:
        """Extract subject (user ID) from token without full validation.

        Args:
            token: Token to extract subject from

        Returns:
            Token subject or None if not found
        """
        try:
            claims = self.jwt_handler.get_unverified_claims(token)
            return claims.get("sub")
        except Exception:
            return None

    def get_token_jti(self, token: str) -> str | None:
        """Extract JTI from token without full validation.

        Args:
            token: Token to extract JTI from

        Returns:
            Token JTI or None if not found
        """
        try:
            claims = self.jwt_handler.get_unverified_claims(token)
            return claims.get("jti")
        except Exception:
            return None

    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired without full validation.

        Args:
            token: Token to check

        Returns:
            True if token is expired, False otherwise
        """
        try:
            claims = self.jwt_handler.get_unverified_claims(token)
            exp = claims.get("exp")
            if exp:
                exp_datetime = datetime.fromtimestamp(exp)
                return datetime.utcnow() > exp_datetime
            return True  # No expiration claim means invalid
        except Exception:
            return True  # Invalid token is considered expired
