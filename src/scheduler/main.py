import platform

from src.scheduler.base_scheduler import BaseScheduler
from src.scheduler.macos_scheduler import MacOSScheduler


def get_scheduler(debug_folder_path: str, project_root: str) -> BaseScheduler:
    """Factory function to get the appropriate scheduler based on the OS."""

    os_name = platform.system()
    if os_name == "Darwin":
        return MacOSScheduler(debug_folder_path=debug_folder_path, project_root=project_root)
    elif os_name == "Windows":
        raise NotImplementedError("Windows Task Scheduler support coming soon.")
    else:
        raise NotImplementedError("Linux systemd support coming soon.")
