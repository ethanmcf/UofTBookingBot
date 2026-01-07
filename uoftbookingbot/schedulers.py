from abc import abstractmethod, ABCMeta
from datetime import datetime, timedelta
import os
from pathlib import Path
import platform
import plistlib
import subprocess
import sys
from typing import Any, Optional
from zoneinfo import ZoneInfo
from ppycron.src import UnixInterface, WindowsInterface, Cron
import re

from uoftbookingbot.activity import Activity
from uoftbookingbot.utils import is_running_as_bundle


_BOT_START_BUFFER_SECONDS = 300  # bot starts 5 minutes before booking time
_FIRST_VALID_CLEANUP_BUFFER_SECONDS = (
    600  # first valid cleanup time is 10 minutes after booking time
)


def _get_activity_start_datetime(activity: Activity) -> datetime:
    """Return a timezone aware datetime object for the activity's start date and time."""

    return datetime.strptime(
        f"{activity.start_date} {activity.start_time}", "%Y-%m-%d %H:%M"
    ).replace(tzinfo=ZoneInfo("America/Toronto"))


def _is_activity_in_future(activity: Activity) -> bool:
    """Returns True iff the activity's start datetime is in the future."""

    activity_dt_toronto = _get_activity_start_datetime(activity)
    now_dt_toronto = datetime.now().astimezone(ZoneInfo("America/Toronto"))
    return activity_dt_toronto > now_dt_toronto


def _get_registration_open_datetime(activity: Activity) -> Optional[datetime]:
    """Return a timezone aware datetime object for when the activity's registration opens."""

    return (
        _get_activity_start_datetime(activity) - timedelta(days=activity.posting_offset)
        if activity.posting_offset is not None
        else None
    )


def _get_scheduler_run_datetime(activity: Activity) -> Optional[datetime]:
    """Return a datetime object for when the scheduler should run to start booking in the local
    timezone or None if the activity cannot be scheduled.

    If the registration period is open, the scheduler run time is set to the next minute from now.
    Otherwise, it's set to the registration open time minus a buffer.
    """

    if not _is_activity_in_future(activity):
        return None

    registration_open_dt_toronto = _get_registration_open_datetime(activity)
    now_dt_local = datetime.now().astimezone()
    now_dt_toronto = now_dt_local.astimezone(ZoneInfo("America/Toronto"))
    if registration_open_dt_toronto is None or registration_open_dt_toronto <= now_dt_toronto:
        return now_dt_local + timedelta(minutes=1)
    else:
        return (
            registration_open_dt_toronto - timedelta(seconds=_BOT_START_BUFFER_SECONDS)
        ).astimezone()


def _create_activity_from_program_args(program_args: list[str]) -> Optional[Activity]:
    """Return an Activity instance from the list of program arguments or None if the args
    don't correspond to a valid Activity."""

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
        return None

    return Activity(
        id=activity_id,
        start_date=activity_date,
        start_time=activity_time,
        posting_offset=posting_offset,
    )


def _get_execution_values(activity: Activity) -> tuple[str, list[str], str]:
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
        Path(sys.executable).parent if is_running_as_bundle() else Path(__file__).parent.parent
    )

    return exec_path, activity_args, project_root


class Scheduler:
    """Base class for scheduling the booking bot."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def schedule_activity(self, activity: Activity) -> None:
        """Schedule the booking bot to book the specified activity. If the activity is already
        scheduled, overwrite the existing schedule. Scheduling an activity in the past raises a
        ValueError.

        Assumes that the user's system timezone doesn't change between the
        time of scheduling and the time of execution.

        Args:
            activity: The activity to schedule.
        """
        ...

    @abstractmethod
    def unschedule_activity(self, activity: Activity) -> None:
        """Unschedule an activity previously scheduled for booking. Unscheduling a non-scheduled
        activity is a no-op.

        Args:
            activity: The activity to unschedule.
        """
        ...

    @abstractmethod
    def get_scheduled_activities(self) -> list[Activity]:
        """Return a list of activities scheduled for booking that are pending execution.

        Returns:
            A list of Activity instances representing the scheduled activities.
        """
        ...

    @abstractmethod
    def is_activity_scheduled(self, activity: Activity) -> bool:
        """Return True iff the activity is already scheduled for booking and is pending
        execution."""
        ...

    @abstractmethod
    def cleanup_expired_schedules(self) -> None:
        """Clean up any artifacts related to previously scheduled activities satisfying any of the following conditions:
        - The activity session has already started (or completed)
        - The scheduled activity session has passed its scheduled booking run time

        Invalid or corrupted scheduled activities should also be cleaned up."""
        ...


class _LaunchdScheduler(Scheduler):
    """Scheduler implementation for macOS using launchd."""

    _JOB_PREFIX = "com.uoftbookingbot"
    _AGENT_DIR: str = os.path.expanduser("~/Library/LaunchAgents")

    def schedule_activity(self, activity: Activity) -> None:
        if self.is_activity_scheduled(activity):
            self.unschedule_activity(activity)

        booking_dt_local = _get_scheduler_run_datetime(activity)
        if booking_dt_local is None:
            raise ValueError("Cannot schedule an activity in the past.")

        label = self._get_unique_launchd_label(activity)
        plist_path = self._get_plist_path_from_label(label)
        exec_path, activity_args, project_root = _get_execution_values(activity)

        plist_content = {
            "Label": label,
            "ProgramArguments": [exec_path] + activity_args,
            "WorkingDirectory": project_root,
            "EnvironmentVariables": {
                "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/homebrew/bin"
            },
            "StartCalendarInterval": {
                "Month": booking_dt_local.month,
                "Day": booking_dt_local.day,
                "Hour": booking_dt_local.hour,
                "Minute": booking_dt_local.minute,
            },
            "RunAtLoad": False,
        }

        with open(plist_path, "wb") as f:
            plistlib.dump(plist_content, f)

        subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", plist_path], check=False)
        subprocess.run(["launchctl", "enable", f"gui/{os.getuid()}/{label}"], check=False)

    def unschedule_activity(self, activity: Activity) -> None:
        if not self.is_activity_scheduled(activity):
            return

        label = self._get_unique_launchd_label(activity)
        plist_path = self._get_plist_path_from_label(label)
        self._remove_job_from_launchctl(plist_path, label)

    def get_scheduled_activities(self) -> list[Activity]:
        activities = []
        plist_paths = self._get_all_activity_plists()
        for plist_path in plist_paths:
            with open(plist_path, "rb") as f:
                plist_content = plistlib.load(f)

                program_args = plist_content.get("ProgramArguments", [])
                candidate_activity = _create_activity_from_program_args(program_args)
                if (
                    candidate_activity is None
                    or not _is_activity_in_future(candidate_activity)
                    or self._is_activity_schedule_expired(candidate_activity, plist_content)
                ):
                    continue

                activities.append(candidate_activity)

        return activities

    def is_activity_scheduled(self, activity: Activity) -> bool:
        scheduled_activities = self.get_scheduled_activities()
        return activity in scheduled_activities

    def cleanup_expired_schedules(self) -> None:
        plist_paths = self._get_all_activity_plists()
        for plist_path in plist_paths:
            with open(plist_path, "rb") as f:
                plist_content = plistlib.load(f)

                program_args = plist_content.get("ProgramArguments", [])
                candidate_activity = _create_activity_from_program_args(program_args)
                if (
                    candidate_activity is None
                    or not _is_activity_in_future(candidate_activity)
                    or self._is_activity_schedule_expired(candidate_activity, plist_content)
                ):
                    label = plist_content.get("Label")
                    self._remove_job_from_launchctl(plist_path, label)
                    continue

    def _is_activity_schedule_expired(
        self, activity: Activity, plist_content: dict[str, Any]
    ) -> bool:
        """Return True iff the schedule for the given activity is expired (or invalid) based on its
        plist content.

        Assumes the activity is valid and in the future."""

        start_interval = plist_content.get("StartCalendarInterval", {})
        scheduled_month = start_interval.get("Month")
        scheduled_day = start_interval.get("Day")
        scheduled_hour = start_interval.get("Hour")
        scheduled_minute = start_interval.get("Minute")
        if (
            scheduled_month is None
            or scheduled_day is None
            or scheduled_hour is None
            or scheduled_minute is None
        ):
            return True

        latest_possible_scheduler_run_datetime = _get_scheduler_run_datetime(activity)
        if latest_possible_scheduler_run_datetime is None:
            return True

        scheduled_dt_local = datetime(
            year=latest_possible_scheduler_run_datetime.year,
            month=scheduled_month,
            day=scheduled_day,
            hour=scheduled_hour,
            minute=scheduled_minute,
        ).astimezone()
        first_valid_cleanup_dt_local = scheduled_dt_local + timedelta(
            seconds=_FIRST_VALID_CLEANUP_BUFFER_SECONDS
        )
        now_dt_local = datetime.now().astimezone()

        return first_valid_cleanup_dt_local < now_dt_local

    def _get_unique_launchd_label(self, activity: Activity) -> str:
        """Return a unique label/job id for launchd to use when scheduling the activity."""

        task_id = f"{activity.id}--{activity.start_date}--{activity.start_time}".replace(":", "-")
        return f"{self._JOB_PREFIX}.{task_id}"

    def _get_plist_path_from_label(self, label: str) -> str:
        """Return the plist path for a given launchd job label."""

        return os.path.join(self._AGENT_DIR, f"{label}.plist")

    def _get_all_activity_plists(self) -> list[str]:
        """Return a list of all plists for scheduled activities, including those which are expired
        or invalid."""

        plist_paths = []
        if not os.path.exists(self._AGENT_DIR):
            return plist_paths

        for filename in os.listdir(self._AGENT_DIR):
            if filename.startswith(self._JOB_PREFIX) and filename.endswith(".plist"):
                plist_path = os.path.join(self._AGENT_DIR, filename)
                plist_paths.append(plist_path)

        return plist_paths

    def _remove_job_from_launchctl(self, plist_path: str, job_id: Optional[str]) -> None:
        """Remove a job from launchctl and delete its plist file."""

        if job_id:
            subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{job_id}"], check=False)
        if os.path.exists(plist_path):
            os.remove(plist_path)


class _PPyCronScheduler(Scheduler):

    ACTIVITY_COMMAND_REGEX = r"^(cd .+ && )?(.+ )?-i .+ -d .+ -t .+"

    interface: WindowsInterface | UnixInterface

    def __init__(self) -> None:
        self.interface = WindowsInterface() if platform.system() == "Windows" else UnixInterface()

    def schedule_activity(self, activity: Activity) -> None:
        if self.is_activity_scheduled(activity):
            self.unschedule_activity(activity)

        command_str = self._get_cron_command_for_activity(activity)
        interval_str = self._get_cron_interval_for_activity(activity)
        self.interface.add(command=command_str, interval=interval_str)

    def unschedule_activity(self, activity: Activity) -> None:
        if not self.is_activity_scheduled(activity):
            return

        activity_crons = self._get_all_crons_for_activity(activity)
        for cron in activity_crons:
            self.interface.delete(cron.id)

    def get_scheduled_activities(self) -> list[Activity]:
        activities = []
        all_crons = self.interface.get_all()
        for cron in all_crons:
            if not re.match(self.ACTIVITY_COMMAND_REGEX, cron.command):
                continue

            # Recreate and validate the activity from program args
            program_args = cron.command.split(" && ", 1)[-1].split()[1:]
            candidate_activity = _create_activity_from_program_args(program_args)
            if (
                candidate_activity is None
                or not _is_activity_in_future(candidate_activity)
                or self._is_future_activity_schedule_expired(candidate_activity, cron)
            ):
                continue

            activities.append(candidate_activity)

        return activities

    def is_activity_scheduled(self, activity: Activity) -> bool:
        activity_crons = self._get_all_crons_for_activity(activity)
        return len(activity_crons) > 0

    def cleanup_expired_schedules(self) -> None:
        all_crons = self.interface.get_all()
        for cron in all_crons:
            if not re.match(self.ACTIVITY_COMMAND_REGEX, cron.command):
                continue

            program_args = cron.command.split(" && ", 1)[-1].split()[1:]
            candidate_activity = _create_activity_from_program_args(program_args)
            if (
                candidate_activity is None
                or not _is_activity_in_future(candidate_activity)
                or self._is_future_activity_schedule_expired(candidate_activity, cron)
            ):
                self.interface.delete(cron.id)
                continue

    def _get_cron_command_for_activity(self, activity: Activity) -> str:
        """Return the command string to pass to ppycron's add command for the given activity."""

        exec_path, activity_args, project_root = _get_execution_values(activity)
        return f"cd {project_root} && {exec_path} {' '.join(activity_args)}"

    def _get_cron_command_with_no_offset_args(self, command: str) -> str:
        """Return the command string with any offset args (-o or --no-wait) removed."""

        return re.sub(r" -o \d+| --no-wait", "", command)

    def _get_cron_interval_for_activity(self, activity: Activity) -> str:
        """Return the cron interval string for the given activity. Raise ValueError if the activity
        is in the past."""

        booking_dt_local = _get_scheduler_run_datetime(activity)
        if booking_dt_local is None:
            raise ValueError("Cannot schedule an activity in the past.")
        return f"{booking_dt_local.minute} {booking_dt_local.hour} {booking_dt_local.day} {booking_dt_local.month} *"

    def _get_all_crons_for_activity(self, activity: Activity) -> list[Cron]:
        """Return all ppycron Cron objects corresponding to the given activity."""

        command_str = self._get_cron_command_for_activity(activity)
        command_str_with_no_offset_args = self._get_cron_command_with_no_offset_args(command_str)
        return [
            cron
            for cron in self.interface.get_all()
            if cron.command.startswith(command_str_with_no_offset_args)
        ]

    def _is_future_activity_schedule_expired(self, activity: Activity, cron: Cron) -> bool:
        """Return True iff the schedule for the given activity is expired (or invalid) based on its
        cron content.

        Assumes the activity is valid and in the future."""

        if not self.interface.is_valid_cron_format(cron.interval):
            return True

        minute, hour, day, month, weekday = cron.interval.split()
        if minute == "*" or hour == "*" or day == "*" or month == "*" or weekday != "*":
            return True

        try:
            scheduled_month = int(month)
            scheduled_day = int(day)
            scheduled_hour = int(hour)
            scheduled_minute = int(minute)
        except Exception:
            return True

        latest_possible_scheduler_run_datetime = _get_scheduler_run_datetime(activity)
        if latest_possible_scheduler_run_datetime is None:
            return True

        scheduled_dt_local = datetime(
            year=latest_possible_scheduler_run_datetime.year,
            month=scheduled_month,
            day=scheduled_day,
            hour=scheduled_hour,
            minute=scheduled_minute,
        ).astimezone()
        first_valid_cleanup_dt_local = scheduled_dt_local + timedelta(
            seconds=_FIRST_VALID_CLEANUP_BUFFER_SECONDS
        )
        now_dt_local = datetime.now().astimezone()

        return first_valid_cleanup_dt_local < now_dt_local


def get_scheduler() -> Scheduler:
    """Factory function to get the appropriate scheduler based on the OS."""

    os_name = platform.system()
    if os_name == "Darwin":
        return _LaunchdScheduler()
    elif os_name == "Windows" or os_name == "Linux":
        return _PPyCronScheduler()
    else:
        raise Exception(f"Your operating system ({os_name}) is not supported for scheduling.")
