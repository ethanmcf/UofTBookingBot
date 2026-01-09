from uoftbookingbot.constants import ACTIVITIES
from uoftbookingbot.frontend.constants import ASSETS_DIR_PATH
from uoftbookingbot.frontend.theme import Colors
from uoftbookingbot.scheduling.api import get_scheduler
from uoftbookingbot.scheduling.scheduler import ScheduledActivity

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

    def __init__(self, scheduled_activity: ScheduledActivity, on_delete_callback: callable):
        super().__init__()
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid #edf2f7;
                border-radius: 8px;
            }}
            QFrame:hover {{
                border: 1px solid #cbd5e0;
            }}
        """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        # Text labels container
        text_container = QWidget()
        text_container.setStyleSheet("border: none; background: transparent;")
        text_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)

        # Activity Details extraction
        sport_name = next(
            (
                name
                for name, d in ACTIVITIES.items()
                if d.get("id", "") == scheduled_activity.activity.id
            ),
            "Unknown Sport",
        )
        session_dt = scheduled_activity.activity.get_session_start_datetime()

        # Labels
        title = QLabel(sport_name.upper())
        title.setStyleSheet(
            f"color: {Colors.TEXT_MAIN}; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;"
        )

        # Using a single style for subtext to create visual hierarchy
        subtext_style = "color: #718096; font-size: 11px; font-weight: 400;"

        session_info = QLabel(f"Session: {session_dt.strftime('%b %d, %I:%M %p')}")
        session_info.setStyleSheet(subtext_style)

        run_info = QLabel(f"Bot Run: {scheduled_activity.run_at.strftime('%b %d, %I:%M %p')}")
        run_info.setStyleSheet(subtext_style)

        text_layout.addWidget(title)
        text_layout.addWidget(session_info)
        text_layout.addWidget(run_info)

        layout.addWidget(text_container)

        # Delete Button
        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(QIcon(os.path.join(ASSETS_DIR_PATH, "trash-icon.png")))
        self.delete_btn.setIconSize(QSize(20, 20))
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setFixedSize(32, 32)
        self.delete_btn.setStyleSheet(
            """
            QPushButton { 
                border: none; 
                background: transparent; 
                border-radius: 4px;
            }
            QPushButton:hover { 
                background-color: #fff5f5; 
            }
        """
        )
        self.delete_btn.clicked.connect(lambda: on_delete_callback(scheduled_activity.activity))

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
