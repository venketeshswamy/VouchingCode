# ocr_tool_qt/app/widgets/results_table.py

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMenu
from PyQt5.QtCore import Qt
import clipboard

class ResultsTable(QTableWidget):
    """
    A QTableWidget specialized for displaying OCR results.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["File", "Page"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setEditTriggers(self.NoEditTriggers) # Read-only
        self.setSelectionBehavior(self.SelectRows)

        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def update_columns(self, templates):
        """Updates the table columns based on the provided templates."""
        headers = ["File", "Page"]
        
        # Logic to determine headers from mixed template types
        # For simplicity, we'll use fields from the first text_parser,
        # or names from all visual snips.
        text_parser = next((t for t in templates if t.get('type') == 'text_parser'), None)
        
        if text_parser:
            headers.extend([field['column_name'] for field in text_parser.get('fields', [])])
        else: # Visual snips
            headers.extend([t['name'] for t in templates if t.get('type') == 'visual'])
            
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

    def add_row(self, row_data):
        """Adds a new row of data to the table."""
        row_count = self.rowCount()
        self.insertRow(row_count)
        
        headers = [self.horizontalHeaderItem(i).text() for i in range(self.columnCount())]
        
        for col_idx, header in enumerate(headers):
            item_value = str(row_data.get(header, ''))
            self.setItem(row_count, col_idx, QTableWidgetItem(item_value))
            
    def clear_results(self):
        """Clears all rows from the table."""
        self.setRowCount(0)

    def show_context_menu(self, pos):
        """Shows the right-click context menu."""
        menu = QMenu()
        copy_row_action = menu.addAction("Copy Row(s) as TSV")
        copy_cell_action = menu.addAction("Copy Cell Value")
        
        action = menu.exec_(self.mapToGlobal(pos))
        
        if action == copy_row_action:
            self.copy_selected_rows()
        elif action == copy_cell_action:
            self.copy_selected_cell()
            
    def copy_selected_rows(self):
        """Copies the selected rows to the clipboard in Tab-Separated Value format."""
        selection = self.selectionModel().selectedRows()
        if not selection:
            return
            
        headers = "\t".join([self.horizontalHeaderItem(i).text() for i in range(self.columnCount())])
        
        rows_text = [headers]
        for index in selection:
            row_items = [self.item(index.row(), col).text() for col in range(self.columnCount())]
            rows_text.append("\t".join(row_items))
            
        clipboard.copy("\n".join(rows_text))

    def copy_selected_cell(self):
        """Copies the value of the currently selected cell."""
        current_item = self.currentItem()
        if current_item:
            clipboard.copy(current_item.text())

