from uoftbookingbot.constants import ACTIVITIES
from uoftbookingbot.frontend.constants import ASSETS_DIR_PATH
from uoftbookingbot.frontend.theme import Colors
from uoftbookingbot.scheduling.api import get_scheduler

import os
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QPushButton,
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
        self.delete_btn.setStyleSheet("border: none; background: transparent;")
        self.delete_btn.clicked.connect(lambda: on_delete_callback(item.activity))

        layout.addWidget(self.delete_btn, alignment=Qt.AlignmentFlag.AlignVCenter)


class ScheduledSidebar(QWidget):
    """Sidebar component that manages the list of scheduled activities."""

    def __init__(self, on_unschedule_handler: callable):
        super().__init__()
        self.on_unschedule_handler = on_unschedule_handler
        self.setFixedWidth(300)

        # Main layout for the widget itself
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)

        # Create the Card Container
        self.container_frame = QFrame()
        self.container_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 12px;
            }}
        """
        )

        # Internal layout for the contents of the card
        self.main_layout = QVBoxLayout(self.container_frame)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)

        # Header
        header_widget = QWidget()
        header_widget.setStyleSheet(
            "border: none; background: transparent;"
        )  # Reset border for children
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        sidebar_title = QLabel("Scheduled Activities")
        sidebar_title.setStyleSheet(
            f"color: {Colors.TEXT_MAIN}; font-size: 16px; font-weight: bold; border: none;"
        )

        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(
            QIcon(os.path.join(ASSETS_DIR_PATH, "arrow-rotate-right-solid-full.svg"))
        )
        self.refresh_btn.setIconSize(QSize(16, 16))
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh_list)

        header_layout.addWidget(sidebar_title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        self.main_layout.addWidget(header_widget)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        # Ensure scroll area doesn't inherit the frame border
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 10, 0)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.list_widget)
        self.main_layout.addWidget(self.scroll_area)

        # 3. Add the styled container to the outer layout
        self.outer_layout.addWidget(self.container_frame)

    def refresh_list(self):
        """Clears and repopulates the scheduled activity list."""

        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        scheduler = get_scheduler()
        scheduled_items = scheduler.get_scheduled_activities()

        if not scheduled_items:
            no_items = QLabel("No activities scheduled for booking.")
            no_items.setStyleSheet(
                f"color: {Colors.TEXT_MAIN};"
                f"font-style: italic;"
                f"border: none;"
                f"background: transparent;"
            )
            self.list_layout.addWidget(no_items)
            return

        scheduled_items.sort(key=lambda x: x.run_at)
        for item in scheduled_items:
            card = ScheduledActivityCard(item, self.on_unschedule_handler)
            self.list_layout.addWidget(card)
