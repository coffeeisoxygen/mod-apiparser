"""Token blacklist management for security."""

from typing import TYPE_CHECKING
from uuid import UUID

from src.config.settings import JWTConfig
from src.domain.token.sch_token import TokenBlacklist
from src.mlogger import get_logger

if TYPE_CHECKING:
    from src.repos.rep_token_blacklist import TokenBlacklistRepository

logger = get_logger(__name__)


class TokenBlacklistManager:
    """Manages JWT token blacklisting for security.

    Provides functionality to blacklist tokens and check if tokens are blacklisted.
    Can use in-memory storage or persistent storage via TokenBlacklistRepository.
    """

    def __init__(
        self,
        jwt_config: JWTConfig,
        blacklist_repo: "TokenBlacklistRepository | None" = None,
    ) -> None:
        """Initialize blacklist manager.

        Args:
            jwt_config: JWT configuration from settings
            blacklist_repo: Optional repository for persistent storage
        """
        self.config = jwt_config
        self.blacklist_repo = blacklist_repo
        self._enabled = jwt_config.blacklist_enabled

        # In-memory storage - used when no repository is provided
        self._blacklist: set[str] = set()
        self._blacklist_entries: dict[str, TokenBlacklist] = {}

        storage_type = "persistent" if blacklist_repo else "in-memory"
        logger.info(
            f"TokenBlacklistManager initialized (enabled: {self._enabled}, storage: {storage_type})"
        )

    @property
    def enabled(self) -> bool:
        """Check if blacklisting is enabled.

        Returns:
            True if blacklisting is enabled
        """
        return self._enabled

    def blacklist_token(
        self, jti: str, user_id: str | UUID, token_type: str, reason: str | None = None
    ) -> None:
        """Add a token to the blacklist.

        Args:
            jti: JWT ID from the token
            user_id: ID of the user who owns the token
            token_type: Type of token (access, refresh)
            reason: Optional reason for blacklisting
        """
        if not self._enabled:
            logger.debug("Blacklisting is disabled, skipping token blacklist")
            return

        if not jti:
            logger.warning("Cannot blacklist token: JTI is empty")
            return

        # Check if already blacklisted
        if self.is_blacklisted(jti):
            logger.debug(f"Token already blacklisted: {jti}")
            return

        # Create blacklist entry
        blacklist_entry = TokenBlacklist(
            jti=jti,
            user_id=user_id,
            token_type=token_type,
            reason=reason,
        )

        # Add to blacklist
        if self.blacklist_repo:
            # Use repository for persistent storage
            self.blacklist_repo.add_token(blacklist_entry)
        else:
            # Use in-memory storage
            self._blacklist.add(jti)
            self._blacklist_entries[jti] = blacklist_entry

        logger.info(
            "Token blacklisted",
            jti=jti,
            user_id=user_id,
            token_type=token_type,
            reason=reason,
        )

    def is_blacklisted(self, jti: str) -> bool:
        """Check if a token is blacklisted.

        Args:
            jti: JWT ID to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        if not self._enabled:
            return False

        if not jti:
            return False

        if self.blacklist_repo:
            # Check in repository
            is_blacklisted = self.blacklist_repo.is_blacklisted(jti)
        else:
            # Check in-memory storage
            is_blacklisted = jti in self._blacklist

        if is_blacklisted:
            logger.debug(f"Token is blacklisted: {jti}")

        return is_blacklisted

    def remove_from_blacklist(self, jti: str) -> bool:
        """Remove a token from the blacklist.

        Args:
            jti: JWT ID to remove

        Returns:
            True if token was removed, False if not found
        """
        if not self._enabled:
            return False

        if jti in self._blacklist:
            self._blacklist.remove(jti)
            self._blacklist_entries.pop(jti, None)
            logger.info(f"Token removed from blacklist: {jti}")
            return True

        return False

    def get_blacklist_entry(self, jti: str) -> TokenBlacklist | None:
        """Get blacklist entry details.

        Args:
            jti: JWT ID to lookup

        Returns:
            TokenBlacklist entry or None if not found
        """
        return self._blacklist_entries.get(jti)

    def blacklist_user_tokens(
        self, user_id: str | UUID, reason: str | None = None
    ) -> int:
        """Blacklist all tokens for a specific user.

        Useful for user logout or account security events.

        Args:
            user_id: User ID whose tokens should be blacklisted
            reason: Reason for blacklisting

        Returns:
            Number of tokens blacklisted
        """
        if not self._enabled:
            return 0

        count = 0
        tokens_to_blacklist = []

        # Find all tokens for the user
        for jti, entry in self._blacklist_entries.items():
            if str(entry.user_id) == str(user_id):
                tokens_to_blacklist.append(jti)

        # Blacklist found tokens
        for jti in tokens_to_blacklist:
            if jti not in self._blacklist:
                entry = self._blacklist_entries[jti]
                self.blacklist_token(
                    jti=jti,
                    user_id=entry.user_id,
                    token_type=entry.token_type,
                    reason=reason or f"User logout: {user_id}",
                )
                count += 1

        logger.info(f"Blacklisted {count} tokens for user: {user_id}")
        return count

    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from blacklist.

        This method should be called periodically to clean up expired tokens
        that no longer need to be tracked.

        Returns:
            Number of expired tokens removed
        """
        if not self._enabled:
            return 0

        # In a real implementation, we would check token expiration times
        # For now, this is a placeholder that can be extended when we have
        # proper token expiration tracking
        expired_jtis = []

        # Remove expired entries
        removed_count = 0
        for jti in expired_jtis:
            if self.remove_from_blacklist(jti):
                removed_count += 1

        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} expired tokens from blacklist")

        return removed_count

    def get_blacklist_size(self) -> int:
        """Get the current size of the blacklist.

        Returns:
            Number of blacklisted tokens
        """
        return len(self._blacklist)

    def get_blacklist_stats(self) -> dict[str, int]:
        """Get blacklist statistics.

        Returns:
            Dictionary with blacklist statistics
        """
        if not self._enabled:
            return {"enabled": False, "total": 0}

        stats = {
            "enabled": True,
            "total": len(self._blacklist),
            "access_tokens": 0,
            "refresh_tokens": 0,
        }

        # Count by token type
        for entry in self._blacklist_entries.values():
            if entry.token_type == "access":
                stats["access_tokens"] += 1
            elif entry.token_type == "refresh":
                stats["refresh_tokens"] += 1

        return stats

    def clear_blacklist(self) -> int:
        """Clear all blacklisted tokens.

        Warning: This removes all blacklisted tokens and should be used carefully.

        Returns:
            Number of tokens cleared
        """
        if not self._enabled:
            return 0

        count = len(self._blacklist)
        self._blacklist.clear()
        self._blacklist_entries.clear()

        logger.warning(f"Cleared {count} tokens from blacklist")
        return count
