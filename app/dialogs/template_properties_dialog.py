# ocr_tool_qt/app/dialogs/template_properties_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QDialogButtonBox, QRadioButton, QCheckBox,
                             QMessageBox, QGroupBox, QTextEdit, QLabel)
import re

class TemplatePropertiesDialog(QDialog):
    """
    A dialog for creating and editing the properties of a template,
    supporting both 'visual' and 'text_parser' types.
    """
    def __init__(self, parent=None, template_data=None):
        super().__init__(parent)
        self.setWindowTitle("Template Properties")
        
        self.template_data = template_data or {}
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Form layout for properties
        form_layout = QFormLayout()
        self.name_edit = QLineEdit(self.template_data.get('name', ''))
        form_layout.addRow("Template Name:", self.name_edit)
        
        # --- Type Selection ---
        self.type_groupbox = QGroupBox("Template Type")
        type_layout = QVBoxLayout()
        self.visual_radio = QRadioButton("Visual OCR Snip")
        self.text_parser_radio = QRadioButton("Text Parsing Template (PDFs)")
        
        self.visual_radio.toggled.connect(self.toggle_type_specific_fields)
        
        if self.template_data.get('type', 'visual') == 'text_parser':
            self.text_parser_radio.setChecked(True)
        else:
            self.visual_radio.setChecked(True)
            
        type_layout.addWidget(self.visual_radio)
        type_layout.addWidget(self.text_parser_radio)
        self.type_groupbox.setLayout(type_layout)
        
        # --- Visual Snip Options ---
        self.visual_snip_frame = QGroupBox("Visual Snip Options")
        visual_layout = QVBoxLayout()
        self.numeric_check = QCheckBox("Optimize for Numbers/Currency (Tesseract only)")
        self.numeric_check.setChecked(self.template_data.get('numeric_optimize', False))
        visual_layout.addWidget(self.numeric_check)
        visual_layout.addWidget(QLabel("(Define region by drawing on the image)"))
        self.visual_snip_frame.setLayout(visual_layout)

        # --- Text Parser Options ---
        self.text_parser_frame = QGroupBox("Text Parser Fields")
        parser_layout = QVBoxLayout()
        parser_layout.addWidget(QLabel("Define one field per line: <b>ColumnName: RegexPattern</b>"))
        self.fields_text_edit = QTextEdit()
        
        initial_fields_text = ""
        if 'fields' in self.template_data:
            initial_fields_text = "\n".join([f"{f['column_name']}: {f['regex']}" for f in self.template_data['fields']])
        self.fields_text_edit.setPlainText(initial_fields_text)
        
        parser_layout.addWidget(self.fields_text_edit)
        self.text_parser_frame.setLayout(parser_layout)

        # --- Dialog Buttons ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        # Add widgets to main layout
        layout.addLayout(form_layout)
        layout.addWidget(self.type_groupbox)
        layout.addWidget(self.visual_snip_frame)
        layout.addWidget(self.text_parser_frame)
        layout.addWidget(self.button_box)
        
        self.toggle_type_specific_fields()

    def toggle_type_specific_fields(self):
        is_visual = self.visual_radio.isChecked()
        self.visual_snip_frame.setVisible(is_visual)
        self.text_parser_frame.setVisible(not is_visual)

    def get_data(self):
        """Returns the edited template data."""
        return self.template_data

    def validate_and_accept(self):
        """Validates the form before closing the dialog."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Template name cannot be empty.")
            return
            
        self.template_data['name'] = name
        
        if self.visual_radio.isChecked():
            self.template_data['type'] = 'visual'
            self.template_data['numeric_optimize'] = self.numeric_check.isChecked()
            # Clear text parser fields if they exist
            self.template_data.pop('fields', None)
        else: # Text parser
            self.template_data['type'] = 'text_parser'
            fields = []
            text = self.fields_text_edit.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "Input Error", "Text Parser Template must have at least one field.")
                return

            for i, line in enumerate(text.split('\n')):
                if not line.strip() or line.strip().startswith('#'):
                    continue
                if ':' not in line:
                    QMessageBox.warning(self, "Input Error", f"Invalid format on line {i+1}. Expected 'ColumnName: RegexPattern'.")
                    return
                
                col_name, regex = line.split(':', 1)
                col_name = col_name.strip()
                regex = regex.strip()
                
                if not col_name:
                    QMessageBox.warning(self, "Input Error", f"Column name cannot be empty on line {i+1}.")
                    return

                try:
                    if regex: re.compile(regex)
                except re.error as e:
                    QMessageBox.warning(self, "Regex Error", f"Invalid Regex for '{col_name}' on line {i+1}: {e}")
                    return
                fields.append({'column_name': col_name, 'regex': regex})
            
            if not fields:
                QMessageBox.warning(self, "Input Error", "No valid fields defined for Text Parser.")
                return

            self.template_data['fields'] = fields
            # Clear visual snip fields
            self.template_data.pop('numeric_optimize', None)
            
        self.accept()

