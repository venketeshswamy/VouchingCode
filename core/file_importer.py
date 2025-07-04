# ocr_tool_qt/core/file_importer.py

import os
import shutil
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from utils.logger import log

class FileImporter(QObject):
    """
    Worker object that handles copying files to the import directory
    in a background thread to prevent GUI freezes. This worker is
    designed to be persistent and reused for multiple import tasks.
    """
    # Signal to emit the path of each successfully imported file
    file_imported = pyqtSignal(str)
    
    # Signal to emit when the entire batch of files has been processed
    import_finished = pyqtSignal()
    
    # Signal to emit if an error occurs during a file copy operation
    error_occurred = pyqtSignal(str)

    def __init__(self, imports_dir):
        """
        Initializes the worker.
        Args:
            imports_dir (str): The target directory to copy files into.
        """
        super().__init__()
        self.original_paths = []
        self.imports_dir = imports_dir
        self.is_stopped = False

    def set_files_to_import(self, file_paths: list):
        """
        Sets the list of files for the next import run. This method is
        called from the main thread before starting the worker's task.
        """
        self.original_paths = file_paths

    @pyqtSlot()
    def stop(self):
        """Allows the import process to be stopped prematurely."""
        log.info("File import process stop requested.")
        self.is_stopped = True

    @pyqtSlot()
    def run(self):
        """
        The main task that runs in the background thread. It iterates through
        the file paths and copies them to the import directory.
        """
        # Reset the stop flag for the new run
        self.is_stopped = False
        
        log.info(f"Starting import for {len(self.original_paths)} files.")
        for original_path in self.original_paths:
            if self.is_stopped:
                log.warning("Import process was stopped by user.")
                break
            
            if not os.path.exists(original_path):
                log.error(f"Cannot import file, path does not exist: {original_path}")
                continue
            
            base_name = os.path.basename(original_path)
            local_copy_path = os.path.join(self.imports_dir, base_name)
            
            try:
                # Use copy2 to preserve metadata like modification time
                shutil.copy2(original_path, local_copy_path)
                log.info(f"Copied '{base_name}' to imports directory.")
                # Signal that one file has been successfully imported
                self.file_imported.emit(local_copy_path)
            except Exception as e:
                log.error(f"Could not copy '{base_name}' to imports directory: {e}", exc_info=True)
                self.error_occurred.emit(f"Could not import '{base_name}': {e}")
        
        log.info("File import process finished.")
        # Signal that the entire batch is finished
        self.import_finished.emit()
