# CSV Editor MSI Installer

This directory contains the WiX Toolset configuration and build scripts for creating a professional MSI installer for CSV Editor.

## Prerequisites

### WiX Toolset Installation

You need to install WiX Toolset to build the MSI installer:

**Option 1: WiX Toolset v3 (Stable)**
- Download from: https://github.com/wixtoolset/wix3/releases
- Download the `.exe` installer and run it
- Version 3.11.2 or later recommended

**Option 2: WiX Toolset v4 (Latest)**
- Download from: https://github.com/wixtoolset/wix4/releases
- Install via: `dotnet tool install --global wix`

After installation, ensure the WiX `bin` directory is in your system PATH.

### Verify Installation

Open a command prompt and run:
```cmd
candle.exe -?
light.exe -?
```

If both commands work, WiX is properly installed.

## Building the MSI

### Method 1: Batch Script (Recommended for Windows)

```cmd
cd installer
build_msi.bat
```

### Method 2: PowerShell Script

```powershell
cd installer
.\build_msi.ps1
```

### Manual Build

If you prefer to build manually:

```cmd
cd installer

REM Step 1: Compile the WiX source
candle.exe -arch x64 -out obj\CSVEditor.wixobj CSVEditor.wxs

REM Step 2: Link and create MSI
light.exe -ext WixUIExtension -out CSVEditor.msi obj\CSVEditor.wixobj
```

## Installation Features

The MSI installer provides:

### Installation Location
- **Default**: `%LOCALAPPDATA%\CSVEditor` (per-user installation)
- User can choose custom location during installation

### What Gets Installed
- CSVEditor.exe (main application)
- csv.ico (application icon)
- Start Menu shortcut
- Desktop shortcut (optional)
- File association for `.csv` files
- Registry entries for proper uninstallation

### Apps & Features Integration
- Appears in Windows Settings > Apps & Features
- Shows app icon, version, and publisher
- Provides "Uninstall" button
- Includes support link to GitHub repository

### File Association
- Registers as handler for `.csv` files
- Allows setting as default application for CSV files
- "Open with CSV Editor" appears in context menu

## Testing the Installer

### Install
```cmd
msiexec /i CSVEditor.msi
```

Or simply double-click `CSVEditor.msi`

### Install Silently
```cmd
msiexec /i CSVEditor.msi /quiet
```

### Uninstall
```cmd
msiexec /x CSVEditor.msi
```

Or use Windows Settings > Apps & Features > CSV Editor > Uninstall

### Install with Logging
```cmd
msiexec /i CSVEditor.msi /l*v install.log
```

## File Structure

```
installer/
├── CSVEditor.wxs       # WiX source configuration
├── License.rtf         # End-user license agreement
├── build_msi.bat       # Windows batch build script
├── build_msi.ps1       # PowerShell build script
├── README.md           # This file
└── obj/                # Build artifacts (generated)
    └── CSVEditor.wixobj
```

## Troubleshooting

### "WiX Toolset not found"
- Ensure WiX is installed
- Check that WiX bin directory is in PATH
- Restart command prompt after installation

### "Error LGHT0001: The system cannot find the file"
- Ensure the EXE exists at `dist\CSVEditor.exe`
- Build the PyInstaller executable first: `pyinstaller CSVEditor.spec`

### "Error LGHT0094: Unresolved reference to symbol"
- Clean the build: Delete `obj` folder and rebuild
- Ensure all GUIDs in the WXS file are unique

### MSI doesn't appear in Apps & Features
- Ensure you're installing with user permissions
- Check registry: `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall`

## Customization

### Change Version
Edit `CSVEditor.wxs`:
```xml
<Product Version="1.0.0.0" ...>
```

### Change Install Location
Edit `CSVEditor.wxs`:
```xml
<Directory Id="LocalAppDataFolder">
  <Directory Id="INSTALLFOLDER" Name="CSVEditor">
```

Change `LocalAppDataFolder` to:
- `ProgramFilesFolder` - Program Files (requires admin)
- `ProgramFiles64Folder` - Program Files (64-bit)
- `AppDataFolder` - Roaming AppData

### Add/Remove Features
Edit the `<ComponentGroup>` sections in `CSVEditor.wxs`

## Release Checklist

Before creating a release:

1. ✅ Build the EXE with PyInstaller
2. ✅ Test the EXE standalone
3. ✅ Build the MSI installer
4. ✅ Test MSI installation
5. ✅ Verify Start Menu shortcut works
6. ✅ Verify file association works
7. ✅ Verify uninstallation works
8. ✅ Check Apps & Features entry
9. ✅ Tag the release in Git
10. ✅ Upload MSI to GitHub Releases

## Support

For issues or questions:
- GitHub Issues: https://github.com/Daolyap/CSVEditor/issues
- WiX Documentation: https://wixtoolset.org/documentation/
