from datetime import datetime, timedelta
import re
import time
from typing import Optional
from playwright.sync_api import sync_playwright, expect, Page
from playwright_stealth import Stealth
from uoftbookingbot.automation.captcha_solver import CaptchaSolver
from uoftbookingbot.automation.login_manager import LoginManager
from uoftbookingbot.automation.debugging import save_debug_screenshot
from uoftbookingbot.automation.constants import DEFAULT_TIMEOUT_MILLISECONDS


_REGISTRATION_START_BUFFER_SECONDS = 1


def _format_date_for_program_instance_text(date_string: str) -> str:
    """
    Converts a date string from "YYYY-MM-DD" format to "Weekday_Abbr Month_Abbr Day_of_Month"
    and removes any leading zero from the day number.

    This function uses a standard format string and then strips the leading zero manually
    to ensure cross-platform consistency.

    Example: "2025-12-07" -> "Sat Dec 7"
    """

    input_format = "%Y-%m-%d"
    standard_output_format = "%a %b %d"
    date_object = datetime.strptime(date_string, input_format)
    formatted_date = date_object.strftime(standard_output_format)
    parts = formatted_date.split(" ")
    day_no_leading_zero = str(int(parts[-1]))
    parts[-1] = day_no_leading_zero

    return " ".join(parts)


def _format_date_for_program_instance_role(date_string: str) -> str:
    """
    Converts a date string from "YYYY-MM-DD" format to "Weekday_Full, Month_Full Day_of_Month,".

    Example: "2025-12-07" -> "Saturday, December 7,"
    """

    input_format = "%Y-%m-%d"
    standard_output_format = "%A, %B %d"
    date_object = datetime.strptime(date_string, input_format)
    formatted_date_temp = date_object.strftime(standard_output_format)
    parts = formatted_date_temp.split(", ")
    month_and_day = parts[1].split(" ")
    month = month_and_day[0]
    day_padded = month_and_day[1]
    day_no_leading_zero = str(int(day_padded))

    return f"{parts[0]}, {month} {day_no_leading_zero},"


def _format_date_for_program_timeslot(date_string: str, time_string: str) -> str:
    """
    Combines date ("YYYY-MM-DD") and time ("HH:MM") strings and formats them
    into a display string starting with "Select ", like "Select Dec 7, 2025 12:10 PM".
    Ensures no leading zero on the day or the hour (12-hour clock).
    """

    datetime_string = f"{date_string} {time_string}"
    input_format = "%Y-%m-%d %H:%M"
    standard_output_format = "%b %d, %Y %I:%M %p"
    datetime_object = datetime.strptime(datetime_string, input_format)
    formatted_date_temp = datetime_object.strftime(standard_output_format)
    parts = formatted_date_temp.split(", ")
    date_parts = parts[0].split(" ")  # ['Dec', '07']
    day_padded = date_parts[-1]
    day_no_leading_zero = str(int(day_padded))
    date_parts[-1] = day_no_leading_zero
    date_part_no_zero = " ".join(date_parts)
    time_parts = parts[1].split(" ")  # ['2025', '07:10', 'AM']
    time_str = time_parts[1]  # "07:10"
    hour_minute = time_str.split(":")  # ['07', '10']
    hour_padded = hour_minute[0]
    minute = hour_minute[1]
    hour_no_leading_zero = str(int(hour_padded))
    time_part_no_zero = f"{hour_no_leading_zero}:{minute}"
    time_parts[1] = time_part_no_zero
    time_part_no_zero_full = " ".join(time_parts)

    return f"Select {date_part_no_zero}, {time_part_no_zero_full}"


def _wait_until_time_slot_opens(
    posting_offset: int, start_date: str, start_time: str, registration_start_buffer_seconds: int
) -> bool:
    """Waits until just before the booking slot opens to start the registration process."""

    activity_datetime = datetime.strptime(f"{start_date} {start_time}:00", "%Y-%m-%d %H:%M:%S")
    wakeup_datetime = (
        activity_datetime
        - timedelta(days=posting_offset)
        - timedelta(seconds=registration_start_buffer_seconds)
    )
    diff_time = wakeup_datetime - datetime.now()
    sleep_seconds = max(0, diff_time.total_seconds())

    print(f"Waiting for {sleep_seconds} second(s)", end="")
    if sleep_seconds > 0:
        print(
            f" until {wakeup_datetime.strftime('%A, %B %d, %Y at %-I:%M:%S %p')}",
            end="",
        )
    print("...")

    time.sleep(sleep_seconds)


def _compete_for_registration(
    page: Page, start_date: str, start_time: str, time_limit: int = 60
) -> bool:
    """Continually attempts to register for the specified date and time slot
    until successful or time limit reached."""

    # Format date and time strings for initial program registration page
    programInstanceTextDate = _format_date_for_program_instance_text(start_date)
    programInstanceRoleDate = _format_date_for_program_instance_role(start_date)
    programTimeslotDateTime = _format_date_for_program_timeslot(start_date, start_time)

    # Continually try to register until successful or time limit reached
    stopping_datetime = datetime.now() + timedelta(seconds=time_limit)
    won_registration = False
    page.set_default_timeout(1000)  # set shorter timeout for element searches
    while True:
        try:
            # Refresh the page
            page.reload()

            # Look for correct date and time selection to press
            expect(page.locator("#programInstances")).to_contain_text(programInstanceTextDate)
            page.get_by_role("button", name=programInstanceRoleDate).click()

            # Look for the correct time slot to press
            page.get_by_role("button", name=programTimeslotDateTime).click()

            # Click the register button to attempt registration
            page.get_by_role("button", name="Register").click()

            won_registration = True
            break
        except Exception as e:
            # No element found this iteration -> throttle refresh rate slightly (~100ms)
            time.sleep(0.1)

            # Stop checking once we reach our maximum time limit
            if datetime.now() >= stopping_datetime:
                break

    page.set_default_timeout(DEFAULT_TIMEOUT_MILLISECONDS)  # reset to default timeout

    return won_registration


def run_registration_flow(
    program_url: str,
    date: str,
    time: str,
    login_manager: LoginManager,
    screenshots_path: str,
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
        screenshots_path: Path to save debug screenshots.
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
                lambda locator: locator.click(),
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
                _wait_until_time_slot_opens(
                    posting_offset=posting_offset,
                    start_date=date,
                    start_time=time,
                    registration_start_buffer_seconds=_REGISTRATION_START_BUFFER_SECONDS,
                )

            # Ensure we are on the initial registration page
            expect(page).to_have_url(
                re.compile(r"^https:\/\/recreation\.utoronto\.ca\/program\/getprogramdetails"),
            )

            print(f"Registering for drop-in activity on {date} at {time}...")

            # Compete for initial registration
            effective_time_limit = (
                time_limit + _REGISTRATION_START_BUFFER_SECONDS
                if posting_offset is not None
                else time_limit
            )
            won_initial_registration = _compete_for_registration(
                page=page,
                start_date=date,
                start_time=time,
                time_limit=effective_time_limit,
            )
            if not won_initial_registration:
                raise Exception(
                    "Failed to register within the time limit. The activity may be full."
                )

            # In this order, clicking the register button should lead to either the:
            # - CAPTCHA confirmation modal (captcha appeared)
            # - Family member selection modal (no captcha appeared; user has family members)
            # - Payment page (no captcha appeared; user has no family members)
            captcha_locator = page.locator("#modal-captcha-confirm")
            family_member_section_locator = page.locator("#family-member-section")
            payment_page_locator = page.locator(
                "#groupRegistrationStepData", has_text="How would you like to pay?"
            )
            expect(
                captcha_locator.filter(visible=True)
                .or_(family_member_section_locator)
                .filter(visible=True)
                .or_(payment_page_locator)
                .filter(visible=True)
            ).to_be_visible()

            # Solve CAPTCHA if it appears
            if captcha_locator.is_visible():
                print("CAPTCHA detected, starting to solve...")

                solver = CaptchaSolver(page)
                solver.solve_captcha()
                page.locator("#btnReCaptchaConfirm").click()

                print("CAPTCHA solved.")

            # CAPTCHA handled (if needed); proceed with registration flow depending on whether user has family members
            expect(family_member_section_locator.or_(payment_page_locator)).to_be_visible()

            # Complete family member selection modal (if applicable)
            if family_member_section_locator.is_visible():
                family_member_section_locator.locator(
                    "[name='radioGroupFamilyMember'] + label"
                ).first.click()
                page.locator("#btnNext").click()

            # Complete payment options page (assumes no payment required)
            # Note: Getting here means registration was successful
            expect(payment_page_locator).to_be_visible()
            print("Successfully registered for the activity. Completing checkout...")

            # Click Next or Proceed to Checkout button (depends on whether waivers are needed)
            next_button_locator = page.get_by_role("button", name="Next")
            checkout_button_locator = page.get_by_role("button", name="shopping_cart Proceed to")
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
            expect(page.get_by_role("heading", name="Payment was Successful")).to_be_visible()

            print("Registration flow completed successfully.")
        except Exception as e:
            if debug:
                save_debug_screenshot(page, screenshots_path)
            raise e from None
        finally:
            context.close()
            browser.close()
