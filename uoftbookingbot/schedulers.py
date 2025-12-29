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

from uoftbookingbot.utils import is_running_as_bundle


_BOT_START_BUFFER_SECONDS = 300  # bot starts 5 minutes before booking time


class Activity:
    """Represents a scheduled activity for the booking bot."""

    id: str
    start_date: str
    start_time: str
    posting_offset: Optional[int]

    def __init__(self, id: str, start_date: str, start_time: str, posting_offset: Optional[int] = None) -> None:
        self.id = id
        self.start_date = start_date
        self.start_time = start_time
        self.posting_offset = posting_offset

        if posting_offset is not None and posting_offset < 0:
            raise ValueError("Posting offset cannot be negative.")

    def __str__(self):
        return f"Activity(id={self.id}, date={self.start_date}, time={self.start_time}, offset={self.posting_offset})"
    
    def __eq__(self, other):
        if not isinstance(other, Activity):
            return False
        return (
            self.id == other.id and
            self.start_date == other.start_date and
            self.start_time == other.start_time and
            self.posting_offset == other.posting_offset
        )


class Scheduler:
    """Base class for scheduling the booking bot."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, error_log_path: str, output_log_path: str) -> None: 
        """Initializes the scheduler with paths for error and output logs.
        
        Args:
            error_log_path: Path to the error log file.
            output_log_path: Path to the output log file.
        """
        ...

    @abstractmethod
    def schedule_bot(
        self,
        activity: Activity
    ) -> None: 
        """Schedules the booking bot for a specified activity.
        
        Args:
            activity: The activity to schedule.
        """
        ...

    @abstractmethod
    def unschedule_bot(self, activity: Activity) -> None: 
        """Unschedules a previously scheduled activity.

        Args:
            activity: The activity to unschedule.
        """
        ...

    @abstractmethod
    def get_scheduled_activities(self) -> list[Activity]:
        """Returns a list of scheduled activities.
        
        Returns:
            A list of Activity instances representing the scheduled activities.
        """
        ...

    @abstractmethod
    def is_activity_scheduled(
        self,
        activity: Activity
    ) -> bool:
        """Checks if a specific activity is already scheduled."""
        ...

class _MacOSScheduler(Scheduler):
    """Scheduler implementation for macOS using launchd."""

    def __init__(self, error_log_path: str, output_log_path: str) -> None:
        self.error_log_path = error_log_path
        self.output_log_path = output_log_path
        self.agent_dir = os.path.expanduser("~/Library/LaunchAgents")
        self.label_prefix = "com.uoftbookingbot"

    def schedule_bot(
        self,
        activity: Activity,
    ) -> None:
        label = self._get_task_label(activity)
        plist_path = os.path.join(self.agent_dir, f"{label}.plist")

        offset_args = ["-o", str(activity.posting_offset)] if activity.posting_offset is not None else ["--no-wait"]
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

        booking_dt_toronto = self._validate_and_get_booking_datetime(activity)

        plist_content = {
            "Label": label,
            "ProgramArguments": [exec_path] + activity_args,
            "WorkingDirectory": project_root,
            "EnvironmentVariables": {
                "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/homebrew/bin"
            },
            "StartCalendarInterval": {
                "Month": booking_dt_toronto.month,
                "Day": booking_dt_toronto.day,
                "Hour": booking_dt_toronto.hour,
                "Minute": booking_dt_toronto.minute,
            },
            "StandardOutPath": self.output_log_path,
            "StandardErrorPath": self.error_log_path,
            "RunAtLoad": False,
        }

        with open(plist_path, "wb") as f:
            plistlib.dump(plist_content, f)

        subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", plist_path], check=False)
        subprocess.run(["launchctl", "enable", f"gui/{os.getuid()}/{label}"], check=False)

    def unschedule_bot(
        self,
        activity: Activity,
    ) -> None:
        label = self._get_task_label(activity)
        plist_path = os.path.join(self.agent_dir, f"{label}.plist")

        subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{label}"], check=False)
        if os.path.exists(plist_path):
            os.remove(plist_path)

    def get_scheduled_activities(self) -> list[Activity]:
        activities = []
        for filename in os.listdir(self.agent_dir):
            if not filename.startswith(self.label_prefix) or not filename.endswith(".plist"):
                continue

            label = filename.removeprefix(self.label_prefix + ".").removesuffix(".plist")
            parts = label.split("--")
            if len(parts) != 4:
                continue

            activity_id, activity_date, activity_time, posting_offset_str = parts
            activity_time = activity_time.replace("-", ":")
            posting_offset = None if posting_offset_str == "none" else int(posting_offset_str)
            activities.append(Activity(id=activity_id, start_date=activity_date, start_time=activity_time, posting_offset=posting_offset))
        return activities
    
    def is_activity_scheduled(
        self,
        activity: Activity,
    ) -> bool:
        scheduled_activities = self.get_scheduled_activities()
        return activity in scheduled_activities

    def _get_task_label(
        self,
        activity: Activity,
    ) -> str:
        """Generates a unique label for the scheduled task based on activity details."""

        offset_str = "none" if activity.posting_offset is None else str(activity.posting_offset)
        task_id = (
            f"{activity.id}--{activity.start_date}--{activity.start_time}--{offset_str}".replace(
                ":", "-"
            )
        )
        return f"{self.label_prefix}.{task_id}"

    def _validate_and_get_booking_datetime(
        self,
        activity: Activity
    ) -> datetime:
        """Validates the activity's date and time strings and returns a datetime object for booking."""

        # Always treat the input datetime as Toronto time
        toronto_tz = ZoneInfo("America/Toronto")
        activity_dt_toronto = datetime.strptime(
            f"{activity.start_date} {activity.start_time}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=toronto_tz)

        now_dt_local = datetime.now().astimezone()
        now_dt_toronto = now_dt_local.astimezone(toronto_tz)
        if activity_dt_toronto - timedelta(seconds=_BOT_START_BUFFER_SECONDS) < now_dt_toronto:
            raise ValueError("Cannot schedule the booking bot for an activity in the past.")

        booking_dt_toronto = None
        if activity.posting_offset is not None:
            booking_dt_toronto = activity_dt_toronto - timedelta(
                days=activity.posting_offset, seconds=_BOT_START_BUFFER_SECONDS
            )

        # No wait or booking time is in the past, schedule immediately (with 1 minute buffer)
        if booking_dt_toronto is None or booking_dt_toronto < now_dt_toronto:
            booking_dt_toronto = now_dt_local + timedelta(minutes=1)

        return booking_dt_toronto


def get_scheduler(error_log_path: str, output_log_path: str) -> Scheduler:
    """Factory function to get the appropriate scheduler based on the OS."""

    os_name = platform.system()
    if os_name == "Darwin":
        return _MacOSScheduler(error_log_path=error_log_path, output_log_path=output_log_path)
    elif os_name == "Windows":
        raise NotImplementedError("Windows Task Scheduler support coming soon.")
    else:
        raise NotImplementedError("Linux systemd support coming soon.")
