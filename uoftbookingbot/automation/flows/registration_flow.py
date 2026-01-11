from datetime import datetime, timedelta
import time
from playwright.sync_api import sync_playwright, expect, Page
from playwright_stealth import Stealth
from uoftbookingbot.activity import Activity
from uoftbookingbot.automation.captcha_solver import CaptchaSolver
from uoftbookingbot.automation.flows.common import complete_utorid_login
from uoftbookingbot.database.db_controller import DBController
from uoftbookingbot.automation.logger import Logger
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
    activity: Activity, registration_start_buffer_seconds: int, logger: Logger
) -> bool:
    """Waits until just before the booking slot opens to start the registration process."""

    activity_datetime = datetime.strptime(
        f"{activity.start_date} {activity.start_time}:00", "%Y-%m-%d %H:%M:%S"
    )
    wakeup_datetime = (
        activity_datetime
        - timedelta(days=activity.posting_offset)
        - timedelta(seconds=registration_start_buffer_seconds)
    )
    diff_time = wakeup_datetime - datetime.now()
    sleep_seconds = max(0, diff_time.total_seconds())
    if sleep_seconds > 0:
        logger.log_info("Registration not open yet, waiting until it opens...")

        # Log every second
        while sleep_seconds > 0:
            # Format the time remaining (HH:MM:SS)
            td = timedelta(seconds=sleep_seconds)
            parts = []

            # Extract days, hours, minutes, seconds
            hours, remainder = divmod(td.seconds, 3600)
            minutes, seconds_only = divmod(remainder, 60)
            if td.days > 0:
                parts.append(f"{td.days} days")
            if hours > 0:
                parts.append(f"{hours} hours")
            if minutes > 0:
                parts.append(f"{minutes} minutes")
            parts.append(f"{seconds_only} seconds")

            wait_str = ", ".join(parts)
            logger.log_info(f"Waiting {wait_str} until registration opens... ")

            time.sleep(1)
            sleep_seconds -= 1

        logger.log_info("Wakeup time reached...")


def _compete_for_registration(page: Page, activity: Activity, time_limit: int) -> bool:
    """Continually attempts to register for the specified date and time slot
    until successful or time limit reached."""

    # Format date and time strings for initial program registration page
    programInstanceTextDate = _format_date_for_program_instance_text(activity.start_date)
    programInstanceRoleDate = _format_date_for_program_instance_role(activity.start_date)
    programTimeslotDateTime = _format_date_for_program_timeslot(
        activity.start_date, activity.start_time
    )

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


def _clear_cart(page: Page) -> None:
    """Clears the shopping cart if it contains any items."""
    page.goto("https://recreation.utoronto.ca/")
    # Check if cart is empty
    page.get_by_role("button", name="Shopping Cart Notfications Area").click()
    go_to_cart_button = page.get_by_role("button", name="Go to Cart Page").filter(visible=True)
    empty_cart_link = page.get_by_role("link", name="Your Cart is Empty!").filter(visible=True)
    expect(go_to_cart_button.or_(empty_cart_link)).to_be_visible()

    if empty_cart_link.is_visible():
        return

    # Cart isn't empty; go to cart page
    page.get_by_role("button", name="Go to Cart Page").click()

    # Wait for one or more remove buttons to appear, then remove all items one by one
    remove_button_locator = page.get_by_role("button", name="Remove")
    expect(remove_button_locator.first).to_be_visible()
    removable_items_count = remove_button_locator.count()
    while removable_items_count > 0:
        expect(remove_button_locator.first).to_be_visible()
        remove_button_locator.first.click()
        removable_items_count -= 1

    # Wait until cart is confirmed empty
    page.wait_for_url("https://recreation.utoronto.ca/")


def run_registration_flow(
    activity: Activity,
    db_controller: DBController,
    logger: Logger,
    time_limit: int = 60,
    user_agent: str | None = None,
    headless: bool = True,
    debug: bool = False,
) -> None:
    """Runs the main registration automation using Playwright.

    Args:
        activity: The activity to register for.
        db_controller: An instance of DBController to handle login credentials and bypass codes.
        logger: Instance of Logger to handle logging
        time_limit: The maximum number of seconds to run the bot past the start time without success.
        user_agent: Optional custom user agent string for the browser.
        headless: Whether to run the browser in headless mode.
        debug: Whether to save debug screenshots on failure.
    """

    logger.log_info("Starting registration flow...")

    with Stealth().use_sync(sync_playwright()) as playwright:
        # Launch browser
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT_MILLISECONDS)
        expect.set_options(timeout=DEFAULT_TIMEOUT_MILLISECONDS)

        try:
            page.goto("https://recreation.utoronto.ca/")

            # Acknowledge cookies if it appears
            page.add_locator_handler(
                page.get_by_role("button", name="Acknowledge Cookies"),
                lambda locator: locator.click(),
            )

            # Sign in with UTORID
            complete_utorid_login(
                db_controller=db_controller,
                page=page,
                recreation_login=True,
                logger=logger,
            )

            # Clear cart (if necessary) before starting registration
            _clear_cart(page)

            # Navigate to the program registration page
            page.goto(activity.get_registration_url())

            # Wait for bookings to open if necessary
            if activity.posting_offset is not None:
                _wait_until_time_slot_opens(
                    activity=activity,
                    registration_start_buffer_seconds=_REGISTRATION_START_BUFFER_SECONDS,
                    logger=logger,
                )

            logger.log_info(
                f"Registering for drop-in activity on {activity.start_date} at {activity.start_time}..."
            )

            # Compete for initial registration
            effective_time_limit = (
                time_limit + _REGISTRATION_START_BUFFER_SECONDS
                if activity.posting_offset is not None
                else time_limit
            )
            won_initial_registration = _compete_for_registration(
                page=page,
                activity=activity,
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
            registration_steps_locator = page.locator("#registrationStepList")
            expect(
                captcha_locator.filter(visible=True)
                .or_(family_member_section_locator)
                .filter(visible=True)
                .or_(registration_steps_locator)
                .filter(visible=True)
            ).to_be_visible()

            # Solve CAPTCHA if it appears
            if captcha_locator.is_visible():
                logger.log_info("CAPTCHA detected, starting to solve...")

                solver = CaptchaSolver(page, logger)
                solver.solve_captcha()
                page.locator("#btnReCaptchaConfirm").click()

                logger.log_info("CAPTCHA solved.")

            # CAPTCHA handled (if needed); proceed with registration flow depending on whether user has family members
            expect(family_member_section_locator.or_(registration_steps_locator)).to_be_visible()

            # Complete family member selection modal (if applicable)
            if family_member_section_locator.is_visible():
                family_member_section_locator.locator(
                    "[name='radioGroupFamilyMember'] + label"
                ).first.click()
                page.locator("#btnNext").click()

            # Check that we are in the registration steps/checkout flow
            # Note: Getting here means that the session slot has been reserved successfully
            # (but not yet registered)
            expect(registration_steps_locator).to_be_visible()
            logger.log_info("Successfully reserved a slot for the activity. Completing checkout...")

            # Complete registration steps until checkout
            on_checkout_page = False
            while not on_checkout_page:
                # Get the active checkout/registration step
                active_step_locator = registration_steps_locator.locator(
                    ".registrationStep.active .stepText"
                )
                active_step = active_step_locator.inner_text().strip().lower()

                # Complete waivers page (if applicable)
                if active_step == "waivers":
                    waivers_page_identifier = page.get_by_role(
                        "heading", name="Please review and accept"
                    )
                    expect(waivers_page_identifier).to_be_visible()
                    page.wait_for_load_state("networkidle")  # Ensure waivers are properly loaded
                    page.get_by_role("button", name="expand_more").click()
                    page.get_by_role("button", name="Accept").click()

                # Click Next or Proceed to Checkout button until we reach checkout
                next_button_locator = page.get_by_role("button", name="Next")
                checkout_button_locator = page.get_by_role("button", name="Proceed to Checkout")
                expect(next_button_locator.or_(checkout_button_locator)).to_be_visible()
                if next_button_locator.is_visible():
                    next_button_locator.click()
                    continue
                else:
                    checkout_button_locator.click()
                    on_checkout_page = True

            # Complete checkout/shopping cart page
            cart_page_identifier = page.locator("h1", has_text="Shopping Cart")
            expect(cart_page_identifier).to_be_visible()
            page.get_by_role("button", name="Checkout").click()
            page.locator("#btnCheckoutCart").click()

            # Confirm successful checkout on receipt page
            expect(page.get_by_role("heading", name="Payment was Successful")).to_be_visible()

            logger.log_info("Registration flow completed successfully.")
        except Exception as e:
            if debug:
                logger.screenshot(page)
            raise
        finally:
            context.close()
            browser.close()
