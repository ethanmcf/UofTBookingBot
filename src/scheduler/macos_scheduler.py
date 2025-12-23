import os
import sys
import plistlib
import subprocess
from hashlib import md5
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.scheduler.base_scheduler import BaseScheduler


class MacOSScheduler(BaseScheduler):
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
        activity_offset: int,
    ):
        label = self._get_task_label(activity_url, activity_date, activity_time)
        plist_path = os.path.join(self.agent_dir, f"{label}.plist")

        activity_args = [
            "-u",
            activity_url,
            "-d",
            activity_date,
            "-t",
            activity_time,
            "-o",
            str(activity_offset),
        ]

        # Determine the execution path
        exec_path = sys.executable
        if not getattr(sys, "frozen", False):
            # in dev, run as: python -m src.main
            activity_args = ["-m", "src.main"] + activity_args

        booking_dt_toronto = self._validate_and_get_booking_datetime(
            activity_date, activity_time, activity_offset
        )

        plist_content = {
            "Label": label,
            "Program": exec_path,
            "ProgramArguments": [exec_path] + activity_args,
            "WorkingDirectory": self.project_root,
            "EnvironmentVariables": {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONUNBUFFERED": "1",  # Ensures logs are written immediately
            },
            "StartCalendarInterval": {
                "Month": booking_dt_toronto.month,
                "Day": booking_dt_toronto.day,
                "Hour": booking_dt_toronto.hour,
                "Minute": booking_dt_toronto.minute,
            },
            "StandardOutPath": os.path.join(self.debug_folder_path, "logs/", "output.log"),
            "StandardErrorPath": os.path.join(self.debug_folder_path, "logs/", "error.log"),
            "RunAtLoad": False,
            "AbandonProcessGroup": True,
        }

        with open(plist_path, "wb") as f:
            plistlib.dump(plist_content, f)

        subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", plist_path], check=False)

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
            f"{md5(activity_url.encode()).hexdigest()}.{activity_date}.{activity_time}".replace(
                ":", "-"
            )
        )
        return f"{self.label_prefix}.{task_id}"

    def _validate_and_get_booking_datetime(
        self,
        activity_date: str,
        activity_time: str,
        activity_offset: int,
    ) -> datetime:
        """Validates the input date and time strings and returns a datetime object for booking."""

        BOT_START_BUFFER_SECONDS = 120

        # Always treat the input datetime as Toronto time
        toronto_tz = ZoneInfo("America/Toronto")
        activity_dt_toronto = datetime.strptime(
            f"{activity_date} {activity_time}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=toronto_tz)

        booking_dt_toronto = activity_dt_toronto - timedelta(
            days=activity_offset, seconds=BOT_START_BUFFER_SECONDS
        )

        now_dt_local = datetime.now().astimezone()
        now_dt_toronto = now_dt_local.astimezone(toronto_tz)
        if activity_dt_toronto - timedelta(seconds=BOT_START_BUFFER_SECONDS) < now_dt_toronto:
            raise ValueError("Cannot schedule the booking bot for an activity in the past.")
        if booking_dt_toronto < now_dt_toronto:
            booking_dt_toronto = now_dt_local + timedelta(minutes=1)

        return booking_dt_toronto
