import os
import logging
import textwrap
from playwright.sync_api import Page
from datetime import datetime
from automation.shared.config import DEBUG_FOLDER_PATH


def get_app_logger():
    """Configures and returns the application logger."""

    log_folder = os.path.join(DEBUG_FOLDER_PATH, "logs")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=os.path.join(log_folder, "error.log"),
        filemode="a",
    )

    return logging.getLogger()


def save_debug_screenshot(page: Page, folder_path: str) -> None:
    """Saves a screenshot of the current page state for debugging."""

    screenshots_folder = os.path.join(folder_path, "screenshots")
    if not os.path.exists(screenshots_folder):
        os.makedirs(screenshots_folder)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(
        screenshots_folder, f"error_screenshot_{timestamp}.png"
    )
    page.screenshot(path=screenshot_path)
    print(f"Debug screenshot saved to: {screenshot_path}")


def print_exception(e):
    title = "ERROR"
    title_width = 20
    message_width = 80  # max width
    f_c = " "  # fill char in title
    title_len = len(title)
    f_len = (title_width - title_len - 2) // 2  # number of fill chars on each side
    ex = (title_width - title_len - 2) % 2  # extra fill char on right side if nec.
    print(
        "-" * title_width
        + "\n"
        + f_c * f_len
        + " "
        + title
        + " "
        + f_c * (f_len + ex)
        + "\n"
        + "-" * title_width
        + "\n"
        + textwrap.fill(str(e), width=message_width)
        + "\n"
    )
