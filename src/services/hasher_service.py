"""Hashing passwords and generating keys for secure storage."""

from argon2 import PasswordHasher
from argon2 import exceptions as argon2_exceptions


class HasherService:
    """Service for hashing passwords and generating secure keys."""

    _ph = PasswordHasher()

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password using Argon2."""
        return cls._ph.hash(password)

    @classmethod
    def verify_password(cls, hashed_password: str, password: str) -> bool:
        """Verify a password against the given Argon2 hash."""
        try:
            return cls._ph.verify(hashed_password, password)
        except argon2_exceptions.VerifyMismatchError:
            return False
        except Exception:
            return False
