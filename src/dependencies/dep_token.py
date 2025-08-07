"""Token service dependencies for FastAPI."""

from typing import Annotated

from fastapi import Depends

from src.config.settings import JWTConfig
from src.dependencies.dep_settings import get_settings
from src.mlogger import get_logger
from src.repos.rep_user import UserRepository
from src.service.token.jwt_handler import JWTHandler
from src.service.token.key_manager import KeyManager
from src.service.token.token_blacklist import TokenBlacklistManager
from src.service.token.token_service import TokenService
from src.service.token.token_validator import TokenValidator

logger = get_logger(__name__)

# Global instances (singleton pattern)
_key_manager: KeyManager | None = None
_jwt_handler: JWTHandler | None = None
_blacklist_manager: TokenBlacklistManager | None = None
_token_validator: TokenValidator | None = None
_token_service: TokenService | None = None


def get_jwt_config() -> JWTConfig:
    """Get JWT configuration from settings.

    Returns:
        JWT configuration
    """
    return get_settings().jwt


def get_key_manager(
    jwt_config: Annotated[JWTConfig, Depends(get_jwt_config)],
) -> KeyManager:
    """Get or create KeyManager instance.

    Args:
        jwt_config: JWT configuration

    Returns:
        KeyManager instance
    """
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyManager(jwt_config=jwt_config)
        logger.info("KeyManager instance created")
    return _key_manager


def get_jwt_handler(
    jwt_config: Annotated[JWTConfig, Depends(get_jwt_config)],
    key_manager: Annotated[KeyManager, Depends(get_key_manager)],
) -> JWTHandler:
    """Get or create JWTHandler instance.

    Args:
        jwt_config: JWT configuration
        key_manager: Key manager instance

    Returns:
        JWTHandler instance
    """
    global _jwt_handler
    if _jwt_handler is None:
        _jwt_handler = JWTHandler(jwt_config=jwt_config, key_manager=key_manager)
        logger.info("JWTHandler instance created")
    return _jwt_handler


def get_blacklist_manager(
    jwt_config: Annotated[JWTConfig, Depends(get_jwt_config)],
) -> TokenBlacklistManager:
    """Get or create TokenBlacklistManager instance.

    Args:
        jwt_config: JWT configuration

    Returns:
        TokenBlacklistManager instance
    """
    global _blacklist_manager
    if _blacklist_manager is None:
        _blacklist_manager = TokenBlacklistManager(jwt_config=jwt_config)
        logger.info("TokenBlacklistManager instance created")
    return _blacklist_manager


def get_token_validator(
    jwt_handler: Annotated[JWTHandler, Depends(get_jwt_handler)],
    blacklist_manager: Annotated[TokenBlacklistManager, Depends(get_blacklist_manager)],
    jwt_config: Annotated[JWTConfig, Depends(get_jwt_config)],
) -> TokenValidator:
    """Get or create TokenValidator instance.

    Args:
        jwt_handler: JWT handler instance
        blacklist_manager: Blacklist manager instance
        jwt_config: JWT configuration

    Returns:
        TokenValidator instance
    """
    global _token_validator
    if _token_validator is None:
        _token_validator = TokenValidator(
            jwt_handler=jwt_handler,
            blacklist_manager=blacklist_manager,
            jwt_config=jwt_config,
        )
        logger.info("TokenValidator instance created")
    return _token_validator


def get_user_repository() -> UserRepository:
    """Get UserRepository from FastAPI app state.

    This function will be updated to use app.state.user_repo
    once we integrate with the lifespan.

    Returns:
        UserRepository instance
    """
    # TODO: Get from app.state.user_repo in actual implementation
    # For now, create a temporary instance
    return UserRepository()


def get_token_service(
    jwt_handler: Annotated[JWTHandler, Depends(get_jwt_handler)],
    validator: Annotated[TokenValidator, Depends(get_token_validator)],
    blacklist_manager: Annotated[TokenBlacklistManager, Depends(get_blacklist_manager)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    jwt_config: Annotated[JWTConfig, Depends(get_jwt_config)],
) -> TokenService:
    """Get or create TokenService instance.

    Args:
        jwt_handler: JWT handler instance
        validator: Token validator instance
        blacklist_manager: Blacklist manager instance
        user_repo: User repository instance
        jwt_config: JWT configuration

    Returns:
        TokenService instance
    """
    global _token_service
    if _token_service is None:
        _token_service = TokenService(
            jwt_handler=jwt_handler,
            validator=validator,
            blacklist_manager=blacklist_manager,
            user_repo=user_repo,
            jwt_config=jwt_config,
        )
        logger.info("TokenService instance created")
    return _token_service


# Convenience type annotations for dependency injection
JWTConfigDep = Annotated[JWTConfig, Depends(get_jwt_config)]
KeyManagerDep = Annotated[KeyManager, Depends(get_key_manager)]
JWTHandlerDep = Annotated[JWTHandler, Depends(get_jwt_handler)]
TokenBlacklistManagerDep = Annotated[
    TokenBlacklistManager, Depends(get_blacklist_manager)
]
TokenValidatorDep = Annotated[TokenValidator, Depends(get_token_validator)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


def reset_token_dependencies() -> None:
    """Reset all token service dependencies (for testing).

    This function clears all global instances, forcing them to be recreated
    on next access. Useful for testing scenarios.
    """
    global \
        _key_manager, \
        _jwt_handler, \
        _blacklist_manager, \
        _token_validator, \
        _token_service

    _key_manager = None
    _jwt_handler = None
    _blacklist_manager = None
    _token_validator = None
    _token_service = None

    logger.info("Token service dependencies reset")
