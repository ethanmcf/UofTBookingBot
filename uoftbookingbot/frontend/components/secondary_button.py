from uoftbookingbot.frontend.theme import Colors
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class SecondaryButton(QFrame):
    def __init__(self, text, parent=None):
        super().__init__(parent)

        normal_start = Colors.LIGHT_BLUE
        normal_end = Colors.PRIMARY_BLUE
        self.setObjectName("OuterFrame")
        self.setContentsMargins(0, 0, 0, 0)

        # Outer gradient
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.setStyleSheet(
            f"""
            #OuterFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {normal_start}, stop:1 {normal_end});
                border-radius: 15px;
            }}
        """
        )

        # Inner button
        self.btn = QPushButton(text)
        self.btn.setCursor(self.btn.cursor().shape().PointingHandCursor)
        self.btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: white;
                border-radius: 13px; /* Slightly smaller to fit inside */
                border: none;
                color: {normal_start};
                font-weight: bold;
                font-size: 14px;
                padding: 8px 25px;
            }}
            QPushButton:hover {{
                background-color: #f9f9f9;
            }}
            QPushButton:pressed {{
                background-color: #f0f0f0;
            }}
        """
        )

        layout.addWidget(self.btn)
