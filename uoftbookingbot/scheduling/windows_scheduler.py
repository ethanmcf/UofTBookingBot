from uoftbookingbot.activity import Activity
from uoftbookingbot.scheduling.scheduler import ScheduledActivity, Scheduler
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
import subprocess  
import csv       
import io         
import shlex       


class PPyCronScheduler(Scheduler):

    ACTIVITY_COMMAND_REGEX = r"^(cd .+ && )?(.+ )?-i .+ -d .+ -t .+"

    interface: WindowsInterface | UnixInterface

    def __init__(self) -> None:
        self.interface = WindowsInterface() if platform.system() == "Windows" else UnixInterface()
        if platform.system() == "Windows":
            self.interface.get_all = self._windows_get_all_patch

    def schedule_activity(self, activity: Activity) -> ScheduledActivity:
        self.unschedule_activity(activity)

        command_str = self._get_cron_command_for_activity(activity)
        booking_dt_local = get_scheduler_run_datetime(activity)
        interval_str = f"{booking_dt_local.minute} {booking_dt_local.hour} {booking_dt_local.day} {booking_dt_local.month} *"
        self.interface.add(command=command_str, interval=interval_str)
        return ScheduledActivity(activity=activity, run_at=booking_dt_local)

    def unschedule_activity(self, activity: Activity) -> None:
        activity_crons = self._get_all_crons_for_activity(activity)
        print(activity_crons)
        for cron in activity_crons:
            self.interface.delete(cron.id)

    def _windows_get_all_patch(self) -> list[Cron]:
        crons = []
        # Raw output of crons
        result = subprocess.run(["schtasks", "/query", "/fo", "CSV", "/v"], 
                                capture_output=True, text=True, encoding='utf-8')

        reader = csv.DictReader(io.StringIO(result.stdout.strip()))
        for row in reader:
            # Remove backslashes and spaces
            clean_row = {k.strip('\\').strip(): v for k, v in row.items()}
            
            # Task name
            task_name = clean_row.get("TaskName") 
            
            clean_id = task_name.strip('\\').replace("Pycron_", "")

            # Log pycron task
            if task_name and "Pycron" in task_name:
                command = clean_row.get("Task To Run")
                raw_date = clean_row.get("Next Run Time")

                # print(task_name)
                # print(raw_date)
                # print(command)
                # print("---")

                # Format into the Cron string: minute hour day month *
                try:
                    dt = datetime.strptime(raw_date, "%Y-%m-%d %I:%M:%S %p")
                    interval_str = f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"
                except:
                    interval_str = "* * * * *"
                crons.append(Cron(command=command, interval=interval_str, id=clean_id))
                
        return crons

    def get_scheduled_activities(self) -> list[ScheduledActivity]:
        activities = []
        all_crons = self.interface.get_all()
        now = datetime.now().astimezone()
        for cron in all_crons:
            if not re.search(self.ACTIVITY_COMMAND_REGEX, cron.command):
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

            scheduled_activity = ScheduledActivity(
                activity=candidate_activity,
                run_at=self._get_cron_scheduled_time(cron, candidate_activity),
            )
            activities.append(scheduled_activity)
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

    def _get_all_crons_for_activity(self, activity: Activity) -> list[Cron]:
        """Return all ppycron Cron objects corresponding to the given activity."""

        id_flag = f"-i {activity.id}"
    
        return [
            cron for cron in self.interface.get_all()
            if id_flag in cron.command
        ]

    def _get_cron_scheduled_time(self, cron: Cron, activity: Activity) -> datetime:
        """Return the scheduled datetime for the given cron and activity in the user's local timezone."""

        if not self.interface.is_valid_cron_format(cron.interval):
            raise ValueError("Invalid cron format")

        minute, hour, day, month, weekday = cron.interval.split()
   
        if minute == "*" or hour == "*" or day == "*" or month == "*" or weekday != "*":
            raise ValueError("Unexpected cron format")

        try:
            month = int(month)
            day = int(day)
            hour = int(hour)
            minute = int(minute)

        except Exception:
            raise ValueError("Cannot parse cron schedule values")

        activity_start_dt_local = activity.get_session_start_datetime().astimezone()
        scheduled_dt_local = datetime(
            year=activity_start_dt_local.year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
        ).astimezone()
        print(scheduled_dt_local)
        if scheduled_dt_local > activity_start_dt_local:
            scheduled_dt_local = scheduled_dt_local.replace(year=activity_start_dt_local.year - 1)

        return scheduled_dt_local

    def _is_schedule_expired(
        self, activity: Activity, cron: Cron, now: datetime, strict: bool
    ) -> bool:
        """Return True iff the schedule for the given activity is expired (or invalid) based on its
        cron content."""

        try:
            scheduled_dt_local = self._get_cron_scheduled_time(cron, activity)
        except ValueError:
            print("ERROR")
            return True
        if strict:
            return scheduled_dt_local < now
        return scheduled_dt_local + timedelta(seconds=FIRST_VALID_CLEANUP_BUFFER_SECONDS) < now
