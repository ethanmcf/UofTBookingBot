import re
from typing import Optional
from playwright.sync_api import sync_playwright, expect
from playwright_stealth import Stealth
from automation.shared.login_manager import LoginManager
from automation.shared.config import (
    DEBUG_FOLDER_PATH,
    DEFAULT_TIMEOUT_MILLISECONDS,
)
from automation.shared.debug_helpers import save_debug_screenshot


def run_bypass_codes_retrieval_flow(
    login_manager: LoginManager,
    user_agent: Optional[str] = None,
    headless: bool = True,
    debug: bool = False,
) -> None:
    """Runs an automation to retrieve bypass codes using Playwright.

    Args:
        login_manager: An instance of LoginManager to handle login credentials and bypass codes.
        user_agent: Optional custom user agent string for the browser.
        headless: Whether to run the browser in headless mode.
        debug: Whether to save debug screenshots on failure.
    """

    print("Starting bypass codes retrieval flow...")

    with Stealth().use_sync(sync_playwright()) as playwright:
        # Launch browser
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT_MILLISECONDS)

        try:
            # Navigate to the UTORMFA bypass codes page
            page.goto("https://bypass.utormfa.utoronto.ca/index.php")

            # Sign in with UTORID
            utorid, password = login_manager.get_credentials()
            page.get_by_role("textbox", name="UTORid / JOINid").click()
            page.get_by_role("textbox", name="UTORid / JOINid").fill(utorid)
            page.locator("#password").click()
            page.locator("#password").fill(password)
            page.get_by_role("button", name="log in").click()

            # Complete multi-factor authentication (MFA)
            bypass_code = login_manager.get_code()
            page.get_by_role("link", name="Other options").click()
            page.get_by_role("link", name="Bypass code Enter a code from").click()
            page.get_by_role("textbox", name="Bypass code").click()
            page.get_by_role("textbox", name="Bypass code").fill(bypass_code)
            page.get_by_test_id("verify-button").click()

            # Generate new bypass codes
            page.get_by_role("button", name="Generate Bypass Codes").click()
            expect(page.locator("h2")).to_contain_text("UTORMFA Bypass Codes")

            # Extract and save bypass codes
            content = page.locator("main > .site-container").text_content()
            codes = re.findall(r"\d{9}", content)
            if not codes:
                raise Exception("No codes found during bypass code extraction.")
            login_manager.save_codes(codes)

            print("Bypass codes retrieval flow completed successfully.")
        except Exception as e:
            if debug:
                save_debug_screenshot(page, DEBUG_FOLDER_PATH)
            raise e from None
        finally:
            context.close()
            browser.close()
