# account_cli.py
import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from services.crypto_service import CryptoService
from src.accounts.account_service import AccountFileService
from src.accounts.sch_account import AccountCreate, EnumAPIProvider

console = Console()
app = typer.Typer(rich_markup_mode="rich")


class AsyncCLI:
    def __init__(self):
        self.crypto_service = CryptoService()
        self.account_service = AccountFileService(self.crypto_service)

    async def interactive_create_account(self) -> AccountCreate | None:
        """Interactive account creation dengan pydantic validation"""
        console.print("[bold blue]Creating New Account[/bold blue]")

        try:
            # Collect all required fields
            accountid = Prompt.ask("Account ID (alphanumeric/underscore, 1-10 chars)")
            username = Prompt.ask("Username", password=False)
            pin = Prompt.ask("PIN", password=True)
            password = Prompt.ask("Password", password=True)
            msisdn = Prompt.ask("MSISDN (phone number)")
            email = Prompt.ask("Email")
            base_url = Prompt.ask("Base URL")

            # Show available providers
            providers = [p.value for p in EnumAPIProvider]
            console.print(f"Available providers: {', '.join(providers)}")
            provider = Prompt.ask("Provider", choices=providers)

            is_active = Confirm.ask("Is Active?", default=True)

            # Optional fields
            name = Prompt.ask("Name (optional)", default=None, show_default=False)
            description = Prompt.ask(
                "Description (optional)", default=None, show_default=False
            )

            # Create and validate dengan pydantic
            account_data = AccountCreate(
                accountid=accountid,
                username=username,
                pin=pin,
                password=password,
                msisdn=msisdn,
                email=email,
                base_url=base_url,
                provider=EnumAPIProvider(provider),
                is_active=is_active,
                name=name if name else None,
                description=description if description else None,
            )

            console.print("[green]✓ Account data validated successfully![/green]")
            return account_data

        except Exception as e:
            console.print(f"[red]❌ Validation error: {e}[/red]")
            return None

    async def create_initial_config(self) -> bool:
        """Create initial accounts.yaml file"""
        accounts_path = Path("accounts.yaml")

        if accounts_path.exists():
            if not Confirm.ask("accounts.yaml already exists. Overwrite?"):
                return False

        console.print("[yellow]No accounts.yaml found. Let's create one![/yellow]")

        accounts = []
        while True:
            account = await self.interactive_create_account()
            if account:
                accounts.append(account)
                console.print(f"[green]✓ Account '{account.accountid}' added[/green]")

            if not Confirm.ask("Add another account?", default=False):
                break

        if not accounts:
            console.print("[red]No accounts created. Exiting...[/red]")
            return False

        # Save encrypted accounts
        success = await self.account_service.save_accounts(accounts, accounts_path)
        if success:
            console.print(
                f"[green]✓ Created accounts.yaml with {len(accounts)} accounts[/green]"
            )
            return True
        else:
            console.print("[red]❌ Failed to save accounts[/red]")
            return False


# CLI Commands
@app.command()
def init():
    """Initialize accounts.yaml configuration"""

    async def _init():
        cli = AsyncCLI()
        success = await cli.create_initial_config()
        if not success:
            raise typer.Exit(1)

    asyncio.run(_init())


@app.command()
def list_accounts():
    """List all accounts"""

    async def _list():
        cli = AsyncCLI()
        accounts = await cli.account_service.load_accounts(Path("accounts.yaml"))

        if not accounts:
            console.print("[yellow]No accounts found[/yellow]")
            return

        table = Table(title="Accounts")
        table.add_column("Account ID", style="cyan")
        table.add_column("Provider", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Name", style="blue")

        for account in accounts:
            status = "✓ Active" if account.is_active else "✗ Inactive"
            table.add_row(
                account.accountid, account.provider.value, status, account.name or "N/A"
            )

        console.print(table)

    asyncio.run(_list())


if __name__ == "__main__":
    app()
