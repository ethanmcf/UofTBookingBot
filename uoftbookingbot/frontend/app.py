from uoftbookingbot.frontend.pages.landing_page import LandingPage
from uoftbookingbot.frontend.pages.setup_page import SetupPage
from uoftbookingbot.frontend.pages.run_page import RunPage
from uoftbookingbot.frontend.components.header import Header
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QGridLayout
from PyQt6.QtCore import Qt, QThread
from uoftbookingbot.automation.bot_worker import BotWorker

class BookingApp(QMainWindow):
    """Main window to handle navigation of pages"""
    def __init__(self):
        super().__init__()
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
        self.run_page = RunPage()

        self.page_stack.addWidget(self.landing_page) 
        self.page_stack.addWidget(self.setup_page)  
        self.page_stack.addWidget(self.run_page)   

        # Connect navigation buttons
        self.landing_page.start_btn.clicked.connect(self.go_to_setup)
        self.header.run_btn.clicked.connect(self.go_to_run)
        self.header.setup_btn.clicked.connect(self.go_to_setup)

        # Connect run btn
        self.run_page.start_run_signal.connect(self.handle_bot_execution)

    def go_to_home(self):
        self.header.should_paint = False
        self.page_stack.setCurrentIndex(0)

    def go_to_setup(self):
        self.header.should_paint = True
        self.page_stack.setCurrentIndex(1)

    def go_to_run(self):
        self.header.should_paint = True
        self.page_stack.setCurrentIndex(2)

    def handle_bot_execution(self, bot_args):
        """Runs bot as a background thread so it doesn't block UI"""
        # Create Thread and Worker
        self.thread = QThread()

        # TEMPRORARY ARGS FOR TESTING
        bot_args = {
            "activity_url": "https://recreation.utoronto.ca/program/GetProgramDetails?courseId=5904837f-6aa4-4707-bcfb-2ece4049bae0",
            "activity_date": "2026-01-08",
            "activity_time": "13:30",
            "activity_offset": 2,
            "time_limit": 10,
            "codes_threshold": 3,
            "headless": True,
            "debug": False,
            "credentials_path": "./secrets/login_credentials.txt",
            "bypass_codes_path": "./secrets/bypass_codes.txt",
            "log_path": "./uoftbookingbot/logs",
            "screenshots_path": "./uoftbookingbot/screenshots",
        }

        self.worker = BotWorker(bot_args)
        self.worker.moveToThread(self.thread)

        # Connect thread
        self.thread.started.connect(self.worker.run)
        
        # 3Handle Completion
        self.worker.finished.connect(self.run_page.on_execution_complete)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start bot
        self.thread.start()