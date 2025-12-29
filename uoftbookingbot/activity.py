from typing import Optional


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
            and self.posting_offset == other.posting_offset
        )

    def get_registration_url(self) -> str:
        """Returns the booking URL for this activity."""

        return f"https://recreation.utoronto.ca/Program/GetProgramDetails?courseId={self.id}"
