"""Simple CLI implementation using pydantic-settings."""

from pathlib import Path

import yaml
from pydantic import EmailStr, Field, ValidationError
from pydantic_settings import BaseSettings, CliApp
from rich.console import Console
from rich.prompt import Prompt
from src.service.hasher_service import HasherService

console = Console()


class UserInput(BaseSettings):
    """User input settings with CLI support."""

    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username (3-50 chars, alphanumeric + underscore/dash)",
    )
    email: EmailStr = Field(description="Valid email address")
    name: str = Field(
        min_length=2, max_length=100, description="Full name (2-100 characters)"
    )
    password: str = Field(min_length=6, description="Password (minimum 6 characters)")
    is_active: bool = Field(default=True, description="User active status")
    is_superuser: bool = Field(default=False, description="Superuser privileges")

    class Config:
        """Pydantic config for CLI."""

        env_prefix = "USER_"
        cli_prog_name = "user-create"

    def get_hashed_password(self) -> str:
        """Get hashed password using HasherService."""
        return HasherService.hash_password(self.password)


def prompt_for_field(
    field_name: str, description: str, default_value: object = None
) -> str | bool:
    """Prompt for single field with validation loop."""
    while True:
        try:
            if field_name == "password":
                value = Prompt.ask(f"🔒 {description}", password=True)
            elif isinstance(default_value, bool):
                value = _prompt_bool_field(description, default_value)
            else:
                value = _prompt_default_field(description, default_value)
            # Test validation
            test_data = get_test_data()
            test_data[field_name] = value
            UserInput(**test_data)
        except ValidationError as e:
            error_msg = e.errors()[0]["msg"] if e.errors() else "Invalid input"
            console.print(f"[red]❌ {error_msg}[/red]")
        else:
            return value


def _prompt_bool_field(description: str, default_value: bool) -> bool:
    choice = Prompt.ask(
        f"{'✅' if default_value else '❌'} {description}",
        choices=["y", "n"],
        default="y" if default_value else "n",
    )
    return choice.lower() == "y"


def _prompt_default_field(description: str, default_value: object) -> str:
    prompt_text = f"📝 {description}"
    if default_value:
        prompt_text += f" [{default_value}]"
    return Prompt.ask(prompt_text, default=str(default_value) if default_value else "")


def get_test_data() -> dict:
    """Get minimal test data for validation."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "name": "Test User",
        "password": "password123",
        "is_active": True,
        "is_superuser": False,
    }


def interactive_mode() -> UserInput:
    """Interactive user creation."""
    console.print("[bold blue]👤 Interactive User Creation[/bold blue]")

    fields = UserInput.model_fields
    data = {}

    data["username"] = prompt_for_field(
        "username", fields["username"].description or "", "admin"
    )
    data["email"] = prompt_for_field(
        "email", fields["email"].description or "", "admin@example.com"
    )
    data["name"] = prompt_for_field(
        "name", fields["name"].description or "", "Administrator"
    )
    data["password"] = prompt_for_field(
        "password", fields["password"].description or ""
    )
    data["is_active"] = prompt_for_field(
        "is_active", fields["is_active"].description or "", True
    )
    data["is_superuser"] = prompt_for_field(
        "is_superuser", fields["is_superuser"].description or "", False
    )

    return UserInput(**data)


def save_to_yaml(user: UserInput, env: str = "dev") -> None:
    """Save user to YAML file."""
    base_dir = Path(__file__).resolve().parent.parent
    yaml_file = base_dir / "secrets" / f"{env}_users.yaml"

    user_data = {
        "username": user.username,
        "email": user.email,
        "name": user.name,
        "password": user.get_hashed_password(),
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
    }

    existing_data = {"users": []}
    if yaml_file.exists():
        with open(yaml_file) as f:
            existing_data = yaml.safe_load(f) or {"users": []}

    existing_data["users"].append(user_data)

    yaml_file.parent.mkdir(parents=True, exist_ok=True)
    with open(yaml_file, "w") as f:
        yaml.dump(existing_data, f, default_flow_style=False)

    console.print(f"[green]✅ User saved to {yaml_file}[/green]")


def cli_main():
    """Main CLI function."""
    try:
        # Try CLI mode first
        user = CliApp.run(UserInput, cli_exit_on_error=False)
        save_to_yaml(user)
        console.print(f"[green]✅ CLI: User '{user.username}' created[/green]")

    except ValidationError:
        # If CLI args are incomplete, switch to interactive mode
        console.print(
            "[yellow]📝 CLI args incomplete, switching to interactive mode[/yellow]"
        )
        user = interactive_mode()
        # Ask for environment
        env = Prompt.ask(
            "🌍 Environment", choices=["dev", "prod", "test", "base"], default="dev"
        )
        save_to_yaml(user, env)
        console.print(
            f"[green]✅ Interactive: User '{user.username}' created in '{env}' environment[/green]"
        )
    except SystemExit:
        raise  # Reraise to stop the application as the user expects


if __name__ == "__main__":
    cli_main()
