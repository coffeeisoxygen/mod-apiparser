import asyncio
import pathlib
from collections.abc import Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from mlogger import logger


def ensure_str_path(path: pathlib.Path | str | bytes) -> str:
    """Ensure the given path is a str, decoding if necessary."""
    if isinstance(path, bytes):
        return path.decode("utf-8")
    return str(path)


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path: pathlib.Path, callback: Callable):
        self.file_path = file_path
        self.callback = callback
        self.debounce_task: asyncio.Task | None = None

    def on_modified(self, event) -> None:
        """Handle file modification event with debouncing."""
        event_path = ensure_str_path(event.src_path)
        if not event.is_directory and pathlib.Path(event_path) == self.file_path:
            logger.info("Change detected. Debouncing for 1 second.")

            # Cancel the old task if it exists
            if self.debounce_task:
                self.debounce_task.cancel()

            # Schedule a new async task to reload
            loop = asyncio.get_event_loop()
            self.debounce_task = loop.create_task(self._trigger_reload_async())

    async def _trigger_reload_async(self):
        """Wait for a brief pause and then trigger the reload callback."""
        try:
            await asyncio.sleep(1.0)
            logger.info("Triggering reload after a brief pause.")
            self.callback()
        except asyncio.CancelledError:
            # Task was cancelled because a new event arrived
            logger.debug("Reload task cancelled due to a new change event.")
            raise  # <-- Tambahkan ini


class FileWatcher:
    def __init__(self, file_path: pathlib.Path, callback: Callable):
        self._observer = Observer()
        self._event_handler = ChangeHandler(file_path, callback)
        self._path_to_watch = file_path.parent

    def start(self):
        """Starts the file system observer."""
        self._observer.schedule(
            self._event_handler,
            str(self._path_to_watch),
            recursive=False,  # <-- str()
        )
        self._observer.start()
        logger.info("File watcher started.", path=str(self._path_to_watch))

    def stop(self):
        """Stops the file system observer and waits for it to finish."""
        self._observer.stop()
        self._observer.join()
        logger.info("File watcher stopped.")
