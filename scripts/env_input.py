"""Enhanced CLI for automatic environment setup."""

import secrets
import time
from pathlib import Path

import typer
from cryptography.fernet import Fernet
from rich.progress import track

app = typer.Typer()

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILES = {
    "base": BASE_DIR / ".env",
    "dev": BASE_DIR / ".env.dev",
    "prod": BASE_DIR / ".env.prod",
    "test": BASE_DIR / ".env.test",
    "example": BASE_DIR / ".env.example",
}


def pbar_process(description: str, duration: float = 2.0):
    """Generic progress bar."""
    for _ in track(range(100), description=description):
        time.sleep(duration / 100)
    typer.echo(f"{description} completed successfully.")


def generate_secure_keys() -> dict[str, str]:
    """Generate all required secure keys."""
    pbar_process("Generating secure keys...")

    return {
        "fernet_key": Fernet.generate_key().decode(),
        "jwt_secret_dev": secrets.token_urlsafe(32),
        "jwt_secret_prod": secrets.token_urlsafe(64),  # Longer for production
        "jwt_secret_test": "test-jwt-secret-key-2024",  # Predictable for tests
        "security_secret_dev": secrets.token_urlsafe(32),
        "security_secret_prod": secrets.token_urlsafe(64),
        "security_secret_test": "test-secret-key-2024",
    }


def create_base_env_content(keys: dict[str, str]) -> str:
    """Create base .env content."""
    return f"""# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_DEBUG=false
APP_ENV=development
APP_SERVICE=mod-apiparser
APP_VERSION=0.1.0

# =============================================================================
# SECURITY & ENCRYPTION
# =============================================================================
SECURITY_SECRET_KEY={keys["security_secret_dev"]}
SECURITY_ALGORITHM=HS256

# =============================================================================
# JWT TOKEN SETTINGS
# =============================================================================
# Algorithm Configuration
JWT_ALGORITHM=HS256
JWT_SECRET_KEY={keys["jwt_secret_dev"]}

# Token Expiration
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# JWT Claims
JWT_ISSUER=otomax-api
JWT_AUDIENCE=otomax-client

# RSA Key Files (for RS256/RS512/ES256/ES512)
JWT_PRIVATE_KEY_PATH=secrets/keys/jwt_private.pem
JWT_PUBLIC_KEY_PATH=secrets/keys/jwt_public.pem
JWT_KEY_SIZE=2048

# Token Security
JWT_VERIFY_SIGNATURE=true
JWT_VERIFY_AUDIENCE=true
JWT_VERIFY_ISSUER=true
JWT_VERIFY_EXPIRATION=true

# Blacklist Settings
JWT_BLACKLIST_ENABLED=true
JWT_BLACKLIST_TOKEN_CHECKS=true

# =============================================================================
# FILE PATHS
# =============================================================================
PATH_USERS=secrets/users.yaml
PATH_MODULES=secrets/modules.yaml
PATH_KEYS=secrets/keys

# =============================================================================
# PRODUCTION SECURITY
# =============================================================================
JWT_REQUIRE_HTTPS=false
JWT_COOKIE_SECURE=false
JWT_COOKIE_SAMESITE=lax
"""


def create_dev_env_content(keys: dict[str, str]) -> str:
    """Create development .env.dev content."""
    return f"""# =============================================================================
# DEVELOPMENT ENVIRONMENT CONFIGURATION
# =============================================================================

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_DEBUG=true
APP_ENV=development
APP_SERVICE=mod-apiparser
APP_VERSION=0.1.0

# =============================================================================
# SECURITY & ENCRYPTION
# =============================================================================
SECURITY_SECRET_KEY={keys["security_secret_dev"]}
SECURITY_ALGORITHM=HS256

# =============================================================================
# JWT TOKEN SETTINGS
# =============================================================================
# Algorithm Configuration
JWT_ALGORITHM=HS256
JWT_SECRET_KEY={keys["jwt_secret_dev"]}

# Token Expiration (longer for dev convenience)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# JWT Claims
JWT_ISSUER=otomax-api-dev
JWT_AUDIENCE=otomax-client-dev

# RSA Key Files (for RS256/RS512/ES256/ES512)
JWT_PRIVATE_KEY_PATH=secrets/keys/dev_jwt_private.pem
JWT_PUBLIC_KEY_PATH=secrets/keys/dev_jwt_public.pem
JWT_KEY_SIZE=2048

# Token Security (relaxed for dev)
JWT_VERIFY_SIGNATURE=true
JWT_VERIFY_AUDIENCE=false
JWT_VERIFY_ISSUER=false
JWT_VERIFY_EXPIRATION=true

# Blacklist Settings
JWT_BLACKLIST_ENABLED=false
JWT_BLACKLIST_TOKEN_CHECKS=false

# =============================================================================
# FILE PATHS
# =============================================================================
PATH_USERS=secrets/dev_users.yaml
PATH_MODULES=secrets/dev_modules.yaml
PATH_KEYS=secrets/keys

# =============================================================================
# DEVELOPMENT SECURITY
# =============================================================================
JWT_REQUIRE_HTTPS=false
JWT_COOKIE_SECURE=false
JWT_COOKIE_SAMESITE=lax
"""


def create_prod_env_content(keys: dict[str, str]) -> str:
    """Create production .env.prod content with placeholders."""
    return f"""# =============================================================================
# PRODUCTION ENVIRONMENT CONFIGURATION
# =============================================================================

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_DEBUG=false
APP_ENV=production
APP_SERVICE=mod-apiparser
APP_VERSION=0.1.0

# =============================================================================
# SECURITY & ENCRYPTION
# =============================================================================
# Use environment variables in production: export PROD_SECURITY_SECRET_KEY="your-key"
SECURITY_SECRET_KEY=${{PROD_SECURITY_SECRET_KEY:-{keys["security_secret_prod"]}}}
SECURITY_ALGORITHM=HS512

# =============================================================================
# JWT TOKEN SETTINGS
# =============================================================================
# Algorithm Configuration (stronger for production)
JWT_ALGORITHM=HS512
JWT_SECRET_KEY=${{PROD_JWT_SECRET_KEY:-{keys["jwt_secret_prod"]}}}

# Token Expiration (shorter for production)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# JWT Claims
JWT_ISSUER=otomax-api
JWT_AUDIENCE=otomax-client

# RSA Key Files (for RS256/RS512/ES256/ES512)
JWT_PRIVATE_KEY_PATH=secrets/keys/prod_jwt_private.pem
JWT_PUBLIC_KEY_PATH=secrets/keys/prod_jwt_public.pem
JWT_KEY_SIZE=4096

# Token Security (strict for production)
JWT_VERIFY_SIGNATURE=true
JWT_VERIFY_AUDIENCE=true
JWT_VERIFY_ISSUER=true
JWT_VERIFY_EXPIRATION=true

# Blacklist Settings
JWT_BLACKLIST_ENABLED=true
JWT_BLACKLIST_TOKEN_CHECKS=true

# =============================================================================
# FILE PATHS
# =============================================================================
PATH_USERS=secrets/prod_users.yaml
PATH_MODULES=secrets/prod_modules.yaml
PATH_KEYS=secrets/keys

# =============================================================================
# PRODUCTION SECURITY
# =============================================================================
JWT_REQUIRE_HTTPS=true
JWT_COOKIE_SECURE=true
JWT_COOKIE_SAMESITE=strict

# =============================================================================
# PRODUCTION SECRETS (set these as environment variables)
# =============================================================================
# export PROD_SECURITY_SECRET_KEY="{keys["security_secret_prod"]}"
# export PROD_JWT_SECRET_KEY="{keys["jwt_secret_prod"]}"
"""


def create_test_env_content(keys: dict[str, str]) -> str:
    """Create testing .env.test content."""
    return f"""# =============================================================================
# TESTING ENVIRONMENT CONFIGURATION
# =============================================================================

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_DEBUG=true
APP_ENV=testing
APP_SERVICE=mod-apiparser
APP_VERSION=0.1.0

# =============================================================================
# SECURITY & ENCRYPTION
# =============================================================================
SECURITY_SECRET_KEY={keys["security_secret_test"]}
SECURITY_ALGORITHM=HS256

# =============================================================================
# JWT TOKEN SETTINGS
# =============================================================================
# Algorithm Configuration
JWT_ALGORITHM=HS256
JWT_SECRET_KEY={keys["jwt_secret_test"]}

# Token Expiration (very short for testing)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=5
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# JWT Claims
JWT_ISSUER=otomax-api-test
JWT_AUDIENCE=otomax-client-test

# RSA Key Files (for RS256/RS512/ES256/ES512)
JWT_PRIVATE_KEY_PATH=secrets/keys/test_jwt_private.pem
JWT_PUBLIC_KEY_PATH=secrets/keys/test_jwt_public.pem
JWT_KEY_SIZE=2048

# Token Security (relaxed for testing)
JWT_VERIFY_SIGNATURE=true
JWT_VERIFY_AUDIENCE=false
JWT_VERIFY_ISSUER=false
JWT_VERIFY_EXPIRATION=false

# Blacklist Settings (disabled for testing)
JWT_BLACKLIST_ENABLED=false
JWT_BLACKLIST_TOKEN_CHECKS=false

# =============================================================================
# FILE PATHS
# =============================================================================
PATH_USERS=secrets/test_users.yaml
PATH_MODULES=secrets/test_modules.yaml
PATH_KEYS=secrets/keys

# =============================================================================
# TESTING SECURITY
# =============================================================================
JWT_REQUIRE_HTTPS=false
JWT_COOKIE_SECURE=false
JWT_COOKIE_SAMESITE=lax
"""


@app.command()
def env_setup():
    """Pure automatic environment setup - no prompts, just generates environment files."""
    typer.echo("🚀 Starting automatic environment setup...")

    # Check for existing files
    existing_files = [name for name, path in ENV_FILES.items() if path.exists()]

    if existing_files:
        typer.echo(f"⚠️  Found existing files: {', '.join(existing_files)}")
        typer.echo("Existing files will be overwritten.")

    # Generate secure keys
    keys = generate_secure_keys()

    # Create environment files
    env_contents = {
        "base": create_base_env_content(keys),
        "dev": create_dev_env_content(keys),
        "prod": create_prod_env_content(keys),
        "test": create_test_env_content(keys),
    }

    # Write environment files
    pbar_process("Creating environment files...")
    for env_type, content in env_contents.items():
        file_path = ENV_FILES["base"] if env_type == "base" else ENV_FILES[env_type]

        with file_path.open("w") as f:
            f.write(content)

        typer.secho(f"✅ Created: {file_path.name}", fg=typer.colors.GREEN)

    # Create secrets directory structure
    secrets_dir = BASE_DIR / "secrets" / "keys"
    secrets_dir.mkdir(parents=True, exist_ok=True)

    # Summary
    typer.echo("\n🎉 Environment setup completed successfully!")
    typer.echo("\n📋 Summary:")
    typer.echo(f"   Environment files: {len(env_contents)} created")
    typer.echo(f"   Secrets directory: {secrets_dir}")

    typer.echo("\n🔐 Production deployment notes:")
    typer.echo("   Set environment variables:")
    typer.echo(f"   export PROD_SECURITY_SECRET_KEY='{keys['security_secret_prod']}'")
    typer.echo(f"   export PROD_JWT_SECRET_KEY='{keys['jwt_secret_prod']}'")

    typer.echo("\n👤 Next steps:")
    typer.echo("   Use 'python scripts/user_cli_input.py' to create admin users")
    typer.echo("   Use 'python scripts/modules_cli_input.py' to manage modules")

@app.command()
def show_info():
    """Show current environment information."""
    typer.echo("📁 Environment files status:")
    for name, path in ENV_FILES.items():
        status = "✅ EXISTS" if path.exists() else "❌ MISSING"
        typer.echo(f"   {name:10} : {status} - {path}")


if __name__ == "__main__":
    app()
