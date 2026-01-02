from uoftbookingbot.utils import get_resources_path


CREDENTIALS_PATH = str(get_resources_path() / "secrets" / "login_credentials.txt")
BYPASS_CODES_PATH = str(get_resources_path() / "secrets" / "bypass_codes.txt")
LOG_DIR_PATH = str(get_resources_path() / "logs")
SCREENSHOTS_DIR_PATH = str(get_resources_path() / "debug" / "screenshots")

ACTIVITIES = {"golf": {"id": "5904837f-6aa4-4707-bcfb-2ece4049bae0", "posting_offset": 2}}
