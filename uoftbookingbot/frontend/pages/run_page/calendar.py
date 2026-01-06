from uoftbookingbot.frontend.theme import Colors
from PyQt6.QtWidgets import QCalendarWidget
from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtCore import Qt


class Calendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._apply_styles()
        self._apply_formatting()

        # Hides week numbers on left
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

    def _apply_styles(self):
        self.setStyleSheet(
            f"""
            /* The main calendar area */
            QCalendarWidget QWidget {{
                background-color: {Colors.LIGHT_BLUE};
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
                selection-background-color: {Colors.LIGHT_BLUE};
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
                selection-background-color: {Colors.LIGHT_BLUE};
            }}

            /* Remove the 'V' arrow from Month/Year buttons */
            QCalendarWidget QToolButton::menu-indicator {{
                image: none;
                width: 0px;
            }}

            /* Shrink the navigation arrows */
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {{
                width: 10px;    
                height: 10px;
                padding: 12px;
            }}
        """
        )

    def _apply_formatting(self):
        # Header format
        header_fmt = self.headerTextFormat()
        header_fmt.setForeground(QColor("white"))

        bg_color = QColor(Colors.LIGHT_BLUE)
        bg_color.setAlphaF(0.5)
        header_fmt.setBackground(bg_color)
        self.setHeaderTextFormat(header_fmt)

        # Weekend format
        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor("black"))
        self.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend_format)
        self.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend_format)
