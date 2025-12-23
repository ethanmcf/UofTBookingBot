import os

from dotenv import load_dotenv

load_dotenv()

LOGIN_CREDENTIALS_PATH = os.getenv(
    "LOGIN_CREDENTIALS_PATH", "./secrets/login_credentials.txt"
)
BYPASS_CODES_PATH = os.getenv("BYPASS_CODES_PATH", "./secrets/bypass_codes.txt")
DEBUG_FOLDER_PATH = "./debug"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17",
]
DEFAULT_TIMEOUT_MILLISECONDS = 30000
