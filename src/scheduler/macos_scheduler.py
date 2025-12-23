import os
import sys
import plistlib
import subprocess
from hashlib import md5
from datetime import datetime, timedelta

from scheduler.base_scheduler import BaseScheduler


class MacOSScheduler(BaseScheduler):
    """Scheduler implementation for macOS using launchd."""

    def __init__(self, debug_file_path: str):
        self.debug_file_path = debug_file_path
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
        if getattr(sys, "frozen", False):
            # Running as a PyInstaller bundle
            exec_path = sys.executable
        else:
            # Running in development -> we must call: python src/main.py [args]
            exec_path = sys.executable
            script_path = os.path.abspath("src/main.py")
            activity_args = [script_path] + activity_args

        booking_datetime = datetime.strptime(
            f"{activity_date} {activity_time}", "%Y-%m-%d %H:%M"
        ) - timedelta(days=activity_offset, seconds=120)
        if booking_datetime <= datetime.now():
            booking_datetime = datetime.now() + timedelta(seconds=5)

        plist_content = {
            "Label": label,
            "ProgramArguments": [exec_path] + activity_args,
            "StartCalendarInterval": {
                "Month": int(booking_datetime.strftime("%m")),
                "Day": int(booking_datetime.strftime("%d")),
                "Hour": int(booking_datetime.strftime("%H")),
                "Minute": int(booking_datetime.strftime("%M")),
            },
            "StandardOutPath": os.path.join(
                self.debug_file_path, "logs/", "output.log"
            ),
            "StandardErrorPath": os.path.join(
                self.debug_file_path, "logs/", "error.log"
            ),
            "RunAtLoad": False,
        }

        with open(plist_path, "wb") as f:
            plistlib.dump(plist_content, f)

        subprocess.run(
            ["launchctl", "bootstrap", f"gui/{os.getuid()}", plist_path], check=False
        )

    def unschedule_bot(
        self,
        activity_url: str,
        activity_date: str,
        activity_time: str,
    ):
        label = self._get_task_label(activity_url, activity_date, activity_time)
        plist_path = os.path.join(self.agent_dir, f"{label}.plist")

        subprocess.run(
            ["launchctl", "bootout", f"gui/{os.getuid()}/{label}"], check=False
        )
        if os.path.exists(plist_path):
            os.remove(plist_path)

    def _get_task_label(
        self,
        activity_url: str,
        activity_date: str,
        activity_time: str,
    ) -> str:
        task_id = f"{md5(activity_url.encode()).hexdigest()}.{activity_date}.{activity_time}".replace(
            ":", "-"
        )
        return f"{self.label_prefix}.{task_id}"
