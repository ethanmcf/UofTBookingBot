from pathlib import Path
from uoftbookingbot.frontend.constants import ASSETS_DIR_PATH
from uoftbookingbot.frontend.pages.base_page import BasePage
from uoftbookingbot.frontend.theme import Colors
from uoftbookingbot.frontend.components.primary_button import PrimaryButton
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette, QPixmap, QIcon
from PyQt6.QtCore import QMargins, QSize
from pyqt_animated_line_edit import AnimatedLineEdit
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
        self.left_col.setContentsMargins(50, 70, 30, 0)
        self.left_col.setSpacing(17)

        # Create form
        self.createForm()

        # Right column (instructions)
        self.right_box = QWidget()
        self.right_col = QVBoxLayout(self.right_box)
        self.right_col.setContentsMargins(70, 0, 10, 0)
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

        label_style = f"color: {Colors.TEXT_MAIN}; font-size: 16px;"
        utorid_label = QLabel("Enter your UTORID", self.right_box)
        utorid_label.setStyleSheet(label_style)
        self.right_col.addWidget(utorid_label)

        password_label = QLabel("Enter your PASSWORD", self.right_box)
        password_label.setStyleSheet(label_style)
        self.right_col.addWidget(password_label)

        # Create bypass info
        self.bypass_label = QLabel("Enter BYPASS CODE")
        self.bypass_label.setStyleSheet(label_style)

        self.bypass_row = QHBoxLayout()
        self.bypass_row.setSpacing(10)

        self.bypass_row.addWidget(self.bypass_label, stretch=0)

        # Create the Info image
        self.info_icon = QLabel()
        info_icon_path = str(Path(ASSETS_DIR_PATH) / "info-icon.png")
        info_pixmap = QPixmap(info_icon_path)
        self.info_icon.setPixmap(
            info_pixmap.scaled(
                30,
                30,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

        # Add the ToolTip to the icon
        tooltip = textwrap.dedent(
            """
            1) Login to https://bypass.utormfa.utoronto.ca/index.php
            2) Click ‘Generate Bypass Codes’ button
            3) Copy any one code into text field
        """
        ).strip()
        self.info_icon.setToolTip(tooltip)
        self.info_icon.setStyleSheet(
            """
            QToolTip {
                background-color: white;
                color: black;
                padding: 1px;
                border-radius: 4px;
                outline: none; 
            }
        """
        )
        self.info_icon.setCursor(Qt.CursorShape.PointingHandCursor)  # Feedback on hover

        self.bypass_row.addWidget(self.info_icon)
        self.right_col.addLayout(self.bypass_row)

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
        todo_img_path = str(Path(ASSETS_DIR_PATH) / "todo.png")
        todo_png = QPixmap(todo_img_path)
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

    def createForm(self):
        BORDER_RADIUS = 5
        WIDTH = 400
        HEIGHT = 50
        INNER_FONT_SIZE = 14
        OUTER_FONT_SIZE = 10

        # Utorid input
        self.username = AnimatedLineEdit("Your utorid", self.left_box)
        self.username.setFixedSize(WIDTH, HEIGHT)
        self.username.setPlaceholderColorOutside(QColor(Colors.TEXT_MAIN))
        self.username.setBorderRadius(BORDER_RADIUS)
        self.username.setPlaceholderFontSizeInner(INNER_FONT_SIZE)
        self.username.setPlaceholderFontSizeOuter(OUTER_FONT_SIZE)
        self.username.setPadding(QMargins(12, 0, 12, 0))
        self.username.setPlaceholderColorOutside(self.palette().color(QPalette.ColorRole.Highlight))
        self.left_col.addWidget(self.username)

        # Password input
        self.password = AnimatedLineEdit("Your password", self.left_box)
        self.password.setFixedSize(WIDTH, HEIGHT)
        self.password.setPlaceholderColorOutside(QColor(Colors.TEXT_MAIN))
        self.password.setBorderRadius(BORDER_RADIUS)
        self.password.setPlaceholderFontSizeInner(INNER_FONT_SIZE)
        self.password.setPlaceholderFontSizeOuter(OUTER_FONT_SIZE)
        self.password.setPadding(QMargins(12, 0, 12, 0))
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderColorOutside(self.palette().color(QPalette.ColorRole.Highlight))
        self.left_col.addWidget(self.password)

        # Bypass input
        self.bypass = AnimatedLineEdit("Current bypass code", self.left_box)
        self.bypass.setFixedSize(WIDTH, HEIGHT)
        self.bypass.setPlaceholderColorOutside(QColor(Colors.TEXT_MAIN))
        self.bypass.setBorderRadius(BORDER_RADIUS)
        self.bypass.setPlaceholderFontSizeInner(INNER_FONT_SIZE)
        self.bypass.setPlaceholderFontSizeOuter(OUTER_FONT_SIZE)
        self.bypass.setPadding(QMargins(12, 0, 12, 0))
        self.bypass.setPlaceholderColorOutside(self.palette().color(QPalette.ColorRole.Highlight))
        self.left_col.addWidget(self.bypass)
        self.left_col.addStretch()

        # Save button
        self.save_btn = PrimaryButton("Save")
        self.save_btn.btn.clicked.connect(self.save_info)

        # Delete button
        self.delete_btn = QPushButton()
        trash_icon_path = str(Path(ASSETS_DIR_PATH) / "trash-icon.png")
        pixmap = QPixmap(trash_icon_path)
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
        self.left_col.addLayout(btn_row, 1)
        self.left_col.addStretch()

    def save_info(self):
        utorid = self.username.text()
        password = self.password.text()
        bypass = self.bypass.text()

        self.db_controller.save_credentials(utorid, password)
        if bypass != "":
            self.db_controller.save_bypass_codes([bypass])

    def delete_user_data(self):
        print(self.db_controller.get_credentials())
        self.db_controller.delete_user_data()
        print(self.db_controller.get_credentials())
