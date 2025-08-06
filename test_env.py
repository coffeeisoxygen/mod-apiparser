# ruff: noqa

"""Test script to verify environment loading."""

import os

# Test different environments
environments = ["development", "production", "testing"]

for env in environments:
    print(f"\n=== Testing {env} environment ===")
    os.environ["APP_ENV"] = env

    try:
        from src.dependencies.dep_settings import get_settings

        # Clear the cache to reload settings
        get_settings.cache_clear()

        settings = get_settings()
        print(f"Environment: {settings.environment}")
        print(f"Debug: {settings.debug}")
        print(f"Service: {settings.service}")
        print(f"Version: {settings.version}")
        print(f"JWT Secret Key (first 20 chars): {settings.jwt.secret_key[:20]}...")
        print(f"JWT Algorithm: {settings.jwt.algorithm}")
        print(f"Access Token Expire: {settings.jwt.access_token_expire_minutes}")
        print(f"Users Path: {settings.paths.users}")
        print(f"Modules Path: {settings.paths.modules}")

    except Exception as e:
        print(f"Error loading {env} environment: {e}")
        import traceback

        traceback.print_exc()
