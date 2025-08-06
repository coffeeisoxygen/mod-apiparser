"""cli interactive for checking .envs."""

import secrets
import time
from pathlib import Path

import typer
from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from rich import print
from rich.progress import track

ENV_NAME = ".env"
ENV_PATH = Path(__file__).resolve().parent.parent / ENV_NAME

# Static key values as per requirements
STATIC_KEY_DECRYPT = "X1VPc29aTE5XU0ZsNzhGSXY2QTN1SHh5WjltU1JPN0hfZmZjSWx0cFNJMD0="
STATIC_KEY_SECRET = "a0f6a727454c1450c2a20c7f6ee0118311c5759ed9b4c709523abad9fdd1a06"


def pbar_load_default():
    """Progress bar for loading default configuration."""
    for _ in track(range(100), description="Loading default configuration..."):
        # Simulate loading time
        time.sleep(0.02)
    typer.echo("Default configuration loaded successfully.")


def pbar_generate_keys():
    """Progress bar for generating keys."""
    for _ in track(range(100), description="Generating keys..."):
        # Simulate key generation time
        time.sleep(0.02)
    typer.echo("Keys generated successfully.")


def pbar_hashing_process():
    """Progress bar for hashing process."""
    for _ in track(range(100), description="Hashing process..."):
        # Simulate hashing time
        time.sleep(0.02)
    typer.echo("Hashing process completed successfully.")


def generating_keys():
    """Generate fernet and secret keys."""
    fernet_key = Fernet.generate_key().decode()
    secret_key = secrets.token_hex(32)
    return fernet_key, secret_key


app = typer.Typer()


@app.command()
def env_setup():
    """Main entry point for the CLI."""
    create_env = False
    if not ENV_PATH.exists():
        print(
            f"[bold red]Alert![/bold red] File [magenta]{ENV_NAME}[/magenta] tidak ditemukan di :warning: [bold yellow]{ENV_PATH}[/bold yellow], membuat baru..."
        )
        create_env = True
    else:
        overwrite = typer.confirm(
            f"File {ENV_PATH} sudah ada. Apakah ingin menimpa (overwrite)?",
            default=False,
        )
        if overwrite:
            create_env = True
        else:
            typer.echo(f"File {ENV_PATH} sudah ada, tidak perlu membuat baru.")
            return

    if create_env:
        pbar_load_default()
        typer.echo("=== Konfigurasi .env, Masukkan username dan password admin. ===")
        admin_username = typer.prompt("Masukan username admin", default="admin")
        admin_password = typer.prompt(
            text="Masukan password admin",
            default="admin1234",
            hide_input=True,
            confirmation_prompt=True,
        )
        pbar_hashing_process()
        ph = PasswordHasher()
        hashed_password = ph.hash(admin_password)
        typer.echo(f"Username admin: {admin_username}")
        typer.echo(f"Password admin (hashed): {hashed_password}")

        env_content = f"""APP_DEBUG=False
APP_ENV="production"
ADMIN_USERNAME="{admin_username}"
ADMIN_PASSWORD="{hashed_password}"
KEY_DECRYPT="{STATIC_KEY_DECRYPT}"
KEY_SECRET="{STATIC_KEY_SECRET}"
KEY_ALGORITHM="HS256"
PATH_ACCOUNTS="accounts.yaml"
"""
        with ENV_PATH.open("w") as f:
            f.write(env_content)
        typer.secho(f"File {ENV_PATH} berhasil dibuat!", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
