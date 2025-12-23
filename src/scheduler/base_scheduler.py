from abc import abstractmethod, ABCMeta


class BaseScheduler:
    """Base class for schedulers."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def schedule_bot(
        self,
        activity_url: str,
        activity_date: str,
        activity_time: str,
        activity_offset: int,
    ): ...

    @abstractmethod
    def unschedule_bot(self, activity_url: str, activity_date: str, activity_time: str): ...
