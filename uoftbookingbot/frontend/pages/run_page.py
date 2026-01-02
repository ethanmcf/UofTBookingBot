import os
from uoftbookingbot.activity import Activity
from uoftbookingbot.constants import LOG_DIR_PATH
from uoftbookingbot.frontend.pages.base_page import BasePage
from uoftbookingbot.frontend.components.primary_button import PrimaryButton
from uoftbookingbot.frontend.components.secondary_button import SecondaryButton
from uoftbookingbot.frontend.theme import Colors
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QCalendarWidget,
    QTimeEdit,
    QComboBox,
    QLabel,
)
from PyQt6 import QtGui
from PyQt6.QtCore import QTime, Qt, pyqtSignal
from PyQt6.QtGui import QTextCharFormat, QColor, QMovie, QPixmap

from uoftbookingbot.schedulers import get_scheduler


class RunPage(BasePage):
    start_run_signal = pyqtSignal(dict)
    activities: dict[str, dict[str, str]]

    def __init__(self, activities: dict[str, dict[str, str]]):
        """Page to run and schedule the bot.

        Args:
            activities (dict[str, dict[str, str]]): Mapping of activity names to their details.
        """
        super().__init__()
        self.activities = activities

        # Grid layout
        self.master_layout = QGridLayout()

        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setSpacing(40)
        self.content_layout.setContentsMargins(20, 50, 20, 20)

        # Left side (calendar)
        self.createCalendar()
        self.calendar.setFixedWidth(350)
        self.content_layout.addWidget(self.calendar)

        # Right side (variables)
        self.form_container = QWidget()
        self.form_container.setMinimumWidth(200)
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setSpacing(15)

        label_style = f"color: {Colors.TEXT_MAIN}"

        # Time Sectection
        time_label = QLabel("Time")
        time_label.setStyleSheet(label_style)
        self.form_layout.addWidget(time_label)
        self.createTimePicker()
        self.form_layout.addWidget(self.time_picker)

        # Sport Section
        sport_label = QLabel("Sport")
        sport_label.setStyleSheet(label_style)
        self.form_layout.addWidget(sport_label)
        self.createDropDown()
        self.form_layout.addWidget(self.sport_dropdown)

        # Action Buttons
        self.form_layout.addStretch()
        self.run_btn = PrimaryButton("Run")
        self.run_btn.btn.clicked.connect(self.on_run_click)

        self.schedule_btn = SecondaryButton("Schedule")
        self.schedule_btn.btn.clicked.connect(self.on_schedule_click)

        self.form_layout.addWidget(self.schedule_btn)
        self.form_layout.addWidget(self.run_btn)

        # Add to center of grid
        self.content_layout.addWidget(self.form_container)
        self.master_layout.addWidget(self.content_widget, 1, 1)

        # Loading content
        loading_view = self.createLoading()
        self.master_layout.addWidget(loading_view, 2, 1, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Center and add spacing
        self.master_layout.setRowStretch(0, 1)
        self.master_layout.setRowStretch(1, 0)
        self.master_layout.setRowStretch(2, 0)
        self.master_layout.setRowStretch(3, 1)
        self.master_layout.setColumnStretch(0, 1)
        self.master_layout.setColumnStretch(2, 1)
        self.page_layout.addLayout(self.master_layout)

    # --- Component functions ---
    def createLoading(self):
        # The container widget
        self.loading_container = QWidget()
        self.loading_container.setStyleSheet("background: transparent;")
        self.loading_container.setFixedHeight(80)
        sp_retain = self.loading_container.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.loading_container.setSizePolicy(sp_retain)
        layout = QVBoxLayout(self.loading_container)

        # Loading animation
        self.loading_visual = QLabel()
        self.loading_visual.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie = QMovie("uoftbookingbot/frontend/assets/loading.gif")
        self.loading_visual.setMovie(self.movie)

        # Log loading label
        self.loading_label = QLabel("Running...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: #64748b; font-size: 12px; border: none;")

        layout.addWidget(self.loading_label)
        layout.addWidget(self.loading_visual)

        self.movie.start()
        self.loading_container.hide()
        return self.loading_container

    def createCalendar(self):
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet(
            f"""
            /* The main calendar area */
            QCalendarWidget QWidget {{
                background-color: {Colors.LIGHT_BLUE };
                color: white;
            }}

            /* Navigation bar at the top */
            QCalendarWidget QToolButton {{
                color: white;
                background-color: transparent;
                icon-size: 30px;
                border: none;

            }}

            /* The grid of days */
            QCalendarWidget QAbstractItemView:enabled {{
                background-color: white; 
                color: #202733;         
                selection-background-color: {Colors.LIGHT_BLUE };
                selection-color: white;
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: #d3d3d3; 
            }}

            /* Dropdown menus for Month/Year */
            QCalendarWidget QMenu {{
                background-color: white;
                color: black;
            }}

            /* The year selector */
            QCalendarWidget QSpinBox {{
                background-color: white;
                color: black;
                selection-background-color: {Colors.LIGHT_BLUE };
            }}
            /* Remove the 'V' arrow (menu indicator) from the Month/Year buttons */
            QCalendarWidget QToolButton::menu-indicator {{
                image: none;
                width: 0px;
            }}

            /* 2. Shrink the actual white arrow image */
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {{
                width: 10px;    
                height: 10px;
                padding: 12px;
            }}
        """
        )

        # Header format
        header_fmt = self.calendar.headerTextFormat()
        header_fmt.setForeground(QtGui.QColor("white"))
        background_color = QtGui.QColor(Colors.LIGHT_BLUE)
        background_color.setAlphaF(0.5)
        header_fmt.setBackground(background_color)
        self.calendar.setHeaderTextFormat(header_fmt)

        # Weekend format
        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor("black"))
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend_format)

        # Hides week numbers on left
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        return self.calendar

    def createTimePicker(self):
        self.time_picker = QTimeEdit()
        self.time_picker.setMinimumHeight(45)
        self.time_picker.setTime(QTime.currentTime())
        self.time_picker.setStyleSheet(
            f"""
            QTimeEdit {{
                background-color: white;
                color: black;
                border: 1px solid #000000;
                border-radius: 12px;
                padding-left: 15px;
            }}

            QTimeEdit::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 25px;
                height: 22px;
                background: transparent;
                border-top-right-radius: 22px;
            }}

            QTimeEdit::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 25px;
                height: 22px;
                background: transparent;
                border-bottom-right-radius: 22px;
            }}

            /* Use images for arrows */
            QTimeEdit::up-arrow {{
                image: url(uoftbookingbot/frontend/assets/chevron-up.svg);
                width: 12px;
                height: 12px;
            }}
            QTimeEdit::down-arrow {{
                image: url(uoftbookingbot/frontend/assets/chevron-down.svg);
                width: 12px;
                height: 12px;
                left: 0px;
            }}   
        """
        )

    def createDropDown(self):
        self.sport_dropdown = QComboBox()
        self.sport_dropdown.setMinimumHeight(45)
        sports = ["Select ..."] + list(self.activities.keys())
        self.sport_dropdown.addItems(sports)

        self.sport_dropdown.setStyleSheet(
            f"""
            QComboBox {{
                background-color: white;
                color: {Colors.TEXT_MAIN};
                border: 1px solid #000000;
                border-radius: 12px;
                padding-left: 15px;
                font-size: 14px;
            }}

            /* The 'drop-down' is the container for the arrow */
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}

            /* Use the border-triangle trick for the down arrow to avoid image issues */
            QComboBox::down-arrow {{
                image: url(uoftbookingbot/frontend/assets/chevron-down.svg);
                width: 10px;
                height: 10px;
            }}

            /* Styling the list that pops up */
            QComboBox QAbstractItemView {{
                background-color: white;
                color: {Colors.TEXT_MAIN};
                border: 1px solid #000000;
                selection-background-color: {Colors.LIGHT_BLUE};
                selection-color: white;
                outline: none;
            }}
        """
        )

    def _get_form_data(self):
        """Extracts and formats current selection from UI components.

        Returns:
            tuple: (date_str, time_str, sport_str)
        """
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        selected_time = self.time_picker.time().toString("HH:mm")
        selected_sport = self.sport_dropdown.currentText()

        return (selected_date, selected_time, selected_sport)

    # --- Bot functions ---
    def on_run_click(self):
        """Shows logging text and signals to start bot"""
        selected_date, selected_time, selected_sport = self._get_form_data()
        if selected_sport not in self.activities:
            return

        self.loading_container.show()
        self.movie = QMovie("uoftbookingbot/frontend/assets/loading.gif")
        self.loading_visual.setMovie(self.movie)
        self.movie.start()

        activity_args = {
            "start_date": selected_date,
            "start_time": selected_time,
            "id": self.activities[selected_sport]["id"],
            "posting_offset": self.activities[selected_sport].get("posting_offset"),
        }
        self.start_run_signal.emit(activity_args)

        self.run_btn.btn.setEnabled(False)

    def on_schedule_click(self):
        selected_date, selected_time, selected_sport = self._get_form_data()
        if selected_sport not in self.activities:
            return

        error_log_path = os.path.join(LOG_DIR_PATH, "error.log")
        output_log_path = os.path.join(LOG_DIR_PATH, "info.log")
        scheduler = get_scheduler(error_log_path, output_log_path)

        activity = Activity(
            id=self.activities[selected_sport]["id"],
            start_date=selected_date,
            start_time=selected_time,
            posting_offset=self.activities[selected_sport].get("posting_offset"),
        )
        try:
            scheduler.schedule_activity(activity)
        except Exception as e:
            # TODO: handle scheduling errors
            pass

    def on_log_update(self, message):
        """Updates loading message when bot logs new info"""
        self.loading_label.setText(message)

    def on_execution_complete(self, success, message):
        """Handles visual update when bot sends failure or success"""

        # Stop loading spinner
        self.movie.stop()
        self.loading_visual.setMovie(None)

        # Paths for success/failure icons
        self.success_icon_path = "uoftbookingbot/frontend/assets/success-icon.png"
        self.error_icon_path = "uoftbookingbot/frontend/assets/error-icon.png"

        icon_path = self.success_icon_path if success else self.error_icon_path
        pix = QPixmap(icon_path)
        pix = pix.scaled(
            32,
            32,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.loading_visual.setPixmap(pix)
        self.loading_label.setText(message)

        # Renable run button
        self.run_btn.btn.setEnabled(True)
