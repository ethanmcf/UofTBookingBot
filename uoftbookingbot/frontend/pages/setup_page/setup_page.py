from uoftbookingbot.frontend.pages.base_page import BasePage
from uoftbookingbot.frontend.pages.setup_page.credentials_form import CredentialsForm
from uoftbookingbot.frontend.pages.setup_page.instructions import Instructions
from uoftbookingbot.database.db_controller import DBController
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout


class SetupPage(BasePage):
    def __init__(self):
        super().__init__()
        self.db_controller = DBController()

        # Initial data
        utorid, password = self.db_controller.get_credentials()
        current_bypass_code = self.db_controller.get_next_bypass_code()

        # Credentials component
        self.credentials_form = CredentialsForm(
            self.db_controller, utorid, password, current_bypass_code
        )

        # Instructions component
        self.instructions = Instructions(
            utorid is not None, password is not None, current_bypass_code is not None
        )

        # Bridge credentials and instrucitons component
        self.credentials_form.dataSaved.connect(self.instructions.update_status)
        self.credentials_form.dataDeleted.connect(
            lambda: self.instructions.update_status(False, False, False)
        )

        # Left column layout
        self.left_box = QWidget()
        self.left_col = QVBoxLayout(self.left_box)
        self.left_col.setContentsMargins(50, 120, 30, 0)
        self.left_col.setSpacing(10)
        self.left_col.addWidget(self.credentials_form)
        self.left_col.addStretch()

        # Right column layout
        self.right_box = QWidget()
        self.right_col = QVBoxLayout(self.right_box)
        self.right_col.setContentsMargins(0, 30, 10, 0)
        self.right_col.setSpacing(22)
        self.right_col.addWidget(self.instructions)
        self.right_col.addStretch()

        # Split layout assembly
        self.split_container = QHBoxLayout()
        self.split_container.setContentsMargins(10, 0, 0, 0)
        self.split_container.setSpacing(0)

        self.split_container.addWidget(self.left_box, 1)
        self.split_container.addWidget(self.right_box, 1)

        # Main Page Assembly
        self.page_layout.addLayout(self.split_container)
        self.page_layout.addStretch()

    def cleanup(self):
        self.db_controller.close()
