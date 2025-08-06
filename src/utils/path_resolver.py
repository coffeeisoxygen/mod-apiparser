"""make sure modules.yaml exist , if not we will create and prompt input for first time."""

from pathlib import Path

from mlogger import logger
from src.exceptions.app_exceptions import AppException


def ensure_file_and_folder(path: str | Path, placeholder: str) -> None:
    """Ensure that a file and its parent folder exist.

    This function checks if the specified file and its parent directory exist.
    If the directory does not exist, it will be created. If the file does not
    exist, it will be created with the provided placeholder content.

    Args:
        path (str | Path): The path to the file.
        placeholder (str): The placeholder content for the file.

    Raises:
        AppException.PathResolverError: If the file or folder creation fails.
    """
    path = Path(path)
    log = logger.bind(action="ensure_file", file=str(path))
    try:
        if not path.parent.exists():
            log.info(f"Creating folder {path.parent}")
            path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            log.info("Creating file")
            path.write_text(placeholder)
    except Exception as e:
        log.exception(f"Failed to create file or folder: {e}")
        raise AppException.PathResolverError(
            f"Failed to create file or folder {path}: {e}"
        ) from e


def ensure_all_files(files: list[tuple[str | Path, str]]) -> None:
    """Ensure that all specified files and their parent folders exist."""
    for path, placeholder in files:
        ensure_file_and_folder(path, placeholder)


# resolver = PathResolver()
