from PyQt6.QtWidgets import QWidget, QVBoxLayout


class BasePage(QWidget):
    HEADER_HEIGHT = 160

    def __init__(self, parent=None):
        super().__init__(parent)
        # Every page gets this main layout automatically and accounts for header
        self.page_layout = QVBoxLayout(self)
        self.page_layout.setContentsMargins(0, self.HEADER_HEIGHT, 0, 0)
        self.page_layout.setSpacing(0)
