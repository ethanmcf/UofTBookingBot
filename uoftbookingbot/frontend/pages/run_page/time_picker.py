from pathlib import Path
from PyQt6.QtWidgets import QTimeEdit
from PyQt6.QtCore import QTime

from uoftbookingbot.frontend.constants import ASSETS_DIR_PATH


class TimePicker(QTimeEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumHeight(45)
        self.setTime(QTime.currentTime())

        # Styling
        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet(
            f"""
            QTimeEdit {{
                background-color: white;
                color: black;
                border: 1px solid #000000;
                border-radius: 12px;
                padding-left: 15px;
                font-size: 14px;
            }}

            QTimeEdit::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 25px;
                height: 22px;
                background: transparent;
                border-top-right-radius: 12px;
                padding-right: 5px;
            }}

            QTimeEdit::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 25px;
                height: 22px;
                background: transparent;
                border-bottom-right-radius: 12px;
                padding-right: 5px;
            }}

            /* Custom Arrow Assets */
            QTimeEdit::up-arrow {{
                image: url({str(Path(ASSETS_DIR_PATH) / 'chevron-up.svg')});
                width: 12px;
                height: 12px;
            }}
            
            QTimeEdit::down-arrow {{
                image: url({str(Path(ASSETS_DIR_PATH) / 'chevron-down.svg')});
                width: 12px;
                height: 12px;
            }}
        """
        )
