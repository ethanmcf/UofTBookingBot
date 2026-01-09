from uoftbookingbot.constants import ACTIVITIES
from uoftbookingbot.frontend.constants import ASSETS_DIR_PATH
from uoftbookingbot.frontend.theme import Colors

import os
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ScheduledActivityCard(QFrame):
    """A card component representing a single scheduled activity."""

    def __init__(self, item, on_delete_callback):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 5px;
            }}
        """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Text labels container
        text_container = QWidget()
        text_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        # Activity Details
        sport_name = next(
            (name for name, d in ACTIVITIES.items() if d.get("id", "") == item.activity.id),
            "Unknown Sport",
        )
        session_dt = item.activity.get_session_start_datetime()
        label_style = f"color: {Colors.TEXT_MAIN}; font-size: 11px;"

        title = QLabel(f"<b>{sport_name}</b>")
        session_info = QLabel(f"Session: {session_dt.strftime('%b %d, %I:%M %p')}")
        run_info = QLabel(f"Bot Run: {item.run_at.strftime('%b %d, %I:%M %p')}")

        for lbl in [title, session_info, run_info]:
            lbl.setStyleSheet(label_style)
            text_layout.addWidget(lbl)

        layout.addWidget(text_container)
        layout.addStretch()

        # Delete Button
        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(QIcon(os.path.join(ASSETS_DIR_PATH, "trash-icon.png")))
        self.delete_btn.setIconSize(QSize(28, 28))
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(lambda: on_delete_callback(item.activity))

        layout.addWidget(self.delete_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
