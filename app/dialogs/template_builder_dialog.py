# ocr_tool_qt/app/dialogs/template_builder_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QTextEdit, QLabel, QMessageBox,
                             QSplitter, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
import re

class TemplateBuilderDialog(QDialog):
    """
    A dialog for visually creating and testing regex patterns for
    text parser templates.
    """
    def __init__(self, parent=None, template_manager=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.setWindowTitle("Regex Template Builder")
        self.setMinimumSize(800, 600)

        # Main Layout
        main_layout = QVBoxLayout(self)
        
        # Top part for name and saving
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Template Name:"))
        self.name_edit = QLineEdit()
        top_layout.addWidget(self.name_edit)
        self.save_button = QPushButton("Save Template")
        self.save_button.clicked.connect(self.save_template)
        top_layout.addWidget(self.save_button)
        main_layout.addLayout(top_layout)

        # Splitter for layout
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Regex and Fields
        left_widget = QGroupBox("Regex Definition")
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Paste sample text below to test your regex against."))
        self.sample_text_edit = QTextEdit()
        self.sample_text_edit.setPlaceholderText("Paste sample text from a PDF here...")
        left_layout.addWidget(self.sample_text_edit)
        left_widget.setLayout(left_layout)
        
        # Right side: Results
        right_widget = QGroupBox("Fields & Testing")
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Define fields (ColumnName: RegexPattern). Click 'Test All' to see matches."))
        self.fields_text_edit = QTextEdit()
        self.fields_text_edit.setPlaceholderText("InvoiceNumber: INVOICE\\s*#\\s*(\\w+)\\nDate: Date:\\s*(\\d{2}/\\d{2}/\\d{4})")
        right_layout.addWidget(self.fields_text_edit)
        
        test_button = QPushButton("Test All Regex")
        test_button.clicked.connect(self.test_regex)
        right_layout.addWidget(test_button)
        right_widget.setLayout(right_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)
        
    def test_regex(self):
        """Highlights regex matches in the sample text."""
        # Reset highlighting first
        self.sample_text_edit.blockSignals(True)
        cursor = self.sample_text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        default_format = QTextCharFormat()
        cursor.setCharFormat(default_format)
        cursor.clearSelection()
        self.sample_text_edit.setTextCursor(cursor)
        self.sample_text_edit.blockSignals(False)

        sample_text = self.sample_text_edit.toPlainText()
        fields_text = self.fields_text_edit.toPlainText()
        
        if not sample_text or not fields_text:
            QMessageBox.warning(self, "Input Missing", "Please provide both sample text and at least one regex field to test.")
            return

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("yellow"))
        
        all_found = True
        for line in fields_text.split('\n'):
            if ':' not in line: continue
            _, regex = line.split(':', 1)
            regex = regex.strip()
            if not regex: continue

            try:
                for match in re.finditer(regex, sample_text, re.DOTALL | re.IGNORECASE):
                    start, end = match.span()
                    # Highlighting logic
                    cursor.setPosition(start)
                    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, end - start)
                    cursor.mergeCharFormat(highlight_format)
            except re.error as e:
                QMessageBox.critical(self, "Regex Error", f"Invalid regex found: {regex}\n\nError: {e}")
                all_found = False
                break
        
        if all_found:
             QMessageBox.information(self, "Test Complete", "Regex testing complete. Matches are highlighted in yellow.")

    def save_template(self):
        """Saves the defined fields as a new text_parser template."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Template name cannot be empty.")
            return

        if self.template_manager.get_template_by_name(name):
            QMessageBox.warning(self, "Duplicate Name", f"A template with the name '{name}' already exists.")
            return
            
        fields_text = self.fields_text_edit.toPlainText().strip()
        if not fields_text:
            QMessageBox.warning(self, "Input Error", "Cannot save a template with no fields defined.")
            return
            
        # Basic validation (similar to properties dialog)
        fields = []
        for line in fields_text.split('\n'):
            if ':' not in line: continue
            col_name, regex = line.split(':', 1)
            fields.append({'column_name': col_name.strip(), 'regex': regex.strip()})
            
        if not fields:
            QMessageBox.warning(self, "Input Error", "No valid fields found to save.")
            return

        new_template = {
            "name": name,
            "type": "text_parser",
            "fields": fields
        }
        
        if self.template_manager.add_template(new_template):
            QMessageBox.information(self, "Success", f"Template '{name}' saved successfully.")
            self.accept() # Close the dialog
        else:
            QMessageBox.critical(self, "Error", "Failed to save the template.")

