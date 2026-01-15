from pathlib import Path
from uoftbookingbot.frontend.constants import ASSETS_DIR_PATH
from uoftbookingbot.frontend.components.primary_button import PrimaryButton
from uoftbookingbot.frontend.components.input import Input
from uoftbookingbot.database.db_controller import DBController
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
import textwrap


class CredentialsForm(QWidget):
    dataSaved = pyqtSignal(bool, bool, bool)
    dataDeleted = pyqtSignal()

    def __init__(
        self, db_controller: DBController, utorid: str, password: str, current_bypass_code: str
    ):
        super().__init__()
        self.db_controller = db_controller

        # Inputs
        self.form_layout = QVBoxLayout(self)
        self.form_layout.setSpacing(10)

        self.utorid_input = Input("Your utorid")
        self.utorid_input.setText(utorid)

        self.password_input = Input("Your password", is_password=True)
        self.password_input.setText(password)

        self.bypass_input = Input("Current bypass code")
        self.bypass_input.setText(current_bypass_code)

        # Save button
        self.save_btn = PrimaryButton("Save")
        self.save_btn.btn.clicked.connect(self.save_user_data)

        # Delete button
        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(QIcon(QPixmap(str(Path(ASSETS_DIR_PATH) / "trash-icon.png"))))
        self.delete_btn.setIconSize(QSize(30, 30))
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(self.delete_user_data)

        self.delete_btn.setToolTip(
            textwrap.dedent(
                """
            Because your info is stored only on your machine,
            we have zero access to your sensitive credentials.
            You can permanently remove all stored information 
            at any time using this button.
        """
            ).strip()
        )
        self.delete_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
                border-radius: 15px; 
            }
            QToolTip {
                background-color: white;
                color: black;
                padding: 5px;
                border-radius: 4px;
                border: 1px solid #ccc;
            }
        """
        )

        # Layout Assembly
        self.form_layout.addWidget(self.utorid_input)
        self.form_layout.addWidget(self.password_input)
        self.form_layout.addWidget(self.bypass_input)
        self.form_layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addWidget(self.save_btn, stretch=1)
        btn_row.addWidget(self.delete_btn)

        self.form_layout.addLayout(btn_row, 1)

    def save_user_data(self):
        utorid, password, bypass_code = (
            self.utorid_input.text(),
            self.password_input.text(),
            self.bypass_input.text(),
        )

        self.db_controller.save_credentials(utorid, password)

        if bypass_code != "":
            self.db_controller.save_bypass_codes([bypass_code])

        # Send signal to todo items in instructions
        self.dataSaved.emit(utorid != "", password != "", bypass_code != "")

    def delete_user_data(self):
        self.db_controller.delete_user_data()

        self.utorid_input.setText("")
        self.password_input.setText("")
        self.bypass_input.setText("")

        # Send to todo items in instructions
        self.dataDeleted.emit()
