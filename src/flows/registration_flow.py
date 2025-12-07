import re
from typing import Optional
from playwright.sync_api import sync_playwright, expect
from playwright_stealth import Stealth
from utils.login_manager import LoginManager
from utils.login_manager import LoginManager
from utils.handlers import button_click_handler, captcha_handler
from utils.debug_helpers import save_debug_screenshot
from utils.constants import (
    DEBUG_FOLDER_PATH,
    DEFAULT_TIMEOUT_MILLISECONDS,
    REGISTRATION_START_BUFFER_SECONDS,
)
from utils.registration_helpers import (
    compete_for_registration,
    wait_until_time_slot_opens,
)


def run_registration_flow(
    program_url: str,
    date: str,
    time: str,
    login_manager: LoginManager,
    posting_offset: Optional[int] = None,
    time_limit: int = 60,
    user_agent: str | None = None,
    headless: bool = True,
    debug: bool = False,
) -> None:
    """Runs the main registration automation using Playwright.

    Args:
        program_url: The URL of the drop-in activity registration page.
        date: The date of the activity in YYYY-MM-DD format.
        time: The start time of the activity in HH:MM format.
        login_manager: An instance of LoginManager to handle login credentials and bypass codes.
        posting_offset: Optional number of days before the start time to begin registration.
        time_limit: The maximum number of seconds to run the bot past the start time without success.
        user_agent: Optional custom user agent string for the browser.
        headless: Whether to run the browser in headless mode.
        debug: Whether to save debug screenshots on failure.
    """

    print("Starting registration flow...")

    with Stealth().use_sync(sync_playwright()) as playwright:
        # Launch browser
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT_MILLISECONDS)

        try:
            # Navigate to the program registration page
            page.goto(program_url)

            # Acknowledge cookies if it appears
            page.add_locator_handler(
                page.get_by_role("button", name="Acknowledge Cookies"),
                button_click_handler,
            )

            # Handle CAPTCHA if it appears
            page.add_locator_handler(
                page.locator("#modal-captcha-confirm"), captcha_handler
            )

            # Sign in with UTORID
            utorid, password = login_manager.get_credentials()
            page.get_by_role("button", name="Sign In").click()
            page.get_by_role("button", name="school Log in with UTORID").click()
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
            page.get_by_role("button", name="Yes, this is my device").click()

            # Wait for bookings to open if necessary
            if posting_offset is not None:
                wait_until_time_slot_opens(
                    posting_offset=posting_offset, start_date=date, start_time=time
                )

            # Ensure we are on the initial registration page
            expect(page).to_have_url(
                re.compile(
                    r"^https:\/\/recreation\.utoronto\.ca\/program\/getprogramdetails"
                ),
            )

            print(f"Registering for drop-in activity on {date} at {time}...")

            # Compete for initial registration
            effective_time_limit = (
                time_limit + REGISTRATION_START_BUFFER_SECONDS
                if posting_offset is not None
                else time_limit
            )
            won_initial_registration = compete_for_registration(
                page=page,
                start_date=date,
                start_time=time,
                time_limit=effective_time_limit,
            )
            if not won_initial_registration:
                raise Exception(
                    "Failed to register within the time limit. The activity may be full."
                )

            # Complete payment options page (assumes no payment required)
            # Note: Getting here means registration was successful
            expect(page.locator("#groupRegistrationStepData")).to_contain_text(
                "How would you like to pay?"
            )
            print("Successfully registered for the activity. Completing checkout...")

            # Click Next or Proceed to Checkout button (depends on whether waivers are needed)
            next_button_locator = page.get_by_role("button", name="Next")
            checkout_button_locator = page.get_by_role(
                "button", name="shopping_cart Proceed to"
            )
            has_waivers = False
            expect(next_button_locator.or_(checkout_button_locator)).to_be_visible()
            if next_button_locator.is_visible():
                next_button_locator.click()
                has_waivers = True
            else:
                checkout_button_locator.click()

            # Complete waivers page (if applicable)
            if has_waivers:
                expect(page.locator("#groupRegistrationStepData")).to_contain_text(
                    "Please review and accept"
                )
                page.get_by_role("button", name="expand_more").click()
                page.get_by_role("button", name="Accept").click()
                page.get_by_role("button", name="shopping_cart Proceed to").click()

            # Complete checkout page
            expect(page.locator("h1")).to_contain_text("Shopping Cart")
            page.get_by_role("button", name="Checkout").click()
            page.locator("#btnCheckoutCart").click()

            # Confirm successful checkout on receipt page
            expect(
                page.get_by_role("heading", name="Payment was Successful")
            ).to_be_visible()

            print("Registration flow completed successfully.")
        except Exception as e:
            if debug:
                save_debug_screenshot(page, DEBUG_FOLDER_PATH)
            raise e from None
        finally:
            context.close()
            browser.close()
