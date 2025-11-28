"""
CSV Data Model Module

This module contains the CSVDataModel class which handles all CSV data operations
with undo/redo support. It is separated from the GUI code to allow headless testing.
"""
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
