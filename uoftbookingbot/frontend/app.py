from uoftbookingbot.frontend.pages.landing_page import LandingPage
from uoftbookingbot.frontend.pages.setup_page import SetupPage
from uoftbookingbot.frontend.pages.run_page import RunPage
from uoftbookingbot.automation.bot_worker import BotWorker
from uoftbookingbot.frontend.components.header import Header
from uoftbookingbot.automation.logger import LogSignaler
from uoftbookingbot.activity import Activity
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QGridLayout, QApplication
from PyQt6.QtCore import Qt, QThread
import sys


class BookingApp(QMainWindow):
    """Main window to handle navigation of pages"""

    activities: dict[str, dict[str, str]]
    credentials_path: str
    bypass_codes_path: str
    log_path: str
    screenshots_path: str

    def __init__(
        self,
        activities: dict[str, dict[str, str]],
        credentials_path: str,
        bypass_codes_path: str,
        log_path: str,
        screenshots_path: str,
    ):
        """Initializes the main booking app window.

        Args:
            activities (dict[str, dict[str, str]]): Mapping of activity names to their details.
            credentials_path (str): Path to the credentials file.
            bypass_codes_path (str): Path to the bypass codes file.
            log_path (str): Path to the log directory.
            screenshots_path (str): Path to the screenshots directory.
        """
        super().__init__()
        self.activities = activities
        self.credentials_path = credentials_path
        self.bypass_codes_path = bypass_codes_path
        self.log_path = log_path
        self.screenshots_path = screenshots_path

        self.setFixedSize(900, 600)

        self.main_container = QWidget()
        self.main_container.setStyleSheet("background-color: white;")
        self.setCentralWidget(self.main_container)

        # Grid layout for overlapping content and header
        self.layout = QGridLayout(self.main_container)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Page stack and header
        self.page_stack = QStackedWidget()
        self.header = Header(False)

        # Overlay header with page stack
        self.layout.addWidget(self.page_stack, 0, 0)
        self.layout.addWidget(self.header, 0, 0, Qt.AlignmentFlag.AlignTop)

        # Create pages and add to stack
        self.landing_page = LandingPage()
        self.setup_page = SetupPage()
        self.run_page = RunPage(activities=self.activities)

        self.page_stack.addWidget(self.landing_page)
        self.page_stack.addWidget(self.setup_page)
        self.page_stack.addWidget(self.run_page)

        # Connect navigation buttons
        self.landing_page.start_btn.clicked.connect(self.go_to_setup)
        self.header.run_btn.clicked.connect(self.go_to_run)
        self.header.setup_btn.clicked.connect(self.go_to_setup)

        # Connect run btn
        self.run_page.start_run_signal.connect(self.handle_bot_execution)

        # Connect log signaler
        self.ui_log_signaler = LogSignaler()
        self.ui_log_signaler.log_signal.connect(self.run_page.on_log_update)

    # --- Navigation functions ---
    def go_to_home(self):
        self.header.should_paint = False
        self.page_stack.setCurrentIndex(0)

    def go_to_setup(self):
        self.header.should_paint = True
        self.page_stack.setCurrentIndex(1)

    def go_to_run(self):
        self.header.should_paint = True
        self.page_stack.setCurrentIndex(2)

    # --- Bot functions ---
    def handle_bot_execution(self, activity_args: dict[str, str]):
        """Runs bot as a background thread so it doesn't block UI

        Args:
            activity_args (dict[str, str]): Arguments for the activity to book.
        """
        # Create Thread and Worker
        self.bot_thread = QThread()

        activity_to_book = Activity(
            id=activity_args["id"],
            start_date=activity_args["start_date"],
            start_time=activity_args["start_time"],
            posting_offset=activity_args["posting_offset"],
        )
        bot_args = {
            "activity": activity_to_book,
            "time_limit": 10,
            "codes_threshold": 3,
            "headless": True,
            "debug": False,
            "credentials_path": self.credentials_path,
            "bypass_codes_path": self.bypass_codes_path,
            "log_path": self.log_path,
            "screenshots_path": self.screenshots_path,
            "ui_signaler": self.ui_log_signaler,
        }

        self.worker = BotWorker(bot_args)
        self.worker.moveToThread(self.bot_thread)

        # Connect thread
        self.bot_thread.started.connect(self.worker.run)

        # 3Handle Completion
        self.worker.finished.connect(self.run_page.on_execution_complete)
        self.worker.finished.connect(self.bot_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        # Start bot
        self.bot_thread.start()

    def closeEvent(self, event):
        """Triggered when the window is closed to cleanly shutdown bot thread if running"""

        try:
            # Check if thread is alive & running
            if hasattr(self, "bot_thread") and self.bot_thread is not None:
                try:
                    if self.bot_thread.isRunning():
                        if hasattr(self, "worker") and self.worker:
                            self.worker.stop()

                        self.bot_thread.quit()
                        if not self.bot_thread.wait(2000):
                            self.bot_thread.terminate()
                except RuntimeError:
                    pass  # Thread has already been cleaned up by Qt
        except Exception as e:
            print(f"Shutdown error: {e}")

        event.accept()


def run_app(
    activities: dict[str, dict[str, str]],
    credentials_path: str,
    bypass_codes_path: str,
    log_path: str,
    screenshots_path: str,
):
    """Runs the PyQt application for the booking bot GUI.
    Args:
        activities (dict[str, dict[str, str]]): Mapping of activity names to their details.
        credentials_path (str): Path to the credentials file.
        bypass_codes_path (str): Path to the bypass codes file.
        log_path (str): Path to the log directory.
        screenshots_path (str): Path to the screenshots directory.
    """
    # Create app
    qt_app = QApplication(sys.argv)

    # Create and show the main window
    window = BookingApp(
        activities=activities,
        credentials_path=credentials_path,
        bypass_codes_path=bypass_codes_path,
        log_path=log_path,
        screenshots_path=screenshots_path,
    )
    window.setWindowTitle("UofT Booking Bot")
    window.show()

    # Run the event loop
    sys.exit(qt_app.exec())
