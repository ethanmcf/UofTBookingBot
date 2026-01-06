from PyQt6.QtWidgets import QComboBox, QAbstractItemView
from PyQt6.QtCore import Qt
from uoftbookingbot.frontend.theme import Colors


class SportDropdown(QComboBox):
    def __init__(self, items=None, placeholder="Select ...", parent=None):
        super().__init__(parent)

        self.setMinimumHeight(45)

        # Add placeholder and items
        if items:
            self.addItem(placeholder)
            self.addItems(items)

        self._apply_styles()

        self.view().window().setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.view().window().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def _apply_styles(self):
        self.setStyleSheet(
            f"""
            QComboBox {{
                background-color: white;
                color: {Colors.TEXT_MAIN};
                border: 1px solid #000000;
                border-radius: 12px;
                padding-left: 15px;
                font-size: 14px;
            }}

            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}

            QComboBox::down-arrow {{
                image: url(uoftbookingbot/frontend/assets/chevron-down.svg);
                width: 10px;
                height: 10px;
            }}

            QComboBox QAbstractItemView {{
                background-color: white;
                color: {Colors.TEXT_MAIN};
                border: 1px solid #000000;
                selection-background-color: {Colors.LIGHT_BLUE};
                selection-color: white;
                outline: none;
                padding: 5px;
            }}
        """
        )
