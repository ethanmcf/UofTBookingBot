import sys
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QLinearGradient, QColor, QPolygonF

class Header(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120) # Adjust height as needed
        
        # 1. Layout for Logo and Buttons
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(50, 0, 50, 30) # Bottom margin leaves space for the slant
        
        # Logo
        self.logo = QLabel("🤖 Blue & Booked")
        self.logo.setStyleSheet("color: white; font-weight: bold; font-size: 18px; border: none;")
        
        # Nav Buttons
        self.setup_btn = QPushButton("Setup")
        self.run_btn = QPushButton("Run")
        
        # Button Styling
        btn_style = "color: white; font-weight: bold; font-size: 16px; border: none; background: none;"
        self.setup_btn.setStyleSheet(btn_style)
        self.run_btn.setStyleSheet(btn_style)
        
        self.layout.addWidget(self.logo)
        self.layout.addStretch()
        self.layout.addWidget(self.setup_btn)
        self.layout.addWidget(self.run_btn)

    def paintEvent(self, event):
        """Custom drawing of the gradient background and the slanted shape"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. Define the Shape (The Polygon)
        # We define a shape that dips down in the middle or tilts
        w = float(self.width())
        h = float(self.height())
        slant_height = 25.0 # How much it 'dips'
        
        path = QPainterPath()
        path.moveTo(0, 0)             # Top Left
        path.lineTo(w, 0)             # Top Right
        path.lineTo(w, h - slant_height) # Right edge (higher up)
        path.lineTo(w * 0.5, h)       # Bottom Middle (the tip of the slant)
        path.lineTo(0, h - slant_height) # Left edge (higher up)
        path.closeSubpath()

        # 2. Define the Gradient
        gradient = QLinearGradient(0, 0, w, 0) # Left to Right
        gradient.setColorAt(0, QColor("#8ab4f8")) # Light Blue
        gradient.setColorAt(1, QColor("#5472f1")) # Deeper Blue
        
        # 3. Draw it
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawPath(path)