import logging
import os
import textwrap
from playwright.sync_api import Page
from datetime import datetime


def get_app_logger(log_path: str) -> logging.Logger:
    """Configures and returns the application logger."""

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=log_path,
        filemode="a",
    )

    return logging.getLogger()


def save_debug_screenshot(page: Page, path: str) -> None:
    """Saves a screenshot of the current page state for debugging."""

    if not os.path.exists(path):
        os.makedirs(path)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(path, f"error_screenshot_{timestamp}.png")
    page.screenshot(path=screenshot_path)
    print(f"Debug screenshot saved to: {screenshot_path}")


def print_exception(e: Exception) -> None:
    """Prints a formatted exception message to the console."""

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
