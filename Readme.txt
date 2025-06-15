# OCR Tool - PyQt5 Edition

This application provides a graphical user interface for performing Optical Character Recognition (OCR) on images and PDFs, defining templates, and exporting results. It is a refactored and modularized version of an original `tkinter`-based script.

## Features

- Import individual files or folders of images/PDFs.
- Multiple OCR engine support (Tesseract, Windows OCR, PyMuPDF native text).
- Define visual "snip" templates by drawing on an image.
- Define powerful "text parser" templates using regular expressions.
- A visual regex builder to test patterns in real-time.
- Batch process multiple files and pages.
- Save and load entire sessions (files, templates, results).
- Export results to Excel or CSV.

## Setup and Installation

### 1. Prerequisites (External Dependencies)

Before running the application, you must have the following external programs installed and available in your system's PATH or configured in `config.json`.

- **Tesseract OCR**:
  - **Windows**: Download the installer from the official [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) page. During installation, make sure to add it to your system PATH.
  - **Linux**: `sudo apt-get install tesseract-ocr`
  - **macOS**: `brew install tesseract`

- **Poppler**: (Required for converting PDF pages to images)
  - **Windows**: Download the latest binary from the [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) page. Unzip it to a location like `C:\poppler` and add the `bin` subdirectory to your system's PATH.
  - **Linux**: `sudo apt-get install poppler-utils`
  - **macOS**: `brew install poppler`

### 2. Python Dependencies

This project uses Python 3. The required Python packages are listed in `requirements.txt`.

Clone the repository and install the packages using pip:
```bash
git clone <repository_url>
cd ocr_tool_qt
pip install -r requirements.txt

(A requirements.txt would be generated for a full project, listing packages like PyQt5, pandas, etc.)

3. Configuration
After the first run, a config.json file will be created. You must edit this file to provide the correct paths to the Tesseract executable and the Poppler bin directory if they are not in your system's PATH.

Example config.json on Windows:

{
    "poppler_path": "C:\\path\\to\\poppler-22.04.0\\Library\\bin",
    "tesseract_cmd": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
    ...
}

How to Run
Once the setup is complete, run the application from the project's root directory:

python main.py

Project Structure
main.py: Application entry point.

app/: Contains all PyQt5 GUI code (windows, widgets, dialogs).

core/: Contains all backend business logic (OCR, session management), with no dependency on the GUI.

utils/: Helper modules for logging and dependency checking.

data/: Workspace for user data (imports, exports, cache, templates).

tests/: Unit tests for the core logic.

How to Extend the Application
Adding a New OCR Engine
Add a new processing method (e.g., _perform_new_ocr(...)) to core/ocr_processor.py.

Add the new engine's name to the OCR engine QComboBox in app/main_window.py.

Update the main processing loop in OcrProcessor to call your new method when the engine is selected.

Add any new required settings to core/config_manager.py and the default config.json.

Adding a New Special Parser
Add a new parsing method (e.g., _parse_my_form(...)) to core/template_manager.py.

In TemplateManager.apply_text_parser, add an elif condition to check for your new template's name and call your parsing method.

You can now create a template with that specific name (e.g., "My Custom Form") in the UI to trigger this specialized logic.

</markdown>
