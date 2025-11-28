import sys
import csv
import copy
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QFileDialog, QMessageBox, QToolBar,
    QMenu, QInputDialog, QHeaderView, QDialog, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QCheckBox
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
        """Load CSV file with robust error handling and auto header detection"""

        def try_load_strategy(skiprows=None, encoding='utf-8', sep=','):
            """Helper function to try loading with specific parameters"""
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    df = pd.read_csv(
                        filepath,
                        dtype=str,
                        keep_default_na=False,
                        on_bad_lines='skip',
                        encoding=encoding,
                        sep=sep,
                        skiprows=skiprows,
                        engine='python' if sep is None else 'c'
                    )
                return df
            except:
                return None

        # Try different combinations of encodings and separators
        encodings = ['utf-8', 'latin-1', 'utf-8-sig', 'cp1252']
        separators = [',', '\t', ';', None]  # None means auto-detect

        best_df = None
        best_score = -1

        # First, try different encodings and separators WITHOUT skipping rows
        for encoding in encodings:
            for sep in separators:
                df = try_load_strategy(skiprows=None, encoding=encoding, sep=sep)
                if df is not None and len(df) > 0:
                    # Score based on: number of rows, number of columns, data completeness
                    score = len(df) * len(df.columns)
                    if score > best_score:
                        best_score = score
                        best_df = df.copy()

        # Now try with skipping initial rows (in case of metadata)
        # Try skipping 0-10 rows to find the real header
        for skip in range(1, 11):
            for encoding in encodings:
                for sep in separators:
                    df = try_load_strategy(skiprows=range(skip), encoding=encoding, sep=sep)
                    if df is not None and len(df) > 0:
                        # Higher score for more data rows and columns
                        score = len(df) * len(df.columns) * 1.1  # Slight bonus for skiprow strategies
                        if score > best_score:
                            best_score = score
                            best_df = df.copy()

        if best_df is None:
            raise Exception("Could not load CSV file with any strategy")

        self.df = best_df

        # Ensure we have at least some data
        if len(self.df.columns) == 0:
            self.df = pd.DataFrame({'Column 1': ['']})

        # Fill any NaN values with empty strings
        self.df = self.df.fillna('')

        # Ensure all column names are strings and handle duplicates
        cols = []
        for i, col in enumerate(self.df.columns):
            col_name = str(col) if col and str(col).strip() else f"Column {i+1}"
            # Handle duplicate column names
            if col_name in cols:
                j = 1
                while f"{col_name}_{j}" in cols:
                    j += 1
                col_name = f"{col_name}_{j}"
            cols.append(col_name)
        self.df.columns = cols

        self.current_file = filepath
        self.modified = False
        self.undo_stack.clear()
        self.redo_stack.clear()
        return True

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

    def delete_rows(self, rows):
        """Delete multiple rows"""
        if rows:
            self.save_state()
            # Sort in reverse to delete from end to beginning
            rows_sorted = sorted(set(rows), reverse=True)
            for row in rows_sorted:
                if 0 <= row < len(self.df):
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

    def delete_columns(self, cols):
        """Delete multiple columns"""
        if cols:
            self.save_state()
            # Sort in reverse to delete from end to beginning
            cols_sorted = sorted(set(cols), reverse=True)
            for col in cols_sorted:
                if 0 <= col < len(self.df.columns):
                    self.df = self.df.drop(self.df.columns[col], axis=1)

    def rename_column(self, col, new_name):
        """Rename column"""
        if 0 <= col < len(self.df.columns):
            self.save_state()
            self.df.columns.values[col] = new_name

    def clear_cells(self, cells):
        """Clear multiple cells"""
        if cells:
            self.save_state()
            for row, col in cells:
                if 0 <= row < len(self.df) and 0 <= col < len(self.df.columns):
                    self.df.iloc[row, col] = ''

    def fill_cells(self, cells, value):
        """Fill multiple cells with a value"""
        if cells:
            self.save_state()
            for row, col in cells:
                if 0 <= row < len(self.df) and 0 <= col < len(self.df.columns):
                    self.df.iloc[row, col] = value

    def find_replace(self, find_text, replace_text, match_case=False, whole_cell=False):
        """Find and replace text across all cells"""
        self.save_state()
        count = 0
        for row in range(len(self.df)):
            for col in range(len(self.df.columns)):
                cell_value = str(self.df.iloc[row, col])

                if whole_cell:
                    if match_case:
                        if cell_value == find_text:
                            self.df.iloc[row, col] = replace_text
                            count += 1
                    else:
                        if cell_value.lower() == find_text.lower():
                            self.df.iloc[row, col] = replace_text
                            count += 1
                else:
                    if match_case:
                        if find_text in cell_value:
                            self.df.iloc[row, col] = cell_value.replace(find_text, replace_text)
                            count += cell_value.count(find_text)
                    else:
                        # Case-insensitive replace
                        import re
                        pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                        matches = len(pattern.findall(cell_value))
                        if matches > 0:
                            self.df.iloc[row, col] = pattern.sub(replace_text, cell_value)
                            count += matches
        return count

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

        # Enable multi-selection
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)

        # Clipboard for copy/paste
        self.clipboard_data = None

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

        edit_menu.addSeparator()

        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_selection)
        edit_menu.addAction(copy_action)

        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.cut_selection)
        edit_menu.addAction(cut_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_selection)
        edit_menu.addAction(paste_action)

        delete_action = QAction("Clear Selected Cells", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self.clear_selected_cells)
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        find_replace_action = QAction("Find && Replace...", self)
        find_replace_action.setShortcut(QKeySequence.StandardKey.Find)
        find_replace_action.triggered.connect(self.find_replace_dialog)
        edit_menu.addAction(find_replace_action)

        edit_menu.addSeparator()

        fill_down_action = QAction("Fill Down", self)
        fill_down_action.setShortcut("Ctrl+Down")
        fill_down_action.triggered.connect(self.fill_down)
        edit_menu.addAction(fill_down_action)

        fill_right_action = QAction("Fill Right", self)
        fill_right_action.setShortcut("Ctrl+Right")
        fill_right_action.triggered.connect(self.fill_right)
        edit_menu.addAction(fill_right_action)

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
        selected_items = self.table.selectedItems()

        # Edit operations
        if selected_items:
            copy_action = QAction("Copy", self)
            copy_action.triggered.connect(self.copy_selection)
            menu.addAction(copy_action)

            cut_action = QAction("Cut", self)
            cut_action.triggered.connect(self.cut_selection)
            menu.addAction(cut_action)

            paste_action = QAction("Paste", self)
            paste_action.triggered.connect(self.paste_selection)
            menu.addAction(paste_action)

            clear_action = QAction("Clear Selected Cells", self)
            clear_action.triggered.connect(self.clear_selected_cells)
            menu.addAction(clear_action)

            menu.addSeparator()

            fill_down_action = QAction("Fill Down", self)
            fill_down_action.triggered.connect(self.fill_down)
            menu.addAction(fill_down_action)

            fill_right_action = QAction("Fill Right", self)
            fill_right_action.triggered.connect(self.fill_right)
            menu.addAction(fill_right_action)

            menu.addSeparator()

        # Row operations
        add_row_action = QAction("Add Row", self)
        add_row_action.triggered.connect(self.add_row)
        menu.addAction(add_row_action)

        insert_row_action = QAction("Insert Row Above", self)
        insert_row_action.triggered.connect(self.insert_row)
        menu.addAction(insert_row_action)

        delete_row_action = QAction("Delete Selected Rows", self)
        delete_row_action.triggered.connect(self.delete_selected_rows)
        menu.addAction(delete_row_action)

        menu.addSeparator()

        # Column operations
        add_col_action = QAction("Add Column", self)
        add_col_action.triggered.connect(self.add_column)
        menu.addAction(add_col_action)

        insert_col_action = QAction("Insert Column Left", self)
        insert_col_action.triggered.connect(self.insert_column)
        menu.addAction(insert_col_action)

        delete_col_action = QAction("Delete Selected Columns", self)
        delete_col_action.triggered.connect(self.delete_selected_columns)
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

    def delete_selected_rows(self):
        """Delete all selected rows"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select rows to delete.")
            return

        # Get unique row numbers
        rows = sorted(set(item.row() for item in selected_items), reverse=True)

        reply = QMessageBox.question(
            self, "Delete Rows",
            f"Delete {len(rows)} row(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.model.delete_rows(rows)
            self.refresh_table()

    def delete_selected_columns(self):
        """Delete all selected columns"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select columns to delete.")
            return

        # Get unique column numbers
        cols = sorted(set(item.column() for item in selected_items), reverse=True)

        reply = QMessageBox.question(
            self, "Delete Columns",
            f"Delete {len(cols)} column(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.model.delete_columns(cols)
            self.refresh_table()

    def copy_selection(self):
        """Copy selected cells to clipboard"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        # Get selection bounds
        rows = sorted(set(item.row() for item in selected_items))
        cols = sorted(set(item.column() for item in selected_items))

        # Create 2D array of selected data
        self.clipboard_data = []
        for row in rows:
            row_data = []
            for col in cols:
                value = self.model.get_value(row, col)
                row_data.append(value)
            self.clipboard_data.append(row_data)

    def cut_selection(self):
        """Cut selected cells to clipboard"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        # Copy first
        self.copy_selection()

        # Then clear
        cells = [(item.row(), item.column()) for item in selected_items]
        self.model.clear_cells(cells)
        self.refresh_table()

    def paste_selection(self):
        """Paste clipboard data to selected cells"""
        if not self.clipboard_data:
            return

        current_item = self.table.currentItem()
        if not current_item:
            return

        start_row = current_item.row()
        start_col = current_item.column()

        self.model.save_state()

        for i, row_data in enumerate(self.clipboard_data):
            for j, value in enumerate(row_data):
                row = start_row + i
                col = start_col + j
                if 0 <= row < self.model.row_count and 0 <= col < self.model.column_count:
                    self.model.df.iloc[row, col] = value

        self.model.modified = True
        self.refresh_table()

    def clear_selected_cells(self):
        """Clear selected cells"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        cells = [(item.row(), item.column()) for item in selected_items]
        self.model.clear_cells(cells)
        self.refresh_table()

    def fill_down(self):
        """Fill down from top cell to selected cells"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        # Get selection bounds
        rows = sorted(set(item.row() for item in selected_items))
        cols = sorted(set(item.column() for item in selected_items))

        if len(rows) < 2:
            return

        # For each column, fill from the first row to all others
        for col in cols:
            source_value = self.model.get_value(rows[0], col)
            cells = [(row, col) for row in rows[1:]]
            self.model.fill_cells(cells, source_value)

        self.refresh_table()

    def fill_right(self):
        """Fill right from left cell to selected cells"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return

        # Get selection bounds
        rows = sorted(set(item.row() for item in selected_items))
        cols = sorted(set(item.column() for item in selected_items))

        if len(cols) < 2:
            return

        # For each row, fill from the first column to all others
        for row in rows:
            source_value = self.model.get_value(row, cols[0])
            cells = [(row, col) for col in cols[1:]]
            self.model.fill_cells(cells, source_value)

        self.refresh_table()

    def find_replace_dialog(self):
        """Show find and replace dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Find and Replace")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Find text
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        find_input = QLineEdit()
        find_layout.addWidget(find_input)
        layout.addLayout(find_layout)

        # Replace text
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace:"))
        replace_input = QLineEdit()
        replace_layout.addWidget(replace_input)
        layout.addLayout(replace_layout)

        # Options
        match_case_check = QCheckBox("Match case")
        layout.addWidget(match_case_check)

        whole_cell_check = QCheckBox("Match whole cell only")
        layout.addWidget(whole_cell_check)

        # Buttons
        button_layout = QHBoxLayout()
        replace_all_button = QPushButton("Replace All")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(replace_all_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        def do_replace():
            find_text = find_input.text()
            replace_text = replace_input.text()

            if not find_text:
                QMessageBox.warning(dialog, "Warning", "Please enter text to find.")
                return

            count = self.model.find_replace(
                find_text, replace_text,
                match_case=match_case_check.isChecked(),
                whole_cell=whole_cell_check.isChecked()
            )

            self.refresh_table()
            QMessageBox.information(dialog, "Replace Complete",
                                   f"Replaced {count} occurrence(s).")
            dialog.accept()

        replace_all_button.clicked.connect(do_replace)
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec()

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
    app.setOrganizationName("CSVEditor")
    app.setApplicationVersion("1.0.0")
    
    window = CSVEditorWindow()
    window.show()
    
    # Check if a file was passed as a command line argument
    # This enables opening CSV files directly via file association
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if Path(filepath).exists() and Path(filepath).suffix.lower() == '.csv':
            try:
                window.model.load_csv(filepath)
                window.refresh_table()
            except Exception as e:
                QMessageBox.critical(window, "Error", f"Failed to open file: {str(e)}")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
