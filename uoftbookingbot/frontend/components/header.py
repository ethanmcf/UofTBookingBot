from pathlib import Path
from uoftbookingbot.frontend.constants import ASSETS_DIR_PATH
from uoftbookingbot.frontend.theme import Colors
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPainterPath, QLinearGradient, QColor, QPixmap


class Header(QWidget):
    def __init__(self, paint_background=True, parent=None):
        super().__init__(parent)

        self.should_paint = paint_background

        self.setFixedHeight(160)

        # Layout for Logo and Buttons
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(115, 12, 115, 12)
        self.layout.setSpacing(16)

        # Logo
        self.logo_group = QWidget()
        self.logo_group.setStyleSheet("background: transparent")
        self.logo_layout = QHBoxLayout(self.logo_group)
        self.logo_layout.setContentsMargins(0, 0, 0, 0)
        self.logo_layout.setSpacing(4)

        self.logo_img = QLabel()
        logo_img_path = str(Path(ASSETS_DIR_PATH) / "robot-logo.svg")
        logo_img_pixmap = QPixmap(logo_img_path)
        scaled_icon = logo_img_pixmap.scaled(
            24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.logo_img.setPixmap(scaled_icon)
        self.logo_label = QLabel("Blue & Booked")
        self.logo_label.setStyleSheet(
            "background: none; font-weight: bold; font-size: 20px; border: none;"
        )
        self.logo_layout.addWidget(self.logo_img)
        self.logo_layout.addWidget(self.logo_label)
        self.logo_layout.addStretch()

        # Nav Buttons
        self.setup_btn = QPushButton("Setup")
        self.run_btn = QPushButton("Run")

        # Cursor hover proptery
        for btn in (self.setup_btn, self.run_btn):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFlat(True)

        btn_style = """
            QPushButton {
                color: white;
                font-weight: bold;
                font-size: 20px;
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                color: #cfe8ff;  /* lighter on hover */
            }
            QPushButton:pressed {
                color: #a8d2ff;  /* slightly darker on press */
            }
        """
        self.setup_btn.setStyleSheet(btn_style)
        self.run_btn.setStyleSheet(btn_style)

        self.layout.addWidget(self.logo_group)
        self.layout.addStretch()
        self.layout.addWidget(self.setup_btn)
        self.layout.addSpacing(32)
        self.layout.addWidget(self.run_btn)

    def paintEvent(self, event):
        """Custom drawing of the gradient background and the slanted shape"""
        if not self.should_paint:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        y1 = 20
        y2 = 34

        # Create the complex path
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(w, 0)
        path.lineTo(w, h - y1)
        path.lineTo(w * 0.75, h)
        path.lineTo(w * 0.5, h - y2)
        path.lineTo(w * 0.25, h - y1)
        path.lineTo(0, h - y1)
        path.closeSubpath()

        # Create gradient
        gradient = QLinearGradient(0, 0, w, 0)
        gradient.setColorAt(0, QColor(Colors.LIGHT_BLUE))
        gradient.setColorAt(1, QColor(Colors.PRIMARY_BLUE))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawPath(path)
