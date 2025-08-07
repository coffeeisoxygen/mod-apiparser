"""Repository for token blacklist persistence."""

import pathlib
from typing import Any

import yaml
from pydantic import ValidationError

from src.dependencies.dep_settings import get_settings
from src.domain.token.sch_token import TokenBlacklist
from src.exceptions.app_exceptions import AppException
from src.mlogger import get_logger

logger = get_logger(__name__)

# Get blacklist file path (we can add this as a setting later)
blacklist_path = pathlib.Path(get_settings().path_data) / "token_blacklist.yaml"


class TokenBlacklistRepository:
    """Repository for token blacklist persistence.

    This repository handles loading and saving blacklisted tokens to/from YAML files,
    with hot-reload capability using the existing file watcher system.
    """

    def __init__(self) -> None:
        """Initialize token blacklist repository."""
        logger.info(
            f"Initializing TokenBlacklistRepository with path: {blacklist_path}"
        )
        self.file_path = blacklist_path
        self._blacklist_entries: dict[str, TokenBlacklist] = {}
        self.reload()

    def _load_data_from_file(self) -> dict[str, TokenBlacklist]:
        """Load blacklist data from YAML file.

        Returns:
            Dictionary mapping JTI to TokenBlacklist entries
        """
        operation_logger = logger.bind(operation="load_blacklist_from_yaml")

        if not self.file_path.exists():
            operation_logger.debug(
                "Blacklist file does not exist, starting with empty blacklist"
            )
            return {}

        try:
            with open(self.file_path) as file:
                data: dict[str, list[dict[str, Any]]] = yaml.safe_load(file) or {}

                if "blacklisted_tokens" not in data:
                    operation_logger.debug("No blacklisted_tokens section in file")
                    return {}

                blacklist_dict = {}
                for token_data in data["blacklisted_tokens"]:
                    token_entry = TokenBlacklist(**token_data)
                    blacklist_dict[token_entry.jti] = token_entry

                operation_logger.debug(
                    f"Successfully loaded {len(blacklist_dict)} blacklisted tokens",
                    tokens_loaded=len(blacklist_dict),
                )
                return blacklist_dict

        except (ValidationError, Exception) as e:
            operation_logger.error(
                "Failed to load or validate blacklist YAML file",
                file=self.file_path,
                exception=e,
            )
            raise AppException.YamlReloadExceptionError(
                message="An error occurred while loading blacklist YAML file",
                context={"error_details": str(e)},
            ) from e

    def _save_data_to_file(self) -> None:
        """Save blacklist data to YAML file."""
        operation_logger = logger.bind(operation="save_blacklist_to_yaml")

        try:
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to YAML-serializable format
            data = {
                "blacklisted_tokens": [
                    entry.model_dump() for entry in self._blacklist_entries.values()
                ]
            }

            with open(self.file_path, "w") as file:
                yaml.safe_dump(data, file, default_flow_style=False, sort_keys=False)

            operation_logger.debug(
                f"Successfully saved {len(self._blacklist_entries)} blacklisted tokens",
                tokens_saved=len(self._blacklist_entries),
            )

        except Exception as e:
            operation_logger.error(
                "Failed to save blacklist to YAML file",
                file=self.file_path,
                exception=e,
            )
            raise AppException.YamlReloadExceptionError(
                message="An error occurred while saving blacklist YAML file",
                context={"error_details": str(e)},
            ) from e

    def reload(self) -> None:
        """Reload blacklist data from file."""
        logger.info("Starting TokenBlacklistRepository reload process")

        try:
            self._blacklist_entries = self._load_data_from_file()
            logger.info("TokenBlacklistRepository successfully reloaded")
        except AppException.YamlReloadExceptionError as e:
            logger.error(
                "Failed to reload blacklist data, using old data",
                error=e.message,
                context=e.context,
            )
        except Exception as e:
            logger.error(
                "Failed to reload blacklist data due to unexpected error, using old data",
                exception=e,
            )

    def add_token(self, token_entry: TokenBlacklist) -> None:
        """Add a token to the blacklist.

        Args:
            token_entry: TokenBlacklist entry to add
        """
        self._blacklist_entries[token_entry.jti] = token_entry
        self._save_data_to_file()
        logger.info(f"Added token to blacklist: {token_entry.jti}")

    def is_blacklisted(self, jti: str) -> bool:
        """Check if a token is blacklisted.

        Args:
            jti: JWT ID to check

        Returns:
            True if token is blacklisted
        """
        return jti in self._blacklist_entries

    def get_blacklist_entry(self, jti: str) -> TokenBlacklist | None:
        """Get blacklist entry by JTI.

        Args:
            jti: JWT ID to lookup

        Returns:
            TokenBlacklist entry or None if not found
        """
        return self._blacklist_entries.get(jti)

    def remove_token(self, jti: str) -> bool:
        """Remove a token from the blacklist.

        Args:
            jti: JWT ID to remove

        Returns:
            True if token was removed, False if not found
        """
        if jti in self._blacklist_entries:
            del self._blacklist_entries[jti]
            self._save_data_to_file()
            logger.info(f"Removed token from blacklist: {jti}")
            return True
        return False

    def get_user_tokens(self, user_id: str) -> list[TokenBlacklist]:
        """Get all blacklisted tokens for a user.

        Args:
            user_id: User ID to search for

        Returns:
            List of TokenBlacklist entries for the user
        """
        return [
            entry
            for entry in self._blacklist_entries.values()
            if str(entry.user_id) == str(user_id)
        ]

    def get_all_entries(self) -> dict[str, TokenBlacklist]:
        """Get all blacklisted tokens.

        Returns:
            Dictionary mapping JTI to TokenBlacklist entries
        """
        return self._blacklist_entries.copy()

    def get_stats(self) -> dict[str, int]:
        """Get blacklist statistics.

        Returns:
            Dictionary with blacklist statistics
        """
        stats = {
            "total": len(self._blacklist_entries),
            "access_tokens": 0,
            "refresh_tokens": 0,
        }

        for entry in self._blacklist_entries.values():
            if entry.token_type == "access":
                stats["access_tokens"] += 1
            elif entry.token_type == "refresh":
                stats["refresh_tokens"] += 1

        return stats

    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from blacklist (placeholder for future implementation).

        In a real implementation, this would check token expiration times
        and remove expired entries.

        Returns:
            Number of tokens removed
        """
        # Placeholder - in real implementation, we would:
        # 1. Check expiration times
        # 2. Remove expired tokens
        # 3. Save to file

        logger.debug("Blacklist cleanup completed (placeholder implementation)")
        return 0

    def clear_all(self) -> int:
        """Clear all blacklisted tokens.

        Returns:
            Number of tokens cleared
        """
        count = len(self._blacklist_entries)
        self._blacklist_entries.clear()
        self._save_data_to_file()
        logger.warning(f"Cleared all {count} blacklisted tokens")
        return count
