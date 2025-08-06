from src.domain.account.sch_account import AccountCreate, AccountRead

# In-memory storage for demonstration purposes
_accounts_db: dict[str, AccountRead] = {}


def create_account(account_data: AccountCreate) -> AccountRead:
    """Create a new account and store it in the in-memory database.

    Raises ValueError if accountid already exists.
    """
    accountid = account_data.accountid
    if accountid in _accounts_db:
        raise ValueError(f"Account with id '{accountid}' already exists.")
    account = AccountRead(**account_data.model_dump())
    _accounts_db[accountid] = account
    return account


# Optionally, add a getter for demonstration/testing
def get_account(accountid: str) -> AccountRead | None:
    return _accounts_db.get(accountid)
