"""make sure modules.yaml exist , if not we will create and prompt input for first time."""

from pathlib import Path

FOLDERNAME = "secrets"
USERFILE = "users.yaml"
MODULEFILE = "modules.yaml"


def check_path():
    """Check if the path exists, if not create it."""
    path = Path(FOLDERNAME)
    if not path.exists():
        print(f"Path {path} does not exist. Creating...")
        path.mkdir(parents=True, exist_ok=True)
        print(f"Path {path} created successfully.")
    else:
        print(f"Path {path} already exists.")


def check_files():
    """Check if the user and module files exist, if not create them with placeholders."""
    user_path = Path(FOLDERNAME) / USERFILE
    module_path = Path(FOLDERNAME) / MODULEFILE

    if not user_path.exists():
        print(f"File {user_path} does not exist. Creating...")
        user_path.write_text("accounts:\n")
        print(f"File {user_path} created successfully with placeholder.")
    else:
        print(f"File {user_path} already exists.")

    if not module_path.exists():
        print(f"File {module_path} does not exist. Creating...")
        module_path.write_text("modules:\n")
        print(f"File {module_path} created successfully with placeholder.")
    else:
        print(f"File {module_path} already exists.")


if __name__ == "__main__":
    check_path()
    check_files()
    # You can add more functionality here if needed
