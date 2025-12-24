from uoftbookingbot.utils import get_resources_path


CREDENTIALS_PATH = str(get_resources_path() / "secrets" / "login_credentials.txt")
BYPASS_CODES_PATH = str(get_resources_path() / "secrets" / "bypass_codes.txt")
ERROR_LOG_PATH = str(get_resources_path() / "debug" / "logs" / "error.log")
OUTPUT_LOG_PATH = str(get_resources_path() / "debug" / "logs" / "output.log")
SCREENSHOTS_PATH = str(get_resources_path() / "debug" / "screenshots")
