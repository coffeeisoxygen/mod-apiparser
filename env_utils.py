"""cli interactive for checking .envs."""

import secrets
import time
from pathlib import Path

import typer
from cryptography.fernet import Fernet
from rich import print
from rich.progress import track

DEFAULT_UVICORN_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "log_level": "info",
    "timeout_keep_alive": 5,
    "timeout_graceful_shutdown": 5,
}


ENV_NAME = ".env.example"
ENV_PATH = Path(__file__).resolve().parent.parent / ENV_NAME


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


def generating_keys():
    """Generate fernet and secret keys."""
    fernet_key = Fernet.generate_key().decode()
    secret_key = secrets.token_hex(32)
    return fernet_key, secret_key


def main():
    """Main entry point for the CLI."""
    if not ENV_PATH.exists():
        print(
            f"[bold red]Alert![/bold red] File [magenta]{ENV_NAME}[/magenta] tidak ditemukan di :warning: [bold yellow]{ENV_PATH}[/bold yellow], membuat baru..."
        )
        pbar_load_default()
        typer.echo("=== Konfigurasi default .env, Sesuaikan Sebelum Running App. ===")
        print(DEFAULT_UVICORN_CONFIG)
        useradmin = typer.prompt("Masukan username admin", default="admin")
        userpassword = typer.prompt(
            text="Masukan password admin",
            default="admin",
            hide_input=True,
            confirmation_prompt=True,
        )
        pbar_generate_keys()
        fernet_key, secret_key = generating_keys()
        decrypt_key = fernet_key
        secret_key = secret_key
        typer.echo(f"Fernet Key: {fernet_key}")
        typer.echo(f"Secret Key: {secret_key}")
    else:
        typer.echo(f"File {ENV_PATH} sudah ada, tidak perlu membuat baru.")


if __name__ == "__main__":
    typer.run(function=main)
