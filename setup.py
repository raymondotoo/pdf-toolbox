from __future__ import annotations

import os
import pathlib
import importlib.resources
from importlib.util import find_spec

from setuptools import setup

try:
    import importlib_resources
except ModuleNotFoundError:
    importlib_resources = None

if not hasattr(importlib.resources, "files") and importlib_resources is not None:
    importlib.resources.files = importlib_resources.files  # type: ignore[attr-defined]

ROOT_DIR = pathlib.Path(__file__).resolve().parent
VERSION = os.environ.get(
    "PDF_TOOLBOX_VERSION",
    (ROOT_DIR / "VERSION").read_text(encoding="utf-8").strip(),
)
APP_NAME = os.environ.get("PDF_TOOLBOX_APP_NAME", "PDF Toolbox")
BUNDLE_ID = os.environ.get("PDF_TOOLBOX_BUNDLE_ID", "com.raymondotoo.pdftoolbox")
MIN_MACOS = os.environ.get("PDF_TOOLBOX_MIN_MACOS", "12.0")

APP = ["pdf_toolkit_app.py"]
def module_exists(name: str) -> bool:
    return find_spec(name) is not None


BUNDLE_PACKAGES = ["pdf_toolkit", "pypdf", "cv2", "numpy"]
OPTIONAL_PACKAGES = ["pymupdf", "fitz"]
for package_name in OPTIONAL_PACKAGES:
    if module_exists(package_name):
        BUNDLE_PACKAGES.append(package_name)

INCLUDES = [
    "tkinter",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.scrolledtext",
    "tkinter.ttk",
    "cv2",
    "fitz",
    "numpy",
    "pypdf",
]
if module_exists("pymupdf"):
    INCLUDES.append("pymupdf")

OPTIONS = {
    "argv_emulation": False,
    "packages": BUNDLE_PACKAGES,
    "includes": INCLUDES,
    "plist": {
        "CFBundleName": APP_NAME,
        "CFBundleDisplayName": APP_NAME,
        "CFBundleIdentifier": BUNDLE_ID,
        "CFBundleShortVersionString": VERSION,
        "CFBundleVersion": VERSION,
        "LSMinimumSystemVersion": MIN_MACOS,
    },
}

setup(
    app=APP,
    name=APP_NAME,
    packages=["pdf_toolkit"],
    options={"py2app": OPTIONS},
)
