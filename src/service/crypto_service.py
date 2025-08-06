"""Secure crypto service for encrypt/decrypt operations."""

import base64

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.dependencies.dep_settings import get_security_config


class CryptoServiceError(Exception):
    """Base exception for crypto service errors."""

    pass


class CryptoService:
    """Service untuk encrypt/decrypt data accounts dengan Fernet."""

    def __init__(self, key: str | None = None):
        """Initialize with proper Fernet key handling."""
        # Get key from config if not provided
        config_key = key or get_security_config().secret_key

        # Generate proper Fernet key from config key
        self._fernet_key = self._derive_fernet_key(config_key)
        self._fernet = Fernet(self._fernet_key)

    def _derive_fernet_key(self, input_key: str) -> bytes:
        """Derive proper 32-byte Fernet key from input string."""
        # Use PBKDF2 to derive proper key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # Fernet requires 32 bytes
            salt=b"otomax_salt_2024",  # Static salt (could be configurable)
            iterations=100000,
        )

        key_bytes = kdf.derive(input_key.encode("utf-8"))
        return base64.urlsafe_b64encode(key_bytes)

    def encrypt(self, data: str | bytes) -> str:
        """Encrypt data and return URL-safe base64 string."""
        try:
            if isinstance(data, str):
                data = data.encode("utf-8")

            # Fernet.encrypt() already returns base64-encoded bytes
            encrypted_data = self._fernet.encrypt(data)

            # Convert bytes to string (already base64-encoded)
            return encrypted_data.decode("utf-8")

        except Exception as e:
            raise CryptoServiceError(f"Encryption failed: {e}") from e

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt Fernet-encrypted base64 string."""
        try:
            # Fernet.decrypt() expects base64-encoded bytes
            encrypted_bytes = encrypted_data.encode("utf-8")
            decrypted_data = self._fernet.decrypt(encrypted_bytes)

            return decrypted_data.decode("utf-8")

        except InvalidToken as e:
            raise CryptoServiceError("Invalid token or corrupted data") from e
        except Exception as e:
            raise CryptoServiceError(f"Decryption failed: {e}") from e

    @classmethod
    def generate_key(cls) -> str:
        """Generate a new Fernet key for configuration."""
        key = Fernet.generate_key()
        return key.decode("utf-8")

    def is_encrypted(self, data: str) -> bool:
        """Check if data appears to be Fernet-encrypted."""
        try:
            # Try to decrypt - if successful, it's encrypted
            self.decrypt(data)
        except CryptoServiceError:
            return False
        else:
            return True
