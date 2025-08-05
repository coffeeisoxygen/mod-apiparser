# services/account_service.py
from pathlib import Path

import yaml

from services.crypto_service import CryptoService
from src.accounts.sch_account import AccountCreate, AccountRead
from src.exceptions import AppException


class AccountFileService:
    """File-based account service dengan encryption support."""

    def __init__(self, crypto_service: CryptoService):
        self.crypto_service = crypto_service
        self._accounts_cache: dict[str, AccountRead] | None = None

    async def save_accounts(
        self, accounts: list[AccountCreate], file_path: Path
    ) -> bool:
        """Save accounts ke YAML file dengan encryption."""
        try:
            # Convert pydantic models ke dict
            accounts_data = []
            for account in accounts:
                account_dict = account.model_dump()

                # Encrypt sensitive fields
                sensitive_fields = ["username", "pin", "password"]
                for field in sensitive_fields:
                    if account_dict.get(field):
                        # Pydantic SecretStr handling
                        if hasattr(account_dict[field], "get_secret_value"):
                            raw_value = account_dict[field].get_secret_value()
                        else:
                            raw_value = str(account_dict[field])

                        account_dict[field] = self.crypto_service.encrypt(raw_value)

                accounts_data.append(account_dict)

            # Save ke YAML
            yaml_data = {"version": "1.0", "encrypted": True, "accounts": accounts_data}

            with open(file_path, "w") as f:
                yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)

            # Clear cache
            self._accounts_cache = None
            return True

        except Exception as e:
            print(f"Error saving accounts: {e}")
            return False

    async def load_accounts(self, file_path: Path) -> list[AccountRead]:
        """Load accounts dari YAML file dengan decryption"""
        if not file_path.exists():
            return []

        try:
            with open(file_path) as f:
                yaml_data = yaml.safe_load(f)

            if not yaml_data or "accounts" not in yaml_data:
                return []

            accounts = []
            for account_data in yaml_data["accounts"]:
                # Decrypt sensitive fields jika encrypted
                if yaml_data.get("encrypted", False):
                    sensitive_fields = ["username", "pin", "password"]
                    for field in sensitive_fields:
                        if account_data.get(field):
                            account_data[field] = self.crypto_service.decrypt(
                                account_data[field]
                            )

                # Create pydantic model
                account = AccountRead(**account_data)
                accounts.append(account)

            return accounts

        except Exception as e:
            raise AccountServiceError(f"Failed to load accounts: {e}")

    async def get_account_by_id(self, account_id: str) -> AccountRead | None:
        """Get account by ID dari cache atau file"""
        if self._accounts_cache is None:
            await self._load_to_cache()

        return self._accounts_cache.get(account_id)

    async def get_all_accounts(self) -> dict[str, AccountRead]:
        """Get all accounts as dict"""
        if self._accounts_cache is None:
            await self._load_to_cache()

        return self._accounts_cache.copy()

    async def _load_to_cache(self, file_path: Path = None):
        """Load accounts ke memory cache"""
        if file_path is None:
            file_path = Path("accounts.yaml")

        accounts = await self.load_accounts(file_path)
        self._accounts_cache = {account.accountid: account for account in accounts}

    async def add_account(self, account: AccountCreate, file_path: Path = None) -> bool:
        """Add single account ke existing file"""
        if file_path is None:
            file_path = Path("accounts.yaml")

        existing_accounts = await self.load_accounts(file_path)

        # Check duplicate accountid
        for existing in existing_accounts:
            if existing.accountid == account.accountid:
                raise AppException.AccountServiceError(
                    f"Account ID '{account.accountid}' already exists"
                )

        # Add new account
        all_accounts = existing_accounts + [account]
        return await self.save_accounts(all_accounts, file_path)

    def clear_cache(self):
        """Clear memory cache"""
        self._accounts_cache = None
