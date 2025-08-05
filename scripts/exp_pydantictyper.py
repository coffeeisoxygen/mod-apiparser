import typer
from pydantic import BaseModel, Field, ValidationError


class Name(BaseModel):
    model_config = {
        "populate_by_name": True,  # allow both field names and aliases
    }
    first: str = Field(min_length=5, max_length=100, alias="first_name")
    last: str = Field(..., alias="last_name")


def prompt_name() -> Name:
    while True:
        first_name = typer.prompt("First Name (min 5 chars)")
        last_name = typer.prompt("Last Name")
        try:
            return Name(first_name=first_name, last_name=last_name)
        except ValidationError as e:
            typer.secho(f"Input error: {e}", fg=typer.colors.RED)
            typer.secho("Please try again.\n", fg=typer.colors.YELLOW)


def write_to_file(data, filename=".env.example"):
    # Write as env variables: key=value
    with open(filename, "w", encoding="utf-8") as f:
        for key, value in data.items():
            f.write(f"{key}={value}\n")


def main():
    try:
        settings = Name()  # type: ignore
    except ValidationError as e:
        typer.secho(f"Env validation error: {e}", fg=typer.colors.RED)
        typer.secho("Please input values manually.", fg=typer.colors.YELLOW)
        settings = prompt_name()
    print(settings.model_dump())
    write_to_file(settings.model_dump())


if __name__ == "__main__":
    typer.run(main)
    typer.secho("Please input values manually.", fg=typer.colors.YELLOW)
    settings = prompt_name()
    print(settings.model_dump())
    write_to_file(settings.model_dump())
