from pathlib import Path
import sys

from uoftbookingbot.utils import is_running_as_bundle


ASSETS_DIR_PATH = str(
    Path(sys._MEIPASS) / "assets" if is_running_as_bundle() else Path(__file__).parent / "assets"
)
