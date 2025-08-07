"""Key management for JWT tokens."""

import secrets
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from src.config.settings import JWTConfig
from src.exceptions.app_exceptions import AppException
from src.mlogger import get_logger

logger = get_logger(__name__)


class KeyManager:
    """Manages JWT signing and verification keys.

    Supports both symmetric (HS256) and asymmetric (RS256) algorithms.
    Keys are generated automatically if not found.
    """

    def __init__(self, jwt_config: JWTConfig) -> None:
        """Initialize key manager with JWT configuration.

        Args:
            jwt_config: JWT configuration from settings
        """
        self.config = jwt_config
        self.algorithm = jwt_config.algorithm.upper()
        self._signing_key: str | bytes | None = None
        self._verification_key: str | bytes | None = None

        logger.info(f"Initializing KeyManager with algorithm: {self.algorithm}")
        self._setup_keys()

    def _setup_keys(self) -> None:
        """Setup keys based on algorithm type."""
        if self.algorithm.startswith("HS"):
            self._setup_symmetric_keys()
        elif self.algorithm.startswith("RS"):
            self._setup_asymmetric_keys()
        else:
            raise AppException.TokenServiceError(
                f"Unsupported algorithm: {self.algorithm}"
            )

    def _setup_symmetric_keys(self) -> None:
        """Setup symmetric keys for HMAC algorithms (HS256, HS384, HS512)."""
        logger.debug("Setting up symmetric keys for HMAC algorithm")

        # Use secret key from config, or generate new one
        if (
            self.config.secret_key
            and self.config.secret_key != "default-jwt-secret-key"
        ):
            self._signing_key = self.config.secret_key.encode()
            self._verification_key = self._signing_key
            logger.debug("Using secret key from configuration")
        else:
            # Generate and save new key
            self._signing_key = self._generate_symmetric_key()
            self._verification_key = self._signing_key
            logger.info("Generated new symmetric key")

    def _setup_asymmetric_keys(self) -> None:
        """Setup asymmetric keys for RSA algorithms (RS256, RS384, RS512)."""
        logger.debug("Setting up asymmetric keys for RSA algorithm")

        private_key_path = Path(self.config.private_key_path)
        public_key_path = Path(self.config.public_key_path)

        try:
            if private_key_path.exists() and public_key_path.exists():
                self._load_rsa_keys(private_key_path, public_key_path)
                logger.debug("Loaded existing RSA keys")
            else:
                self._generate_rsa_keys(private_key_path, public_key_path)
                logger.info("Generated new RSA key pair")
        except Exception as e:
            logger.error(f"Failed to setup RSA keys: {e}")
            raise AppException.TokenServiceError(f"RSA key setup failed: {e}") from e

    def _generate_symmetric_key(self) -> bytes:
        """Generate a secure symmetric key."""
        # Generate 256-bit (32 bytes) key for maximum security
        key = secrets.token_bytes(32)
        logger.debug("Generated 256-bit symmetric key")
        return key

    def _generate_rsa_keys(self, private_path: Path, public_path: Path) -> None:
        """Generate RSA key pair and save to files.

        Args:
            private_path: Path to save private key
            public_path: Path to save public key
        """
        logger.info(f"Generating RSA {self.config.key_size}-bit key pair...")

        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.config.key_size,
        )

        # Get public key
        public_key = private_key.public_key()

        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Ensure directories exist
        private_path.parent.mkdir(parents=True, exist_ok=True)
        public_path.parent.mkdir(parents=True, exist_ok=True)

        # Save keys to files
        with open(private_path, "wb") as f:
            f.write(private_pem)

        with open(public_path, "wb") as f:
            f.write(public_pem)

        self._signing_key = private_pem
        self._verification_key = public_pem

        logger.info(f"RSA keys saved to: {private_path.parent}")

    def _load_rsa_keys(self, private_path: Path, public_path: Path) -> None:
        """Load RSA keys from files.

        Args:
            private_path: Path to private key file
            public_path: Path to public key file
        """
        try:
            with open(private_path, "rb") as f:
                self._signing_key = f.read()

            with open(public_path, "rb") as f:
                self._verification_key = f.read()

            logger.debug("Successfully loaded RSA keys from files")

        except FileNotFoundError as e:
            logger.error(f"RSA key files not found: {e}")
            raise AppException.TokenServiceError(f"RSA key files not found: {e}") from e

    def get_signing_key(self) -> str | bytes:
        """Get the signing key for token creation.

        Returns:
            Signing key (private key for RSA, secret key for HMAC)
        """
        if self._signing_key is None:
            raise AppException.TokenServiceError("Signing key not initialized")
        return self._signing_key

    def get_verification_key(self) -> str | bytes:
        """Get the verification key for token validation.

        Returns:
            Verification key (public key for RSA, secret key for HMAC)
        """
        if self._verification_key is None:
            raise AppException.TokenServiceError("Verification key not initialized")
        return self._verification_key

    def get_algorithm(self) -> str:
        """Get the JWT algorithm.

        Returns:
            JWT algorithm string
        """
        return self.algorithm

    def rotate_keys(self) -> None:
        """Rotate keys (generate new ones).

        Note: This will invalidate all existing tokens.
        """
        logger.warning("Rotating keys - this will invalidate all existing tokens")

        if self.algorithm.startswith("HS"):
            self._signing_key = self._generate_symmetric_key()
            self._verification_key = self._signing_key
        elif self.algorithm.startswith("RS"):
            private_path = Path(self.config.private_key_path)
            public_path = Path(self.config.public_key_path)
            self._generate_rsa_keys(private_path, public_path)

        logger.info("Key rotation completed")
