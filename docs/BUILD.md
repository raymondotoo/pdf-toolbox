# Build Guide

## Requirements

- macOS
- Python with `tkinter`
- Xcode Command Line Tools
- Network access to install Python packages when building for the first time

## Build Apple Silicon release

On an Apple Silicon Mac:

```bash
./scripts/build_arm64_release.sh
```

This creates:

- `dist/PDF Toolbox.app`
- `dist/PDF-Toolbox-macOS-Apple-Silicon-1.0.0.zip`
- `release-assets/apple-silicon/PDF-Toolbox-macOS-Apple-Silicon-1.0.0.zip`

## Build Intel release

For older Intel Macs, build from:

- an actual Intel Mac, or
- an x86_64 Python / Rosetta environment that truly installs x86_64 wheels

Run:

```bash
./scripts/build_intel_release.sh
```

This creates:

- `dist/PDF Toolbox.app`
- `dist/PDF-Toolbox-macOS-Intel-1.0.0.zip`
- `release-assets/intel/PDF-Toolbox-macOS-Intel-1.0.0.zip`

If you want the build script to refresh `pip` inside the build environment first, run:

```bash
PDF_TOOLBOX_UPGRADE_PIP=1 ./scripts/build_intel_release.sh
```

## Build legacy Intel / Mojave release

For Intel Macs that need macOS `10.14.6` support, use:

- an actual Intel Mac, or
- a true Rosetta / x86_64 Python 3.8 environment
- preferably the official Python.org 64-bit Intel Python 3.8 installer

Run:

```bash
PYTHON_BIN=/Library/Frameworks/Python.framework/Versions/3.8/bin/python3.8 ./scripts/build_legacy_intel_release.sh
```

This creates:

- `dist/PDF Toolbox.app`
- `dist/PDF-Toolbox-macOS-Legacy-Intel-1.0.0.zip`
- `release-assets/legacy-intel/PDF-Toolbox-macOS-Legacy-Intel-1.0.0.zip`

This legacy track uses a separate dependency set in `requirements-mac-app-legacy.txt`
because Mojave support requires older compatible OpenCV / NumPy / PyMuPDF wheels.

If you are creating the legacy build from an extracted Python.org framework on Apple Silicon
instead of installing that Python into `/Library/Frameworks`, also set:

```bash
TCL_LIBRARY=/path/to/Python.framework/Versions/3.8/lib/tcl8.6
TK_LIBRARY=/path/to/Python.framework/Versions/3.8/lib/tk8.6
PDF_TOOLBOX_DYLD_FRAMEWORK_PATH=/path/to/Library/Frameworks
PDF_TOOLBOX_DYLD_LIBRARY_PATH=/path/to/Python.framework/Versions/3.8/lib
PYTHON_BIN=/path/to/Python.framework/Versions/3.8/bin/python3.8
./scripts/build_legacy_intel_release.sh
```

## Important note about older macOS versions

“Older Macs” can mean two different things:

- Intel hardware
- older macOS versions

Those are related, but not the same.

If you want support for significantly older macOS releases, you may also need:

- an older compatible Python runtime
- an older compatible wheel set for `numpy`, `opencv`, `pymupdf`, and `py2app`
- a lower deployment target

You can override the minimum macOS version during build:

```bash
PDF_TOOLBOX_MIN_MACOS=11.0 ./scripts/build_intel_release.sh
```

For very old Intel systems, use a Python build that still supports that target macOS version before lowering the deployment target.

## Update release checksums

After staging release files:

```bash
./scripts/update_release_checksums.sh
```
