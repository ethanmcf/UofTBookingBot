from app.frontend.theme import Colors  
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QLinearGradient, QColor, QPolygonF

class Header(QWidget):
    def __init__(self, paint_background=True, parent=None):
        super().__init__(parent)

        self.should_paint = paint_background

        self.setFixedHeight(160) 
        
        # 1. Layout for Logo and Buttons
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(115, 12, 115, 12)
        self.layout.setSpacing(16)
        
        # Logo
        self.logo = QLabel("Blue & Booked")
        self.logo.setStyleSheet("background: none; font-weight: bold; font-size: 20px; border: none;")
        
        # Nav Buttons
        self.setup_btn = QPushButton("Setup")
        self.run_btn = QPushButton("Run")
        
        # Cursor hover proptery
        for btn in (self.setup_btn, self.run_btn):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFlat(True)

        btn_style =  """
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
        
        self.layout.addWidget(self.logo)
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