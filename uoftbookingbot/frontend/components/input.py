from uoftbookingbot.frontend.theme import Colors
from PyQt6.QtWidgets import QWidget, QLineEdit, QLabel, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QPoint


class Input(QWidget):

    def __init__(self, label_text="", is_password=False, width=490):
        super().__init__()
        self.setMinimumHeight(65)
        self.label_text = label_text
        self.is_password = is_password

        # Input field
        self.input_field = QLineEdit(self)
        self.input_field.setGeometry(0, 10, width, 45)
        self.input_field.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {Colors.TEXT_MAIN};
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                color: {Colors.TEXT_MAIN};
                background-color: transparent;
            }}
            QLineEdit:focus {{
                border: 2px solid #000000;
            }}
        """
        )

        # Label
        self.title_label = QLabel(label_text, self)
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.title_label.setStyleSheet(
            f"color: {Colors.DARK_GRAY}; font-size: 15px; background-color: transparent; padding: 0 4px;"
        )

        # Initial label position
        self.title_label.move(12, 22)

        # Animation
        self.anim_group = QPropertyAnimation(self.title_label, b"pos")
        self.anim_group.setDuration(150)
        self.anim_group.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Connect events
        self.input_field.focusInEvent = self._on_focus_in
        self.input_field.focusOutEvent = self._on_focus_out
        self.input_field.textChanged.connect(self._check_text)
        if self.is_password:
            self.input_field.setEchoMode(QLineEdit.EchoMode.Password)

    def _on_focus_in(self, event):
        self._float_label(True)
        QLineEdit.focusInEvent(self.input_field, event)

    def _on_focus_out(self, event):
        if not self.input_field.text():
            self._float_label(False)
        QLineEdit.focusOutEvent(self.input_field, event)

    def _check_text(self, text):
        if text:
            self._float_label(True)

    def _float_label(self, up):
        # Target positions
        up_pos = QPoint(15, 2)
        down_pos = QPoint(12, 22)

        if up and self.title_label.pos() != up_pos:
            self.title_label.setStyleSheet("color: #000; font-size: 12px; background-color: white;")
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.anim_group.setEndValue(up_pos)
            self.anim_group.start()
        elif not up and self.title_label.pos() != down_pos:
            self.title_label.setStyleSheet(
                f"color: {Colors.DARK_GRAY}; font-size: 15px; background-color: transparent;"
            )
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.anim_group.setEndValue(down_pos)
            self.anim_group.start()

    # Accessor methods
    def text(self):
        return self.input_field.text()

    def setText(self, text):
        self.input_field.setText(text)
        self._check_text(text)
