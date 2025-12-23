import sys
import os
from pathlib import Path


def get_internal_root() -> Path:
    """Get the internal base path for extra bundled files, depending on the execution context."""

    if getattr(sys, "frozen", False):
        # RUNNING AS BUNDLE
        return Path(sys._MEIPASS)  # internal temp folder for PyInstaller
    else:
        # RUNNING IN DEV -> All files are relative to the project root (one level up from /src)
        return Path(__file__).resolve().parent.parent


def get_external_root() -> Path:
    """Get the external base path for persistent files, depending on the execution context."""

    if getattr(sys, "frozen", False):
        # RUNNING AS BUNDLE -> system dependent paths
        APP_NAME = "UofTBookingBot"
        if sys.platform == "darwin":
            # Standard macOS path: ~/Library/Application Support/UofTBookingBot
            path = Path.home() / "Library" / "Application Support" / APP_NAME
        elif sys.platform == "win32":
            # Standard Windows path: ~/AppData/Roaming/UofTBookingBot
            path = Path(os.environ["APPDATA"]) / APP_NAME
        else:
            # Standard Linux path: ~/.local/share/UofTBookingBot
            path = Path.home() / ".local" / "share" / APP_NAME

        path.mkdir(parents=True, exist_ok=True)
        return path
    else:
        # RUNNING IN DEV -> All files are relative to the project root (one level up from /src)
        return get_internal_root()


def get_project_root() -> Path:
    """Get the root path of the project, depending on the execution context."""

    if getattr(sys, "frozen", False):
        # In bundle, PROJECT_ROOT usually refers to the folder where the .exe sits
        return Path(sys.executable).parent
    else:
        return get_internal_root()


# Define global paths
INTERNAL_ROOT = get_internal_root()
EXTERNAL_ROOT = get_external_root()
PROJECT_ROOT = get_project_root()
SECRETS_DIR = EXTERNAL_ROOT / "secrets"
DEBUG_DIR = EXTERNAL_ROOT / "debug"


def run_global_configurations():
    """Run any global configurations needed at startup."""

    SECRETS_DIR.mkdir(exist_ok=True)
    DEBUG_DIR.mkdir(exist_ok=True)
