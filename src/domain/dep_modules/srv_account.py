# from domain.modules.sch_base import Settings, get_settings


# class AccountService:
#     def __init__(self, settings: Settings | None = None):
#         self.settings = settings or get_settings()

#     def is_username_exist(self, username: str) -> bool:
#         """Check if a username exists in the application's account configuration.

#         Args:
#             username (str): The username to check.

#         Returns:
#             bool: True if the username exists, False otherwise.
#         """
#         return any(
#             account.username == username for account in self.settings.accounts.accounts
#         )

#     def is_username_active(self, username: str) -> bool:
#         """Check if a username is marked as active in the application's account configuration.

#         Args:
#             username (str): The username to check.

#         Returns:
#             bool: True if the username is active, False otherwise.
#         """
#         for account in self.settings.accounts.accounts:
#             if account.username == username:
#                 return account.is_aktif
#         return False

#     def get_username_account_data(self, username: str) -> dict | None:
#         """Retrieve the properties of an account by username.

#         Args:
#             username (str): The username of the account.

#         Returns:
#             dict | None: A dictionary containing account properties if found, otherwise None.
#         """
#         for account in self.settings.accounts.accounts:
#             if account.username == username:
#                 return {
#                     "type": account.type,
#                     "username": account.username,
#                     "password": account.password,
#                     "pin": account.pin,
#                     "msisdn": account.msisdn,
#                     "is_aktif": account.is_aktif,
#                     "base_url": account.base_url,
#                 }
#         return None
