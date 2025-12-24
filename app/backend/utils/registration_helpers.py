from playwright.sync_api import expect, Page
from datetime import datetime, timedelta
import time
from utils.constants import (
    DEFAULT_TIMEOUT_MILLISECONDS,
    REGISTRATION_START_BUFFER_SECONDS,
)
from utils.date_helpers import (
    format_date_for_program_instance_role,
    format_date_for_program_instance_text,
    format_date_for_program_timeslot,
)


def wait_until_time_slot_opens(
    posting_offset: int, start_date: str, start_time: str
) -> bool:
    """Waits until just before the booking slot opens to start the registration process."""

    activity_datetime = datetime.strptime(
        f"{start_date} {start_time}:00", "%Y-%m-%d %H:%M:%S"
    )
    wakeup_datetime = (
        activity_datetime
        - timedelta(days=posting_offset)
        - timedelta(seconds=REGISTRATION_START_BUFFER_SECONDS)
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


def compete_for_registration(
    page: Page, start_date: str, start_time: str, time_limit: int = 60
) -> bool:
    """Continually attempts to register for the specified date and time slot
    until successful or time limit reached."""

    # Format date and time strings for initial program registration page
    programInstanceTextDate = format_date_for_program_instance_text(start_date)
    programInstanceRoleDate = format_date_for_program_instance_role(start_date)
    programTimeslotDateTime = format_date_for_program_timeslot(start_date, start_time)

    # Continually try to register until successful or time limit reached
    stopping_datetime = datetime.now() + timedelta(seconds=time_limit)
    won_registration = False
    page.set_default_timeout(1000)  # set shorter timeout for element searches
    while True:
        try:
            # Refresh the page
            page.reload()

            # Look for correct date and time selection to press
            expect(page.locator("#programInstances")).to_contain_text(
                programInstanceTextDate
            )
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
