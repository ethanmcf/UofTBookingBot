from uoftbookingbot.activity import Activity
from uoftbookingbot.scheduling.scheduler import Scheduler
from uoftbookingbot.scheduling.constants import FIRST_VALID_CLEANUP_BUFFER_SECONDS
from uoftbookingbot.scheduling.utils import (
    create_activity_from_program_args,
    get_execution_values,
    get_scheduler_run_datetime,
)

import os
import plistlib
import subprocess
from datetime import datetime, timedelta
from typing import Any, Optional


class LaunchdScheduler(Scheduler):
    """Scheduler implementation for macOS using launchd."""

    _JOB_PREFIX = "com.uoftbookingbot"
    _AGENT_DIR: str = os.path.expanduser("~/Library/LaunchAgents")

    def schedule_activity(self, activity: Activity) -> None:
        if self.is_activity_scheduled(activity):
            self.unschedule_activity(activity)

        booking_dt_local = get_scheduler_run_datetime(activity)
        label = self._get_unique_launchd_label(activity)
        plist_path = self._get_plist_path_from_label(label)
        bot_exec_path, activity_args, project_root = get_execution_values(activity)
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
                try:
                    program_args = plist_content.get("ProgramArguments", [])
                    candidate_activity = create_activity_from_program_args(program_args)
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
                    candidate_activity = create_activity_from_program_args(program_args)
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

        activity_start_dt_local = activity.get_session_start_datetime().astimezone()
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
        return scheduled_dt_local + timedelta(seconds=FIRST_VALID_CLEANUP_BUFFER_SECONDS) < now
