import sys
from PyQt6.QtWidgets import QApplication
from app.frontend.app import BookingApp 

def main():
    # Create the application instance
    qt_app = QApplication(sys.argv)
    
    # Create and show the main window
    window = BookingApp()
    window.show()

    # Run the event loop
    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()