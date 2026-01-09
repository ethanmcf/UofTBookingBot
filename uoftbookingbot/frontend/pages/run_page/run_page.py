from uoftbookingbot.activity import Activity
from uoftbookingbot.frontend.pages.base_page import BasePage
from uoftbookingbot.frontend.components.primary_button import PrimaryButton
from uoftbookingbot.frontend.components.secondary_button import SecondaryButton
from uoftbookingbot.frontend.pages.run_page.scheduled_sidebar import ScheduledSidebar
from uoftbookingbot.frontend.pages.run_page.calendar import Calendar
from uoftbookingbot.frontend.pages.run_page.sport_dropdown import SportDropdown
from uoftbookingbot.frontend.pages.run_page.time_picker import TimePicker
from uoftbookingbot.frontend.pages.run_page.status_indicator import StatusIndicator
from uoftbookingbot.automation.logger import LogSignaler
from uoftbookingbot.automation.bot_worker import BotWorker
from uoftbookingbot.scheduling.api import get_scheduler
from uoftbookingbot.frontend.theme import Colors
from uoftbookingbot.constants import ACTIVITIES
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QMessageBox,
)


class RunPage(BasePage):
    """Page to run and schedule the bot."""

    start_run_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.ui_log_signaler = LogSignaler()
        self.ui_log_signaler.log_signal.connect(self.on_log_update)

        # Grid layout
        self.master_layout = QGridLayout()

        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setSpacing(40)
        self.content_layout.setContentsMargins(20, 50, 20, 20)

        # Left side (calendar)
        self.calendar = Calendar()
        self.calendar.setFixedWidth(400)
        self.content_layout.addWidget(self.calendar)

        # Center (variables)
        self.form_container = QWidget()
        self.form_container.setMinimumWidth(300)
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setSpacing(15)
        self.form_layout.addStretch()

        label_style = f"color: {Colors.TEXT_MAIN}"

        # Time Section
        time_label = QLabel("Start Time")
        time_label.setStyleSheet(label_style)
        self.form_layout.addWidget(time_label)
        self.time_picker = TimePicker()
        self.form_layout.addWidget(self.time_picker)

        # Sport Section
        sport_label = QLabel("Sport")
        sport_label.setStyleSheet(label_style)
        self.form_layout.addWidget(sport_label)
        self.sport_dropdown = SportDropdown(items=ACTIVITIES)
        self.form_layout.addWidget(self.sport_dropdown)

        # Action Buttons
        self.run_btn = PrimaryButton("Run")
        self.run_btn.btn.clicked.connect(self.on_run_click)

        self.schedule_btn = SecondaryButton("Schedule")
        self.schedule_btn.btn.clicked.connect(self.on_schedule_click)

        self.form_layout.addWidget(self.schedule_btn)
        self.form_layout.addWidget(self.run_btn)
        self.form_layout.addStretch()

        # Add to center of grid
        self.content_layout.addWidget(self.form_container)

        # Right side (Scheduled Activities Sidebar)
        self.sidebar = ScheduledSidebar(on_unschedule_handler=self.on_unschedule_click)
        self.sidebar.setFixedHeight(400)
        self.content_layout.addWidget(self.sidebar)

        self.master_layout.addWidget(self.content_widget, 1, 1)

        # Loading content
        self.status_indicator = StatusIndicator()
        self.master_layout.addWidget(
            self.status_indicator, 2, 1, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        # Center and add spacing
        self.master_layout.setRowStretch(0, 1)
        self.master_layout.setRowStretch(3, 1)
        self.master_layout.setColumnStretch(0, 1)
        self.master_layout.setColumnStretch(2, 1)
        self.page_layout.addLayout(self.master_layout)

        # Style message boxes
        self.setStyleSheet(
            f"""
            QMessageBox QLabel {{
                color: {Colors.TEXT_MAIN};
            }}
            QMessageBox QPushButton {{
                color: {Colors.TEXT_MAIN};
                background-color: #eeeeee;
                border: 1px solid #aaaaaa;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 70px;
            }}
            """
        )

        self.sidebar.refresh_list()

    def _get_form_data(self):
        """Extracts and formats current selection from UI components.

        Returns:
            tuple: (date_str, time_str, sport_str)
        """
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        selected_time = self.time_picker.time().toString("HH:mm")
        selected_sport = self.sport_dropdown.currentText()

        return (selected_date, selected_time, selected_sport)

    def on_run_click(self):
        """Shows logging text and signals to start bot"""
        selected_date, selected_time, selected_sport = self._get_form_data()
        if selected_sport not in ACTIVITIES:
            QMessageBox.warning(self, "Selection Error", "Please select a sport.")
            return

        self.status_indicator.start()

        activity_args = {
            "start_date": selected_date,
            "start_time": selected_time,
            "id": ACTIVITIES[selected_sport]["id"],
            "posting_offset": ACTIVITIES[selected_sport].get("posting_offset"),
        }

        self._start_booking_process(activity_args)

        self.run_btn.btn.setEnabled(False)

    def on_schedule_click(self):
        selected_date, selected_time, selected_sport = self._get_form_data()
        if selected_sport not in ACTIVITIES:
            QMessageBox.warning(self, "Selection Error", "Please select a sport.")
            return

        activity = Activity(
            id=ACTIVITIES[selected_sport]["id"],
            start_date=selected_date,
            start_time=selected_time,
            posting_offset=ACTIVITIES[selected_sport].get("posting_offset"),
        )
        scheduler = get_scheduler()
        try:
            scheduled_activity = scheduler.schedule_activity(activity)

            # Show success message
            session_start = activity.get_session_start_datetime()
            success_message = (
                f"Successfully scheduled the bot to book the following activity:"
                f"\n\n"
                f"{selected_sport} on {session_start.strftime('%A, %B %-d')} at"
                f"  {session_start.strftime('%I:%M %p %Z')}"
                f"\n\n"
                f"The bot will attempt to run on {scheduled_activity.run_at.strftime('%A, %B %-d')}"
                f" at {scheduled_activity.run_at.strftime('%I:%M %p %Z')}. Please ensure your"
                f" computer is on and connected to the internet at this time."
            )
            QMessageBox.information(self, "Success", success_message)
        except ValueError as e:
            QMessageBox.critical(
                self,
                "Scheduling Failed",
                str(e),
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Scheduling Failed",
                "An unexpected error occurred while scheduling the activity. Please try again.",
            )

        self.sidebar.refresh_list()

    def on_unschedule_click(self, activity: Activity):
        """Removes the activity from the scheduler and refreshes UI."""
        try:
            scheduler = get_scheduler()
            scheduler.unschedule_activity(activity)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Unscheduling Failed",
                "An unexpected error occurred while unscheduling the activity. Please try again.",
            )

        self.sidebar.refresh_list()

    def on_log_update(self, message):
        """Updates loading message when bot logs new info"""
        self.status_indicator.update_message(message)

    def on_execution_complete(self, success, message):
        """Handles visual update when bot sends failure or success"""

        self.status_indicator.set_result(success, message)
        self.run_btn.btn.setEnabled(True)  # Renable run button

    def _start_booking_process(self, activity_args: dict[str, str]):
        """Runs bot as a background thread so it doesn't block UI

        Args:
            activity_args (dict[str, str]): Arguments for the activity to book.
        """
        # Create Thread and Worker
        self.bot_thread = QThread()

        activity_to_book = Activity(
            id=activity_args["id"],
            start_date=activity_args["start_date"],
            start_time=activity_args["start_time"],
            posting_offset=activity_args["posting_offset"],
        )
        bot_args = {
            "activity": activity_to_book,
            "time_limit": 10,
            "codes_threshold": 3,
            "headless": True,
            "debug": False,
            "ui_signaler": self.ui_log_signaler,
        }

        self.worker = BotWorker(bot_args)
        self.worker.moveToThread(self.bot_thread)

        # Connect thread
        self.bot_thread.started.connect(self.worker.run)

        # Handle Completion
        self.worker.finished.connect(self.on_execution_complete)
        self.worker.finished.connect(self.bot_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        # Start bot
        self.bot_thread.start()

    def cleanup(self):
        thread = getattr(self, "bot_thread", None)
        worker = getattr(self, "worker", None)

        if worker:
            try:
                worker.log_updated.disconnect()
                worker.finished.disconnect()
            except:
                pass

            worker.stop()

        if thread and thread.isRunning():
            thread.quit()
