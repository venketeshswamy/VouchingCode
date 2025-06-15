# ocr_tool_qt/app/main_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QAction, QFileDialog, QMessageBox, QSplitter,
                             QGroupBox, QLabel, QToolBar, QListWidget,
                             QRadioButton, QLineEdit, QListWidgetItem,
                             QProgressBar, QComboBox, QPushButton)
from PyQt5.QtCore import Qt, QThread, QTimer

# Import local modules
from app.widgets.file_list import FileList
from app.widgets.image_view import ImageView
from app.widgets.results_table import ResultsTable
from app.dialogs.template_properties_dialog import TemplatePropertiesDialog
from app.dialogs.tesseract_preferences_dialog import TesseractPreferencesDialog
from core.initializer import AppInitializer
from core.config_manager import ConfigManager
from core.template_manager import TemplateManager
from core.session_manager import SessionManager
from core.ocr_processor import OcrProcessor
from core.file_importer import FileImporter
from utils.logger import log
from utils.dependency_checker import get_missing_packages, check_external_dependencies
from core.file_importer import FileImporter # Make sure this is imported

class MainWindow(QMainWindow):
    """The main window of the OCR Tool application."""

    def __init__(self):
        super().__init__()
        
        # --- Stage 1: Immediate Initialization ---
        self.setWindowTitle("OCR Tool - PyQt5 Edition")
        self.setGeometry(100, 100, 1500, 950)

        self.loading_label = QLabel("Initializing application, please wait...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.loading_label)

        self.config = None
        self.templates = None
        self.session = None
        self.ocr_thread = None
        self.ocr_processor = None
        self.importer_thread = None
        self.file_importer = None
        self.initializer_thread = None
        self.initializer = None

        # --- Stage 2: Deferred Initialization ---
        QTimer.singleShot(50, self.start_background_initialization)

    def start_background_initialization(self):
        """Launches the background thread to perform slow startup tasks."""
        self.initializer_thread = QThread()
        self.initializer = AppInitializer()
        self.initializer.moveToThread(self.initializer_thread)
        self.initializer.initialization_finished.connect(self.on_initialization_complete)
        self.initializer_thread.started.connect(self.initializer.run)
        self.initializer_thread.finished.connect(self.initializer_thread.deleteLater)
        self.initializer.moveToThread(None)
        self.initializer_thread.start()

    def on_initialization_complete(self, config, templates, session):
        """Slot called when the background initializer is finished."""
        if config is None:
            QMessageBox.critical(self, "Fatal Error", "Application could not initialize correctly. Please check app.log for details.")
            self.close()
            return

        log.info("Initialization complete. Populating UI.")
        self.config = config
        self.templates = templates
        self.session = session
        
        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.create_main_layout()
        self.create_status_bar()
        self.setup_threads_post_init()
        self.load_initial_templates()
        self.update_ui_post_init()
        self.status_label.setText("Ready")

    def create_main_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel with Drag-and-Drop enabled FileList
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        files_group = QGroupBox("Files")
        files_layout = QVBoxLayout(files_group)
        self.file_list = FileList()
        self.file_list.currentItemChanged.connect(self.on_file_selected)
        self.file_list.files_dropped.connect(self.start_file_import) # Connect drop signal
        files_layout.addWidget(self.file_list)
        left_layout.addWidget(files_group)

        # Page Selection Group
        page_group = QGroupBox("Page Selection")
        page_layout = QVBoxLayout(page_group)
        self.all_pages_radio = QRadioButton("All")
        self.first_page_radio = QRadioButton("First")
        self.specific_pages_radio = QRadioButton("Page(s):")
        self.specific_pages_edit = QLineEdit("1,3,5-7")
        self.all_pages_radio.setChecked(True)
        page_layout.addWidget(self.all_pages_radio)
        page_layout.addWidget(self.first_page_radio)
        page_layout.addWidget(self.specific_pages_radio)
        page_layout.addWidget(self.specific_pages_edit)
        left_layout.addWidget(page_group)

        # Templates Group with functional buttons
        templates_group = QGroupBox("Templates")
        templates_layout = QVBoxLayout(templates_group)
        self.template_list_widget = QListWidget()
        templates_layout.addWidget(self.template_list_widget)
        template_btn_layout = QHBoxLayout()
        self.new_template_btn = QPushButton("New...")
        self.edit_template_btn = QPushButton("Edit...")
        self.delete_template_btn = QPushButton("Delete")
        template_btn_layout.addWidget(self.new_template_btn)
        template_btn_layout.addWidget(self.edit_template_btn)
        template_btn_layout.addWidget(self.delete_template_btn)
        templates_layout.addLayout(template_btn_layout)
        left_layout.addWidget(templates_group)
        
        self.new_template_btn.clicked.connect(self.create_new_template)
        self.edit_template_btn.clicked.connect(self.edit_selected_template)
        self.delete_template_btn.clicked.connect(self.delete_selected_template)

        # Center and Right Panels
        self.image_view = ImageView()
        self.results_table = ResultsTable()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(self.image_view)
        splitter.addWidget(self.results_table)
        splitter.setSizes([300, 800, 400])
        main_layout.addWidget(splitter)

    def manual_dependency_check(self):
        if not self.config: return
        log.info("Performing manual dependency check...")
        ext_warnings = check_external_dependencies(self.config.config)
        py_missing = get_missing_packages()
        messages = []
        if ext_warnings: messages.append("<b>External Dependency Issues:</b><br>" + "<br>".join(ext_warnings))
        if py_missing: messages.append("<b>Missing Python Packages:</b><br>" + ", ".join(py_missing) + "<br><br><i>Install via 'pip install ...'</i>")
        if not messages: QMessageBox.information(self, "Dependencies Check", "All dependencies appear to be installed correctly.")
        else: QMessageBox.warning(self, "Dependencies Check Results", "<br><br>".join(messages))

    def setup_threads_post_init(self):
        # --- OCR Processor Thread Setup (existing) ---
        self.ocr_thread = QThread()
        self.ocr_processor = OcrProcessor(self.config, self.templates)
        self.ocr_processor.moveToThread(self.ocr_thread)
        self.ocr_thread.started.connect(self.ocr_processor.run)
        self.ocr_processor.processing_finished.connect(self.on_ocr_finished)
        self.ocr_processor.progress_updated.connect(self.update_progress_bar)
        self.ocr_processor.result_ready.connect(self.results_table.add_row)
        self.ocr_processor.error_occurred.connect(lambda msg: QMessageBox.critical(self, "Processing Error", msg))
        
        # --- File Importer Thread Setup (NEW and CORRECTED) ---
        self.importer_thread = QThread()
        # Initialize the worker without specific files for now
        self.file_importer = FileImporter(self.session.imports_dir) 
        self.file_importer.moveToThread(self.importer_thread)

        # Connect signals from the worker to the main thread
        self.file_importer.file_imported.connect(self.file_list.add_file)
        self.file_importer.import_finished.connect(self.on_import_finished)
        self.file_importer.error_occurred.connect(lambda msg: QMessageBox.critical(self, "Import Error", msg))

        # When the thread starts, run the worker's process method
        self.importer_thread.started.connect(self.file_importer.run)
        
        # When the worker finishes, it should signal the thread to quit
        self.file_importer.import_finished.connect(self.importer_thread.quit)

    def create_actions(self):
        self.import_files_action = QAction("Import Files...", self)
        self.save_session_action = QAction("Save Session As...", self)
        self.load_session_action = QAction("Load Session...", self)
        self.exit_action = QAction("Exit", self)
        self.tesseract_prefs_action = QAction("Tesseract Preferences...", self)
        self.zoom_fit_action = QAction("Zoom Fit", self, checkable=True)
        self.check_deps_action = QAction("Check Dependencies...", self)
        self.process_files_action = QAction("Process Files", self)
        self.stop_process_action = QAction("Stop Processing", self)

        self.import_files_action.triggered.connect(self.import_files)
        self.exit_action.triggered.connect(self.close)
        self.process_files_action.triggered.connect(self.start_ocr_processing)
        self.stop_process_action.triggered.connect(self.stop_ocr_processing)
        self.zoom_fit_action.toggled.connect(self.toggle_auto_zoom)
        self.check_deps_action.triggered.connect(self.manual_dependency_check)
        self.tesseract_prefs_action.triggered.connect(self.open_tesseract_preferences)

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.import_files_action)
        file_menu.addSeparator(); file_menu.addAction(self.save_session_action); file_menu.addAction(self.load_session_action); file_menu.addSeparator(); file_menu.addAction(self.exit_action)
        edit_menu = menubar.addMenu("&Edit"); edit_menu.addAction(self.tesseract_prefs_action)
        view_menu = menubar.addMenu("&View"); view_menu.addAction(self.zoom_fit_action)
        help_menu = menubar.addMenu("&Help"); help_menu.addAction(self.check_deps_action)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar"); self.addToolBar(toolbar)
        toolbar.addAction(self.import_files_action); toolbar.addSeparator(); toolbar.addAction(self.process_files_action); toolbar.addAction(self.stop_process_action); toolbar.addSeparator()
        toolbar.addWidget(QLabel("OCR Engine:")); self.ocr_engine_combo = QComboBox()
        self.ocr_engine_combo.addItems(["windows", "tesseract", "pdf_native"]); toolbar.addWidget(self.ocr_engine_combo)

    def create_status_bar(self):
        self.statusBar = self.statusBar(); self.status_label = QLabel("Initializing..."); self.statusBar.addWidget(self.status_label, 1)
        self.progress_bar = QProgressBar(); self.progress_bar.setVisible(False); self.statusBar.addPermanentWidget(self.progress_bar)
        
    def update_ui_post_init(self):
        self.image_view.set_poppler_path(self.config.get('poppler_path'))
        self.ocr_engine_combo.setCurrentText(self.config.get("default_ocr_engine", "none"))
        self.stop_process_action.setEnabled(False)

    def import_files(self):
        if not self.config: return
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Import", "", "Image/PDF Files (*.png *.jpg *.jpeg *.bmp *.tiff *.pdf);;All files (*.*)")
        if files: self.start_file_import(files)

    def start_file_import(self, files_to_import):
        """
        Starts the file import process using the pre-configured background thread.
        (This replaces the old version of the method entirely).
        """
        if self.importer_thread.isRunning():
            QMessageBox.warning(self, "Busy", "An import process is already running.")
            return
            
        # Set the list of files for the existing worker to process
        self.file_importer.set_files_to_import(files_to_import)
        
        # Start the existing thread
        self.importer_thread.start()
        
    def on_import_finished(self):
        """A new slot to handle when the import is complete."""
        # This is a good place for any logic that needs to run after import,
        # like logging or updating the status bar.
        self.status_label.setText("Import finished.")

    def start_ocr_processing(self):
        if not self.file_list.get_all_paths(): return QMessageBox.warning(self, "No Files", "Please import files before processing.")
        if self.ocr_thread.isRunning(): return QMessageBox.warning(self, "Busy", "An OCR process is already running.")
        self.results_table.clear_results(); self.progress_bar.setVisible(True); self.process_files_action.setEnabled(False); self.stop_process_action.setEnabled(True)
        self.ocr_processor.files_to_process = self.file_list.get_all_paths(); self.ocr_processor.templates_to_use = self.templates.get_templates()
        self.ocr_processor.ocr_engine = self.ocr_engine_combo.currentText(); self.ocr_thread.start()

    def stop_ocr_processing(self):
        if self.ocr_processor: self.ocr_processor.stop()

    def on_ocr_finished(self):
        self.status_label.setText("Processing finished."); self.progress_bar.setVisible(False)
        self.process_files_action.setEnabled(True); self.stop_process_action.setEnabled(False)

    def update_progress_bar(self, current, total):
        self.progress_bar.setMaximum(total); self.progress_bar.setValue(current); self.status_label.setText(f"Processing... {current}/{total}")

    def on_file_selected(self, current_item, _):
        if current_item: self.image_view.load_page(current_item.data(Qt.UserRole))
            
    def toggle_auto_zoom(self, checked):
        self.image_view.auto_zoom_enabled = checked
        if checked and self.image_view.pixmap_item: self.image_view.fit_in_view()
            
    def load_initial_templates(self):
        self.template_list_widget.clear()
        for t in self.templates.get_templates(): self.template_list_widget.addItem(QListWidgetItem(t['name']))

    def create_new_template(self):
        dialog = TemplatePropertiesDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            if self.templates.get_template_by_name(new_data['name']): return QMessageBox.warning(self, "Duplicate Name", "A template with this name already exists.")
            self.templates.add_template(new_data); self.load_initial_templates()

    def edit_selected_template(self):
        selected_item = self.template_list_widget.currentItem()
        if not selected_item: return QMessageBox.warning(self, "No Selection", "Please select a template to edit.")
        template_data = self.templates.get_template_by_name(selected_item.text())
        dialog = TemplatePropertiesDialog(self, template_data=template_data)
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.get_data(); self.templates.delete_template(selected_item.text()); self.templates.add_template(updated_data) 
            self.load_initial_templates()
    
    def delete_selected_template(self):
        selected_item = self.template_list_widget.currentItem()
        if not selected_item: return QMessageBox.warning(self, "No Selection", "Please select a template to delete.")
        if QMessageBox.question(self, "Confirm Delete", f"Delete template '{selected_item.text()}'?") == QMessageBox.Yes:
            self.templates.delete_template(selected_item.text()); self.load_initial_templates()

    def open_tesseract_preferences(self):
        dialog = TesseractPreferencesDialog(self, current_config=self.config.config)
        if dialog.exec_() == QDialog.Accepted:
            psm, oem = dialog.get_selected_options(); self.config.set('tesseract_psm', psm); self.config.set('tesseract_oem', oem)
            self.config.save_config(); QMessageBox.information(self, "Saved", "Tesseract preferences have been saved.")

    def closeEvent(self, event):
        threads = [self.ocr_thread, self.importer_thread, self.initializer_thread]
        for thread in threads:
            if thread and thread.isRunning(): thread.quit(); thread.wait(1000)
        if self.config: self.config.save_config()
        log.info("Application shutting down."); event.accept()

