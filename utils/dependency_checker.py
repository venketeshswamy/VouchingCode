# ocr_tool_qt/utils/dependency_checker.py

import sys
import platform
import shutil
import os
from PyQt5.QtWidgets import QMessageBox

def get_missing_packages():
    """
    Checks for required Python packages and returns a list of missing ones.
    Does NOT attempt to install them.
    """
    # Corrected the check for Pillow to use 'PIL' as the import name.
    required_packages = {
        'pillow': 'PIL',  # Corrected from 'Pillow'
        'PyQt5': 'PyQt5',
        'pandas': 'pandas',
        'opencv-python-headless': 'cv2',
        'pdf2image': 'pdf2image',
        'clipboard': 'clipboard',
        'openpyxl': 'openpyxl',
        'pytesseract': 'pytesseract',
        'PyMuPDF': 'fitz',
        'psutil': 'psutil'
    }

    if platform.system() == "Windows":
        required_packages['pywin32'] = 'win32'
        required_packages['winrt-Windows.Media.Ocr'] = 'winrt'

    missing = []
    for pip_name, import_name in required_packages.items():
        try:
            # Special handling for packages with different import names
            if import_name == 'winrt':
                 __import__('winrt.windows.media.ocr')
            elif import_name == 'fitz':
                 __import__('fitz')
            elif import_name == 'PIL':
                 __import__('PIL')
            else:
                __import__(import_name)
        except ImportError:
            missing.append(pip_name)
    return missing

def check_external_dependencies(config):
    """
    Checks for non-Python dependencies and returns a list of warnings.
    """
    warnings = []
    try:
        # Check Tesseract
        tesseract_cmd = config.get('tesseract_cmd')
        if not tesseract_cmd or not shutil.which(tesseract_cmd):
            warnings.append(
                "- Tesseract OCR command path is not set or the executable was not found. Tesseract OCR will be unavailable."
            )

        # Check Poppler
        poppler_path = config.get('poppler_path')
        if not poppler_path or not os.path.isdir(poppler_path):
             warnings.append(
                "- Poppler path is not set or is not a valid directory. PDF rendering will fail."
            )
        elif not any(f.lower().startswith("pdftoppm") for f in os.listdir(poppler_path)):
             warnings.append(
                "- Poppler path does not seem to contain the required utilities (e.g., pdftoppm). PDF rendering will likely fail."
            )
    except Exception as e:
        warnings.append(f"An error occurred while checking external dependencies: {e}")
        
    return warnings
