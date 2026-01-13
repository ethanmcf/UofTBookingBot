from pathlib import Path
from uoftbookingbot.utils import get_resources_path


ACTIVITIES = {
    "golf": {"id": "5904837f-6aa4-4707-bcfb-2ece4049bae0", "posting_offset": 2},
    "test": {"id": "ca92214b-0334-4e97-a60e-2144af28e435", "posting_offset": None},
}

# Global Paths
DB_PATH = str(get_resources_path() / "database" / "database.db")
LOG_DIR_PATH = str(get_resources_path() / "logs")
SCREENSHOTS_DIR_PATH = str(get_resources_path() / "debug" / "screenshots")
# Ensure necessary directories exist
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
Path(LOG_DIR_PATH).mkdir(parents=True, exist_ok=True)
Path(SCREENSHOTS_DIR_PATH).mkdir(parents=True, exist_ok=True)
