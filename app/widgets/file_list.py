# ocr_tool_qt/app/widgets/file_list.py

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon
import os

try:
    import fitz # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class FileList(QListWidget):
    """
    A QListWidget to display imported files, with drag-and-drop support.
    """
    # Signal to notify the main window of dropped files.
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QListWidget.ListMode)
        self.setIconSize(QSize(64, 64))
        self.setSpacing(5)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        self.setDragDropMode(self.NoDragDrop) # We handle drops, not internal moves
        self.setSelectionMode(self.ExtendedSelection)

        self.file_paths = []

    def dragEnterEvent(self, event):
        """Accepts the drag event if it contains file URLs."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        """Ensures the cursor indicates a valid drop target."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        """Handles the dropping of files onto the widget."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            urls = event.mimeData().urls()
            filepaths = [url.toLocalFile() for url in urls]
            
            # Filter for supported file types to avoid errors
            supported_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.pdf')
            valid_files = [path for path in filepaths if path.lower().endswith(supported_exts)]
            
            if valid_files:
                # Emit a signal with the list of valid file paths
                self.files_dropped.emit(valid_files)
        else:
            super().dropEvent(event)

    def add_file(self, file_path):
        """Adds a file to the list if it's not already present."""
        if file_path in self.file_paths:
            return
            
        self.file_paths.append(file_path)
        base_name = os.path.basename(file_path)
        
        item = QListWidgetItem(base_name)
        item.setData(Qt.UserRole, file_path) # Store full path
        
        self.addItem(item)
        
    def get_selected_path(self):
        if self.currentItem():
            return self.currentItem().data(Qt.UserRole)
        return None
        
    def get_all_paths(self):
        return self.file_paths

    def clear_files(self):
        self.clear()
        self.file_paths.clear()
        
    def get_item_by_path(self, path):
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.UserRole) == path:
                return item
        return None

    def remove_selected_file(self):
        current_item = self.currentItem()
        if not current_item:
            return None
        
        path_to_remove = current_item.data(Qt.UserRole)
        self.file_paths.remove(path_to_remove)
        self.takeItem(self.row(current_item))
        return path_to_remove

