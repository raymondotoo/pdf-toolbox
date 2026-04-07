#!/usr/bin/env python3
from __future__ import annotations

import os
import pathlib
import sys
import traceback

from pdf_toolkit.runtime import bootstrap_local_site_packages

bootstrap_local_site_packages(pathlib.Path(__file__).resolve())


def configure_tk_resources(script_path: pathlib.Path) -> None:
    resources_dir = script_path.resolve().parent
    for env_name, folder_name in (
        ("TCL_LIBRARY", "tcl8.6"),
        ("TK_LIBRARY", "tk8.6"),
    ):
        if os.environ.get(env_name):
            continue
        candidate = resources_dir / folder_name
        if candidate.exists():
            os.environ[env_name] = str(candidate)


configure_tk_resources(pathlib.Path(__file__))


def write_launch_error_log(error_text: str) -> None:
    candidates = [
        pathlib.Path.home() / "Desktop" / "PDF Toolbox Launch Error.txt",
        pathlib.Path.home() / "PDF Toolbox Launch Error.txt",
    ]
    for candidate in candidates:
        try:
            candidate.write_text(error_text, encoding="utf-8")
            return
        except OSError:
            continue


def main() -> None:
    try:
        if os.environ.get("PDF_TOOLKIT_SELFTEST") == "1":
            import cv2
            import fitz
            import numpy
            import pypdf
            import tkinter

            print("selftest_ok")
            print(f"fitz={getattr(fitz, '__file__', 'built-in')}")
            print(f"cv2={getattr(cv2, '__file__', 'built-in')}")
            print(f"numpy={getattr(numpy, '__file__', 'built-in')}")
            print(f"pypdf={getattr(pypdf, '__file__', 'built-in')}")
            print(f"tkinter={getattr(tkinter, '__file__', 'built-in')}")
            return

        from pdf_toolkit.gui import main as launch_gui

        launch_gui()
    except Exception:
        error_text = traceback.format_exc()
        write_launch_error_log(error_text)
        sys.stderr.write(error_text)
        raise


if __name__ == "__main__":
    main()
