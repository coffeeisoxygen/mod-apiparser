"""Environment setup CLI - handles ONLY environment configuration.

This module is responsible for:
- Generating secure keys
- Creating environment files (.env, .env.dev, .env.prod, .env.test)
- Setting up directory structure
"""

import secrets
import time
from pathlib import Path
from typing import Any

import typer
from cryptography.fernet import Fernet
from rich.console import Console
from rich.progress import track

app = typer.Typer(
    name="env-setup", help="Environment configuration setup tool", no_args_is_help=True
)


class EnvManager:
    """Manages environment file creation, validation, and cleanup."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.console = Console()
        self.env_files = {
            "base": self.base_dir / ".env",
            "dev": self.base_dir / ".env.dev",
            "prod": self.base_dir / ".env.prod",
            "test": self.base_dir / ".env.test",
        }
        self.keys: dict[str, str] = {}

    def _pbar_process(self, description: str, duration: float = 1.0):
        """Generic progress bar."""
        for _ in track(range(100), description=description, console=self.console):
            time.sleep(duration / 100)
        self.console.print(f"[green]✅ {description} completed.[/green]")

    def generate_secure_keys(self):
        """Generate all required secure keys."""
        self._pbar_process("Generating secure keys")
        self.keys = {
            "fernet_key": Fernet.generate_key().decode(),
            "jwt_secret_dev": secrets.token_urlsafe(32),
            "jwt_secret_prod": secrets.token_urlsafe(64),
            "jwt_secret_test": "test-jwt-secret-key-2024",
            "security_secret_dev": secrets.token_urlsafe(32),
            "security_secret_prod": secrets.token_urlsafe(64),
            "security_secret_test": "test-secret-key-2024",
        }

    def _get_env_config(self, env_type: str) -> dict[str, Any]:
        """Get configuration for a specific environment type."""
        configs = {
            "base": {
                "APP_DEBUG": "false",
                "APP_ENV": "development",
                "SECURITY_SECRET_KEY": self.keys["security_secret_dev"],
                "SECURITY_ALGORITHM": "HS256",
                "JWT_ALGORITHM": "HS256",
                "JWT_SECRET_KEY": self.keys["jwt_secret_dev"],
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": 30,
                "JWT_REFRESH_TOKEN_EXPIRE_DAYS": 7,
                "JWT_ISSUER": "otomax-api",
                "JWT_AUDIENCE": "otomax-client",
                "JWT_PRIVATE_KEY_PATH": "secrets/keys/jwt_private.pem",
                "JWT_PUBLIC_KEY_PATH": "secrets/keys/jwt_public.pem",
                "JWT_KEY_SIZE": 2048,
                "JWT_VERIFY_SIGNATURE": "true",
                "JWT_VERIFY_AUDIENCE": "true",
                "JWT_VERIFY_ISSUER": "true",
                "JWT_VERIFY_EXPIRATION": "true",
                "JWT_BLACKLIST_ENABLED": "true",
                "JWT_BLACKLIST_TOKEN_CHECKS": "true",
                "PATH_USERS": "secrets/users.yaml",
                "PATH_KEYS": "secrets/keys",
                "JWT_REQUIRE_HTTPS": "false",
                "JWT_COOKIE_SECURE": "false",
                "JWT_COOKIE_SAMESITE": "lax",
            },
            "dev": {
                "APP_DEBUG": "true",
                "APP_ENV": "development",
                "SECURITY_SECRET_KEY": self.keys["security_secret_dev"],
                "SECURITY_ALGORITHM": "HS256",
                "JWT_ALGORITHM": "HS256",
                "JWT_SECRET_KEY": self.keys["jwt_secret_dev"],
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": 60,
                "JWT_REFRESH_TOKEN_EXPIRE_DAYS": 1,
                "JWT_ISSUER": "otomax-api-dev",
                "JWT_AUDIENCE": "otomax-client-dev",
                "JWT_PRIVATE_KEY_PATH": "secrets/keys/dev_jwt_private.pem",
                "JWT_PUBLIC_KEY_PATH": "secrets/keys/dev_jwt_public.pem",
                "JWT_VERIFY_AUDIENCE": "false",
                "JWT_VERIFY_ISSUER": "false",
                "JWT_BLACKLIST_ENABLED": "false",
                "JWT_BLACKLIST_TOKEN_CHECKS": "false",
                "PATH_USERS": "secrets/dev_users.yaml",
            },
            "prod": {
                "APP_ENV": "production",
                "SECURITY_SECRET_KEY": f"${{PROD_SECURITY_SECRET_KEY:-{self.keys['security_secret_prod']}}}",
                "SECURITY_ALGORITHM": "HS512",
                "JWT_ALGORITHM": "HS512",
                "JWT_SECRET_KEY": f"${{PROD_JWT_SECRET_KEY:-{self.keys['jwt_secret_prod']}}}",
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": 15,
                "JWT_REFRESH_TOKEN_EXPIRE_DAYS": 7,
                "JWT_PRIVATE_KEY_PATH": "secrets/keys/prod_jwt_private.pem",
                "JWT_PUBLIC_KEY_PATH": "secrets/keys/prod_jwt_public.pem",
                "JWT_KEY_SIZE": 4096,
                "PATH_USERS": "secrets/prod_users.yaml",
                "JWT_REQUIRE_HTTPS": "true",
                "JWT_COOKIE_SECURE": "true",
                "JWT_COOKIE_SAMESITE": "strict",
            },
            "test": {
                "APP_DEBUG": "true",
                "APP_ENV": "testing",
                "SECURITY_SECRET_KEY": self.keys["security_secret_test"],
                "SECURITY_ALGORITHM": "HS256",
                "JWT_ALGORITHM": "HS256",
                "JWT_SECRET_KEY": self.keys["jwt_secret_test"],
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": 5,
                "JWT_REFRESH_TOKEN_EXPIRE_DAYS": 1,
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
            },
        }
        # Start with base config and update with specific env config
        config = configs["base"].copy()
        if env_type != "base":
            config.update(configs[env_type])
        return config

    def _create_env_content(self, env_type: str) -> str:
        """Generate .env file content from a template."""
        config = self._get_env_config(env_type)

        # Special handling for production secrets note
        prod_secrets_note = ""
        if env_type == "prod":
            prod_secrets_note = f'''
# =============================================================================
# PRODUCTION SECRETS (set these as environment variables)
# =============================================================================
# export PROD_SECURITY_SECRET_KEY="{self.keys["security_secret_prod"]}"
# export PROD_JWT_SECRET_KEY="{self.keys["jwt_secret_prod"]}"
'''

        return f"""# =============================================================================
# {env_type.upper()} ENVIRONMENT CONFIGURATION
# =============================================================================
# APPLICATION SETTINGS
APP_DEBUG={config["APP_DEBUG"]}
APP_ENV={config["APP_ENV"]}
APP_SERVICE=mod-apiparser
APP_VERSION=0.1.0

# SECURITY & ENCRYPTION
SECURITY_SECRET_KEY={config["SECURITY_SECRET_KEY"]}
SECURITY_ALGORITHM={config["SECURITY_ALGORITHM"]}

# JWT TOKEN SETTINGS
JWT_ALGORITHM={config["JWT_ALGORITHM"]}
JWT_SECRET_KEY={config["JWT_SECRET_KEY"]}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES={config["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"]}
JWT_REFRESH_TOKEN_EXPIRE_DAYS={config["JWT_REFRESH_TOKEN_EXPIRE_DAYS"]}
JWT_ISSUER={config["JWT_ISSUER"]}
JWT_AUDIENCE={config["JWT_AUDIENCE"]}
JWT_PRIVATE_KEY_PATH={config["JWT_PRIVATE_KEY_PATH"]}
JWT_PUBLIC_KEY_PATH={config["JWT_PUBLIC_KEY_PATH"]}
JWT_KEY_SIZE={config["JWT_KEY_SIZE"]}
JWT_VERIFY_SIGNATURE={config["JWT_VERIFY_SIGNATURE"]}
JWT_VERIFY_AUDIENCE={config["JWT_VERIFY_AUDIENCE"]}
JWT_VERIFY_ISSUER={config["JWT_VERIFY_ISSUER"]}
JWT_VERIFY_EXPIRATION={config["JWT_VERIFY_EXPIRATION"]}
JWT_BLACKLIST_ENABLED={config["JWT_BLACKLIST_ENABLED"]}
JWT_BLACKLIST_TOKEN_CHECKS={config["JWT_BLACKLIST_TOKEN_CHECKS"]}

# FILE PATHS
PATH_USERS={config["PATH_USERS"]}
PATH_KEYS={config["PATH_KEYS"]}

# SECURITY
JWT_REQUIRE_HTTPS={config["JWT_REQUIRE_HTTPS"]}
JWT_COOKIE_SECURE={config["JWT_COOKIE_SECURE"]}
JWT_COOKIE_SAMESITE={config["JWT_COOKIE_SAMESITE"]}
{prod_secrets_note}
"""

    def create_env_files(self):
        """Create all environment files."""
        self.console.print("[bold blue]🌍 Environment Setup Tool[/bold blue]")
        self.console.print("This tool creates environment files with secure keys.")

        existing_files = [
            name for name, path in self.env_files.items() if path.exists()
        ]
        if existing_files:
            self.console.print(
                f"\n[yellow]Found existing files: {', '.join(existing_files)}[/yellow]"
            )
            if not typer.confirm(
                "Overwrite existing environment files?", default=False
            ):
                self.console.print("[red]❌ Environment setup cancelled by user.[/red]")
                raise typer.Exit(1)

        try:
            self.generate_secure_keys()
            self._pbar_process("Creating environment files")
            for env_type, path in self.env_files.items():
                content = self._create_env_content(env_type)
                with path.open("w") as f:
                    f.write(content)
                self.console.print(f"   [green]✓ Created: {path.name}[/green]")

            self.setup_directory_structure()

            self.console.print(
                "\n[bold green]🎉 Environment setup completed successfully![/bold green]"
            )
            self.console.print("\n[bold]📋 Summary:[/bold]")
            self.console.print(f"   - Environment files: {len(self.env_files)} created")
            self.console.print(
                f"   - Secrets directory: {self.base_dir / 'secrets' / 'keys'}"
            )
            self.console.print("\n[bold yellow]📝 Next Steps:[/bold yellow]")
            self.console.print(
                "   1. Run user setup: [cyan]uv run scripts/user_input.py[/cyan]"
            )
            self.console.print("   2. Start application: [cyan]start.bat[/cyan]")

        except Exception as e:
            self.console.print(f"\n[red]❌ Environment setup failed: {e}[/red]")
            raise typer.Exit(1) from e

    def setup_directory_structure(self):
        """Create necessary directory structures."""
        self._pbar_process("Setting up directory structure")
        secrets_dir = self.base_dir / "secrets" / "keys"
        secrets_dir.mkdir(parents=True, exist_ok=True)
        self.console.print(
            f"   [green]✓ Ensured directory exists: {secrets_dir}[/green]"
        )

    def validate(self):
        """Validate existing environment configuration."""
        self.console.print("[bold blue]🔍 Environment Validation[/bold blue]")
        missing_files = [
            name for name, path in self.env_files.items() if not path.exists()
        ]

        for name, path in self.env_files.items():
            if name in missing_files:
                self.console.print(f"[red]❌ Missing: {name} ({path})[/red]")
            else:
                self.console.print(f"[green]✅ Found:   {name} ({path})[/green]")

        if missing_files:
            self.console.print(
                f"\n[red]❌ Validation failed: {len(missing_files)} files missing.[/red]"
            )
            self.console.print(
                "[yellow]Run: uv run scripts/env_input.py env-setup[/yellow]"
            )
            raise typer.Exit(1)

        self.console.print("\n[green]✅ All environment files present.[/green]")

    def show_info(self):
        """Show current environment files status."""
        self.console.print("[bold blue]📁 Environment Files Status[/bold blue]")
        for name, path in self.env_files.items():
            status = (
                "[green]✅ EXISTS[/green]" if path.exists() else "[red]❌ MISSING[/red]"
            )
            size = f"({path.stat().st_size} bytes)" if path.exists() else ""
            self.console.print(f"   {name:10} : {status} - {path} {size}")

    def clean(self):
        """Remove all environment files."""
        self.console.print("[bold red]🧹 Environment Cleanup[/bold red]")
        self.console.print("[yellow]This will remove ALL environment files![/yellow]")
        if not typer.confirm(
            "Are you sure you want to delete all environment files?", default=False
        ):
            self.console.print("[yellow]Cleanup cancelled.[/yellow]")
            raise typer.Exit()

        removed_count = 0
        for name, path in self.env_files.items():
            if path.exists():
                path.unlink()
                self.console.print(f"[red]🗑️  Removed: {name}[/red]")
                removed_count += 1

        if removed_count > 0:
            self.console.print(
                f"\n[green]✅ Removed {removed_count} environment files.[/green]"
            )
        else:
            self.console.print(
                "\n[yellow]No environment files found to remove.[/yellow]"
            )


BASE_DIR = Path(__file__).resolve().parent.parent
manager = EnvManager(BASE_DIR)


@app.command()
def env_setup():
    """Create environment files with secure keys."""
    manager.create_env_files()


@app.command()
def validate():
    """Validate existing environment configuration."""
    manager.validate()


@app.command()
def show_info():
    """Show current environment files status."""
    manager.show_info()


@app.command()
def clean():
    """Remove all environment files (use with caution!)."""
    manager.clean()


if __name__ == "__main__":
    app()
