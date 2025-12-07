import os
import textwrap
from playwright.sync_api import Page
from datetime import datetime


def save_debug_screenshot(page: Page, folder_path: str) -> None:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(folder_path, f"error_screenshot_{timestamp}.png")
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
