from playwright.sync_api import expect, Page
from datetime import datetime, timedelta
import time
from automation.shared.config import DEFAULT_TIMEOUT_MILLISECONDS
from automation.registration.config import REGISTRATION_START_BUFFER_SECONDS


def wait_until_time_slot_opens(posting_offset: int, start_date: str, start_time: str) -> bool:
    """Waits until just before the booking slot opens to start the registration process."""

    activity_datetime = datetime.strptime(f"{start_date} {start_time}:00", "%Y-%m-%d %H:%M:%S")
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


def format_date_for_program_instance_text(date_string: str) -> str:
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


def format_date_for_program_instance_role(date_string: str) -> str:
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


def format_date_for_program_timeslot(date_string: str, time_string: str) -> str:
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
