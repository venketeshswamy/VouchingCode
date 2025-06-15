# ocr_tool_qt/core/file_importer.py

import os
import shutil
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from utils.logger import log

class FileImporter(QObject):
    """
    Worker object that handles copying files to the import directory
    in a background thread to prevent GUI freezes.
    """
    file_imported = pyqtSignal(str)  # Emits the path of the newly imported file
    import_finished = pyqtSignal()   # Emits when all files are processed
    error_occurred = pyqtSignal(str) # Emits on a file copy error

    def __init__(self, original_file_paths, imports_dir):
        super().__init__()
        self.original_paths = original_file_paths
        self.imports_dir = imports_dir
        self.is_stopped = False

    @pyqtSlot()
    def stop(self):
        log.info("File import process stop requested.")
        self.is_stopped = True

    @pyqtSlot()
    def run(self):
        """Copies the files to the import directory."""
        log.info(f"Starting import for {len(self.original_paths)} files.")
        for original_path in self.original_paths:
            if self.is_stopped:
                break
            
            if not os.path.exists(original_path):
                log.error(f"Cannot import file, path does not exist: {original_path}")
                continue
            
            base_name = os.path.basename(original_path)
            local_copy_path = os.path.join(self.imports_dir, base_name)
            
            try:
                shutil.copy2(original_path, local_copy_path)
                log.info(f"Copied '{base_name}' to imports directory.")
                self.file_imported.emit(local_copy_path)
            except Exception as e:
                log.error(f"Could not copy '{base_name}' to imports directory: {e}")
                self.error_occurred.emit(f"Could not import '{base_name}': {e}")
        
        log.info("File import process finished.")
        self.import_finished.emit()

