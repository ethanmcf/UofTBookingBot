from pathlib import Path
from uoftbookingbot.frontend.constants import ASSETS_DIR_PATH
from uoftbookingbot.frontend.theme import Colors
from uoftbookingbot.frontend.components.todo_item import TodoItem
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


class Instructions(QWidget):
    def __init__(self, utorid_filled, pass_filled, bypass_filled):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(70, 30, 10, 0)
        self.layout.setSpacing(22)

        # Image
        self.image_label = QLabel()
        self.image_label.setStyleSheet("background: transparent;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setPixmap(
            QPixmap(str(Path(ASSETS_DIR_PATH) / "todo.png")).scaled(
                300,
                300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.layout.addWidget(self.image_label)

        # Title
        self.title = QLabel("Setup Instructions")
        self.title.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-weight: bold; font-size: 16px;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

        # Todo Items
        self.utorid_item = TodoItem("Enter & save your utorid", utorid_filled)
        self.pass_item = TodoItem("Enter & save your password", pass_filled)
        self.bypass_item = TodoItem("Enter & save a bypass code", bypass_filled)

        # Bypass Sub-Instructions
        self.bypass_desc = QLabel(
            "1) Login to https://bypass.utormfa.utoronto.ca/\n\n"
            "2) Click ‘Generate Bypass Codes’\n\n"
            "3) Copy any one code into text field"
        )
        # self.bypass_desc.setTextFormat(Qt.TextFormat.RichText)
        self.bypass_desc.setOpenExternalLinks(True)
        self.bypass_desc.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        self.bypass_desc.setWordWrap(True)
        self.bypass_desc.setStyleSheet(
            f"color: {Colors.DARK_GRAY}; font-size: 12px; padding-left: 65px"
        )

        # Add to layout
        self.layout.addWidget(self.utorid_item)
        self.layout.addWidget(self.pass_item)
        self.layout.addWidget(self.bypass_item)
        self.layout.addWidget(self.bypass_desc)
        self.layout.addStretch()

    def update_status(self, utorid_ok, password_ok, bypass_code_ok):
        self.utorid_item.set_checked(utorid_ok)
        self.pass_item.set_checked(password_ok)
        self.bypass_item.set_checked(bypass_code_ok)
