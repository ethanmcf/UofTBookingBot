from .pages.landing_page import LandingPage
from .pages.setup_page import SetupPage
from .pages.run_page import RunPage
from .components.header import Header
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget, QGridLayout
from PyQt6.QtCore import Qt

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

    def go_to_home(self):
        self.header.should_paint = False
        self.page_stack.setCurrentIndex(0)

    def go_to_setup(self):
        self.header.should_paint = True
        self.page_stack.setCurrentIndex(1)

    def go_to_run(self):
        self.header.should_paint = True
        self.page_stack.setCurrentIndex(2)