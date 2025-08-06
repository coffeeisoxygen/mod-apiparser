"""Advanced token service using Authlib for robust JWT handling."""

import secrets
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from authlib.jose import JsonWebSignature, JsonWebToken
from authlib.jose.errors import JoseError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from dependencies.dep_settings import get_settings
from src.mlogger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class TokenServiceError(Exception):
    """Base exception for token service errors."""

    pass


class TokenExpiredError(TokenServiceError):
    """Token has expired."""

    pass


class TokenInvalidError(TokenServiceError):
    """Token is invalid."""

    pass


class AdvancedTokenService:
    """Advanced JWT token service with configuration-driven setup."""

    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str | None = None,
        issuer: str | None = None,
        audience: str | None = None,
        access_token_expire_minutes: int | None = None,
        refresh_token_expire_days: int | None = None,
        key_file_path: Path | None = None,
    ):
        """Initialize advanced token service with settings."""
        # Use settings with fallbacks
        self.algorithm = algorithm or settings.jwt_algorithm
        self.issuer = issuer or settings.jwt_issuer
        self.audience = audience or settings.jwt_audience
        self.access_token_expire_minutes = (
            access_token_expire_minutes or settings.jwt_access_token_expire_minutes
        )
        self.refresh_token_expire_days = (
            refresh_token_expire_days or settings.jwt_refresh_token_expire_days
        )

        # Initialize JWT handler
        self.jwt = JsonWebToken([self.algorithm])
        self.jws = JsonWebSignature([self.algorithm])

        # Token blacklist (configurable)
        self._blacklist: set[str] = set()
        self._blacklist_enabled = settings.jwt_blacklist_enabled

        # Setup keys based on algorithm
        key_path = key_file_path or settings.jwt_key_file_path
        secret = secret_key or settings.effective_jwt_secret
        self._setup_keys(secret, key_path)

        logger.info(f"TokenService initialized with algorithm: {self.algorithm}")

    def _setup_keys(self, secret_key: str | None, key_file_path: Path) -> None:
        """Setup signing keys based on algorithm."""
        if self.algorithm.startswith("HS"):
            # HMAC algorithms
            self.secret_key = secret_key or self._generate_secret_key()
            self.public_key = None
            logger.debug("Using HMAC algorithm with secret key")

        elif self.algorithm.startswith("RS") or self.algorithm.startswith("ES"):
            # RSA/ECDSA algorithms
            if key_file_path.exists():
                self._load_rsa_keys(key_file_path)
                logger.debug(f"Loaded RSA keys from: {key_file_path}")
            else:
                self._generate_rsa_keys(key_file_path)
                logger.info(f"Generated new RSA keys at: {key_file_path}")
        else:
            raise TokenServiceError(f"Unsupported algorithm: {self.algorithm}")

    def _generate_secret_key(self) -> str:
        """Generate a cryptographically secure secret key."""
        key = secrets.token_urlsafe(32)
        logger.warning(
            "Generated new secret key. In production, set JWT_SECRET_KEY in environment!"
        )
        return key

    def _generate_rsa_keys(self, save_path: Path) -> None:
        """Generate RSA key pair for RS256/RS512 algorithms."""
        logger.info("Generating new RSA key pair...")

        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=settings.jwt_key_size,
        )

        # Get public key
        public_key = private_key.public_key()

        # Serialize keys
        self.secret_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        self.public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Save to file
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path.with_suffix(".pem"), "wb") as f:
            f.write(self.secret_key)

        with open(save_path.with_suffix(".pub"), "wb") as f:
            f.write(self.public_key)

        logger.info(f"RSA keys saved to: {save_path}")

    def _load_rsa_keys(self, key_file_path: Path) -> None:
        """Load RSA keys from file."""
        try:
            with open(key_file_path.with_suffix(".pem"), "rb") as f:
                self.secret_key = f.read()

            with open(key_file_path.with_suffix(".pub"), "rb") as f:
                self.public_key = f.read()

        except FileNotFoundError as e:
            logger.error(f"Key files not found: {e}")
            raise TokenServiceError(f"Key files not found: {e}")

    def verify_token(
        self,
        token: str,
        expected_type: str = "access",
        verify_signature: bool | None = None,
    ) -> dict[str, Any]:
        """Verify and decode JWT token with configuration-driven validation."""
        if not token:
            raise TokenInvalidError("Token is required")

        # Check blacklist (if enabled)
        if self._blacklist_enabled and self._is_blacklisted(token):
            raise TokenInvalidError("Token has been revoked")

        try:
            # Use configuration for verification options
            verification_key = self.public_key or self.secret_key
            verify_sig = (
                verify_signature
                if verify_signature is not None
                else settings.jwt_verify_signature
            )

            # Decode and verify token
            claims = self.jwt.decode(
                token,
                key=verification_key,
                claims_options={
                    "verify_signature": verify_sig,
                    "verify_aud": settings.jwt_verify_audience,
                    "verify_iss": settings.jwt_verify_issuer,
                    "verify_exp": settings.jwt_verify_expiration,
                },
            )

            # Validate claims
            claims.validate()

            # Check token type
            if claims.get("token_type") != expected_type:
                raise TokenInvalidError(f"Expected {expected_type} token")

            # Check audience (if verification enabled)
            if settings.jwt_verify_audience and claims.get("aud") != self.audience:
                raise TokenInvalidError("Invalid audience")

            # Check issuer (if verification enabled)
            if settings.jwt_verify_issuer and claims.get("iss") != self.issuer:
                raise TokenInvalidError("Invalid issuer")

            logger.debug(
                f"Token verified successfully for subject: {claims.get('sub')}"
            )
            return dict(claims)

        except JoseError as e:
            logger.warning(f"Token verification failed: {e}")
            if "expired" in str(e).lower():
                raise TokenExpiredError("Token has expired")
            else:
                raise TokenInvalidError(f"Invalid token: {e}")

    def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        """Create new access token from valid refresh token."""
        # Verify refresh token
        claims = self.verify_token(refresh_token, expected_type="refresh")

        # Extract subject and relevant claims
        subject = claims["sub"]
        extra_claims = {
            k: v
            for k, v in claims.items()
            if k not in ["sub", "iss", "aud", "iat", "exp", "jti", "token_type"]
        }

        # Create new tokens
        new_access_token = self.create_access_token(subject, extra_claims)
        new_refresh_token = self.create_refresh_token(subject, extra_claims)

        # Blacklist old refresh token
        self.blacklist_token(refresh_token)

        logger.info(f"Tokens refreshed for subject: {subject}")
        return new_access_token, new_refresh_token

    def blacklist_token(self, token: str) -> None:
        """Add token to blacklist."""
        try:
            claims = self.jwt.decode(
                token,
                key=self.secret_key,
                options={
                    "verify_signature": False,  # Don't verify for blacklisting
                    "verify_exp": False,  # Allow expired tokens to be blacklisted
                },
            )

            jti = claims.get("jti")
            if jti:
                self._blacklist.add(jti)
                logger.info(f"Token blacklisted: {jti}")

        except Exception as e:
            logger.warning(f"Failed to blacklist token: {e}")

    def _is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        try:
            claims = self.jwt.decode(
                token,
                key=self.secret_key,
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                },
            )

            jti = claims.get("jti")
            return jti in self._blacklist if jti else False

        except Exception:
            return False

    def get_token_info(self, token: str) -> dict[str, Any]:
        """Get token information without verification."""
        try:
            claims = self.jwt.decode(
                token,
                key=self.secret_key,
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                },
            )

            return {
                "subject": claims.get("sub"),
                "issued_at": datetime.fromtimestamp(claims.get("iat", 0), UTC),
                "expires_at": datetime.fromtimestamp(claims.get("exp", 0), UTC),
                "token_type": claims.get("token_type"),
                "jti": claims.get("jti"),
                "is_expired": datetime.now(UTC)
                > datetime.fromtimestamp(claims.get("exp", 0), UTC),
                "is_blacklisted": self._is_blacklisted(token),
            }

        except Exception as e:
            logger.error(f"Failed to get token info: {e}")
            return {}

    def cleanup_blacklist(self) -> None:
        """Remove expired tokens from blacklist (call periodically)."""
        # In production, implement with database/Redis expiration
        # This is a basic in-memory implementation
        current_time = int(time.time())
        expired_tokens = set()

        for jti in self._blacklist:
            # This would need token lookup in production
            # For now, keep all tokens (implement proper cleanup in production)
            pass

        logger.info("Blacklist cleanup completed")


# Factory function with settings
def create_token_service() -> AdvancedTokenService:
    """Create token service with settings configuration."""
    return AdvancedTokenService()


# Global token service instance
_token_service: AdvancedTokenService | None = None


def get_token_service() -> AdvancedTokenService:
    """Get global token service instance."""
    global _token_service
    if _token_service is None:
        _token_service = create_token_service()
    return _token_service
