from uoftbookingbot.activity import Activity
from abc import ABCMeta, abstractmethod


class Scheduler:
    """Base class for scheduling the booking bot.

    Scheduling an activity session means scheduling the booking bot to run at a specific time in the
    future to attempt to book the activity session on behalf of the user. Once scheduled, the
    booking bot will run automatically at the scheduled time without any further user intervention.

    Invariants:
    - An activity session can only be scheduled for booking once at any given time.
    - An activity session can only be scheduled for booking if its start time is in the future.
    - The scheduler attempts execution of the booking bot for a scheduled activity session exactly
      once at the scheduled time.
    - A scheduled activity session is no longer considered scheduled once the booking bot has
      executed the booking (or attempted to) for that activity session. If the scheduler fails to
      execute the booking bot at the scheduled time (e.g. the user's computer was off), the
      scheduled activity session is considered expired (i.e. no longer scheduled) and must be
      rescheduled by the user if they still wish to book it.

    Other Assumptions/Notes:
    - Activity session start times are in the America/Toronto timezone.
    - All scheduled booking run times are in the user's local timezone.
    - The scheduler assumes that the user's system timezone does not change between the time of
      scheduling and the time of execution. If the user's system timezone does change, the
      scheduled booking run time may be incorrect.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def schedule_activity(self, activity: Activity) -> None:
        """Schedule the booking bot to book the specified activity session. If the activity session
        is already scheduled for booking, overwrite the existing schedule. Scheduling an activity
        session for booking whose session has already started raises a ValueError.

        Args:
            activity: The activity session to schedule.
        """
        ...

    @abstractmethod
    def unschedule_activity(self, activity: Activity) -> None:
        """Unschedule an activity session previously scheduled for booking. Unscheduling a
        non-scheduled activity session is a no-op.

        Args:
            activity: The activity session to unschedule.
        """
        ...

    @abstractmethod
    def get_scheduled_activities(self) -> list[Activity]:
        """Return a list of activity sessions scheduled for booking.

        Returns:
            list[Activity]: A list of scheduled activity sessions.
        """
        ...

    @abstractmethod
    def is_activity_scheduled(self, activity: Activity) -> bool:
        """Return True iff the activity session is scheduled for booking.

        Args:
            activity: The activity session to check.

        Returns:
            bool: True iff the activity session is scheduled for booking.
        """
        ...

    @abstractmethod
    def cleanup_expired_schedules(self) -> None:
        """Cleanup any expired or invalid scheduled activity sessions from the scheduler."""
        ...
