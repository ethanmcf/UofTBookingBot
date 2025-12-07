import os
from dotenv import load_dotenv


load_dotenv()


LOGIN_CREDENTIALS_PATH = os.getenv(
    "LOGIN_CREDENTIALS_PATH", "./secrets/login_credentials.txt"
)
BYPASS_CODES_PATH = os.getenv("BYPASS_CODES_PATH", "./secrets/bypass_codes.txt")
DEBUG_FOLDER_PATH = os.getenv("DEBUG_FOLDER_PATH", "./debug")
BYPASS_CODES_URL = "https://bypass.utormfa.utoronto.ca/index.php"
ACTIVITY_URLS = {
    "golf": "https://recreation.utoronto.ca/program/GetProgramDetails?courseId=5904837f-6aa4-4707-bcfb-2ece4049bae0",
    "volleyball": "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=ca92214b-0334-4e97-a60e-2144af28e435",
}
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17",
]
REGISTRATION_START_BUFFER_SECONDS = 1
DEFAULT_TIMEOUT_MILLISECONDS = 30000
