from uoftbookingbot.utils import get_resources_path


CREDENTIALS_PATH = str(get_resources_path() / "secrets" / "login_credentials.txt")
BYPASS_CODES_PATH = str(get_resources_path() / "secrets" / "bypass_codes.txt")
LOG_DIR_PATH = str(get_resources_path() / "logs")
SCREENSHOTS_DIR_PATH = str(get_resources_path() / "debug" / "screenshots")

ACTIVITIES = {
    "golf": {"id": "5904837f-6aa4-4707-bcfb-2ece4049bae0", "posting_offset": 2},
    "test": {"id": "92c30d9c-3a40-4f05-96f0-21b2c18f292c", "posting_offset": None},
}
