import sys
from components.header import Header
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

def main():
    app = QApplication(sys.argv)
    
    main_win = QWidget()
    main_win.setStyleSheet("background-color: white;")
    main_win.resize(900, 300)
    
    v_layout = QVBoxLayout(main_win)
    v_layout.setContentsMargins(0,0,0,0)
    v_layout.addWidget(Header())
    v_layout.addStretch()
    
    main_win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()