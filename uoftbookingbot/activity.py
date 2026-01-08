from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo


class Activity:
    """Represents a bookable activity for the booking bot."""

    id: str
    start_date: str
    start_time: str
    posting_offset: Optional[int]

    def __init__(
        self, id: str, start_date: str, start_time: str, posting_offset: Optional[int] = None
    ) -> None:
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
            self.id == other.id
            and self.start_date == other.start_date
            and self.start_time == other.start_time
        )

    def get_registration_url(self) -> str:
        """Returns the booking URL for this activity."""

        return f"https://recreation.utoronto.ca/Program/GetProgramDetails?courseId={self.id}"

    def get_session_start_datetime(self) -> datetime:
        """Return a timezone aware datetime object for this activity session's start date and
        time."""

        return datetime.strptime(f"{self.start_date} {self.start_time}", "%Y-%m-%d %H:%M").replace(
            tzinfo=ZoneInfo("America/Toronto")
        )

    def get_registration_open_datetime(self) -> Optional[datetime]:
        """Return a timezone aware datetime object for when the activity's registration opens or
        None if registration open is not known (which we assume means registration is open)."""

        return (
            self.get_session_start_datetime() - timedelta(days=self.posting_offset)
            if self.posting_offset is not None
            else None
        )
