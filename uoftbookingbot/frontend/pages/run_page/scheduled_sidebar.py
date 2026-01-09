from uoftbookingbot.frontend.components.secondary_button import SecondaryButton
from uoftbookingbot.frontend.constants import ASSETS_DIR_PATH
from uoftbookingbot.frontend.pages.run_page.scheduled_activity_card import ScheduledActivityCard
from uoftbookingbot.frontend.theme import Colors
from uoftbookingbot.scheduling.api import get_scheduler

import os
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget


class ScheduledSidebar(QWidget):
    """Sidebar component that manages the list of scheduled activities."""

    def __init__(self, on_unschedule_handler: callable):
        super().__init__()
        self.on_unschedule_handler = on_unschedule_handler
        self.setFixedWidth(300)
        self.main_layout = QVBoxLayout(self)

        # Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        sidebar_title = QLabel("Activities to Book")
        sidebar_title.setStyleSheet(
            f"color: {Colors.TEXT_MAIN}; font-size: 16px; font-weight: bold;"
        )

        self.refresh_btn = SecondaryButton("")
        self.refresh_btn.btn.setIcon(
            QIcon(os.path.join(ASSETS_DIR_PATH, "arrow-rotate-right-solid-full.svg"))
        )
        self.refresh_btn.btn.setIconSize(QSize(16, 16))
        self.refresh_btn.btn.setFixedSize(32, 32)
        self.refresh_btn.btn.clicked.connect(self.refresh_list)

        header_layout.addWidget(sidebar_title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        self.main_layout.addWidget(header_widget)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 10, 0)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.list_widget)
        self.main_layout.addWidget(self.scroll_area)

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
            no_items.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-style: italic;")
            self.list_layout.addWidget(no_items)
            return

        scheduled_items.sort(key=lambda x: x.run_at)
        for item in scheduled_items:
            card = ScheduledActivityCard(item, self.on_unschedule_handler)
            self.list_layout.addWidget(card)
