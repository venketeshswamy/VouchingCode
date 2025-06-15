# ocr_tool_qt/core/initializer.py

from PyQt5.QtCore import QObject, pyqtSignal

from core.config_manager import ConfigManager
from core.template_manager import TemplateManager
from core.session_manager import SessionManager
from utils.logger import log

class AppInitializer(QObject):
    """
    A worker that handles the slow, blocking initialization tasks in a 
    background thread, preventing the GUI from freezing on startup.
    """
    # Signal to pass back the fully initialized manager objects
    initialization_finished = pyqtSignal(object, object, object)

    def run(self):
        """
        Executes the initialization sequence. This method is meant to be
        run in a separate QThread.
        """
        try:
            log.info("Background initialization started...")
            config = ConfigManager()
            templates = TemplateManager(config)
            session = SessionManager(config)
            log.info("Background initialization finished successfully.")
            self.initialization_finished.emit(config, templates, session)
        except Exception as e:
            log.error(f"A critical error occurred during background initialization: {e}", exc_info=True)
            # In a real app, you might emit an error signal here to show a fatal error dialog
            self.initialization_finished.emit(None, None, None)

