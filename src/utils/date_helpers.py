from datetime import datetime


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
    """

    datetime_string = f"{date_string} {time_string}"
    input_format = "%Y-%m-%d %H:%M"
    standard_output_format = "%b %d, %Y %I:%M %p"
    datetime_object = datetime.strptime(datetime_string, input_format)
    formatted_date_temp = datetime_object.strftime(standard_output_format)
    parts = formatted_date_temp.split(", ")
    first_part_elements = parts[0].split(" ")
    day_no_leading_zero = str(int(first_part_elements[-1]))
    first_part_elements[-1] = day_no_leading_zero
    first_part_no_zero = " ".join(first_part_elements)

    return f"Select {first_part_no_zero}, {parts[1]}"
