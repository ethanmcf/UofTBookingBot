from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt
from uoftbookingbot.frontend.theme import Colors


class StatusIndicator(QWidget):
    def __init__(self, is_checked=False, size=30):
        super().__init__()
        self.is_checked = is_checked
        self.setFixedSize(size, size)

    def set_status(self, checked: bool):
        """Update the state and trigger a redraw."""
        if self.is_checked != checked:
            self.is_checked = checked
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        rect = self.rect().adjusted(4, 4, -4, -4)
        pen_width = 3

        if self.is_checked:
            # Draw Green Ring
            green_color = QColor(Colors.LIGHT_GREEN)
            painter.setPen(
                QPen(green_color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            )
            painter.drawEllipse(rect)

            # Draw Checkmark
            w, h = self.width(), self.height()
            painter.drawLine(int(w * 0.35), int(h * 0.5), int(w * 0.45), int(h * 0.62))
            painter.drawLine(int(w * 0.45), int(h * 0.62), int(w * 0.65), int(h * 0.38))
        else:
            # Draw Gray Ring
            gray_color = QColor(Colors.LIGHT_GRAY)
            painter.setPen(QPen(gray_color, pen_width))
            painter.drawEllipse(rect)


class TodoItem(QWidget):
    """Combines the Indicator and a Label into one component."""

    def __init__(self, text="", is_checked=False):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.indicator = StatusIndicator(is_checked)
        self.label = QLabel(text)
        self.label.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-size: 16px;")

        layout.addWidget(self.indicator)
        layout.addWidget(self.label)
        layout.addStretch()

    def set_checked(self, checked: bool):
        self.indicator.set_status(checked)
