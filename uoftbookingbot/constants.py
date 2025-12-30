from uoftbookingbot.utils import get_resources_path


CREDENTIALS_PATH = str(get_resources_path() / "secrets" / "login_credentials.txt")
BYPASS_CODES_PATH = str(get_resources_path() / "secrets" / "bypass_codes.txt")
LOG_DIR_PATH = str(get_resources_path() / "uoftbookingbot" / "logs")
SCREENSHOTS_DIR_PATH = str(get_resources_path() / "uoftbookingbot" / "screenshots")