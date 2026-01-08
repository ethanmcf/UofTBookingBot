from uoftbookingbot.activity import Activity
from uoftbookingbot.scheduling.scheduler import Scheduler
from uoftbookingbot.scheduling.constants import FIRST_VALID_CLEANUP_BUFFER_SECONDS
from uoftbookingbot.scheduling.utils import (
    create_activity_from_program_args,
    get_execution_values,
    get_scheduler_run_datetime,
)

from ppycron.src import Cron, UnixInterface, WindowsInterface
import platform
import re
from datetime import datetime, timedelta


class PPyCronScheduler(Scheduler):

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
                candidate_activity = create_activity_from_program_args(program_args)
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
                candidate_activity = create_activity_from_program_args(program_args)
            except ValueError:
                self.interface.delete(cron.id)
                continue

            # Ensure scheduled activity is valid and set to be booked in the future
            if self._is_schedule_expired(candidate_activity, cron, now, strict=False):
                self.interface.delete(cron.id)
                continue

    def _get_cron_command_for_activity(self, activity: Activity) -> str:
        """Return the command string to pass to ppycron's add command for the given activity."""

        exec_path, activity_args, project_root = get_execution_values(activity)
        return f"cd {project_root} && {exec_path} {' '.join(activity_args)}"

    def _get_cron_command_with_no_offset_args(self, command: str) -> str:
        """Return the command string with any offset args (-o or --no-wait) removed."""

        return re.sub(r" -o \d+| --no-wait", "", command)

    def _get_cron_interval_for_activity(self, activity: Activity) -> str:
        """Return the cron interval string for the given activity. Raise ValueError if the activity
        is in the past."""

        booking_dt_local = get_scheduler_run_datetime(activity)
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
