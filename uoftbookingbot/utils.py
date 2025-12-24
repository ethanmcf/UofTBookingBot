import sys
import os
from pathlib import Path


_APP_NAME = "UofTBookingBot"


def is_running_as_bundle() -> bool:
    """Check if the application is running as a bundled executable."""

    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_resources_path() -> str:
    """Get the base path for persistent files, depending on the execution context."""

    if is_running_as_bundle():
        # RUNNING AS BUNDLE -> system dependent paths
        if sys.platform == "darwin":
            path = Path.home() / "Library" / "Application Support" / _APP_NAME
        elif sys.platform == "win32":
            path = Path(os.environ["APPDATA"]) / _APP_NAME
        else:
            path = Path.home() / ".local" / "share" / _APP_NAME

        path.mkdir(parents=True, exist_ok=True)
        return path
    else:
        # RUNNING IN DEV -> All files are relative to the project root
        return Path(__file__).resolve().parent.parent
