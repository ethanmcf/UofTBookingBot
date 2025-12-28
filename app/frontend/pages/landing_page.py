from app.frontend.theme import Colors 
from app.frontend.pages.base_page import BasePage
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QLinearGradient, QColor, QImage
from PyQt6.QtSvg import QSvgRenderer
import math

class LandingPage(BasePage):
    def __init__(self):
        super().__init__() 

        # Welcome title
        self.title_label = QLabel("Welcome to\nBlue & Booked")
        self.title_label.setStyleSheet("color: white; background: transparent; font-weight: bold; font-size: 40px")

        # Info subttile
        self.subtitle_label = QLabel("Automated recreation sport reservations for UofT students")
        self.subtitle_label.setStyleSheet("color: white; background: transparent; font-size: 14px")

        # Get started button
        self.start_btn = QPushButton("Get Started")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setFlat(True)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.3);  
                color: white;                               
                border-radius: 15px;                        
                padding: 8px 25px;                          
                font-weight: bold;
                font-size: 14px;
            }}
            
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.5);  
            }}
            
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.4);  
            }}
        """)

        # Create Left side layout
        content_container_style = "background: transparent"
        self.split_container = QHBoxLayout()
        self.split_container.setContentsMargins(0,0,0,0)

        self.left_box = QWidget()
        self.left_box.setStyleSheet(content_container_style)
        self.content = QVBoxLayout(self.left_box)
        self.content.setSpacing(35)
        self.content.setContentsMargins(115, 40, 0, 0)

        # Add widgets to layout
        self.content.addWidget(self.title_label)
        self.content.addWidget(self.subtitle_label)
        self.content.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content.addStretch()

        self.split_container.addWidget(self.left_box, 1)
        self.split_container.addStretch(1)

        # Add content to page and fix to top
        self.page_layout.addLayout(self.split_container)
        self.page_layout.addStretch()

    def paintEvent(self, event):
        """Custom drawing of the gradient background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = float(self.width())
        h = float(self.height())
        x = w * 0.15
        y1 = 120
        y2 = 300
        r = 70.0  

        # Corner point
        cx, cy = x, h - y1

        # Offset before corner 
        v1x, v1y = (x - w), (-y1)
        len1 = math.hypot(v1x, v1y) or 1.0
        p1x = cx - (v1x / len1) * min(r, len1 * 0.5)
        p1y = cy - (v1y / len1) * min(r, len1 * 0.5)

        # Offset after corner 
        v2x, v2y = (-x), (-(y2 - y1))
        len2 = math.hypot(v2x, v2y) or 1.0
        p2x = cx + (v2x / len2) * min(r, len2 * 0.5)
        p2y = cy + (v2y / len2) * min(r, len2 * 0.5)

        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(w, 0)
        path.lineTo(w, h)

        # Rounded corner 
        path.lineTo(p1x, p1y)
        path.quadTo(cx, cy, p2x, p2y)
        path.lineTo(0, h - y2)
        path.closeSubpath()

        # Create gradient
        gradient = QLinearGradient(0, 0, w, h)
        gradient.setColorAt(0, QColor(Colors.LIGHT_BLUE))
        gradient.setColorAt(1, QColor(Colors.PRIMARY_BLUE))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawPath(path)

        renderer = QSvgRenderer("app/frontend/assets/robot-full.svg")
        if renderer.isValid():
            # Create image buffer
            img_buffer = QImage(int(w), int(h), QImage.Format.Format_ARGB32_Premultiplied)
            img_buffer.fill(Qt.GlobalColor.transparent)
            
            buffer_painter = QPainter(img_buffer)
            svg_size = h * 1.2
            svg_rect = QRectF(svg_size - (svg_size * 0.5), h - (svg_size * 0.78), svg_size, svg_size)
            renderer.render(buffer_painter, svg_rect)
            
            # Create gradient and apply buffer
            buffer_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
            
            mask_gradient = QLinearGradient(w * 0.4, 0, w, h)
            mask_gradient.setColorAt(0.0, QColor(0, 0, 0, 0))  
            mask_gradient.setColorAt(1.0, QColor(0, 0, 0, 255)) 
            
            buffer_painter.fillRect(img_buffer.rect(), mask_gradient)
            buffer_painter.end()

            painter.setOpacity(0.4)
            painter.drawImage(0, 0, img_buffer)
            painter.setOpacity(1.0)