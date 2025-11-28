# CSV Editor

A modern, feature-rich CSV editor built with Python and PyQt6. Edit CSV files with a professional interface that supports all essential operations on rows, columns, and cells.

**Now available as a Windows desktop application with MSI installer!**

## Installation

### Windows (Recommended)

1. **Download the MSI installer** from the [Releases](https://github.com/Daolyap/CSVEditor/releases) page
2. Run `CSVEditor.msi` and follow the installation wizard
3. The application will be installed to Program Files and added to your Start Menu
4. You can set CSV Editor as the default application for `.csv` files in Windows Settings

### From Source

1. Clone the repository:
```bash
git clone https://github.com/daolyap/CSVEditor.git
cd CSVEditor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python csv_editor.py
```

## Features

### File Operations
- **New**: Create a new CSV file with custom dimensions
- **Open**: Open existing CSV files
- **Save**: Save changes to the current file
- **Save As**: Save to a new file location
- **File Association**: Double-click CSV files to open them directly

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
- **Copy/Cut/Paste**: Standard clipboard operations
- **Find & Replace**: Search and replace text across all cells
- **Fill Down/Right**: Quickly fill cells with values
- **Multi-Select**: Select multiple cells, rows, or columns
- **Context Menu**: Right-click for quick access to operations
- **Keyboard Shortcuts**: Comprehensive keyboard support

### UI Features
- Modern, clean interface with professional styling
- Alternating row colors for better readability
- Resizable columns
- Modified indicator in title bar
- Confirmation prompts for unsaved changes

## Building from Source (Windows)

### Prerequisites
- Python 3.8 or later
- pip (Python package manager)
- For MSI installer: [WiX Toolset v4+](https://wixtoolset.org/releases/)

### Build the Application

**Using Command Prompt:**
```cmd
build.bat
```

**Using PowerShell:**
```powershell
.\Build.ps1
```

This will:
1. Install Python dependencies
2. Install PyInstaller
3. Build the executable to `dist\CSVEditor\`

### Build the MSI Installer

**Using Command Prompt:**
```cmd
build_installer.bat
```

**Using PowerShell:**
```powershell
.\Build-Installer.ps1
```

This will create `installer\CSVEditor.msi`.

### What the Installer Does

The MSI installer:
- Installs CSV Editor to `C:\Program Files\CSV Editor`
- Creates Start Menu shortcuts
- Creates Desktop shortcut
- Registers file association for `.csv` files
- Adds CSV Editor to the "Open with" menu for CSV files

## Setting as Default CSV Application

After installation, you can set CSV Editor as the default application for CSV files:

1. Right-click any `.csv` file
2. Select "Open with" → "Choose another app"
3. Select "CSV Editor"
4. Check "Always use this app to open .csv files"
5. Click "OK"

Alternatively:
1. Open Windows Settings
2. Go to Apps → Default apps
3. Search for ".csv" or scroll to find it
4. Select "CSV Editor"

## Keyboard Shortcuts

### File Operations
| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+Q` | Quit |

### Edit Operations
| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+C` | Copy |
| `Ctrl+X` | Cut |
| `Ctrl+V` | Paste |
| `Ctrl+F` | Find & Replace |
| `Delete` | Clear selected cells |
| `Ctrl+Down` | Fill Down |
| `Ctrl+Right` | Fill Right |

### Row Operations
| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Add row |
| `Ctrl+Shift+R` | Insert row above |
| `Ctrl+D` | Delete row |

### Column Operations
| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Add column |
| `Ctrl+Shift+L` | Insert column left |
| `Ctrl+Shift+D` | Delete column |
| `F2` | Rename column |

## Requirements

### For Running from Source
- Python 3.8+
- PyQt6 6.7.0+
- pandas 2.2.1+

### For Building
- PyInstaller (installed automatically by build scripts)
- WiX Toolset v4+ (for MSI installer only)

## GitHub Actions

This repository includes automated builds via GitHub Actions:
- Every push to `main`/`master` triggers a build
- Tagged releases (`v*`) automatically create MSI installers
- Build artifacts are available for download from the Actions tab

## License

This project is open source and available under the MIT License.
