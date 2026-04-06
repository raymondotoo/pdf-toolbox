from __future__ import annotations

import os
import pathlib

from setuptools import setup

ROOT_DIR = pathlib.Path(__file__).resolve().parent
VERSION = os.environ.get(
    "PDF_TOOLBOX_VERSION",
    (ROOT_DIR / "VERSION").read_text(encoding="utf-8").strip(),
)
APP_NAME = os.environ.get("PDF_TOOLBOX_APP_NAME", "PDF Toolbox")
BUNDLE_ID = os.environ.get("PDF_TOOLBOX_BUNDLE_ID", "com.raymondotoo.pdftoolbox")
MIN_MACOS = os.environ.get("PDF_TOOLBOX_MIN_MACOS", "12.0")

APP = ["pdf_toolkit_app.py"]
BUNDLE_PACKAGES = ["pdf_toolkit", "pypdf", "pymupdf", "cv2", "numpy"]
OPTIONS = {
    "argv_emulation": False,
    "packages": BUNDLE_PACKAGES,
    "includes": [
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "tkinter.scrolledtext",
        "tkinter.ttk",
        "cv2",
        "fitz",
        "numpy",
        "pypdf",
    ],
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
