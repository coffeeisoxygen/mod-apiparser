"""Test cleaned dependencies."""

import os

os.environ["APP_ENV"] = "development"

# Test all dependencies
from src.dependencies.dep_settings import (
    get_app_config,
    get_jwt_config,
    get_path_config,
    get_security_config,
    get_settings,
)

settings = get_settings()
app_config = get_app_config()
jwt_config = get_jwt_config()
security_config = get_security_config()
path_config = get_path_config()

print("=== TESTING CLEANED DEPENDENCIES ===")
print(f"Settings working: {settings.service}")
print(
    f"App config: {app_config.service} v{app_config.version} (debug={app_config.debug})"
)
print(
    f"JWT config: {jwt_config.algorithm}, expire={jwt_config.access_token_expire_minutes}min"
)
print(f"Security config: {security_config.algorithm}")
print(f"Path config: users={path_config.users}")
print("All dependencies working perfectly! ✅")

# Test FastAPI Dependencies types
from src.dependencies.dep_settings import (
    AppConfigDep,
    JWTConfigDep,
    PathConfigDep,
    SecurityConfigDep,
    SettingsDep,
)

print("\nFastAPI Dependencies available:")
print(f"- AppConfigDep: {AppConfigDep}")
print(f"- JWTConfigDep: {JWTConfigDep}")
print(f"- SecurityConfigDep: {SecurityConfigDep}")
print(f"- PathConfigDep: {PathConfigDep}")
print(f"- SettingsDep: {SettingsDep}")
