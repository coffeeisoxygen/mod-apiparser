"""make sure modules.yaml exist , if not we will create and prompt input for first time."""

from pathlib import Path

from src.exceptions.app_exceptions import AppException
from src.mlogger import logger
from src.mlogger.utils import log_error


def ensure_file_and_folder(path: str | Path, placeholder: str = "") -> None:
    """Ensure that a file and its parent folder exist.

    This function checks if the specified file and its parent directory exist.
    If the directory does not exist, it will be created. If the file does not
    exist, it will be created with the provided placeholder content (or empty if not given).

    Args:
        path (str | Path): The path to the file.
        placeholder (str, optional): The placeholder content for the file. Defaults to empty string.

    Raises:
        AppException.PathResolverError: If the file or folder creation fails.
    """
    path = Path(path)

    # Bind context untuk tracking operasi file ini
    bound_logger = logger.bind(
        operation="ensure_file_and_folder",
        file_path=str(path),
        parent_folder=str(path.parent),
    )

    bound_logger.debug("Checking file and folder existence")

    try:
        # Create parent directory if it doesn't exist
        if not path.parent.exists():
            bound_logger.info("Creating parent directory: {}", path.parent)
            path.parent.mkdir(parents=True, exist_ok=True)
            bound_logger.success("Parent directory created successfully")
        else:
            bound_logger.debug("Parent directory already exists")

        # Create file if it doesn't exist
        if not path.exists():
            if placeholder:
                bound_logger.info("Creating file with placeholder content")
                path.write_text(placeholder)
                bound_logger.success(
                    "File created successfully with placeholder content"
                )
            else:
                bound_logger.info("Creating empty file (no placeholder)")
                path.touch()
                bound_logger.success("Empty file created successfully")
        else:
            bound_logger.debug("File already exists")

    except PermissionError as e:
        log_error(
            error=e,
            message="Permission denied while creating file or folder",
            extra_context={
                "file_path": str(path),
                "parent_folder": str(path.parent),
                "operation": "ensure_file_and_folder",
            },
        )
        raise AppException.PathResolverError(
            f"Permission denied: Cannot create file or folder {path}"
        ) from e

    except OSError as e:
        log_error(
            error=e,
            message="OS error while creating file or folder",
            extra_context={
                "file_path": str(path),
                "parent_folder": str(path.parent),
                "operation": "ensure_file_and_folder",
            },
        )
        raise AppException.PathResolverError(
            f"OS error: Failed to create file or folder {path}"
        ) from e

    except Exception as e:
        log_error(
            error=e,
            message="Unexpected error while creating file or folder",
            extra_context={
                "file_path": str(path),
                "parent_folder": str(path.parent),
                "operation": "ensure_file_and_folder",
                "placeholder_length": len(placeholder)
                if placeholder is not None
                else 0,
            },
        )
        raise AppException.PathResolverError(
            f"Failed to create file or folder {path}: {e}"
        ) from e


def ensure_all_files(files: list[tuple[str | Path, str]]) -> None:
    """Ensure that all specified files and their parent folders exist.

    Args:
        files: List of tuples containing (file_path, placeholder_content). If placeholder_content is omitted or None, file will be empty.
    """
    logger.info("Starting batch file creation for {} files", len(files))

    success_count = 0
    error_count = 0

    for entry in files:
        # Support (path,) or (path, placeholder)
        if isinstance(entry, (list, tuple)) and len(entry) == 2:
            path, placeholder = entry
        elif isinstance(entry, (list, tuple)) and len(entry) == 1:
            path = entry[0]
            placeholder = ""
        else:
            path = entry
            placeholder = ""
        try:
            ensure_file_and_folder(path, placeholder)
            success_count += 1
        except Exception as e:
            error_count += 1
            # Gunakan log_error utility untuk error yang lebih comprehensive
            log_error(
                error=e,
                message="Failed to ensure file in batch operation",
                extra_context={
                    "file_path": str(path),
                    "batch_operation": "ensure_all_files",
                },
            )

    # Log summary
    if error_count == 0:
        logger.success("All {} files ensured successfully", success_count)
    else:
        logger.warning(
            "Batch file creation completed: {} successful, {} failed",
            success_count,
            error_count,
        )
