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


_BOT_START_BUFFER_SECONDS = 300  # bot starts 5 mins before booking time
_FIRST_VALID_CLEANUP_BUFFER_SECONDS = _BOT_START_BUFFER_SECONDS + 120  # 2 min after ideal bot start


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


def _get_scheduler_run_datetime(activity: Activity) -> datetime:
    """Return a datetime object for when the scheduler should run to start booking in the local
    timezone. Raises ValueError if the activity is in the past.

    If the registration period is open, the scheduler run time is set to the next minute from now.
    Otherwise, it's set to the registration open time minus a buffer.
    """

    if not _is_activity_in_future(activity):
        raise ValueError("Cannot schedule an activity in the past.")

    registration_open_dt_toronto = _get_registration_open_datetime(activity)
    now_dt_local = datetime.now().astimezone()
    now_dt_toronto = now_dt_local.astimezone(ZoneInfo("America/Toronto"))
    if registration_open_dt_toronto is None or registration_open_dt_toronto <= now_dt_toronto:
        return now_dt_local + timedelta(minutes=1)
    else:
        return (
            registration_open_dt_toronto - timedelta(seconds=_BOT_START_BUFFER_SECONDS)
        ).astimezone()


def _create_activity_from_program_args(program_args: list[str]) -> Activity:
    """Return an Activity instance from the list of program arguments. Raises ValueError if the args
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
        raise ValueError("Invalid program arguments for creating Activity.")

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
    """Base class for scheduling the booking bot.

    Scheduling an activity session means scheduling the booking bot to run at a specific time in the
    future to attempt to book the activity session on behalf of the user. Once scheduled, the
    booking bot will run automatically at the scheduled time without any further user intervention.

    Invariants:
    - An activity session can only be scheduled for booking once at any given time.
    - An activity session can only be scheduled for booking if its start time is in the future.
    - The scheduler attempts execution of the booking bot for a scheduled activity session exactly
      once at the scheduled time.
    - A scheduled activity session is no longer considered scheduled once the booking bot has
      executed the booking (or attempted to) for that activity session. If the scheduler fails to
      execute the booking bot at the scheduled time (e.g. the user's computer was off), the
      scheduled activity session is considered expired/invalid (i.e. is no longer scheduled) and
      must be rescheduled by the user if they still wish to book it.

    Other Assumptions/Notes:
    - Activity session start times are in the America/Toronto timezone.
    - All scheduled booking run times are in the user's local timezone.
    - The scheduler assumes that the user's system timezone does not change between the time of
      scheduling and the time of execution.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def schedule_activity(self, activity: Activity) -> None:
        """Schedule the booking bot to book the specified activity session. If the activity session
        is already scheduled for booking, overwrite the existing schedule. Scheduling an activity
        session for booking whose session start time is in the past raises a ValueError.

        Args:
            activity: The activity session to schedule.
        """
        ...

    @abstractmethod
    def unschedule_activity(self, activity: Activity) -> None:
        """Unschedule an activity session previously scheduled for booking. Unscheduling a
        non-scheduled activity session is a no-op.

        Args:
            activity: The activity session to unschedule.
        """
        ...

    @abstractmethod
    def get_scheduled_activities(self) -> list[Activity]:
        """Return a list of activity sessions scheduled for booking.

        Returns:
            list[Activity]: A list of scheduled activity sessions.
        """
        ...

    @abstractmethod
    def is_activity_scheduled(self, activity: Activity) -> bool:
        """Return True iff the activity session is scheduled for booking.

        Args:
            activity: The activity session to check.

        Returns:
            bool: True iff the activity session is scheduled for booking.
        """
        ...

    @abstractmethod
    def cleanup_expired_schedules(self) -> None:
        """Cleanup any expired/invalid scheduled activity sessions from the scheduler."""
        ...


class _LaunchdScheduler(Scheduler):
    """Scheduler implementation for macOS using launchd."""

    _JOB_PREFIX = "com.uoftbookingbot"
    _AGENT_DIR: str = os.path.expanduser("~/Library/LaunchAgents")

    def schedule_activity(self, activity: Activity) -> None:
        if self.is_activity_scheduled(activity):
            self.unschedule_activity(activity)

        booking_dt_local = _get_scheduler_run_datetime(activity)
        label = self._get_unique_launchd_label(activity)
        plist_path = self._get_plist_path_from_label(label)
        bot_exec_path, activity_args, project_root = _get_execution_values(activity)
        run_bot_args = [bot_exec_path] + activity_args

        plist_content = {
            "Label": label,
            "ProgramArguments": run_bot_args,
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
        now = datetime.now().astimezone()
        for plist_path in plist_paths:
            with open(plist_path, "rb") as f:
                plist_content = plistlib.load(f)

                # Recreate and validate the activity from program args
                program_args = plist_content.get("ProgramArguments", [])
                try:
                    candidate_activity = _create_activity_from_program_args(program_args)
                except ValueError:
                    continue

                # Ensure scheduled activity is valid and set to be booked in the future
                if self._is_schedule_expired(candidate_activity, plist_content, now, strict=True):
                    continue

                activities.append(candidate_activity)

        return activities

    def is_activity_scheduled(self, activity: Activity) -> bool:
        scheduled_activities = self.get_scheduled_activities()
        return activity in scheduled_activities

    def cleanup_expired_schedules(self) -> None:
        plist_paths = self._get_all_activity_plists()
        now = datetime.now().astimezone()
        for plist_path in plist_paths:
            with open(plist_path, "rb") as f:
                plist_content = plistlib.load(f)

                # Recreate and validate the activity from program args
                program_args = plist_content.get("ProgramArguments", [])
                try:
                    candidate_activity = _create_activity_from_program_args(program_args)
                except ValueError:
                    label = plist_content.get("Label")
                    self._remove_job_from_launchctl(plist_path, label)
                    continue

                # Ensure scheduled activity is valid and set to be booked in the future
                if self._is_schedule_expired(candidate_activity, plist_content, now, strict=False):
                    label = plist_content.get("Label")
                    self._remove_job_from_launchctl(plist_path, label)
                    continue

    def _get_unique_launchd_label(self, activity: Activity) -> str:
        """Return a unique label/job id for launchd to use when scheduling the activity."""

        task_id = f"{activity.id}--{activity.start_date}--{activity.start_time}".replace(":", "-")
        return f"{self._JOB_PREFIX}.{task_id}"

    def _get_plist_path_from_label(self, label: str) -> str:
        """Return the plist path for a given launchd job label."""

        return os.path.join(self._AGENT_DIR, f"{label}.plist")

    def _get_all_activity_plists(self) -> list[str]:
        """Return a list of all plists related to this application in the LaunchAgents directory."""

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

    def _is_schedule_expired(
        self, activity: Activity, plist_content: dict[str, Any], now: datetime, strict: bool
    ) -> bool:
        """Return True iff the schedule for the given activity is expired (or invalid) based on its
        plist content."""

        start_calendar_interval = plist_content.get("StartCalendarInterval", {})
        month = start_calendar_interval.get("Month")
        day = start_calendar_interval.get("Day")
        hour = start_calendar_interval.get("Hour")
        minute = start_calendar_interval.get("Minute")

        if month is None or day is None or hour is None or minute is None:
            return True

        activity_start_dt_local = _get_activity_start_datetime(activity).astimezone()
        scheduled_dt_local = datetime(
            year=activity_start_dt_local.year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
        ).astimezone()
        if scheduled_dt_local > activity_start_dt_local:
            scheduled_dt_local = scheduled_dt_local.replace(year=activity_start_dt_local.year - 1)

        if strict:
            return scheduled_dt_local < now
        return scheduled_dt_local + timedelta(seconds=_FIRST_VALID_CLEANUP_BUFFER_SECONDS) < now


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
        now = datetime.now().astimezone()
        for cron in all_crons:
            if not re.match(self.ACTIVITY_COMMAND_REGEX, cron.command):
                continue

            # Recreate and validate the activity from program args
            program_args = cron.command.split(" && ", 1)[-1].split()[1:]
            try:
                candidate_activity = _create_activity_from_program_args(program_args)
            except ValueError:
                continue

            # Ensure scheduled activity is valid and set to be booked in the future
            if self._is_schedule_expired(candidate_activity, cron, now, strict=True):
                continue

            activities.append(candidate_activity)

        return activities

    def is_activity_scheduled(self, activity: Activity) -> bool:
        activity_crons = self._get_all_crons_for_activity(activity)
        return len(activity_crons) > 0

    def cleanup_expired_schedules(self) -> None:
        all_crons = self.interface.get_all()
        now = datetime.now().astimezone()
        for cron in all_crons:
            if not re.match(self.ACTIVITY_COMMAND_REGEX, cron.command):
                continue

            # Recreate and validate the activity from program args
            program_args = cron.command.split(" && ", 1)[-1].split()[1:]
            try:
                candidate_activity = _create_activity_from_program_args(program_args)
            except ValueError:
                self.interface.delete(cron.id)
                continue

            # Ensure scheduled activity is valid and set to be booked in the future
            if self._is_schedule_expired(candidate_activity, cron, now, strict=False):
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

    def _is_schedule_expired(
        self, activity: Activity, cron: Cron, now: datetime, strict: bool
    ) -> bool:
        """Return True iff the schedule for the given activity is expired (or invalid) based on its
        cron content."""

        if not self.interface.is_valid_cron_format(cron.interval):
            return True

        minute, hour, day, month, weekday = cron.interval.split()
        if minute == "*" or hour == "*" or day == "*" or month == "*" or weekday != "*":
            return True

        try:
            month = int(month)
            day = int(day)
            hour = int(hour)
            minute = int(minute)
        except Exception:
            return True

        activity_start_dt_local = _get_activity_start_datetime(activity).astimezone()
        scheduled_dt_local = datetime(
            year=activity_start_dt_local.year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
        ).astimezone()
        if scheduled_dt_local > activity_start_dt_local:
            scheduled_dt_local = scheduled_dt_local.replace(year=activity_start_dt_local.year - 1)

        if strict:
            return scheduled_dt_local < now
        return scheduled_dt_local + timedelta(seconds=_FIRST_VALID_CLEANUP_BUFFER_SECONDS) < now


def get_scheduler() -> Scheduler:
    """Factory function to get the appropriate scheduler based on the OS."""

    os_name = platform.system()
    if os_name == "Darwin":
        return _LaunchdScheduler()
    elif os_name == "Windows" or os_name == "Linux":
        return _PPyCronScheduler()
    else:
        raise Exception(f"Your operating system ({os_name}) is not supported for scheduling.")
