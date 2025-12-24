from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ..components.button import PrimaryButton
from ..components.header import Header

class WelcomePage(QWidget):
    def __init__(self, controller):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Add Reusable Header
        self.header = Header()
        layout.addWidget(self.header)
        
        layout.addStretch()
        layout.addWidget(QLabel("Welcome to the Bot"))
        
        # Add Reusable Button
        self.start_btn = PrimaryButton("Get Started")
        self.start_btn.clicked.connect(lambda: controller.setCurrentIndex(1))
        layout.addWidget(self.start_btn)
        layout.addStretch()