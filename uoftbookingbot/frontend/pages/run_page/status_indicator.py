from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtCore import Qt

from uoftbookingbot.frontend.constants import ASSETS_DIR_PATH


class StatusIndicator(QWidget):
    def __init__(self, text="Running...", parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.setFixedHeight(80)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        # Retain space
        sp_retain = self.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.setSizePolicy(sp_retain)

        # Loading Label
        self.loading_label = QLabel(text)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: #64748b; font-size: 12px; border: none;")

        # Loading Animation
        self.loading_visual = QLabel()
        self.loading_visual.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Assembly
        self.layout.addWidget(self.loading_label)
        self.layout.addWidget(self.loading_visual)

        # Start hidden by default
        self.hide()

    def start(self):
        """Displays the indicator and starts the animation."""
        self.show()
        self.movie = QMovie(str(Path(ASSETS_DIR_PATH) / "loading.gif"))
        self.loading_visual.setMovie(self.movie)
        self.movie.start()

    def update_message(self, message):
        """Updates the label text during execution."""
        self.loading_label.setText(message)

    def set_result(self, success, message):
        """Stops animation and displays a success or error icon."""
        self.movie.stop()
        self.loading_visual.setMovie(None)

        success_icon_path = str(Path(ASSETS_DIR_PATH) / "success-icon.png")

        error_icon_path = str(Path(ASSETS_DIR_PATH) / "error-icon.png")
        icon_path = success_icon_path if success else error_icon_path
        pix = QPixmap(icon_path)
        pix = pix.scaled(
            32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )

        self.loading_visual.setPixmap(pix)
        self.loading_label.setText(message)
