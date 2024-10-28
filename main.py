# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Main entry point for the application."""
    # Initialize the Qt Application
    app = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Execute the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
