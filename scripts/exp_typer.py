from enum import Enum

import click
import typer


class Size(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


def main():
    """Prompt user to select a size from Enum choices."""
    size_choice = click.Choice([s.value for s in Size])
    try:
        selected_size_str = typer.prompt(
            "What size do you prefer?",
            type=size_choice,
            default=Size.MEDIUM.value,
            show_choices=True,
        )
        selected_size = Size(selected_size_str)
    except ValueError:
        typer.secho(
            f"Input tidak valid. Pilihan hanya: {[s.value for s in Size]}",
            fg=typer.colors.RED,
        )
        return
    print(f"You selected: {selected_size.value}")


if __name__ == "__main__":
    typer.run(main)
