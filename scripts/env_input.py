"""cli interactive for checking .envs."""

import secrets
import time
from enum import StrEnum
from pathlib import Path

import click
import click_prompt
import typer
from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from rich import print
from rich.progress import track

ENV_NAME = ".env.example"
ENV_PATH = Path(__file__).resolve().parent.parent / ENV_NAME


class EnvironmentEnum(StrEnum):
    """Enumeration for environment types."""

    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TESTING = "testing"


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


class Command(typer.core.TyperCommand):
    def __call__(self, *args, **kwargs) -> None:
        for p in self.params:
            if isinstance(p, click.Option) and isinstance(p.type, click.Choice):
                p.__class__ = click_prompt.ChoiceOption
        super().__call__(*args, **kwargs)


app = typer.Typer(cls=Command)


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
        typer.echo("=== Konfigurasi .env, Masukkan semua data yang diperlukan. ===")
        useradmin = typer.prompt("Masukan username admin", default="admin")
        userpassword = typer.prompt(
            text="Masukan password admin",
            default="admin",
            hide_input=True,
            confirmation_prompt=True,
        )
        pbar_hashing_process()
        ph = PasswordHasher()
        hashed_password = ph.hash(userpassword)
        typer.echo(f"Username admin: {useradmin}")
        typer.echo(f"Password admin (hashed): {hashed_password}")
        pbar_generate_keys()
        fernet_key, secret_key = generating_keys()
        typer.echo(f"Fernet Key: {fernet_key}")
        typer.echo(f"Secret Key: {secret_key}")
        typer.echo("generating Algorithm: HS256")
        debug = typer.confirm("Aktifkan debug mode?", default=True)
        env_choice = click.Choice([e.value for e in EnvironmentEnum])
        app_env = typer.prompt(
            text="Pilih environment",
            type=env_choice,
            default=EnvironmentEnum.PRODUCTION.value,
            show_choices=True,
        )

        env_content = f"""APP_DEBUG={debug}
APP_ENV="{app_env}"
APP_DECRYPT_KEY="{fernet_key}"
APP_SECRET_KEY="{secret_key}"
APP_HASH_ALGORITHM="HS256"
ADMIN_USER="{useradmin}"
ADMIN_PASSWORD="{hashed_password}"
"""
        with ENV_PATH.open("w") as f:
            f.write(env_content)
        typer.secho(f"File {ENV_PATH} berhasil dibuat!", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
