from uoftbookingbot.automation.runner import run_registration_bot
from PyQt6.QtCore import QObject, pyqtSignal

class BotWorker(QObject):
    finished = pyqtSignal(bool)

    def __init__(self, bot_args):
        super().__init__()
        self.bot_args = bot_args

    def run(self):
        try:
            success = run_registration_bot(**self.bot_args)
            self.finished.emit(success)
        except Exception as e:
            print(f"Worker Error: {e}")
            self.finished.emit(False)