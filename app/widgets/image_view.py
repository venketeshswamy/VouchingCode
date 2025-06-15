# ocr_tool_qt/app/widgets/image_view.py

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QBrush

# Conditional import for PDF rendering
try:
    from pdf2image import convert_from_path, pdfinfo_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

class ImageView(QGraphicsView):
    """
    A QGraphicsView for displaying images/PDF pages and interacting with snips.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setResizeAnchor(self.AnchorUnderMouse)

        self.pixmap_item = None
        self.current_file_path = None
        self.current_page_num = 1
        self.total_pages = 0
        self.auto_zoom_enabled = False
        self.poppler_path = None # To be set from config

    def set_poppler_path(self, path):
        self.poppler_path = path

    def load_page(self, file_path, page_num=1):
        """Loads and displays a specific page of a file."""
        self.current_file_path = file_path
        self.current_page_num = page_num
        self.scene.clear()
        
        pixmap = None
        if file_path.lower().endswith('.pdf'):
            if not PDF2IMAGE_AVAILABLE:
                # Handle error display on the canvas
                return
            
            try:
                info = pdfinfo_from_path(file_path, poppler_path=self.poppler_path)
                self.total_pages = info.get('Pages', 0)
                
                # Render page to QImage
                images = convert_from_path(
                    file_path, 
                    dpi=150, 
                    first_page=page_num, 
                    last_page=page_num,
                    poppler_path=self.poppler_path
                )
                if images:
                    q_image = QImage(
                        images[0].tobytes("raw", "RGB"),
                        images[0].width,
                        images[0].height,
                        QImage.Format_RGB888
                    )
                    pixmap = QPixmap.fromImage(q_image)

            except Exception as e:
                print(f"Error loading PDF page: {e}")
                # Display an error message on the scene
                return
        else: # It's an image
            pixmap = QPixmap(file_path)
            self.total_pages = 1
        
        if pixmap:
            self.pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.pixmap_item)
            self.setSceneRect(self.pixmap_item.boundingRect())
            if self.auto_zoom_enabled:
                self.fit_in_view()
    
    def fit_in_view(self):
        """Zooms to fit the image to the view."""
        if self.pixmap_item:
            self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        """Handles mouse wheel zooming."""
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)
            
    # Placeholder methods for snip drawing
    def start_drawing_snip(self):
        pass
        
    def redraw_snips(self, templates):
        # This would clear existing QGraphicsRectItems and redraw them
        # based on the coordinates in the templates.
        pass

