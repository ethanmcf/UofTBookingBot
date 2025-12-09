from playwright.sync_api import sync_playwright, expect
from playwright_stealth import Stealth
from src.utils.constants import DEFAULT_TIMEOUT_MILLISECONDS, USER_AGENTS
from src.utils.captcha_solver import CaptchaSolver
import time, random


def test_captcha_handler(): 

    captcha_url = "https://www.google.com/recaptcha/api2/demo"


    with Stealth().use_sync(sync_playwright()) as playwright:
        # Launch browser
        browser = playwright.chromium.launch(headless=False, slow_mo=500)
        user_agent = random.choice(USER_AGENTS)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT_MILLISECONDS)

        try:
            # Navigate to the UTORMFA bypass codes page
            page.goto(captcha_url)
            solver = CaptchaSolver(page)
            try: 
                solver.solve_captcha()
                time.sleep(5)
            except Exception as e:
                print(e)

        except:
           print()

if __name__ == "__main__":
    test_captcha_handler()