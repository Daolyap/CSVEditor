# CSV Editor

A modern, feature-rich CSV editor built with Python and PyQt6. Edit CSV files with a professional interface that supports all essential operations on rows, columns, and cells.

## Features

### File Operations
- **New**: Create a new CSV file with custom dimensions
- **Open**: Open existing CSV files
- **Save**: Save changes to the current file
- **Save As**: Save to a new file location

### Row Operations
- **Add Row**: Add a new row at the end (Ctrl+R)
- **Insert Row**: Insert a row above the current selection (Ctrl+Shift+R)
- **Delete Row**: Delete the selected row (Ctrl+D)

### Column Operations
- **Add Column**: Add a new column at the end (Ctrl+L)
- **Insert Column**: Insert a column before the current selection (Ctrl+Shift+L)
- **Delete Column**: Delete the selected column (Ctrl+Shift+D)
- **Rename Column**: Rename the selected column (F2)

### Editing Features
- **Cell Editing**: Click any cell to edit its contents
- **Undo/Redo**: Full undo/redo support (Ctrl+Z / Ctrl+Y)
- **Context Menu**: Right-click for quick access to operations
- **Keyboard Shortcuts**: Comprehensive keyboard support

### UI Features
- Modern, clean interface with professional styling
- Alternating row colors for better readability
- Resizable columns
- Modified indicator in title bar
- Confirmation prompts for unsaved changes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/daolyap/CSVEditor.git
cd CSVEditor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python csv_editor.py
```

## Keyboard Shortcuts

### File Operations
- `Ctrl+N` - New file
- `Ctrl+O` - Open file
- `Ctrl+S` - Save
- `Ctrl+Shift+S` - Save As
- `Ctrl+Q` - Quit

### Edit Operations
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo

### Row Operations
- `Ctrl+R` - Add row
- `Ctrl+Shift+R` - Insert row above
- `Ctrl+D` - Delete row

### Column Operations
- `Ctrl+L` - Add column
- `Ctrl+Shift+L` - Insert column left
- `Ctrl+Shift+D` - Delete column
- `F2` - Rename column

## Requirements

- Python 3.7+
- PyQt6 6.7.0+
- pandas 2.2.1+

## License

This project is open source and available under the MIT License.
