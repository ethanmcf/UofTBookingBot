from abc import abstractmethod, ABCMeta
from datetime import datetime, timedelta
import os
from pathlib import Path
import platform
import plistlib
import subprocess
import sys
from typing import Optional
from zoneinfo import ZoneInfo

from uoftbookingbot.activity import Activity
from uoftbookingbot.utils import is_running_as_bundle


class Scheduler:
    """Base class for scheduling the booking bot."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def schedule_activity(self, activity: Activity) -> None:
        """Schedule the booking bot to book the specified activity. If the activity is already
        scheduled, overwrite the existing schedule. Scheduling an activity in the past raises
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
        """Clean up any artifacts related to previously scheduled activities that have already
        executed or are past their scheduled run time."""
        ...


_BOT_START_BUFFER_SECONDS = 300  # bot starts 5 minutes before booking time
_JOB_PREFIX = "com.uoftbookingbot"


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
            registration_open_dt_toronto - timedelta(seconds=_BOT_START_BUFFER_SECONDS).astimezone()
        )


def _get_unique_job_id(activity: Activity) -> str:
    """Return a unique label/job id for schedulers to use when scheduling the activity."""

    task_id = f"{activity.id}--{activity.start_date}--{activity.start_time}".replace(":", "-")
    return f"{_JOB_PREFIX}.{task_id}"


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


class _MacOSScheduler(Scheduler):
    """Scheduler implementation for macOS using launchd."""

    _AGENT_DIR: str = os.path.expanduser("~/Library/LaunchAgents")

    def schedule_activity(self, activity: Activity) -> None:
        if self.is_activity_scheduled(activity):
            self.unschedule_activity(activity)

        label = _get_unique_job_id(activity)
        plist_path = self._get_plist_path_from_label(label)

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

        # Determine the execution path
        exec_path = sys.executable
        if not is_running_as_bundle():
            # in dev, run as: python -m uoftbookingbot
            activity_args = ["-m", "uoftbookingbot"] + activity_args

        project_root = str(
            Path(sys.executable).parent if is_running_as_bundle() else Path(__file__).parent.parent
        )

        booking_dt_local = _get_scheduler_run_datetime(activity)
        if booking_dt_local is None:
            raise ValueError("Cannot schedule an activity in the past.")

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

        label = _get_unique_job_id(activity)
        plist_path = self._get_plist_path_from_label(label)
        self._remove_job_from_launchctl(plist_path, label)

    def get_scheduled_activities(self) -> list[Activity]:
        activities = []
        plist_paths = self._get_all_activity_plists()
        for plist_path in plist_paths:
            with open(plist_path, "rb") as f:
                plist_content = plistlib.load(f)

                # Recreate and validate the activity from ProgramArguments
                program_args = plist_content.get("ProgramArguments", [])
                candidate_activity = _create_activity_from_program_args(program_args)
                if candidate_activity is None or not _is_activity_in_future(candidate_activity):
                    continue

                # Check that the scheduled run time is still valid and in the future
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
                    continue
                possible_scheduler_run_datetime = _get_scheduler_run_datetime(candidate_activity)
                if possible_scheduler_run_datetime is None:
                    continue
                scheduled_dt_local = datetime(
                    year=possible_scheduler_run_datetime.year,
                    month=scheduled_month,
                    day=scheduled_day,
                    hour=scheduled_hour,
                    minute=scheduled_minute,
                ).astimezone()
                now_dt_local = datetime.now().astimezone()
                if scheduled_dt_local < now_dt_local:
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

                # Recreate and validate the activity from ProgramArguments
                program_args = plist_content.get("ProgramArguments", [])
                candidate_activity = _create_activity_from_program_args(program_args)
                if candidate_activity is None:
                    # Invalid activity, remove it
                    label = plist_content.get("Label")
                    self._remove_job_from_launchctl(plist_path, label)
                    continue

                # Check if the activity is expired
                if not _is_activity_in_future(candidate_activity):
                    label = plist_content.get("Label")
                    self._remove_job_from_launchctl(plist_path, label)

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
            if filename.startswith(_JOB_PREFIX) and filename.endswith(".plist"):
                plist_path = os.path.join(self._AGENT_DIR, filename)
                plist_paths.append(plist_path)

        return plist_paths

    def _remove_job_from_launchctl(self, plist_path: str, job_id: Optional[str]) -> None:
        """Remove a job from launchctl and delete its plist file."""

        if job_id:
            subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{job_id}"], check=False)
        if os.path.exists(plist_path):
            os.remove(plist_path)


def get_scheduler() -> Scheduler:
    """Factory function to get the appropriate scheduler based on the OS."""

    os_name = platform.system()
    if os_name == "Darwin":
        return _MacOSScheduler()
    elif os_name == "Windows":
        raise NotImplementedError("Windows Task Scheduler support coming soon.")
    else:
        raise NotImplementedError("Linux systemd support coming soon.")
