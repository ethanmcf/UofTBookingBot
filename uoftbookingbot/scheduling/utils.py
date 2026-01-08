from pathlib import Path
import sys
from datetime import datetime, timedelta
from uoftbookingbot.activity import Activity
from uoftbookingbot.scheduling.constants import BOT_START_BUFFER_SECONDS
from uoftbookingbot.utils import is_running_as_bundle


def get_scheduler_run_datetime(activity: Activity) -> datetime:
    """Return a timezone aware datetime object for when the scheduler should run to start booking
    in the local timezone. Raises ValueError if the activity is in the past.

    If the registration period is open, the scheduler run time is set to the next minute from now.
    Otherwise, it's set to the registration open time minus a buffer.
    """

    # Validate that activity is in the future
    session_start_dt = activity.get_session_start_datetime()
    now_dt = datetime.now().astimezone()
    if session_start_dt <= now_dt:
        raise ValueError("Cannot schedule an activity that has already started.")

    # Determine scheduler run time
    registration_open_dt = activity.get_registration_open_datetime()
    if registration_open_dt is None or registration_open_dt <= now_dt:
        return now_dt + timedelta(minutes=1)
    return (registration_open_dt - timedelta(seconds=BOT_START_BUFFER_SECONDS)).astimezone()


def create_activity_from_program_args(program_args: list[str]) -> Activity:
    """Build and return an activity from the list of program arguments. Raises ValueError if the
    args don't correspond to a valid activity."""

    try:
        # Get positions of required args
        i_index = program_args.index("-i")
        d_index = program_args.index("-d")
        t_index = program_args.index("-t")
        o_index = program_args.index("-o") if "--no-wait" not in program_args else None

        # Extract values
        activity_id = program_args[i_index + 1]
        activity_date = program_args[d_index + 1]
        activity_time = program_args[t_index + 1]
        posting_offset = int(program_args[o_index + 1]) if o_index is not None else None
    except Exception:
        raise ValueError("Invalid program arguments for creating Activity.")

    return Activity(
        id=activity_id,
        start_date=activity_date,
        start_time=activity_time,
        posting_offset=posting_offset,
    )


def get_execution_values(activity: Activity) -> tuple[str, list[str], str]:
    """Return the Python executable path, bot args for the scheduled activity, and working directory
    (project root) for running the scheduled task.

    Args:
        activity: The activity to schedule.
    Returns:
        A tuple of (exec_path, activity_args, project_root)."""

    # Determine the execution path
    exec_path = sys.executable

    # Determine the bot args for the scheduled activity
    offset_args = (
        ["-o", str(activity.posting_offset)]
        if activity.posting_offset is not None
        else ["--no-wait"]
    )
    activity_args = [
        "-i",
        activity.id,
        "-d",
        activity.start_date,
        "-t",
        activity.start_time,
    ] + offset_args
    if not is_running_as_bundle():
        # in dev, run as: python -m uoftbookingbot
        activity_args = ["-m", "uoftbookingbot"] + activity_args

    # Determine the project root/working directory
    project_root = str(
        Path(sys.executable).parent
        if is_running_as_bundle()
        else Path(__file__).parent.parent.parent
    )

    return exec_path, activity_args, project_root
