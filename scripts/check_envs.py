"""scripts to check ".env" if exists skip, if not create it."""

# ruff: noqa: T201
import secrets
from pathlib import Path

from cryptography.fernet import Fernet

DEFAULT_UVICORN_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "log_level": "info",
    "timeout_keep_alive": 5,
    "timeout_graceful_shutdown": 5,
}


ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class EnvManager:
    def __init__(self):
        self.fernet_key = self.generate_fernet_key()
        self.secret_key = self.generate_secret_key()

    def generate_fernet_key(self):
        """Generate a new Fernet key."""
        return Fernet.generate_key().decode()

    def generate_secret_key(self):
        """Generate a new secret key."""
        return secrets.token_hex(32)


def write_env_file(path: Path, env_manager: EnvManager) -> None:
    """Write the environment variables to a .env file.

    :param path: The path to the .env file.
    :type path: Path
    :param env_manager: The EnvManager instance containing the keys.
    :type env_manager: EnvManager
    """
    env_content: str = f"""APP_DEBUG=True
APP_ENV="production"
APP_DECRYPT_KEY="{env_manager.fernet_key}"
APP_SECRET_KEY="{env_manager.secret_key}"

UVICORN_HOST="{DEFAULT_UVICORN_CONFIG["host"]}"
UVICORN_PORT={DEFAULT_UVICORN_CONFIG["port"]}
UVICORN_RELOAD={DEFAULT_UVICORN_CONFIG["reload"]!s}
UVICORN_LOG_LEVEL="{DEFAULT_UVICORN_CONFIG["log_level"]}"
UVICORN_TIMEOUT_KEEP_ALIVE={DEFAULT_UVICORN_CONFIG["timeout_keep_alive"]}
UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN={DEFAULT_UVICORN_CONFIG["timeout_graceful_shutdown"]}
"""
    with path.open("w") as f:
        f.write(env_content)


def main() -> None:
    """Check if the .env file exists and create it if it doesn't.

    This script checks for the existence of a .env file in the project root.
    If the file does not exist, it creates one with the necessary environment
    variables.
    """
    if ENV_PATH.exists():
        print(f".env already exists at {ENV_PATH}, skipping creation.")
        return
    env_manager = EnvManager()
    write_env_file(ENV_PATH, env_manager)
    print(f".env created at {ENV_PATH}")


if __name__ == "__main__":
    main()
