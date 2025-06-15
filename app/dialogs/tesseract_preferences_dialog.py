# ocr_tool_qt/app/dialogs/tesseract_preferences_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                             QDialogButtonBox, QLabel)

class TesseractPreferencesDialog(QDialog):
    """
    A dialog for configuring Tesseract OCR engine preferences (PSM and OEM).
    """
    def __init__(self, parent=None, current_config=None):
        super().__init__(parent)
        self.setWindowTitle("Tesseract Preferences")
        self.config = current_config if current_config else {}

        # Layout
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- Page Segmentation Mode (PSM) ---
        self.psm_combo = QComboBox()
        self.psm_options = {
            "3": "3: Fully automatic page segmentation (Default)",
            "1": "1: Automatic page segmentation with OSD",
            "4": "4: Assume a single column of text",
            "6": "6: Assume a single uniform block of text",
            "7": "7: Treat the image as a single text line",
            "8": "8: Treat the image as a single word",
            "11": "11: Sparse text. Find as much text as possible",
            "0": "0: Orientation and script detection (OSD) only",
        }
        self.psm_combo.addItems(self.psm_options.values())
        # Set current value
        current_psm = self.config.get("tesseract_psm", "3")
        for key, value in self.psm_options.items():
            if key == current_psm:
                self.psm_combo.setCurrentText(value)
                break
        form_layout.addRow("Page Segmentation Mode (PSM):", self.psm_combo)

        # --- OCR Engine Mode (OEM) ---
        self.oem_combo = QComboBox()
        self.oem_options = {
            "3": "3: Default, based on what is available",
            "1": "1: Neural nets LSTM engine only",
            "0": "0: Legacy engine only",
            "2": "2: Legacy + LSTM engines",
        }
        self.oem_combo.addItems(self.oem_options.values())
        # Set current value
        current_oem = self.config.get("tesseract_oem", "3")
        for key, value in self.oem_options.items():
            if key == current_oem:
                self.oem_combo.setCurrentText(value)
                break
        form_layout.addRow("OCR Engine Mode (OEM):", self.oem_combo)
        
        layout.addLayout(form_layout)

        # --- Dialog Buttons ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_selected_options(self):
        """Returns the selected PSM and OEM values."""
        selected_psm_text = self.psm_combo.currentText()
        selected_oem_text = self.oem_combo.currentText()
        
        # Find key from value
        selected_psm = next((key for key, value in self.psm_options.items() if value == selected_psm_text), "3")
        selected_oem = next((key for key, value in self.oem_options.items() if value == selected_oem_text), "3")
        
        return selected_psm, selected_oem

