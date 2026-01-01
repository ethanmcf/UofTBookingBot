import time, random
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from uoftbookingbot.automation.captcha_solver import CaptchaSolver
from uoftbookingbot.automation.constants import (
    DEFAULT_TIMEOUT_MILLISECONDS,
    USER_AGENTS,
)
from uoftbookingbot.automation.logger import Logger


def test_captcha_solver(headless: bool = True) -> None:
    """Test the captcha handling functionality."""
    folder_dir = "./tests/logs"
    screenshot_dir = "./tests/screenshots"
    logger = Logger(folder_dir, screenshot_dir, name="TestLogger")
    captcha_url = "https://www.google.com/recaptcha/api2/demo"

    with Stealth().use_sync(sync_playwright()) as playwright:
        # Launch browser and navigate to captcha page
        browser = playwright.chromium.launch(headless=headless)
        user_agent = random.choice(USER_AGENTS)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT_MILLISECONDS)
        page.goto(captcha_url)

        # Solve captcha
        solver = CaptchaSolver(page, logger)
        solver.solve_captcha()

        if not headless:
            # Pause to visually confirm captcha solved in non-headless mode
            time.sleep(3)

    assert True  # If no exceptions were raised, the test passes


if __name__ == "__main__":
    # Verify captcha solver manually in non-headless mode
    test_captcha_solver(headless=False)
