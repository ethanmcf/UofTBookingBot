import sys
from app.frontend.pages.landing_page import LandingPage
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

def main():
    app = QApplication(sys.argv)
    
    main_win = QWidget()
    main_win.setStyleSheet("background-color: white;")
    main_win.setFixedWidth(1200)
    main_win.setFixedHeight(800) 
    
    v_layout = QVBoxLayout(main_win)
    v_layout.setContentsMargins(0,0,0,0)
    v_layout.addWidget(LandingPage(), 1)
    
    main_win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()