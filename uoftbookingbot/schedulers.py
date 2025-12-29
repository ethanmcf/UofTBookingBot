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
        activity_id: str,
        activity_date: str,
        activity_time: str,
        activity_offset: Optional[int],
    ) -> None: 
        """Schedules the booking bot for a specified activity.
        
        Args:
            activity_id: The ID of the drop-in activity.
            activity_date: The start date of the activity in YYYY-MM-DD format.
            activity_time: The start time of the activity in HH:MM format.
            activity_offset: The offset in days before the start time when registration opens or None to run immediately.
        """
        ...

    @abstractmethod
    def unschedule_bot(self, activity_id: str, activity_date: str, activity_time: str) -> None: 
        """Unschedules a previously scheduled activity.

        Args:
            activity_id: The ID of the drop-in activity.
            activity_date: The start date of the activity in YYYY-MM-DD format.
            activity_time: The start time of the activity in HH:MM format.
        """
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
        activity_id: str,
        activity_date: str,
        activity_time: str,
        activity_offset: Optional[int],
    ) -> None:
        label = self._get_task_label(activity_id, activity_date, activity_time)
        plist_path = os.path.join(self.agent_dir, f"{label}.plist")

        offset_args = ["-o", str(activity_offset)] if activity_offset is not None else ["--no-wait"]
        activity_args = [
            "-i",
            activity_id,
            "-d",
            activity_date,
            "-t",
            activity_time,
        ] + offset_args

        # Determine the execution path
        exec_path = sys.executable
        if not is_running_as_bundle():
            # in dev, run as: python -m uoftbookingbot
            activity_args = ["-m", "uoftbookingbot"] + activity_args

        project_root = str(
            Path(sys.executable).parent if is_running_as_bundle() else Path(__file__).parent.parent
        )

        booking_dt_toronto = self._validate_and_get_booking_datetime(
            activity_date, activity_time, activity_offset
        )

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
        activity_id: str,
        activity_date: str,
        activity_time: str,
    ) -> None:
        label = self._get_task_label(activity_id, activity_date, activity_time)
        plist_path = os.path.join(self.agent_dir, f"{label}.plist")

        subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{label}"], check=False)
        if os.path.exists(plist_path):
            os.remove(plist_path)

    def _get_task_label(
        self,
        activity_id: str,
        activity_date: str,
        activity_time: str,
    ) -> str:
        task_id = (
            f"{activity_id}--{activity_date}--{activity_time}".replace(
                ":", "-"
            )
        )
        return f"{self.label_prefix}.{task_id}"

    def _validate_and_get_booking_datetime(
        self,
        activity_date: str,
        activity_time: str,
        activity_offset: Optional[int],
    ) -> datetime:
        """Validates the input date and time strings and returns a datetime object for booking."""

        # Always treat the input datetime as Toronto time
        toronto_tz = ZoneInfo("America/Toronto")
        activity_dt_toronto = datetime.strptime(
            f"{activity_date} {activity_time}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=toronto_tz)

        now_dt_local = datetime.now().astimezone()
        now_dt_toronto = now_dt_local.astimezone(toronto_tz)
        if activity_dt_toronto - timedelta(seconds=_BOT_START_BUFFER_SECONDS) < now_dt_toronto:
            raise ValueError("Cannot schedule the booking bot for an activity in the past.")

        booking_dt_toronto = None
        if activity_offset is not None:
            booking_dt_toronto = activity_dt_toronto - timedelta(
                days=activity_offset, seconds=_BOT_START_BUFFER_SECONDS
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
