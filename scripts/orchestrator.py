# type: ignore
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import track

from .envmanager import config  # type: ignore
from .envmanager.generator import EnvFileGenerator

app = typer.Typer(
    name="orchestrator",
    help="A modern tool to manage application setup and environment files.",
    no_args_is_help=True,
)

console = Console()
BASE_DIR = Path(__file__).resolve().parent.parent


def pbar_process(description: str, duration: float = 1.0):
    """Generic progress bar."""
    for _ in track(range(100), description=description, console=console):
        time.sleep(duration / 100)
    console.print(f"[green]✅ {description} completed.[/green]")


@app.command()
def setup(
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        "-o",
        help="Overwrite existing environment files without asking.",
    ),
):
    """Generates all environment files (.env, .env.dev, .env.prod, .env.test)."""
    console.print("[bold blue]🚀 Starting Modern Environment Setup...[/bold blue]")

    env_files_to_create = {
        "base": BASE_DIR / ".env",
        "dev": BASE_DIR / ".env.dev",
        "prod": BASE_DIR / ".env.prod",
        "test": BASE_DIR / ".env.test",
    }

    # Check for existing files
    if not overwrite:
        existing_files = [p.name for p in env_files_to_create.values() if p.exists()]
        if existing_files:
            console.print("\n[yellow]⚠️ Found existing files:[/yellow]")
            for f in existing_files:
                console.print(f"   - {f}")

            confirm = typer.confirm("\nDo you want to overwrite them?", default=False)
            if not confirm:
                console.print("[red]❌ Setup cancelled by user.[/red]")
                raise typer.Exit()

    try:
        pbar_process("Initializing configurations")

        # The core logic using the new factory
        for env_name, path in env_files_to_create.items():
            console.print(f"\n[cyan]Processing: {env_name} environment...[/cyan]")

            # 1. Get config from the factory
            overrides = config.ENVIRONMENTS.get(env_name, {})

            # 2. Create the generator ("the factory")
            file_generator = EnvFileGenerator(config.BASE_CONFIG, overrides)

            # 3. Generate the content
            content = file_generator.generate_content(env_name)

            # 4. Write the file
            with path.open("w") as f:
                f.write(content)
            console.print(f"   [green]✓ Created: {path.name}[/green]")

        # Setup other necessary structures (can be expanded later)
        pbar_process("Finalizing directory structures")
        secrets_dir = BASE_DIR / "secrets" / "keys"
        secrets_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"   [green]✓ Ensured directory exists: {secrets_dir}[/green]")

        console.print(
            "\n[bold green]🎉 Modern environment setup completed successfully![/bold green]"
        )
        console.print("\n[bold yellow]Next Steps:[/bold yellow]")
        console.print("   - Review the generated .env files.")
        console.print("   - When ready, you can start the application.")

    except Exception as e:
        console.print(f"\n[bold red]❌ An error occurred during setup: {e}[/bold red]")
        raise typer.Exit(1) from e


@app.command()
def validate():
    """Validates that all required environment files exist."""
    # This can be implemented later to check file integrity
    console.print("[yellow]Validation command is not fully implemented yet.[/yellow]")
    console.print("Checking for file existence...")

    env_files_to_check = {
        "base": BASE_DIR / ".env",
        "dev": BASE_DIR / ".env.dev",
        "prod": BASE_DIR / ".env.prod",
        "test": BASE_DIR / ".env.test",
    }

    missing_files = []
    for name, path in env_files_to_check.items():
        if not path.exists():
            missing_files.append(name)
            console.print(f"[red]❌ Missing: {name} ({path})[/red]")
        else:
            console.print(f"[green]✅ Found:   {name}[/green]")

    if missing_files:
        console.print(
            f"\n[red]Validation failed. Missing {len(missing_files)} files.[/red]"
        )
        raise typer.Exit(1)
    else:
        console.print("\n[green]✅ All required environment files are present.[/green]")


if __name__ == "__main__":
    app()
