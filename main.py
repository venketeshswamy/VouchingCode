# ocr_tool_qt/main.py

import sys
from PyQt5.QtWidgets import QApplication

# Import only the main window. All other modules will be managed by it.
from app.main_window import MainWindow
from utils.logger import log

def main():
    """
    The main entry point for the OCR Tool application.
    Initializes the QApplication and the main window. The window itself
    handles its own deferred initialization to prevent startup freezes.
    """
    log.info("--- Application Starting ---")
    
    app = QApplication(sys.argv)
    
    # Create the main window. The constructor will only perform the most
    # basic setup to ensure the window is shown quickly.
    main_win = MainWindow()
    main_win.show()
    
    # Start the Qt Event Loop.
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
