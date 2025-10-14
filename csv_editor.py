import sys
import csv
import copy
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QFileDialog, QMessageBox, QToolBar,
    QMenu, QInputDialog, QHeaderView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence, QIcon
import pandas as pd


class CSVDataModel:
    """Data model for CSV operations with undo/redo support"""

    def __init__(self):
        self.df = pd.DataFrame()
        self.current_file = None
        self.modified = False
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo = 50

    def save_state(self):
        """Save current state to undo stack"""
        if len(self.undo_stack) >= self.max_undo:
            self.undo_stack.pop(0)
        self.undo_stack.append(self.df.copy())
        self.redo_stack.clear()
        self.modified = True

    def undo(self):
        """Undo last operation"""
        if self.undo_stack:
            self.redo_stack.append(self.df.copy())
            self.df = self.undo_stack.pop()
            self.modified = True
            return True
        return False

    def redo(self):
        """Redo last undone operation"""
        if self.redo_stack:
            self.undo_stack.append(self.df.copy())
            self.df = self.redo_stack.pop()
            self.modified = True
            return True
        return False

    def load_csv(self, filepath):
        """Load CSV file with robust error handling"""
        # Try multiple strategies to load the CSV
        strategies = [
            # Strategy 1: Standard CSV with error handling
            lambda: pd.read_csv(filepath, dtype=str, keep_default_na=False,
                               on_bad_lines='skip', encoding='utf-8'),

            # Strategy 2: Try different encoding
            lambda: pd.read_csv(filepath, dtype=str, keep_default_na=False,
                               on_bad_lines='skip', encoding='latin-1'),

            # Strategy 3: Try with different separator
            lambda: pd.read_csv(filepath, dtype=str, keep_default_na=False,
                               on_bad_lines='skip', sep=None, engine='python'),

            # Strategy 4: Force load with errors ignored, fill missing columns
            lambda: pd.read_csv(filepath, dtype=str, keep_default_na=False,
                               on_bad_lines='skip', encoding='utf-8-sig'),

            # Strategy 5: Tab-separated
            lambda: pd.read_csv(filepath, dtype=str, keep_default_na=False,
                               on_bad_lines='skip', sep='\t'),

            # Strategy 6: Semicolon-separated
            lambda: pd.read_csv(filepath, dtype=str, keep_default_na=False,
                               on_bad_lines='skip', sep=';'),

            # Strategy 7: Use Python engine with more flexibility
            lambda: pd.read_csv(filepath, dtype=str, keep_default_na=False,
                               engine='python', on_bad_lines='skip',
                               encoding='utf-8', quoting=csv.QUOTE_MINIMAL),
        ]

        last_error = None
        for i, strategy in enumerate(strategies):
            try:
                self.df = strategy()

                # Ensure we have at least some data
                if len(self.df.columns) == 0:
                    self.df = pd.DataFrame({'Column 1': ['']})

                # Fill any NaN values with empty strings
                self.df = self.df.fillna('')

                # Ensure all column names are strings
                self.df.columns = [str(col) if col else f"Column {i+1}"
                                  for i, col in enumerate(self.df.columns)]

                self.current_file = filepath
                self.modified = False
                self.undo_stack.clear()
                self.redo_stack.clear()
                return True
            except Exception as e:
                last_error = e
                continue

        # If all strategies failed, raise the last error
        raise Exception(f"Could not load CSV file. Last error: {str(last_error)}")

    def save_csv(self, filepath=None):
        """Save CSV file"""
        try:
            save_path = filepath or self.current_file
            if not save_path:
                return False
            self.df.to_csv(save_path, index=False)
            self.current_file = save_path
            self.modified = False
            return True
        except Exception as e:
            raise Exception(f"Error saving CSV: {str(e)}")

    def new_csv(self, rows=10, cols=5):
        """Create new CSV with default dimensions"""
        self.save_state()
        columns = [f"Column {i+1}" for i in range(cols)]
        self.df = pd.DataFrame('', index=range(rows), columns=columns)
        self.current_file = None
        self.modified = True

    def get_value(self, row, col):
        """Get cell value"""
        if 0 <= row < len(self.df) and 0 <= col < len(self.df.columns):
            return str(self.df.iloc[row, col])
        return ""

    def set_value(self, row, col, value):
        """Set cell value"""
        if 0 <= row < len(self.df) and 0 <= col < len(self.df.columns):
            self.save_state()
            self.df.iloc[row, col] = value

    def add_row(self, position=None):
        """Add row at position (default: end)"""
        self.save_state()
        if position is None or position >= len(self.df):
            new_row = pd.DataFrame([''] * len(self.df.columns)).T
            new_row.columns = self.df.columns
            self.df = pd.concat([self.df, new_row], ignore_index=True)
        else:
            new_row = pd.DataFrame([''] * len(self.df.columns)).T
            new_row.columns = self.df.columns
            self.df = pd.concat([
                self.df.iloc[:position],
                new_row,
                self.df.iloc[position:]
            ], ignore_index=True)

    def delete_row(self, row):
        """Delete row"""
        if 0 <= row < len(self.df):
            self.save_state()
            self.df = self.df.drop(self.df.index[row]).reset_index(drop=True)

    def add_column(self, position=None, name=None):
        """Add column at position (default: end)"""
        self.save_state()
        if name is None:
            name = f"Column {len(self.df.columns) + 1}"

        if position is None or position >= len(self.df.columns):
            self.df[name] = ''
        else:
            cols = list(self.df.columns)
            cols.insert(position, name)
            self.df.insert(position, name, '')

    def delete_column(self, col):
        """Delete column"""
        if 0 <= col < len(self.df.columns):
            self.save_state()
            self.df = self.df.drop(self.df.columns[col], axis=1)

    def rename_column(self, col, new_name):
        """Rename column"""
        if 0 <= col < len(self.df.columns):
            self.save_state()
            self.df.columns.values[col] = new_name

    @property
    def row_count(self):
        return len(self.df)

    @property
    def column_count(self):
        return len(self.df.columns)

    def get_column_names(self):
        return list(self.df.columns)


class CSVEditorWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.model = CSVDataModel()
        self.init_ui()
        self.create_new()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("CSV Editor")
        self.setGeometry(100, 100, 1200, 800)

        # Apply modern stylesheet with explicit colors
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                color: #000000;
            }
            QTableWidget {
                background-color: white;
                color: #000000;
                alternate-background-color: #f9f9f9;
                selection-background-color: #0078d4;
                selection-color: white;
                gridline-color: #e0e0e0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #e8e8e8;
                color: #000000;
                padding: 6px;
                border: none;
                border-right: 1px solid #d0d0d0;
                border-bottom: 1px solid #d0d0d0;
                font-weight: bold;
            }
            QToolBar {
                background-color: #ffffff;
                color: #000000;
                border-bottom: 1px solid #d0d0d0;
                spacing: 3px;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                color: #000000;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 5px;
                margin: 2px;
            }
            QToolButton:hover {
                background-color: #e8e8e8;
                color: #000000;
                border: 1px solid #d0d0d0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
                color: #000000;
            }
            QMenuBar {
                background-color: #ffffff;
                color: #000000;
                border-bottom: 1px solid #d0d0d0;
            }
            QMenuBar::item {
                color: #000000;
            }
            QMenuBar::item:selected {
                background-color: #e8e8e8;
                color: #000000;
            }
            QMenu {
                background-color: white;
                color: #000000;
                border: 1px solid #d0d0d0;
            }
            QMenu::item {
                color: #000000;
            }
            QMenu::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QInputDialog {
                background-color: white;
                color: #000000;
            }
            QLabel {
                color: #000000;
            }
            QLineEdit {
                background-color: white;
                color: #000000;
                border: 1px solid #d0d0d0;
                padding: 4px;
            }
            QPushButton {
                background-color: #e8e8e8;
                color: #000000;
                border: 1px solid #d0d0d0;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #b8b8b8;
            }
            QMessageBox {
                background-color: white;
                color: #000000;
            }
            QMessageBox QLabel {
                color: #000000;
            }
        """)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create table widget
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.table)

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        self.update_title()

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.create_new)
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        # Row menu
        row_menu = menubar.addMenu("Row")

        add_row_action = QAction("Add Row", self)
        add_row_action.setShortcut("Ctrl+R")
        add_row_action.triggered.connect(self.add_row)
        row_menu.addAction(add_row_action)

        insert_row_action = QAction("Insert Row Above", self)
        insert_row_action.setShortcut("Ctrl+Shift+R")
        insert_row_action.triggered.connect(self.insert_row)
        row_menu.addAction(insert_row_action)

        delete_row_action = QAction("Delete Row", self)
        delete_row_action.setShortcut("Ctrl+D")
        delete_row_action.triggered.connect(self.delete_row)
        row_menu.addAction(delete_row_action)

        # Column menu
        col_menu = menubar.addMenu("Column")

        add_col_action = QAction("Add Column", self)
        add_col_action.setShortcut("Ctrl+L")
        add_col_action.triggered.connect(self.add_column)
        col_menu.addAction(add_col_action)

        insert_col_action = QAction("Insert Column Left", self)
        insert_col_action.setShortcut("Ctrl+Shift+L")
        insert_col_action.triggered.connect(self.insert_column)
        col_menu.addAction(insert_col_action)

        delete_col_action = QAction("Delete Column", self)
        delete_col_action.setShortcut("Ctrl+Shift+D")
        delete_col_action.triggered.connect(self.delete_column)
        col_menu.addAction(delete_col_action)

        rename_col_action = QAction("Rename Column", self)
        rename_col_action.setShortcut("F2")
        rename_col_action.triggered.connect(self.rename_column)
        col_menu.addAction(rename_col_action)

    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # File actions
        new_action = QAction("New", self)
        new_action.triggered.connect(self.create_new)
        toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Edit actions
        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.undo)
        toolbar.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(self.redo)
        toolbar.addAction(redo_action)

        toolbar.addSeparator()

        # Row actions
        add_row_action = QAction("Add Row", self)
        add_row_action.triggered.connect(self.add_row)
        toolbar.addAction(add_row_action)

        delete_row_action = QAction("Delete Row", self)
        delete_row_action.triggered.connect(self.delete_row)
        toolbar.addAction(delete_row_action)

        toolbar.addSeparator()

        # Column actions
        add_col_action = QAction("Add Column", self)
        add_col_action.triggered.connect(self.add_column)
        toolbar.addAction(add_col_action)

        delete_col_action = QAction("Delete Column", self)
        delete_col_action.triggered.connect(self.delete_column)
        toolbar.addAction(delete_col_action)

    def show_context_menu(self, position):
        """Show context menu"""
        menu = QMenu()

        # Row operations
        add_row_action = QAction("Add Row", self)
        add_row_action.triggered.connect(self.add_row)
        menu.addAction(add_row_action)

        insert_row_action = QAction("Insert Row Above", self)
        insert_row_action.triggered.connect(self.insert_row)
        menu.addAction(insert_row_action)

        delete_row_action = QAction("Delete Row", self)
        delete_row_action.triggered.connect(self.delete_row)
        menu.addAction(delete_row_action)

        menu.addSeparator()

        # Column operations
        add_col_action = QAction("Add Column", self)
        add_col_action.triggered.connect(self.add_column)
        menu.addAction(add_col_action)

        insert_col_action = QAction("Insert Column Left", self)
        insert_col_action.triggered.connect(self.insert_column)
        menu.addAction(insert_col_action)

        delete_col_action = QAction("Delete Column", self)
        delete_col_action.triggered.connect(self.delete_column)
        menu.addAction(delete_col_action)

        rename_col_action = QAction("Rename Column", self)
        rename_col_action.triggered.connect(self.rename_column)
        menu.addAction(rename_col_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def refresh_table(self):
        """Refresh table from model"""
        self.table.blockSignals(True)
        self.table.clear()

        self.table.setRowCount(self.model.row_count)
        self.table.setColumnCount(self.model.column_count)
        self.table.setHorizontalHeaderLabels(self.model.get_column_names())

        for row in range(self.model.row_count):
            for col in range(self.model.column_count):
                value = self.model.get_value(row, col)
                item = QTableWidgetItem(value)
                self.table.setItem(row, col, item)

        self.table.blockSignals(False)
        self.update_title()

    def on_item_changed(self, item):
        """Handle item change"""
        row = item.row()
        col = item.column()
        value = item.text()
        self.model.set_value(row, col, value)
        self.update_title()

    def create_new(self):
        """Create new CSV"""
        if not self.check_save():
            return

        rows, ok1 = QInputDialog.getInt(self, "New CSV", "Number of rows:", 10, 1, 10000)
        if not ok1:
            return

        cols, ok2 = QInputDialog.getInt(self, "New CSV", "Number of columns:", 5, 1, 1000)
        if not ok2:
            return

        self.model.new_csv(rows, cols)
        self.refresh_table()

    def open_file(self):
        """Open CSV file"""
        if not self.check_save():
            return

        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )

        if filepath:
            try:
                self.model.load_csv(filepath)
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def save_file(self):
        """Save CSV file"""
        if self.model.current_file:
            try:
                self.model.save_csv()
                self.update_title()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save CSV file as"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )

        if filepath:
            try:
                self.model.save_csv(filepath)
                self.update_title()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def check_save(self):
        """Check if file needs saving"""
        if self.model.modified:
            reply = QMessageBox.question(
                self, "Save Changes",
                "Do you want to save changes?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.save_file()
                return True
            elif reply == QMessageBox.StandardButton.No:
                return True
            else:
                return False
        return True

    def undo(self):
        """Undo last operation"""
        if self.model.undo():
            self.refresh_table()

    def redo(self):
        """Redo last operation"""
        if self.model.redo():
            self.refresh_table()

    def add_row(self):
        """Add row at end"""
        self.model.add_row()
        self.refresh_table()

    def insert_row(self):
        """Insert row at current position"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.model.add_row(current_row)
        else:
            self.model.add_row()
        self.refresh_table()

    def delete_row(self):
        """Delete current row"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.model.delete_row(current_row)
            self.refresh_table()
        else:
            QMessageBox.warning(self, "Warning", "Please select a row to delete.")

    def add_column(self):
        """Add column at end"""
        name, ok = QInputDialog.getText(self, "Add Column", "Column name:")
        if ok:
            self.model.add_column(name=name if name else None)
            self.refresh_table()

    def insert_column(self):
        """Insert column at current position"""
        current_col = self.table.currentColumn()
        name, ok = QInputDialog.getText(self, "Insert Column", "Column name:")
        if ok:
            if current_col >= 0:
                self.model.add_column(current_col, name if name else None)
            else:
                self.model.add_column(name=name if name else None)
            self.refresh_table()

    def delete_column(self):
        """Delete current column"""
        current_col = self.table.currentColumn()
        if current_col >= 0:
            self.model.delete_column(current_col)
            self.refresh_table()
        else:
            QMessageBox.warning(self, "Warning", "Please select a column to delete.")

    def rename_column(self):
        """Rename current column"""
        current_col = self.table.currentColumn()
        if current_col >= 0:
            old_name = self.model.get_column_names()[current_col]
            new_name, ok = QInputDialog.getText(
                self, "Rename Column", "New column name:", text=old_name
            )
            if ok and new_name:
                self.model.rename_column(current_col, new_name)
                self.refresh_table()
        else:
            QMessageBox.warning(self, "Warning", "Please select a column to rename.")

    def update_title(self):
        """Update window title"""
        title = "CSV Editor"
        if self.model.current_file:
            title += f" - {Path(self.model.current_file).name}"
        if self.model.modified:
            title += " *"
        self.setWindowTitle(title)

    def closeEvent(self, event):
        """Handle window close"""
        if self.check_save():
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CSV Editor")
    window = CSVEditorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
