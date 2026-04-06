#!/usr/bin/env python3
from __future__ import annotations

import os
import pathlib

from pdf_toolkit.runtime import bootstrap_local_site_packages

bootstrap_local_site_packages(pathlib.Path(__file__).resolve())

from pdf_toolkit.gui import main as launch_gui


def main() -> None:
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

    launch_gui()


if __name__ == "__main__":
    main()
