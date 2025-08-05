class AccountServiceError(Exception):
    """Base exception untuk account service"""
    pass

class AccountNotFoundError(AccountServiceError):
    """Account tidak ditemukan"""
    pass
