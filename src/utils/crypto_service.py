import base64

from cryptography.fernet import Fernet

from src.dependencies.dep_settings import get_settings

secret_key_value = get_settings().secret_key


class CryptoService:
    """Service untuk encrypt/decrypt data accounts."""

    def __init__(self, key: str | None = None):
        # Use Fernet key from config, or optionally from argument
        self._fernet_key = (key or secret_key_value).encode("utf-8")
        self._fernet = Fernet(self._fernet_key)

    def encrypt(self, data: str | bytes) -> str:
        """Encrypt data dan return base64 encoded string."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        encrypted_data = self._fernet.encrypt(data)
        return base64.b64encode(encrypted_data).decode("utf-8")

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded string."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode("utf-8"))
            decrypted_data = self._fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {e}") from e
