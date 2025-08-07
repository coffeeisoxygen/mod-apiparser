"""This module contains the configuration data for generating environment files.

It defines a BASE_CONFIG with all common settings and then environment-specific
overrides for development, production, and testing.
"""

# Base configuration shared across all environments
BASE_CONFIG = {
    # Application Settings
    "APP_DEBUG": "false",
    "APP_ENV": "development",
    "APP_SERVICE": "mod-apiparser",
    "APP_VERSION": "0.1.0",
    # Security & Encryption
    "SECURITY_ALGORITHM": "HS256",
    # JWT Token Settings
    "JWT_ALGORITHM": "HS256",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "JWT_REFRESH_TOKEN_EXPIRE_DAYS": "7",
    "JWT_ISSUER": "otomax-api",
    "JWT_AUDIENCE": "otomax-client",
    "JWT_PRIVATE_KEY_PATH": "secrets/keys/jwt_private.pem",
    "JWT_PUBLIC_KEY_PATH": "secrets/keys/jwt_public.pem",
    "JWT_KEY_SIZE": "2048",
    "JWT_VERIFY_SIGNATURE": "true",
    "JWT_VERIFY_AUDIENCE": "true",
    "JWT_VERIFY_ISSUER": "true",
    "JWT_VERIFY_EXPIRATION": "true",
    "JWT_BLACKLIST_ENABLED": "true",
    "JWT_BLACKLIST_TOKEN_CHECKS": "true",
    # File Paths
    "PATH_USERS": "secrets/users.yaml",
    "PATH_KEYS": "secrets/keys",
    # Production Security
    "JWT_REQUIRE_HTTPS": "false",
    "JWT_COOKIE_SECURE": "false",
    "JWT_COOKIE_SAMESITE": "lax",
}

# Overrides for the Development environment
DEV_OVERRIDES = {
    "APP_DEBUG": "true",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "60",
    "JWT_REFRESH_TOKEN_EXPIRE_DAYS": "1",
    "JWT_ISSUER": "otomax-api-dev",
    "JWT_AUDIENCE": "otomax-client-dev",
    "JWT_PRIVATE_KEY_PATH": "secrets/keys/dev_jwt_private.pem",
    "JWT_PUBLIC_KEY_PATH": "secrets/keys/dev_jwt_public.pem",
    "JWT_VERIFY_AUDIENCE": "false",
    "JWT_VERIFY_ISSUER": "false",
    "JWT_BLACKLIST_ENABLED": "false",
    "JWT_BLACKLIST_TOKEN_CHECKS": "false",
    "PATH_USERS": "secrets/dev_users.yaml",
}

# Overrides for the Production environment
PROD_OVERRIDES = {
    "APP_ENV": "production",
    "SECURITY_ALGORITHM": "HS512",
    "JWT_ALGORITHM": "HS512",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "15",
    "JWT_KEY_SIZE": "4096",
    "PATH_USERS": "secrets/prod_users.yaml",
    "JWT_REQUIRE_HTTPS": "true",
    "JWT_COOKIE_SECURE": "true",
    "JWT_COOKIE_SAMESITE": "strict",
}

# Overrides for the Testing environment
TEST_OVERRIDES = {
    "APP_DEBUG": "true",
    "APP_ENV": "testing",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "5",
    "JWT_REFRESH_TOKEN_EXPIRE_DAYS": "1",
    "JWT_ISSUER": "otomax-api-test",
    "JWT_AUDIENCE": "otomax-client-test",
    "JWT_PRIVATE_KEY_PATH": "secrets/keys/test_jwt_private.pem",
    "JWT_PUBLIC_KEY_PATH": "secrets/keys/test_jwt_public.pem",
    "JWT_VERIFY_AUDIENCE": "false",
    "JWT_VERIFY_ISSUER": "false",
    "JWT_VERIFY_EXPIRATION": "false",
    "JWT_BLACKLIST_ENABLED": "false",
    "JWT_BLACKLIST_TOKEN_CHECKS": "false",
    "PATH_USERS": "secrets/test_users.yaml",
}

# This dictionary maps an environment name to its override configuration
ENVIRONMENTS = {
    "dev": DEV_OVERRIDES,
    "prod": PROD_OVERRIDES,
    "test": TEST_OVERRIDES,
    # The 'base' environment has no overrides
    "base": {},
}
