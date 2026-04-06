# Build Guide

## Requirements

- macOS
- Python 3.12 or another compatible Python with `tkinter`
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
