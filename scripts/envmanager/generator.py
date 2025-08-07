"""This module provides the EnvFileGenerator class.

which is responsible for creating the content of an environment file based on a given configuration.
"""

import secrets

from cryptography.fernet import Fernet


class EnvFileGenerator:
    """Generates the content for an environment file."""

    def __init__(self, base_config: dict, overrides: dict):
        self.config = base_config.copy()
        self.config.update(overrides)
        self._secure_keys = {}

    def _generate_secure_keys(self):
        """Generate all necessary secure keys."""
        self._secure_keys = {
            "fernet_key": Fernet.generate_key().decode(),
            "jwt_secret_dev": secrets.token_urlsafe(32),
            "jwt_secret_prod": secrets.token_urlsafe(64),
            "jwt_secret_test": "test-jwt-secret-key-2024",
            "security_secret_dev": secrets.token_urlsafe(32),
            "security_secret_prod": secrets.token_urlsafe(64),
            "security_secret_test": "test-secret-key-2024",
        }

    def _inject_security_keys(self, env_type: str):
        """Inject the correct security keys based on the environment type."""
        if env_type == "prod":
            self.config["SECURITY_SECRET_KEY"] = (
                f"${{PROD_SECURITY_SECRET_KEY:-{self._secure_keys['security_secret_prod']}}}"
            )
            self.config["JWT_SECRET_KEY"] = (
                f"${{PROD_JWT_SECRET_KEY:-{self._secure_keys['jwt_secret_prod']}}}"
            )
        elif env_type == "test":
            self.config["SECURITY_SECRET_KEY"] = self._secure_keys[
                "security_secret_test"
            ]
            self.config["JWT_SECRET_KEY"] = self._secure_keys["jwt_secret_test"]
        else:  # dev and base
            self.config["SECURITY_SECRET_KEY"] = self._secure_keys[
                "security_secret_dev"
            ]
            self.config["JWT_SECRET_KEY"] = self._secure_keys["jwt_secret_dev"]

    def _format_section(self, title: str, keys: list[str]) -> str:
        """Formats a section of the .env file."""
        lines = [
            "# ============================================================================",
            f"# {title}",
            "# ============================================================================",
        ]
        lines.extend(f"{key}={self.config[key]}" for key in keys if key in self.config)
        return "\n".join(lines)

    def generate_content(self, env_type: str) -> str:
        """Generates the full .env file content for a given environment."""
        self._generate_secure_keys()
        self._inject_security_keys(env_type)

        sections = {
            "APPLICATION SETTINGS": [
                "APP_DEBUG",
                "APP_ENV",
                "APP_SERVICE",
                "APP_VERSION",
            ],
            "SECURITY & ENCRYPTION": ["SECURITY_SECRET_KEY", "SECURITY_ALGORITHM"],
            "JWT TOKEN SETTINGS": [
                "JWT_ALGORITHM",
                "JWT_SECRET_KEY",
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
                "JWT_REFRESH_TOKEN_EXPIRE_DAYS",
                "JWT_ISSUER",
                "JWT_AUDIENCE",
                "JWT_PRIVATE_KEY_PATH",
                "JWT_PUBLIC_KEY_PATH",
                "JWT_KEY_SIZE",
                "JWT_VERIFY_SIGNATURE",
                "JWT_VERIFY_AUDIENCE",
                "JWT_VERIFY_ISSUER",
                "JWT_VERIFY_EXPIRATION",
                "JWT_BLACKLIST_ENABLED",
                "JWT_BLACKLIST_TOKEN_CHECKS",
            ],
            "FILE PATHS": ["PATH_USERS", "PATH_KEYS"],
            "PRODUCTION SECURITY": [
                "JWT_REQUIRE_HTTPS",
                "JWT_COOKIE_SECURE",
                "JWT_COOKIE_SAMESITE",
            ],
        }

        content_parts = []
        for title, keys in sections.items():
            content_parts.append(self._format_section(title, keys))

        # Add special note for production
        if env_type == "prod":
            prod_secrets_note = f'''
# =============================================================================
# PRODUCTION SECRETS (set these as environment variables)
# =============================================================================
# export PROD_SECURITY_SECRET_KEY="{self._secure_keys["security_secret_prod"]}"
# export PROD_JWT_SECRET_KEY="{self._secure_keys["jwt_secret_prod"]}"'''
            content_parts.append(prod_secrets_note)

        return "\n\n".join(content_parts) + "\n"
