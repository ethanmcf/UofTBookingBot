from uoftbookingbot.frontend.pages.base_page import BasePage
from uoftbookingbot.frontend.theme import Colors
from uoftbookingbot.frontend.components.primary_button import PrimaryButton
from uoftbookingbot.frontend.components.todo_item import TodoItem
from uoftbookingbot.frontend.components.input import Input
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
import textwrap


class SetupPage(BasePage):
    def __init__(self, db_controller):
        super().__init__()
        self.db_controller = db_controller

        # Split layout
        self.split_container = QHBoxLayout()
        self.split_container.setContentsMargins(10, 0, 0, 0)
        self.split_container.setSpacing(0)

        # Left column (form)
        self.left_box = QWidget()

        self.left_col = QVBoxLayout(self.left_box)
        self.left_col.setContentsMargins(50, 160, 30, 0)
        self.left_col.setSpacing(10)

        # Create form
        utorid, password = self.db_controller.get_credentials()
        current_bypass_code = self.db_controller.get_next_bypass_code()
        form = self.createForm(utorid, password, current_bypass_code)
        self.left_col.addLayout(form)
        self.left_col.addStretch()

        # Right column (instructions)
        self.right_box = QWidget()
        self.right_col = QVBoxLayout(self.right_box)
        self.right_col.setContentsMargins(70, 30, 10, 0)
        self.right_col.setSpacing(22)

        # Todo image
        self.createTodoImage()

        # Instructions
        instruction_title = QLabel("Setup Instructions")
        instruction_title.setStyleSheet(
            f"color: {Colors.TEXT_MAIN}; font-weight: bold; font-size: 16px;"
        )
        instruction_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_col.addWidget(instruction_title)

        self.utorid_item = TodoItem("Enter & save your utorid", utorid != None)
        self.right_col.addWidget(self.utorid_item)

        self.password_item = TodoItem("Enter & save your password", password != None)
        self.right_col.addWidget(self.password_item)

        # Create bypass info
        self.bypass_item = TodoItem("Enter & save a bypass code", current_bypass_code != None)
        self.bypass_instruction_label = QLabel(
            (
                "1) Login to https://bypass.utormfa.utoronto.ca/index.php\n\n"
                "2) Click ‘Generate Bypass Codes’ button\n\n"
                "3) Copy any one code into text field"
            )
        )
        self.bypass_instruction_label.setStyleSheet(
            f"color: {Colors.DARK_GRAY}; font-size: 12px; padding-left: 65px"
        )
        self.bypass_instruction_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.right_col.addWidget(self.bypass_item)
        self.right_col.addWidget(self.bypass_instruction_label)

        self.right_col.addStretch()

        # Add columns to split layout
        self.split_container.addWidget(self.left_box, 1)
        self.split_container.addWidget(self.right_box, 1)

        # Add content to page and keep aligned to top
        self.page_layout.addLayout(self.split_container)
        self.page_layout.addStretch()

    def createTodoImage(self):
        self.image_label = QLabel(self.right_box)
        self.image_label.setStyleSheet("background: transparent;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        todo_png = QPixmap("uoftbookingbot/frontend/assets/todo.png")
        self.image_label.setPixmap(
            todo_png.scaled(
                300,
                300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.right_col.addStretch()
        self.right_col.addWidget(self.image_label)

    def createForm(self, utorid, password, current_bypass_code):
        # Inputs
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(10)

        self.utorid_input = Input("Your utorid")
        self.utorid_input.setText(utorid)
        self.form_layout.addWidget(self.utorid_input)

        self.password_input = Input("Your password")
        self.password_input.setText(password)
        self.form_layout.addWidget(self.password_input)

        self.bypass_input = Input("Current bypass code")
        self.bypass_input.setText(current_bypass_code)
        self.form_layout.addWidget(self.bypass_input)
        self.form_layout.addStretch()

        # Save button
        self.save_btn = PrimaryButton("Save")
        self.save_btn.btn.clicked.connect(self.save_info)

        # Delete button
        self.delete_btn = QPushButton()
        pixmap = QPixmap("uoftbookingbot/frontend/assets/trash-icon.png")
        self.delete_btn.setIcon(QIcon(pixmap))
        self.delete_btn.setIconSize(QSize(30, 30))

        tooltip = textwrap.dedent(
            """
            Because your info is stored only on your machine,
            we have zero access to your sensitive credentials.
            You can permanently remove all stored information 
            at any time using this button.
        """
        ).strip()
        self.delete_btn.setToolTip(tooltip)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
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

        self.delete_btn.clicked.connect(self.delete_user_data)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_row.addWidget(self.save_btn, stretch=1)
        btn_row.addWidget(self.delete_btn)
        self.form_layout.addLayout(btn_row, 1)
        return self.form_layout

    def save_info(self):
        utorid = self.utorid_input.text()
        password = self.password_input.text()
        bypass = self.bypass_input.text()

        if utorid != "":
            self.utorid_item.set_checked(True)

        if password != "":
            self.password_item.set_checked(True)

        self.db_controller.save_credentials(utorid, password)

        if bypass != "":
            self.db_controller.save_bypass_codes([bypass])
            self.bypass_item.set_checked(True)

    def delete_user_data(self):
        self.db_controller.delete_user_data()

        self.utorid_item.set_checked(False)
        self.password_item.set_checked(False)
        self.bypass_item.set_checked(False)

        self.utorid_input.setText("")
        self.password_input.setText("")
        self.bypass_input.setText("")
