"""Module Module Helper untuk mengelola konfigurasi aplikasi."""

from domain.modules.sch_base import get_settings


def is_username_exist(username: str) -> bool:
    """Check if a username exists in the application's account configuration.

    Args:
        username (str): The username to check.

    Returns:
        bool: True if the username exists, False otherwise.
    """
    settings = get_settings()
    return any(account.username == username for account in settings.accounts.accounts)


def is_username_active(username: str) -> bool:
    """Check if a username is marked as active in the application's account configuration.

    Args:
        username (str): The username to check.

    Returns:
        bool: True if the username is active, False otherwise.
    """
    settings = get_settings()
    for account in settings.accounts.accounts:
        if account.username == username:
            return account.is_aktif
    return False


def get_username_account_data(username: str) -> dict | None:
    """Retrieve the properties of an account by username.

    Args:
        username (str): The username of the account.

    Returns:
        dict | None: A dictionary containing account properties if found, otherwise None.
    """
    settings = get_settings()
    for account in settings.accounts.accounts:
        if account.username == username:
            return {
                "type": account.type,
                "username": account.username,
                "password": account.password,
                "pin": account.pin,
                "msisdn": account.msisdn,
                "is_aktif": account.is_aktif,
                "base_url": account.base_url,
            }
    return None


def get_response_config_for_type(type_: str):
    """Retrieve the response configuration for a specific type.

    Args:
        type_ (str): The type of the response configuration to retrieve.

    Returns:
        The response configuration item if found, None otherwise.
    """
    settings = get_settings()
    for item in settings.responses.items:
        if item.type == type_:
            return item
    return None
