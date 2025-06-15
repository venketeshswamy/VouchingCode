# ocr_tool_qt/core/ocr_processor.py

import os
import re
import numpy as np
import cv2
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

# Conditional imports for OCR engines
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    
# More complex imports need careful handling
try:
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.globalization import Language
    # ... other winrt imports
    WINRT_AVAILABLE = True
except ImportError:
    WINRT_AVAILABLE = False

from utils.logger import log

class OcrProcessor(QObject):
    """
    Worker object that performs OCR processing in a separate thread.
    Communicates with the main thread via signals.
    """
    # Signals to communicate with the main GUI thread
    progress_updated = pyqtSignal(int, int)  # current, total
    processing_finished = pyqtSignal()
    result_ready = pyqtSignal(dict) # Emits one row of results at a time
    error_occurred = pyqtSignal(str)

    def __init__(self, config_manager, template_manager):
        super().__init__()
        self.config_manager = config_manager
        self.template_manager = template_manager
        self.is_stopped = False
        
        self.files_to_process = []
        self.templates_to_use = []
        self.page_selection = {}
        self.ocr_engine = "none"

    @pyqtSlot()
    def stop(self):
        """Stops the processing loop."""
        log.info("OCR processing stop requested.")
        self.is_stopped = True
        
    def _post_process_ocr_text(self, text):
        """Cleans up extracted OCR text."""
        return ' '.join(text.replace('\n', ' ').replace('\r', ' ').split())

    def _perform_tesseract_ocr(self, image, snip_config):
        """Performs OCR on an image crop using Tesseract."""
        if not TESSERACT_AVAILABLE:
            return "[Tesseract N/A]"
        try:
            psm = self.config_manager.get("tesseract_psm", "3")
            oem = self.config_manager.get("tesseract_oem", "3")
            lang = self.config_manager.get("tesseract_lang", "eng")
            custom_config = f'--psm {psm} --oem {oem}'

            if snip_config and snip_config.get('numeric_optimize', False):
                custom_config += ' -c tessedit_char_whitelist=0123456789.,$€£¥'

            text = pytesseract.image_to_string(image, lang=lang, config=custom_config)
            return self._post_process_ocr_text(text)
        except Exception as e:
            log.error(f"Tesseract OCR failed: {e}", exc_info=True)
            return "[Tesseract Error]"

    # Placeholder for Windows OCR logic
    def _perform_windows_ocr(self, image, snip_config):
        """Performs OCR using Windows RT OCR."""
        if not WINRT_AVAILABLE:
            return "[Windows OCR N/A]"
        # The full async implementation would be complex and is stubbed here
        # It requires running an async function in a sync context from a thread,
        # which can be tricky.
        log.warning("Windows OCR processing is a placeholder and not fully implemented in this refactor.")
        return "[Windows OCR Not Implemented]"

    def _process_page_with_visual_snips(self, image_path, page_num):
        """Processes a single page/image using visual snip templates."""
        # This function would contain the logic from the original script's
        # _process_single_image_page_with_visual_snips, adapted for this class structure.
        # It involves loading the image, finding template matches with OpenCV,
        # cropping, and running the selected OCR engine.
        pass # Placeholder for the detailed implementation

    def _process_page_with_text_parser(self, pdf_path, page_num):
        """Processes a single PDF page using a text parser template."""
        if not PYMUPDF_AVAILABLE:
            self.error_occurred.emit("PyMuPDF is not available for text parsing.")
            return

        try:
            doc = fitz.open(pdf_path)
            if page_num > doc.page_count:
                return

            page = doc.load_page(page_num - 1)
            full_text = page.get_text("text")
            doc.close()

            # Assuming the first template is the one we want to use
            parser_template = self.templates_to_use[0]
            results = self.template_manager.apply_text_parser(parser_template['name'], full_text)
            
            row_data = {'File': os.path.basename(pdf_path), 'Page': page_num}
            row_data.update(results)
            self.result_ready.emit(row_data)

        except Exception as e:
            log.error(f"Failed to parse PDF {pdf_path} page {page_num}: {e}", exc_info=True)
            self.error_occurred.emit(f"Error processing {os.path.basename(pdf_path)}: {e}")

    @pyqtSlot()
    def run(self):
        """The main processing loop."""
        self.is_stopped = False
        total_files = len(self.files_to_process)
        log.info(f"Starting OCR processing for {total_files} files.")
        
        # In a real implementation, a more complex loop would be needed to handle
        # page ranges and count total pages for the progress bar.
        # This is a simplified version for demonstration.
        
        for i, filepath in enumerate(self.files_to_process):
            if self.is_stopped:
                log.info("Processing was stopped by user.")
                break

            log.info(f"Processing file: {filepath}")
            self.progress_updated.emit(i + 1, total_files)
            
            # Simple logic: if a text parser is defined, use it for PDFs.
            # Otherwise, use visual snips.
            is_pdf = filepath.lower().endswith('.pdf')
            has_text_parser = any(t.get('type') == 'text_parser' for t in self.templates_to_use)

            if is_pdf and has_text_parser:
                # Here you would loop through the selected page numbers
                self._process_page_with_text_parser(filepath, 1) # Simplified to page 1
            else:
                # Process with visual snips
                self._process_page_with_visual_snips(filepath, 1) # Simplified
                
        log.info("OCR processing finished.")
        self.processing_finished.emit()

