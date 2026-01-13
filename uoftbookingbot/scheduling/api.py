import platform
from uoftbookingbot.scheduling.scheduler import Scheduler
from uoftbookingbot.scheduling.launchd_scheduler import LaunchdScheduler
from uoftbookingbot.scheduling.ppycron_scheduler import PPyCronScheduler


def get_scheduler() -> Scheduler:
    """Factory function to get the appropriate scheduler based on the OS."""

    os_name = platform.system()
    if os_name == "Darwin":
        return LaunchdScheduler()
    elif os_name == "Linux":
        return PPyCronScheduler()
    else:
        raise Exception(
            f"Your operating system ({os_name}) is not supported for scheduling for this app at the moment."
        )
