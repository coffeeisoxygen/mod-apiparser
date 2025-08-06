"""Admin user creation CLI - focused on creating admin accounts.

This module is responsible for:
- Creating admin user accounts only
- Simple prompts for username, email, name, password
- Auto-sets is_active=True and is_superuser=True
"""

from pathlib import Path

import typer
import yaml
from pydantic import BaseModel, EmailStr, Field, ValidationError
from rich.console import Console
from rich.prompt import Prompt
from src.service.hasher_service import HasherService

app = typer.Typer(
    name="admin-create", help="Admin user creation tool", no_args_is_help=True
)
console = Console()


class AdminUserInput(BaseModel):
    """Admin user input model with validation."""

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

    # Auto-set admin properties
    is_active: bool = Field(
        default=True, description="User active status (always True for admin)"
    )
    is_superuser: bool = Field(
        default=True, description="Superuser privileges (always True for admin)"
    )

    def get_hashed_password(self) -> str:
        """Get hashed password using HasherService."""
        return HasherService.hash_password(self.password)


def prompt_for_field(field_name: str, description: str, default_value: str = "") -> str:
    """Prompt for single field with validation loop."""
    while True:
        try:
            if field_name == "password":
                value = Prompt.ask(f"🔒 {description}", password=True)
            else:
                prompt_text = f"📝 {description}"
                if default_value:
                    prompt_text += f" [{default_value}]"
                value = Prompt.ask(prompt_text, default=default_value)

            # Test validation with dummy data
            test_data = {
                "username": "testuser",
                "email": "test@example.com",
                "name": "Test User",
                "password": "password123",
                "is_active": True,  # Ensure correct type
                "is_superuser": True,  # Ensure correct type
            }
            test_data[field_name] = value
            AdminUserInput(**test_data)
        except ValidationError as e:
            error_msg = e.errors()[0]["msg"] if e.errors() else "Invalid input"
            console.print(f"[red]❌ {error_msg}[/red]")
        else:
            return value


@app.command()
def create_admin(
    username: str = typer.Option(None, "--username", "-u", help="Admin username"),
    email: str = typer.Option(None, "--email", "-e", help="Admin email"),
    name: str = typer.Option(None, "--name", "-n", help="Admin full name"),
    password: str = typer.Option(None, "--password", "-p", help="Admin password"),
    env: str = typer.Option("dev", "--env", help="Environment (dev/prod/test)"),
):
    """Create admin user account.

    Creates an admin user with superuser privileges.
    Auto-sets is_active=True and is_superuser=True.
    """
    console.print("[bold blue]👤 Admin User Creation[/bold blue]")
    console.print("[yellow]Creating admin account with full privileges[/yellow]\n")

    # Collect data interactively if not provided via CLI
    data = {}

    fields = AdminUserInput.model_fields

    data["username"] = username or prompt_for_field(
        "username", fields["username"].description or "Admin username", "admin"
    )
    data["email"] = email or prompt_for_field(
        "email", fields["email"].description or "Admin email", "admin@example.com"
    )
    data["name"] = name or prompt_for_field(
        "name", fields["name"].description or "Admin full name", "Administrator"
    )
    data["password"] = password or prompt_for_field(
        "password", fields["password"].description or "Admin password"
    )

    try:
        # Create admin user (automatically sets is_active=True, is_superuser=True)
        admin_user = AdminUserInput(**data)

        # Save to YAML
        save_admin_to_yaml(admin_user, env)

        console.print(
            f"\n[bold green]✅ Admin user '{admin_user.username}' created successfully![/bold green]"
        )
        console.print(f"[green]📁 Environment: {env}[/green]")
        console.print("[green]🔑 Superuser privileges: ✅ Enabled[/green]")
        console.print(f"[green]📧 Email: {admin_user.email}[/green]")

    except typer.Abort:
        console.print("\n[yellow]❌ Admin creation cancelled by user[/yellow]")
        raise typer.Exit(1) from None
    except ValidationError as e:
        console.print(f"[red]❌ Validation error: {e}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]❌ Failed to create admin user: {e}[/red]")
        raise typer.Exit(1) from e


def save_admin_to_yaml(admin_user: AdminUserInput, env: str = "dev") -> None:
    """Save admin user to YAML file."""
    base_dir = Path(__file__).resolve().parent.parent
    yaml_file = base_dir / "secrets" / f"{env}_users.yaml"

    admin_data = {
        "username": admin_user.username,
        "email": admin_user.email,
        "name": admin_user.name,
        "password": admin_user.get_hashed_password(),
        "is_active": True,  # Always True for admin
        "is_superuser": True,  # Always True for admin
    }

    existing_data = {"users": []}
    if yaml_file.exists():
        with open(yaml_file) as f:
            existing_data = yaml.safe_load(f) or {"users": []}

    # Check if admin user already exists
    for existing_user in existing_data["users"]:
        if existing_user.get("username") == admin_user.username:
            console.print(
                f"[yellow]⚠️  User '{admin_user.username}' already exists. Updating...[/yellow]"
            )
            existing_user.update(admin_data)
            break
    else:
        existing_data["users"].append(admin_data)

    # Ensure directory exists
    yaml_file.parent.mkdir(parents=True, exist_ok=True)

    with open(yaml_file, "w") as f:
        yaml.dump(existing_data, f, default_flow_style=False)

    console.print(f"[green]✅ Admin user saved to {yaml_file}[/green]")


@app.command()
def show_info():
    """Show information about existing users."""
    console.print("[bold blue]👥 User Information[/bold blue]")

    base_dir = Path(__file__).resolve().parent.parent
    environments = ["dev", "prod", "test"]

    for env in environments:
        _show_env_users(base_dir, env)


def _show_env_users(base_dir: Path, env: str) -> None:
    """Show users for a specific environment."""
    yaml_file = base_dir / "secrets" / f"{env}_users.yaml"
    console.print(f"\n[bold]{env.upper()} Environment:[/bold]")

    if not yaml_file.exists():
        console.print("  [red]❌ No user file found[/red]")
        return

    with open(yaml_file) as f:
        data = yaml.safe_load(f) or {"users": []}

    users = data.get("users", [])
    if not users:
        console.print("  [dim]No users found[/dim]")
        return

    for user in users:
        _display_user_info(user)


def _display_user_info(user: dict) -> None:
    """Display single user information."""
    status = "🔑 ADMIN" if user.get("is_superuser") else "👤 USER"
    active = "✅" if user.get("is_active") else "❌"
    console.print(f"  {status} {active} {user.get('username')} ({user.get('email')})")


if __name__ == "__main__":
    app()
