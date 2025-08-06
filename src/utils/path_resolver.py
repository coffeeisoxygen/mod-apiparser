"""make sure modules.yaml exist , if not we will create and prompt input for first time."""

from pathlib import Path

from mlogger import logger


class PathResolver:
    def __init__(
        self,
        foldername="secrets",
        userfile="users.yaml",
        modulefile="modules.yaml",
        user_path=None,
        module_path=None,
    ):
        if user_path:
            self.user_path = Path(user_path)
            self.folder_path = self.user_path.parent
        else:
            self.folder_path = Path(foldername)
            self.user_path = self.folder_path / userfile

        if module_path:
            self.module_path = Path(module_path)
            # Optionally update folder_path if not set by user_path
            if not user_path:
                self.folder_path = self.module_path.parent
        else:
            self.module_path = self.folder_path / modulefile

        self.foldername = str(self.folder_path)
        self.userfile = self.user_path.name
        self.modulefile = self.module_path.name

    def check_path(self):
        """Check if the path exists, if not create it."""
        if not self.folder_path.exists():
            logger.info(f"Path {self.folder_path} does not exist. Creating...")
            self.folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Path {self.folder_path} created successfully.")
        else:
            logger.info(f"Path {self.folder_path} already exists.")

    def check_files(self):
        """Check if the user and module files exist, if not create them with placeholders."""
        if not self.user_path.exists():
            logger.info(f"File {self.user_path} does not exist. Creating...")
            self.user_path.write_text("accounts:\n")
            logger.info(f"File {self.user_path} created successfully with placeholder.")
        else:
            logger.info(f"File {self.user_path} already exists.")

        if not self.module_path.exists():
            logger.info(f"File {self.module_path} does not exist. Creating...")
            self.module_path.write_text("modules:\n")
            logger.info(
                f"File {self.module_path} created successfully with placeholder."
            )
        else:
            logger.info(f"File {self.module_path} already exists.")

    def ensure_all(self):
        """Ensure both path and files exist."""
        self.check_path()
        self.check_files()


# Usage example (for lifespan or elsewhere):
# resolver = PathResolver()
# resolver.ensure_all()
