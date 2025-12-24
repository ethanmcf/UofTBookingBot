from abc import abstractmethod, ABCMeta
from datetime import datetime, timedelta
from hashlib import md5
import os
import platform
import plistlib
import subprocess
import sys
from typing import Optional
from zoneinfo import ZoneInfo


_BOT_START_BUFFER_SECONDS = 300  # bot starts 5 minutes before booking time


class _BaseScheduler:
    """Base class for schedulers."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def schedule_bot(
        self,
        activity_url: str,
        activity_date: str,
        activity_time: str,
        activity_offset: Optional[int],
    ): ...

    @abstractmethod
    def unschedule_bot(self, activity_url: str, activity_date: str, activity_time: str): ...


class _MacOSScheduler(_BaseScheduler):
    """Scheduler implementation for macOS using launchd."""

    def __init__(self, debug_folder_path: str, project_root: str):
        self.debug_folder_path = debug_folder_path
        self.project_root = project_root
        self.agent_dir = os.path.expanduser("~/Library/LaunchAgents")
        self.label_prefix = "com.uoftbookingbot"

    def schedule_bot(
        self,
        activity_url: str,
        activity_date: str,
        activity_time: str,
        activity_offset: Optional[int],
    ):
        label = self._get_task_label(activity_url, activity_date, activity_time)
        plist_path = os.path.join(self.agent_dir, f"{label}.plist")

        offset_args = ["-o", str(activity_offset)] if activity_offset is not None else ["--no-wait"]
        activity_args = [
            "-u",
            activity_url,
            "-d",
            activity_date,
            "-t",
            activity_time,
        ] + offset_args

        # Determine the execution path
        exec_path = sys.executable
        if not getattr(sys, "frozen", False):
            # in dev, run as: python -m uoftbookingbot
            activity_args = ["-m", "uoftbookingbot"] + activity_args

        booking_dt_toronto = self._validate_and_get_booking_datetime(
            activity_date, activity_time, activity_offset
        )

        plist_content = {
            "Label": label,
            "ProgramArguments": [exec_path] + activity_args,
            "WorkingDirectory": self.project_root,
            "EnvironmentVariables": {
                "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/homebrew/bin"
            },
            "StartCalendarInterval": {
                "Month": booking_dt_toronto.month,
                "Day": booking_dt_toronto.day,
                "Hour": booking_dt_toronto.hour,
                "Minute": booking_dt_toronto.minute,
            },
            "StandardOutPath": os.path.join(self.debug_folder_path, "logs", "output.log"),
            "StandardErrorPath": os.path.join(self.debug_folder_path, "logs", "error.log"),
            "RunAtLoad": False,
        }

        with open(plist_path, "wb") as f:
            plistlib.dump(plist_content, f)

        subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", plist_path], check=False)
        subprocess.run(["launchctl", "enable", f"gui/{os.getuid()}/{label}"], check=False)

    def unschedule_bot(
        self,
        activity_url: str,
        activity_date: str,
        activity_time: str,
    ):
        label = self._get_task_label(activity_url, activity_date, activity_time)
        plist_path = os.path.join(self.agent_dir, f"{label}.plist")

        subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{label}"], check=False)
        if os.path.exists(plist_path):
            os.remove(plist_path)

    def _get_task_label(
        self,
        activity_url: str,
        activity_date: str,
        activity_time: str,
    ) -> str:
        task_id = (
            f"{md5(activity_url.encode()).hexdigest()}--{activity_date}--{activity_time}".replace(
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

        if booking_dt_toronto is None or booking_dt_toronto < now_dt_toronto:
            booking_dt_toronto = now_dt_local + timedelta(minutes=1)

        return booking_dt_toronto


def get_scheduler(debug_folder_path: str, project_root: str) -> _BaseScheduler:
    """Factory function to get the appropriate scheduler based on the OS."""

    os_name = platform.system()
    if os_name == "Darwin":
        return _MacOSScheduler(debug_folder_path=debug_folder_path, project_root=project_root)
    elif os_name == "Windows":
        raise NotImplementedError("Windows Task Scheduler support coming soon.")
    else:
        raise NotImplementedError("Linux systemd support coming soon.")
