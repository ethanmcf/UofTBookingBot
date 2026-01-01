from uoftbookingbot.automation.runner import run_registration_bot
from PyQt6.QtCore import QObject, pyqtSignal


class BotWorker(QObject):
    """Bridge used by the frontend to execute the backend bot in a background thread."""

    finished = pyqtSignal(bool, str)

    def __init__(self, bot_args):
        super().__init__()
        self.bot_args = bot_args
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        try:
            run_registration_bot(**self.bot_args)
            self.finished.emit(
                True, "Successfully booked! You should receive a confirmation email soon."
            )
        except Exception as e:
            self.finished.emit(False, f"'{str(e)}'. Try again.")
