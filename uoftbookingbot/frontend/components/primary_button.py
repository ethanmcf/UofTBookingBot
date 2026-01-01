from uoftbookingbot.frontend.theme import Colors
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class PrimaryButton(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)

        self.btn = QPushButton(text, self)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setFlat(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.btn)

        normal_start = Colors.LIGHT_BLUE
        normal_end = Colors.PRIMARY_BLUE
        hover_start = QColor(normal_start).lighter(115).name()
        hover_end = QColor(normal_end).lighter(115).name()
        press_start = QColor(normal_start).darker(115).name()
        press_end = QColor(normal_end).darker(115).name()

        self.btn.setStyleSheet(
            f"""
            QPushButton {{
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 25px;
                font-weight: bold;
                font-size: 14px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {normal_start}, stop:1 {normal_end});
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {hover_start}, stop:1 {hover_end});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {press_start}, stop:1 {press_end});
            }}
        """
        )
