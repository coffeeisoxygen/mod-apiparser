"""JWT token handling operations."""

import time
import uuid
from datetime import datetime, timedelta
from typing import Any

from jose import JOSEError, jwt

from src.config.settings import JWTConfig
from src.domain.token.sch_token import TokenPayload
from src.exceptions.app_exceptions import AppException
from src.mlogger import get_logger
from src.service.token.key_manager import KeyManager

logger = get_logger(__name__)


class JWTHandler:
    """Pure JWT encoding and decoding operations.

    This class handles the technical aspects of JWT tokens without business logic.
    It focuses solely on JWT creation, parsing, and validation.
    """

    def __init__(self, jwt_config: JWTConfig, key_manager: KeyManager) -> None:
        """Initialize JWT handler.

        Args:
            jwt_config: JWT configuration from settings
            key_manager: Key manager for signing and verification
        """
        self.config = jwt_config
        self.key_manager = key_manager
        logger.info(
            f"JWTHandler initialized with algorithm: {key_manager.get_algorithm()}"
        )

    def encode_token(self, payload: dict[str, Any]) -> str:
        """Encode a JWT token from payload.

        Args:
            payload: Token payload dictionary

        Returns:
            Encoded JWT token string

        Raises:
            AppException.TokenServiceError: If encoding fails
        """
        try:
            # Add standard JWT claims if not present
            current_time = int(time.time())

            # Ensure required claims are present
            if "iat" not in payload:
                payload["iat"] = current_time
            if "jti" not in payload:
                payload["jti"] = str(uuid.uuid4())
            if "iss" not in payload:
                payload["iss"] = self.config.issuer
            if "aud" not in payload:
                payload["aud"] = self.config.audience

            signing_key = self.key_manager.get_signing_key()
            algorithm = self.key_manager.get_algorithm()

            token = jwt.encode(
                payload,
                signing_key,
                algorithm=algorithm,
            )

            logger.debug(
                "Token encoded successfully",
                subject=payload.get("sub"),
                token_type=payload.get("token_type"),
                jti=payload.get("jti"),
            )

            return token

        except Exception as e:
            logger.error(f"Failed to encode token: {e}", payload=payload)
            raise AppException.TokenServiceError(f"Token encoding failed: {e}") from e

    def decode_token(self, token: str, verify: bool = True) -> dict[str, Any]:
        """Decode and verify a JWT token.

        Args:
            token: JWT token string to decode
            verify: Whether to verify the token signature and claims

        Returns:
            Decoded token payload

        Raises:
            AppException.TokenExpiredError: If token is expired
            AppException.TokenInvalidError: If token is invalid
        """
        try:
            if not token:
                raise AppException.TokenInvalidError("Token is required")

            verification_key = self.key_manager.get_verification_key()
            algorithm = self.key_manager.get_algorithm()

            options = {
                "verify_signature": verify and self.config.verify_signature,
                "verify_aud": verify and self.config.verify_audience,
                "verify_iss": verify and self.config.verify_issuer,
                "verify_exp": verify and self.config.verify_expiration,
            }

            # Set audience and issuer for verification if enabled
            audience = self.config.audience if self.config.verify_audience else None
            issuer = self.config.issuer if self.config.verify_issuer else None

            payload = jwt.decode(
                token,
                verification_key,
                algorithms=[algorithm],
                audience=audience,
                issuer=issuer,
                options=options,
            )

            logger.debug(
                "Token decoded successfully",
                subject=payload.get("sub"),
                token_type=payload.get("token_type"),
                jti=payload.get("jti"),
            )

            return payload

        except JOSEError as e:
            error_msg = str(e).lower()
            if "expired" in error_msg:
                logger.warning(f"Token expired: {e}")
                raise AppException.TokenExpiredError("Token has expired") from e
            else:
                logger.warning(f"Token validation failed: {e}")
                raise AppException.TokenInvalidError(f"Invalid token: {e}") from e

        except Exception as e:
            logger.error(f"Unexpected error during token decoding: {e}")
            raise AppException.TokenServiceError(f"Token decoding failed: {e}") from e

    def get_unverified_claims(self, token: str) -> dict[str, Any]:
        """Get token claims without verification.

        Useful for extracting token information for blacklisting or debugging.

        Args:
            token: JWT token string

        Returns:
            Unverified token claims

        Raises:
            AppException.TokenInvalidError: If token format is invalid
        """
        try:
            return self.decode_token(token, verify=False)
        except AppException.TokenExpiredError:
            # For unverified claims, we don't care about expiration
            return jwt.get_unverified_claims(token)
        except Exception as e:
            logger.error(f"Failed to get unverified claims: {e}")
            raise AppException.TokenInvalidError(f"Invalid token format: {e}") from e

    def create_access_token(
        self,
        subject: str,
        extra_claims: dict[str, Any] | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create an access token.

        Args:
            subject: Token subject (usually user ID)
            extra_claims: Additional claims to include
            expires_delta: Custom expiration time

        Returns:
            Encoded access token
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.config.access_token_expire_minutes)

        return self._create_token(
            subject=subject,
            token_type="access",
            expires_delta=expires_delta,
            extra_claims=extra_claims,
        )

    def create_refresh_token(
        self,
        subject: str,
        extra_claims: dict[str, Any] | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a refresh token.

        Args:
            subject: Token subject (usually user ID)
            extra_claims: Additional claims to include
            expires_delta: Custom expiration time

        Returns:
            Encoded refresh token
        """
        if expires_delta is None:
            expires_delta = timedelta(days=self.config.refresh_token_expire_days)

        return self._create_token(
            subject=subject,
            token_type="refresh",
            expires_delta=expires_delta,
            extra_claims=extra_claims,
        )

    def _create_token(
        self,
        subject: str,
        token_type: str,
        expires_delta: timedelta,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """Create a token with specified parameters.

        Args:
            subject: Token subject
            token_type: Type of token (access, refresh)
            expires_delta: Token expiration time
            extra_claims: Additional claims

        Returns:
            Encoded JWT token
        """
        current_time = datetime.utcnow()
        expire_time = current_time + expires_delta

        payload = {
            "sub": subject,
            "token_type": token_type,
            "exp": int(expire_time.timestamp()),
            "iat": int(current_time.timestamp()),
            "jti": str(uuid.uuid4()),
            "iss": self.config.issuer,
            "aud": self.config.audience,
        }

        if extra_claims:
            payload.update(extra_claims)

        return self.encode_token(payload)

    def validate_token_payload(self, payload: dict[str, Any]) -> TokenPayload:
        """Validate and convert payload to TokenPayload schema.

        Args:
            payload: Token payload dictionary

        Returns:
            Validated TokenPayload instance

        Raises:
            AppException.TokenInvalidError: If payload validation fails
        """
        try:
            return TokenPayload(**payload)
        except Exception as e:
            logger.error(f"Token payload validation failed: {e}", payload=payload)
            raise AppException.TokenInvalidError(f"Invalid token payload: {e}") from e

    def get_token_expiry(self, token: str) -> datetime | None:
        """Get token expiration time.

        Args:
            token: JWT token string

        Returns:
            Token expiration datetime or None if not found
        """
        try:
            claims = self.get_unverified_claims(token)
            exp_timestamp = claims.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
            return None
        except Exception:
            return None

    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired.

        Args:
            token: JWT token string

        Returns:
            True if token is expired, False otherwise
        """
        expiry = self.get_token_expiry(token)
        if expiry is None:
            return True
        return datetime.utcnow() > expiry
