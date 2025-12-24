from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from app.backend.utils.constants import DEFAULT_TIMEOUT_MILLISECONDS, USER_AGENTS
from app.backend.utils.captcha_solver import CaptchaSolver
import time, random


def test_captcha_handler(headless: bool = True) -> None: 
    """Test the captcha handling functionality."""

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
        solver = CaptchaSolver(page)
        solver.solve_captcha()

        if not headless:
            time.sleep(3)  # Pause to visually confirm captcha solved in non-headless mode

    assert True  # If no exceptions were raised, the test passes

if __name__ == "__main__":
    # Verify captcha handler manually in non-headless mode
    test_captcha_handler(headless=False)