from app.frontend.theme import Colors 
from app.frontend.pages.base_page import BasePage
from app.frontend.components.button import Button
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette, QPixmap
from PyQt6.QtCore import QMargins
from pyqt_animated_line_edit import AnimatedLineEdit

class SetupPage(BasePage):
    def __init__(self):
        super().__init__() 

        # Split layout (left: inputs, right: instructions)
        self.split_container = QHBoxLayout()
        self.split_container.setContentsMargins(0, 0, 0, 0)
        self.split_container.setSpacing(0)

        # Left column
        self.left_box = QWidget()

        self.left_col = QVBoxLayout(self.left_box)
        self.left_col.setContentsMargins(50, 70, 30, 0)
        self.left_col.setSpacing(17)

        # Create form
        self.createForm()

        # Right column (instructions)
        self.right_box = QWidget()
        self.right_col = QVBoxLayout(self.right_box)
        self.right_col.setContentsMargins(10, 0, 10, 0) 
        self.right_col.setSpacing(12)

        # Todo image
        self.createTodoImage()

        # Instructions
        instr_title = QLabel("Setup Instructions", self.right_box)
        instr_title.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-weight: bold; font-size: 16px;")
        instr_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_col.addWidget(instr_title)

        instr_1 = QLabel("Enter your UTORID", self.right_box)
        instr_2 = QLabel("Enter your PASSWORD", self.right_box)
        instr_3 = QLabel("Enter bypass code\n    • Login to https://bypass.utormfa.utoronto.ca/index.php\n    • Click ‘Generate Bypass Codes’ button\n    • Copy any one code into text field", self.right_box)
        for label in (instr_1, instr_2, instr_3):
            label.setStyleSheet(f"color: {Colors.TEXT_MAIN}; font-size: 16px;")
            label.setWordWrap(True)
            self.right_col.addWidget(label)
        self.right_col.addStretch()

        # Add columns to split layout
        self.split_container.addWidget(self.left_box, 1)
        self.split_container.addWidget(self.right_box, 1)

        # Add content to page and keep aligned to top
        self.page_layout.addLayout(self.split_container)
        self.page_layout.addStretch()

    def createTodoImage(self):
        self.image_label = QLabel(self.right_box)
        self.image_label.setStyleSheet("background: transparent;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        todo_png = QPixmap("app/frontend/assets/todo.png")
        todo_png_size = 300
        self.image_label.setPixmap(todo_png.scaled(todo_png_size, todo_png_size, Qt.AspectRatioMode.KeepAspectRatio,
                                                  Qt.TransformationMode.SmoothTransformation))
        self.right_col.addStretch()
        self.right_col.addWidget(self.image_label)

    def createForm(self):
        BORDER_RADIUS = 5
        WIDTH = 350
        HEIGHT = 50
        INNER_FONT_SIZE = 14
        OUTER_FONT_SIZE = 10
    
         # Utorid input
        self.username = AnimatedLineEdit('Your utorid', self.left_box)
        self.username.setFixedSize(WIDTH, HEIGHT)
        self.username.setPlaceholderColorOutside(QColor(Colors.TEXT_MAIN))
        self.username.setBorderRadius(BORDER_RADIUS)
        self.username.setPlaceholderFontSizeInner(INNER_FONT_SIZE)
        self.username.setPlaceholderFontSizeOuter(OUTER_FONT_SIZE)
        self.username.setPadding(QMargins(12, 0, 12, 0))
        self.username.setPlaceholderColorOutside(self.palette().color(QPalette.ColorRole.Highlight))
        self.left_col.addWidget(self.username)

        # Password input
        self.password = AnimatedLineEdit('Your password', self.left_box)
        self.password.setFixedSize(WIDTH, HEIGHT)
        self.password.setPlaceholderColorOutside(QColor(Colors.TEXT_MAIN))
        self.password.setBorderRadius(BORDER_RADIUS)
        self.password.setPlaceholderFontSizeInner(INNER_FONT_SIZE)
        self.password.setPlaceholderFontSizeOuter(OUTER_FONT_SIZE)
        self.password.setPadding(QMargins(12, 0, 12, 0))
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderColorOutside(self.palette().color(QPalette.ColorRole.Highlight))
        self.left_col.addWidget(self.password)

        # Bypass input
        self.bypass = AnimatedLineEdit('Current bypass code', self.left_box)
        self.bypass.setFixedSize(WIDTH, HEIGHT)
        self.bypass.setPlaceholderColorOutside(QColor(Colors.TEXT_MAIN))
        self.bypass.setBorderRadius(BORDER_RADIUS)
        self.bypass.setPlaceholderFontSizeInner(INNER_FONT_SIZE)
        self.bypass.setPlaceholderFontSizeOuter(OUTER_FONT_SIZE)
        self.bypass.setPadding(QMargins(12, 0, 12, 0))
        self.bypass.setPlaceholderColorOutside(self.palette().color(QPalette.ColorRole.Highlight))
        self.left_col.addWidget(self.bypass)
        self.left_col.addStretch()

        self.save_btn = Button("Save")
        self.left_col.addWidget(self.save_btn)
        self.left_col.addStretch()
