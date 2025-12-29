from abc import abstractmethod, ABCMeta
from datetime import datetime, timedelta
import os
from pathlib import Path
import platform
import plistlib
import subprocess
import sys
from zoneinfo import ZoneInfo

from uoftbookingbot.activity import Activity
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
    def schedule_activity(self, activity: Activity) -> None:
        """Schedules the booking bot for a specified activity.
        If the activity is already scheduled, overwrite the existing schedule.

        Args:
            activity: The activity to schedule.
        """
        ...

    @abstractmethod
    def unschedule_activity(self, activity: Activity) -> None:
        """Unschedules a previously scheduled activity. Unscheduling a non-scheduled activity is a no-op.

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
    def is_activity_scheduled(self, activity: Activity) -> bool:
        """Returns True iff the activity is already scheduled."""
        ...


class _MacOSScheduler(Scheduler):
    """Scheduler implementation for macOS using launchd."""

    def __init__(self, error_log_path: str, output_log_path: str) -> None:
        self.error_log_path = error_log_path
        self.output_log_path = output_log_path
        self.agent_dir = os.path.expanduser("~/Library/LaunchAgents")
        self.label_prefix = "com.uoftbookingbot"

    def schedule_activity(
        self,
        activity: Activity,
    ) -> None:
        if self.is_activity_scheduled(activity):
            self.unschedule_activity(activity)

        label = self._get_task_label(activity)
        plist_path = os.path.join(self.agent_dir, f"{label}.plist")

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

    def unschedule_activity(
        self,
        activity: Activity,
    ) -> None:
        if not self.is_activity_scheduled(activity):
            return

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

            with open(os.path.join(self.agent_dir, filename), "rb") as f:
                plist_content = plistlib.load(f)
                program_args = plist_content.get("ProgramArguments", [])

                if (
                    "-i" not in program_args
                    or "-d" not in program_args
                    or "-t" not in program_args
                    or ("--no-wait" not in program_args and "-o" not in program_args)
                ):
                    continue

                i_index = program_args.index("-i")
                activity_id = program_args[i_index + 1]

                d_index = program_args.index("-d")
                activity_date = program_args[d_index + 1]

                t_index = program_args.index("-t")
                activity_time = program_args[t_index + 1]

                if "--no-wait" in program_args:
                    posting_offset = None
                else:
                    o_index = program_args.index("-o")
                    posting_offset = int(program_args[o_index + 1])

                activities.append(
                    Activity(
                        id=activity_id,
                        start_date=activity_date,
                        start_time=activity_time,
                        posting_offset=posting_offset,
                    )
                )

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

        task_id = f"{activity.id}--{activity.start_date}--{activity.start_time}".replace(":", "-")
        return f"{self.label_prefix}.{task_id}"

    def _validate_and_get_booking_datetime(self, activity: Activity) -> datetime:
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
