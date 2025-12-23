import platform

from scheduler.base_scheduler import BaseScheduler
from scheduler.macos_scheduler import MacOSScheduler


def get_scheduler(debug_file_path: str) -> BaseScheduler:
    """Factory function to get the appropriate scheduler based on the OS."""

    os_name = platform.system()
    if os_name == "Darwin":
        return MacOSScheduler(debug_file_path=debug_file_path)
    elif os_name == "Windows":
        raise NotImplementedError("Windows Task Scheduler support coming soon.")
    else:
        raise NotImplementedError("Linux systemd support coming soon.")
