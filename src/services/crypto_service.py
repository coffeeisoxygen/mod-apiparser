# services/crypto_service.py
import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoService:
    """Service untuk encrypt/decrypt data accounts"""

    def __init__(self, password: str = None):
        self.password = password or os.getenv(
            "ACCOUNTS_PASSWORD", "default-key-change-me"
        )
        self._key = None

    def _generate_key(self, salt: bytes = None) -> bytes:
        """Generate encryption key dari password"""
        if salt is None:
            salt = b"salt_1234567890"  # In production, use random salt

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        return key

    @property
    def key(self) -> bytes:
        """Lazy loading untuk encryption key"""
        if self._key is None:
            self._key = self._generate_key()
        return self._key

    def encrypt(self, data: str | bytes) -> str:
        """Encrypt data dan return base64 encoded string"""
        if isinstance(data, str):
            data = data.encode("utf-8")

        fernet = Fernet(self.key)
        encrypted_data = fernet.encrypt(data)
        return base64.b64encode(encrypted_data).decode("utf-8")

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded string"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode("utf-8"))
            fernet = Fernet(self.key)
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {e}")
