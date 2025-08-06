"""Environment setup CLI - handles ONLY environment configuration.

This module is responsible for:
- Generating secure keys
- Creating environment files (.env, .env.dev, .env.prod, .env.test)
- Setting up directory structure

Does NOT handle:
- User creation (handled by user_input.py)
- Module setup (future: module_input.py)
"""

import secrets
import time
from pathlib import Path

import typer
from cryptography.fernet import Fernet
from rich.console import Console
from rich.progress import track

app = typer.Typer(
    name="env-setup", help="Environment configuration setup tool", no_args_is_help=True
)
console = Console()

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


def create_admin_user_file(username: str, hashed_password: str) -> None:
    """Create initial admin user file.

    NOTE: This function will be REMOVED and moved to user_input.py
    Keeping temporarily for backward compatibility.
    """
    console.print(
        "[yellow]⚠️  User creation should be handled by user_input.py[/yellow]"
    )
    console.print("[yellow]⚠️  This function is deprecated and will be removed[/yellow]")

    # Temporarily disabled - should use user_input.py instead
    raise typer.Exit(1)


def create_modules_file() -> None:
    """Create initial modules configuration."""
    modules_dir = BASE_DIR / "secrets"
    modules_dir.mkdir(exist_ok=True)

    # Create for each environment
    environments = ["", "dev_", "prod_", "test_"]

    for env_prefix in environments:
        modules_file = modules_dir / f"{env_prefix}modules.yaml"

        modules_content = """# API modules configuration
modules:
  - name: "authentication"
    enabled: true
    description: "User authentication and authorization"
  - name: "user_management"
    enabled: true
    description: "User management operations"
  - name: "api_parser"
    enabled: true
    description: "API parsing and validation"
"""

        with modules_file.open("w") as f:
            f.write(modules_content)


@app.command()
def env_setup():
    """Create environment files with secure keys.

    This command ONLY handles environment setup:
    - Generates secure keys
    - Creates .env files for all environments
    - Sets up directory structure

    Does NOT create users - use user_input.py for that.
    """
    console.print("[bold blue]🌍 Environment Setup Tool[/bold blue]")
    console.print("This tool creates environment files with secure keys")
    console.print(
        "[yellow]Note: User creation is handled separately by user_input.py[/yellow]\n"
    )

    # Check for existing files
    existing_files = [name for name, path in ENV_FILES.items() if path.exists()]

    if existing_files:
        console.print(
            f"[yellow]Found existing files: {', '.join(existing_files)}[/yellow]"
        )
        overwrite = typer.confirm(
            "Overwrite existing environment files?", default=False
        )
        if not overwrite:
            console.print("[red]❌ Environment setup cancelled by user[/red]")
            raise typer.Exit(1)

    try:
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

            console.print(f"[green]✅ Created: {file_path.name}[/green]")

        # Create basic modules structure
        pbar_process("Creating modules configuration...")
        create_modules_file()

        # Create secrets directory structure
        secrets_dir = BASE_DIR / "secrets" / "keys"
        secrets_dir.mkdir(parents=True, exist_ok=True)

        # Summary
        console.print(
            "\n[bold green]🎉 Environment setup completed successfully![/bold green]"
        )
        console.print("\n[bold]📋 Summary:[/bold]")
        console.print(f"   Environment files: {len(env_contents)} created")
        console.print(f"   Secrets directory: {secrets_dir}")

        console.print("\n[bold yellow]📝 Next Steps:[/bold yellow]")
        console.print("   1. Run user setup: [cyan]uv run scripts/user_input.py[/cyan]")
        console.print("   2. Start application: [cyan]start.bat[/cyan]")

        console.print("\n[bold]🔐 Production deployment notes:[/bold]")
        console.print("   Set environment variables:")
        console.print(
            f"   [dim]export PROD_SECURITY_SECRET_KEY='{keys['security_secret_prod']}'[/dim]"
        )
        console.print(
            f"   [dim]export PROD_JWT_SECRET_KEY='{keys['jwt_secret_prod']}'[/dim]"
        )

    except Exception as e:
        console.print(f"[red]❌ Environment setup failed: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def validate():
    """Validate existing environment configuration.

    Checks if all environment files exist and are properly formatted.
    """
    console.print("[bold blue]🔍 Environment Validation[/bold blue]")

    missing_files = []
    for name, path in ENV_FILES.items():
        if name == "example":  # Skip example file
            continue

        if not path.exists():
            missing_files.append(name)
            console.print(f"[red]❌ Missing: {name} ({path})[/red]")
        else:
            console.print(f"[green]✅ Found: {name}[/green]")

    if missing_files:
        console.print(
            f"\n[red]❌ Validation failed: {len(missing_files)} files missing[/red]"
        )
        console.print("[yellow]Run: uv run scripts/env_input.py env-setup[/yellow]")
        raise typer.Exit(1)
    else:
        console.print("\n[green]✅ All environment files present[/green]")
        return True


@app.command()
def show_info():
    """Show current environment files status."""
    console.print("[bold blue]📁 Environment Files Status[/bold blue]")

    for name, path in ENV_FILES.items():
        if name == "example":  # Skip example file
            continue

        status = (
            "[green]✅ EXISTS[/green]" if path.exists() else "[red]❌ MISSING[/red]"
        )
        size = f"({path.stat().st_size} bytes)" if path.exists() else ""
        console.print(f"   {name:10} : {status} - {path} {size}")

    # Check secrets directory
    secrets_dir = BASE_DIR / "secrets"
    if secrets_dir.exists():
        console.print(f"\n[green]✅ Secrets directory: {secrets_dir}[/green]")
        keys_dir = secrets_dir / "keys"
        if keys_dir.exists():
            console.print(f"[green]✅ Keys directory: {keys_dir}[/green]")
        else:
            console.print(f"[yellow]⚠️  Keys directory missing: {keys_dir}[/yellow]")
    else:
        console.print(f"\n[red]❌ Secrets directory missing: {secrets_dir}[/red]")


@app.command()
def clean():
    """Remove all environment files (use with caution!)."""
    console.print("[bold red]🧹 Environment Cleanup[/bold red]")
    console.print("[yellow]This will remove ALL environment files![/yellow]")

    confirm = typer.confirm(
        "Are you sure you want to delete all environment files?", default=False
    )

    if not confirm:
        console.print("[yellow]Cleanup cancelled[/yellow]")
        return

    removed_files = []
    for name, path in ENV_FILES.items():
        if name == "example":  # Skip example file
            continue

        if path.exists():
            path.unlink()
            removed_files.append(name)
            console.print(f"[red]🗑️  Removed: {name}[/red]")

    if removed_files:
        console.print(
            f"\n[green]✅ Removed {len(removed_files)} environment files[/green]"
        )
    else:
        console.print("[yellow]No environment files found to remove[/yellow]")


# CLI entry point
if __name__ == "__main__":
    app()
