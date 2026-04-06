from __future__ import annotations

import pathlib
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from .operations import (
    CompressionOptions,
    WatermarkOptions,
    collect_pdfs_sorted_by_date_prefix,
    compress_pdf,
    extract_date_prefix,
    format_file_size,
    images_to_pdf,
    merge_pdfs,
    remove_watermark_file,
    split_pdf_pages,
)

HELP_GUIDE_TEXT = """Quick Start

1. Merge PDFs
Add two or more PDFs, arrange them in order, choose an output file, and click Merge PDFs.

2. Date-Sorted Merge
Use this when filenames begin with YYYYMMDD. Load a folder or add files manually, then merge in date order.

3. Images to PDF
Add PNG, JPG, JPEG, BMP, TIFF, or WEBP images, arrange them, choose output, and convert them into one PDF.

4. Split Pages
Choose one PDF, pick an output folder and optional filename prefix, then split it into one PDF per page.

5. Remove Watermark
Auto is the recommended setting. It tries the lighter PDF overlay cleanup first and falls back to inpaint when needed.
Use Overlay for small scanner logos near page corners. Use Inpaint for harder raster watermarks.

6. Compress PDF
Pick a PDF, choose DPI and JPEG quality, and compress it for smaller file size. The app shows the file size before and after compression.

Tips

- Keep original source files until you confirm the result looks right.
- For forms and scanned documents, 200 DPI and JPEG quality 75 are usually a good balance.
- If a watermark still shows, retry with Inpaint.
"""

ABOUT_BRIEF_TEXT = (
    "Designed by Raymond Otoo Ph.D. This edition is tailored for fast PDF cleanup, "
    "merging, splitting, compression, and document packaging on macOS."
)

ABOUT_COPYRIGHT_TEXT = "Copyright 2026 Raymond Otoo Ph.D. All rights reserved."


class PdfToolkitApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PDF Toolbox")
        self.geometry("980x760")
        self.minsize(920, 700)

        self._worker: threading.Thread | None = None

        self.status_var = tk.StringVar(value="Ready")
        self.merge_output_var = tk.StringVar(value="merged.pdf")
        self.bank_output_var = tk.StringVar(value="merged_by_date.pdf")
        self.bank_folder_var = tk.StringVar(value=str(pathlib.Path.cwd()))
        self.bank_pattern_var = tk.StringVar(value="*.pdf")
        self.images_output_var = tk.StringVar(value="images.pdf")
        self.images_dpi_var = tk.IntVar(value=300)
        self.split_input_var = tk.StringVar()
        self.split_output_dir_var = tk.StringVar(value=str(pathlib.Path.cwd()))
        self.split_prefix_var = tk.StringVar()
        self.watermark_input_var = tk.StringVar()
        self.watermark_output_var = tk.StringVar(value="watermark_removed.pdf")
        self.watermark_mode_var = tk.StringVar(value="auto")
        self.watermark_dpi_var = tk.IntVar(value=300)
        self.watermark_roi_var = tk.StringVar(value="bottom")
        self.watermark_roi_height_var = tk.DoubleVar(value=0.25)
        self.watermark_threshold_var = tk.IntVar(value=16)
        self.watermark_dilate_var = tk.IntVar(value=2)
        self.watermark_inpaint_radius_var = tk.IntVar(value=3)
        self.watermark_jpeg_quality_var = tk.IntVar(value=85)
        self.compress_input_var = tk.StringVar()
        self.compress_output_var = tk.StringVar(value="compressed.pdf")
        self.compress_dpi_var = tk.IntVar(value=200)
        self.compress_quality_var = tk.IntVar(value=75)
        self.compress_input_size_var = tk.StringVar(value="No file selected")
        self.compress_output_size_var = tk.StringVar(value="Not compressed yet")

        self._build_ui()

    def _build_ui(self) -> None:
        self._build_menu()

        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x")
        ttk.Label(
            header,
            text="PDF Toolbox",
            font=("Helvetica", 22, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Merge, sort, split, clean, and compress PDFs from one Mac app.",
        ).pack(anchor="w", pady=(4, 12))

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        self.notebook.add(self._build_merge_tab(self.notebook), text="Merge PDFs")
        self.notebook.add(self._build_bank_tab(self.notebook), text="Date-Sorted Merge")
        self.notebook.add(self._build_images_tab(self.notebook), text="Images to PDF")
        self.notebook.add(self._build_split_tab(self.notebook), text="Split Pages")
        self.notebook.add(self._build_watermark_tab(self.notebook), text="Remove Watermark")
        self.notebook.add(self._build_compress_tab(self.notebook), text="Compress PDF")
        self.help_tab = self._build_help_tab(self.notebook)
        self.notebook.add(self.help_tab, text="Guide & About")

        footer = ttk.Frame(container)
        footer.pack(fill="both", expand=False, pady=(12, 0))
        ttk.Label(footer, textvariable=self.status_var).pack(anchor="w", pady=(0, 6))

        self.log_widget = ScrolledText(footer, height=12, wrap="word")
        self.log_widget.pack(fill="both", expand=False)
        self.log("App ready.")

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self)
        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="Guide / Help", command=self.show_help_tab)
        help_menu.add_command(label="About PDF Toolbox", command=self.show_about_dialog)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu_bar)

    def _build_merge_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)

        ttk.Label(
            frame,
            text="Choose two or more PDFs, arrange them in order, then save the combined file.",
        ).pack(anchor="w", pady=(0, 10))

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True)

        self.merge_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=16)
        self.merge_listbox.pack(side="left", fill="both", expand=True)

        controls = ttk.Frame(list_frame)
        controls.pack(side="left", fill="y", padx=(10, 0))
        ttk.Button(controls, text="Add PDFs", command=self.add_merge_files).pack(fill="x")
        ttk.Button(controls, text="Remove Selected", command=self.remove_merge_files).pack(
            fill="x", pady=(8, 0)
        )
        ttk.Button(controls, text="Move Up", command=self.move_merge_up).pack(
            fill="x", pady=(8, 0)
        )
        ttk.Button(controls, text="Move Down", command=self.move_merge_down).pack(
            fill="x", pady=(8, 0)
        )

        output_row = ttk.Frame(frame)
        output_row.pack(fill="x", pady=(12, 0))
        ttk.Label(output_row, text="Output").pack(anchor="w")
        ttk.Entry(output_row, textvariable=self.merge_output_var).pack(
            side="left", fill="x", expand=True, pady=(4, 0)
        )
        ttk.Button(output_row, text="Browse", command=self.choose_merge_output).pack(
            side="left", padx=(8, 0), pady=(4, 0)
        )

        ttk.Button(frame, text="Merge PDFs", command=self.run_merge).pack(
            anchor="e", pady=(14, 0)
        )
        return frame

    def _build_bank_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)

        ttk.Label(
            frame,
            text="Load PDFs whose filenames begin with YYYYMMDD, then merge them in date order.",
        ).pack(anchor="w", pady=(0, 10))

        folder_row = ttk.Frame(frame)
        folder_row.pack(fill="x")
        ttk.Label(folder_row, text="Folder").pack(anchor="w")
        ttk.Entry(folder_row, textvariable=self.bank_folder_var).pack(
            side="left", fill="x", expand=True, pady=(4, 0)
        )
        ttk.Button(folder_row, text="Browse", command=self.choose_bank_folder).pack(
            side="left", padx=(8, 0), pady=(4, 0)
        )

        pattern_row = ttk.Frame(frame)
        pattern_row.pack(fill="x", pady=(10, 0))
        ttk.Label(pattern_row, text="Pattern").pack(anchor="w")
        ttk.Entry(pattern_row, textvariable=self.bank_pattern_var).pack(
            side="left", fill="x", expand=True, pady=(4, 0)
        )
        ttk.Button(pattern_row, text="Load Folder", command=self.load_bank_folder).pack(
            side="left", padx=(8, 0), pady=(4, 0)
        )

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.bank_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=14)
        self.bank_listbox.pack(side="left", fill="both", expand=True)

        controls = ttk.Frame(list_frame)
        controls.pack(side="left", fill="y", padx=(10, 0))
        ttk.Button(controls, text="Add PDFs", command=self.add_bank_files).pack(fill="x")
        ttk.Button(controls, text="Sort by Date", command=self.sort_bank_files).pack(
            fill="x", pady=(8, 0)
        )
        ttk.Button(controls, text="Remove Selected", command=self.remove_bank_files).pack(
            fill="x", pady=(8, 0)
        )

        output_row = ttk.Frame(frame)
        output_row.pack(fill="x", pady=(12, 0))
        ttk.Label(output_row, text="Output").pack(anchor="w")
        ttk.Entry(output_row, textvariable=self.bank_output_var).pack(
            side="left", fill="x", expand=True, pady=(4, 0)
        )
        ttk.Button(output_row, text="Browse", command=self.choose_bank_output).pack(
            side="left", padx=(8, 0), pady=(4, 0)
        )

        ttk.Button(frame, text="Merge by Date", command=self.run_bank_merge).pack(
            anchor="e", pady=(14, 0)
        )
        return frame

    def _build_images_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)

        ttk.Label(
            frame,
            text="Choose PNG, JPEG, TIFF, BMP, or WEBP images and combine them into one PDF.",
        ).pack(anchor="w", pady=(0, 10))

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True)

        self.images_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=16)
        self.images_listbox.pack(side="left", fill="both", expand=True)

        controls = ttk.Frame(list_frame)
        controls.pack(side="left", fill="y", padx=(10, 0))
        ttk.Button(controls, text="Add Images", command=self.add_image_files).pack(fill="x")
        ttk.Button(controls, text="Remove Selected", command=self.remove_image_files).pack(
            fill="x", pady=(8, 0)
        )
        ttk.Button(controls, text="Move Up", command=self.move_images_up).pack(
            fill="x", pady=(8, 0)
        )
        ttk.Button(controls, text="Move Down", command=self.move_images_down).pack(
            fill="x", pady=(8, 0)
        )

        output_row = ttk.Frame(frame)
        output_row.pack(fill="x", pady=(12, 0))
        ttk.Label(output_row, text="Output").pack(anchor="w")
        ttk.Entry(output_row, textvariable=self.images_output_var).pack(
            side="left", fill="x", expand=True, pady=(4, 0)
        )
        ttk.Button(output_row, text="Browse", command=self.choose_images_output).pack(
            side="left", padx=(8, 0), pady=(4, 0)
        )

        options = ttk.Frame(frame)
        options.pack(fill="x", pady=(14, 0))
        self._labeled_spinbox(options, "DPI", self.images_dpi_var, 120, 400, 0, 0)

        ttk.Button(frame, text="Convert Images to PDF", command=self.run_images_to_pdf).pack(
            anchor="e", pady=(16, 0)
        )
        return frame

    def _build_split_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)

        ttk.Label(
            frame,
            text="Split one PDF into separate single-page PDF files.",
        ).pack(anchor="w", pady=(0, 10))

        self._build_path_row(
            frame,
            "Input PDF",
            self.split_input_var,
            self.choose_split_input,
        )
        self._build_path_row(
            frame,
            "Output Folder",
            self.split_output_dir_var,
            self.choose_split_output_dir,
            pady=(10, 0),
        )

        prefix_row = ttk.Frame(frame)
        prefix_row.pack(fill="x", pady=(10, 0))
        ttk.Label(prefix_row, text="Filename Prefix").pack(anchor="w")
        ttk.Entry(prefix_row, textvariable=self.split_prefix_var).pack(
            fill="x", expand=True, pady=(4, 0)
        )

        ttk.Label(
            frame,
            text="Example output: my_file_page_01.pdf, my_file_page_02.pdf",
        ).pack(anchor="w", pady=(16, 0))
        ttk.Button(frame, text="Split Pages", command=self.run_split).pack(
            anchor="e", pady=(16, 0)
        )
        return frame

    def _build_watermark_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)

        ttk.Label(
            frame,
            text="Clean scanner watermarks. Auto uses the old overlay-style cleanup for PDFs first, then falls back to inpaint when needed.",
        ).pack(anchor="w", pady=(0, 10))

        self._build_path_row(
            frame,
            "Input",
            self.watermark_input_var,
            self.choose_watermark_input,
        )
        self._build_path_row(
            frame,
            "Output",
            self.watermark_output_var,
            self.choose_watermark_output,
            pady=(10, 0),
        )

        options = ttk.Frame(frame)
        options.pack(fill="x", pady=(14, 0))

        self._labeled_combobox(
            options,
            "Mode",
            self.watermark_mode_var,
            ["auto", "overlay", "inpaint"],
            0,
            0,
        )
        self._labeled_spinbox(
            options,
            "DPI",
            self.watermark_dpi_var,
            120,
            400,
            0,
            1,
        )
        self._labeled_combobox(
            options,
            "ROI",
            self.watermark_roi_var,
            ["bottom", "top", "full"],
            1,
            0,
        )
        self._labeled_spinbox(
            options,
            "ROI Height",
            self.watermark_roi_height_var,
            0.05,
            0.5,
            1,
            1,
            increment=0.01,
        )
        self._labeled_spinbox(
            options,
            "Threshold",
            self.watermark_threshold_var,
            1,
            100,
            2,
            0,
        )
        self._labeled_spinbox(
            options,
            "Dilate",
            self.watermark_dilate_var,
            0,
            10,
            2,
            1,
        )
        self._labeled_spinbox(
            options,
            "Inpaint Radius",
            self.watermark_inpaint_radius_var,
            1,
            10,
            3,
            0,
        )
        self._labeled_spinbox(
            options,
            "JPEG Quality",
            self.watermark_jpeg_quality_var,
            40,
            95,
            3,
            1,
        )

        ttk.Label(
            frame,
            text="Overlay is best for small scanner logos in PDF corners. Inpaint is still available for harder cases.",
        ).pack(anchor="w", pady=(16, 0))
        ttk.Button(frame, text="Remove Watermark", command=self.run_watermark).pack(
            anchor="e", pady=(16, 0)
        )
        return frame

    def _build_compress_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)

        ttk.Label(
            frame,
            text="Reduce file size by rasterizing each page to a lower resolution JPEG PDF. Best for scanned PDFs.",
        ).pack(anchor="w", pady=(0, 10))

        self._build_path_row(
            frame, "Input", self.compress_input_var, self.choose_compress_input
        )
        self._build_path_row(
            frame,
            "Output",
            self.compress_output_var,
            self.choose_compress_output,
            pady=(10, 0),
        )

        options = ttk.Frame(frame)
        options.pack(fill="x", pady=(14, 0))
        self._labeled_spinbox(options, "DPI", self.compress_dpi_var, 120, 300, 0, 0)
        self._labeled_spinbox(
            options, "JPEG Quality", self.compress_quality_var, 40, 95, 0, 1
        )

        size_row = ttk.Frame(frame)
        size_row.pack(fill="x", pady=(14, 0))
        size_row.columnconfigure(0, weight=1)
        size_row.columnconfigure(1, weight=1)

        input_size = ttk.Frame(size_row)
        input_size.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        ttk.Label(input_size, text="Selected File Size").pack(anchor="w")
        ttk.Label(input_size, textvariable=self.compress_input_size_var).pack(anchor="w", pady=(4, 0))

        output_size = ttk.Frame(size_row)
        output_size.grid(row=0, column=1, sticky="ew")
        ttk.Label(output_size, text="Compressed File Size").pack(anchor="w")
        ttk.Label(output_size, textvariable=self.compress_output_size_var).pack(anchor="w", pady=(4, 0))

        ttk.Label(
            frame,
            text="Tip: 200 DPI / quality 75 is a good balance for visa and scanner forms.",
        ).pack(anchor="w", pady=(16, 0))
        ttk.Button(frame, text="Compress PDF", command=self.run_compress).pack(
            anchor="e", pady=(16, 0)
        )
        return frame

    def _build_help_tab(self, parent: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)

        ttk.Label(
            frame,
            text="Guide / Help",
            font=("Helvetica", 18, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="A quick walkthrough of every tool in the app, plus the About section.",
        ).pack(anchor="w", pady=(4, 12))

        guide_box = ttk.LabelFrame(frame, text="Quick Guide", padding=12)
        guide_box.pack(fill="both", expand=True)
        ttk.Label(
            guide_box,
            text=HELP_GUIDE_TEXT,
            justify="left",
            wraplength=860,
        ).pack(anchor="w")

        about_box = ttk.LabelFrame(frame, text="About", padding=12)
        about_box.pack(fill="x", pady=(12, 0))
        ttk.Label(
            about_box,
            text="PDF Toolbox",
            font=("Helvetica", 16, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            about_box,
            text=ABOUT_BRIEF_TEXT,
            justify="left",
            wraplength=860,
        ).pack(anchor="w", pady=(6, 0))
        ttk.Label(
            about_box,
            text=ABOUT_COPYRIGHT_TEXT,
        ).pack(anchor="w", pady=(8, 0))

        button_row = ttk.Frame(frame)
        button_row.pack(fill="x", pady=(12, 0))
        ttk.Button(button_row, text="Open About Dialog", command=self.show_about_dialog).pack(
            anchor="e"
        )
        return frame

    def _build_path_row(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        command,
        pady: tuple[int, int] = (0, 0),
    ) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=pady)
        ttk.Label(row, text=label).pack(anchor="w")
        ttk.Entry(row, textvariable=variable).pack(
            side="left", fill="x", expand=True, pady=(4, 0)
        )
        ttk.Button(row, text="Browse", command=command).pack(
            side="left", padx=(8, 0), pady=(4, 0)
        )

    def _labeled_combobox(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        values: list[str],
        row: int,
        column: int,
    ) -> None:
        wrapper = ttk.Frame(parent)
        wrapper.grid(row=row, column=column, sticky="ew", padx=(0, 12), pady=(0, 10))
        parent.columnconfigure(column, weight=1)
        ttk.Label(wrapper, text=label).pack(anchor="w")
        ttk.Combobox(
            wrapper, textvariable=variable, values=values, state="readonly"
        ).pack(fill="x", pady=(4, 0))

    def _labeled_spinbox(
        self,
        parent: ttk.Frame,
        label: str,
        variable,
        minimum,
        maximum,
        row: int,
        column: int,
        increment=1,
    ) -> None:
        wrapper = ttk.Frame(parent)
        wrapper.grid(row=row, column=column, sticky="ew", padx=(0, 12), pady=(0, 10))
        parent.columnconfigure(column, weight=1)
        ttk.Label(wrapper, text=label).pack(anchor="w")
        ttk.Spinbox(
            wrapper,
            textvariable=variable,
            from_=minimum,
            to=maximum,
            increment=increment,
        ).pack(fill="x", pady=(4, 0))

    def log(self, message: str) -> None:
        self.log_widget.insert("end", message + "\n")
        self.log_widget.see("end")

    def set_status(self, message: str) -> None:
        self.status_var.set(message)
        self.log(message)

    def show_help_tab(self) -> None:
        self.notebook.select(self.help_tab)

    def show_about_dialog(self) -> None:
        messagebox.showinfo(
            "About PDF Toolbox",
            "PDF Toolbox\n\n"
            + ABOUT_BRIEF_TEXT
            + "\n\n"
            + ABOUT_COPYRIGHT_TEXT,
        )

    def _run_async(self, label: str, work) -> None:
        if self._worker and self._worker.is_alive():
            messagebox.showinfo("PDF Toolbox", "A task is already running.")
            return

        def runner() -> None:
            self.after(0, lambda: self.status_var.set(f"{label}..."))
            try:
                result = work()
            except Exception as exc:
                self.after(0, lambda: self._task_failed(label, exc))
                return
            self.after(0, lambda: self._task_succeeded(label, result))

        self._worker = threading.Thread(target=runner, daemon=True)
        self._worker.start()

    def _task_failed(self, label: str, exc: Exception) -> None:
        self.status_var.set(f"{label} failed")
        self.log(f"{label} failed: {exc}")
        messagebox.showerror("PDF Toolbox", str(exc))

    def _task_succeeded(self, label: str, result) -> None:
        self.status_var.set(f"{label} finished")
        if result:
            self.log(f"{label} finished: {result}")
            messagebox.showinfo("PDF Toolbox", f"{label} finished.\n\n{result}")
        else:
            self.log(f"{label} finished.")
            messagebox.showinfo("PDF Toolbox", f"{label} finished.")

    def _add_files_to_listbox(self, listbox: tk.Listbox, files: tuple[str, ...]) -> None:
        existing = set(listbox.get(0, "end"))
        for file in files:
            if file not in existing:
                listbox.insert("end", file)

    def _move_selected_up(self, listbox: tk.Listbox) -> None:
        for index in listbox.curselection():
            if index == 0:
                continue
            value = listbox.get(index)
            listbox.delete(index)
            listbox.insert(index - 1, value)
            listbox.selection_set(index - 1)

    def _move_selected_down(self, listbox: tk.Listbox) -> None:
        for index in reversed(listbox.curselection()):
            if index == listbox.size() - 1:
                continue
            value = listbox.get(index)
            listbox.delete(index)
            listbox.insert(index + 1, value)
            listbox.selection_set(index + 1)

    def add_merge_files(self) -> None:
        files = filedialog.askopenfilenames(
            title="Choose PDFs",
            filetypes=[("PDF files", "*.pdf")],
        )
        self._add_files_to_listbox(self.merge_listbox, files)

    def remove_merge_files(self) -> None:
        for index in reversed(self.merge_listbox.curselection()):
            self.merge_listbox.delete(index)

    def move_merge_up(self) -> None:
        self._move_selected_up(self.merge_listbox)

    def move_merge_down(self) -> None:
        self._move_selected_down(self.merge_listbox)

    def choose_merge_output(self) -> None:
        output = filedialog.asksaveasfilename(
            title="Save merged PDF",
            defaultextension=".pdf",
            initialfile=pathlib.Path(self.merge_output_var.get()).name,
            filetypes=[("PDF files", "*.pdf")],
        )
        if output:
            self.merge_output_var.set(output)

    def run_merge(self) -> None:
        files = list(self.merge_listbox.get(0, "end"))
        output = self.merge_output_var.get().strip()
        self._run_async(
            "Merge PDFs",
            lambda: str(merge_pdfs(files, output)),
        )

    def choose_bank_folder(self) -> None:
        folder = filedialog.askdirectory(title="Choose folder with dated PDFs")
        if folder:
            self.bank_folder_var.set(folder)

    def load_bank_folder(self) -> None:
        try:
            folder = pathlib.Path(self.bank_folder_var.get()).expanduser()
            pdfs = collect_pdfs_sorted_by_date_prefix([], folder, self.bank_pattern_var.get())
            self.bank_listbox.delete(0, "end")
            for pdf in pdfs:
                self.bank_listbox.insert("end", str(pdf))
            self.log(f"Loaded {len(pdfs)} date-prefixed PDFs from {folder}")
        except Exception as exc:
            messagebox.showerror("PDF Toolbox", str(exc))

    def add_bank_files(self) -> None:
        files = filedialog.askopenfilenames(
            title="Choose date-prefixed PDFs",
            filetypes=[("PDF files", "*.pdf")],
        )
        self._add_files_to_listbox(self.bank_listbox, files)
        self.sort_bank_files()

    def sort_bank_files(self) -> None:
        try:
            files = [pathlib.Path(item) for item in self.bank_listbox.get(0, "end")]
            files = sorted(files, key=extract_date_prefix)
            self.bank_listbox.delete(0, "end")
            for file in files:
                self.bank_listbox.insert("end", str(file))
        except Exception as exc:
            messagebox.showerror("PDF Toolbox", str(exc))

    def remove_bank_files(self) -> None:
        for index in reversed(self.bank_listbox.curselection()):
            self.bank_listbox.delete(index)

    def choose_bank_output(self) -> None:
        output = filedialog.asksaveasfilename(
            title="Save date-sorted merged PDF",
            defaultextension=".pdf",
            initialfile=pathlib.Path(self.bank_output_var.get()).name,
            filetypes=[("PDF files", "*.pdf")],
        )
        if output:
            self.bank_output_var.set(output)

    def run_bank_merge(self) -> None:
        files = list(self.bank_listbox.get(0, "end"))
        output = self.bank_output_var.get().strip()
        self._run_async(
            "Merge by Date",
            lambda: str(
                merge_pdfs(
                    collect_pdfs_sorted_by_date_prefix(files),
                    output,
                )
            ),
        )

    def add_image_files(self) -> None:
        files = filedialog.askopenfilenames(
            title="Choose images",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp"),
                ("All files", "*.*"),
            ],
        )
        self._add_files_to_listbox(self.images_listbox, files)
        current_items = self.images_listbox.get(0, "end")
        if current_items:
            first_image = pathlib.Path(current_items[0])
            if self.images_output_var.get() == "images.pdf":
                self.images_output_var.set(str(first_image.with_name(f"{first_image.stem}_images.pdf")))

    def remove_image_files(self) -> None:
        for index in reversed(self.images_listbox.curselection()):
            self.images_listbox.delete(index)

    def move_images_up(self) -> None:
        self._move_selected_up(self.images_listbox)

    def move_images_down(self) -> None:
        self._move_selected_down(self.images_listbox)

    def choose_images_output(self) -> None:
        output = filedialog.asksaveasfilename(
            title="Save images as PDF",
            defaultextension=".pdf",
            initialfile=pathlib.Path(self.images_output_var.get()).name,
            filetypes=[("PDF files", "*.pdf")],
        )
        if output:
            self.images_output_var.set(output)

    def run_images_to_pdf(self) -> None:
        files = list(self.images_listbox.get(0, "end"))
        output = self.images_output_var.get().strip()
        dpi = int(self.images_dpi_var.get())
        self._run_async(
            "Images to PDF",
            lambda: str(images_to_pdf(files, output, dpi=dpi, jpeg_quality=None)),
        )

    def choose_split_input(self) -> None:
        file = filedialog.askopenfilename(
            title="Choose PDF to split",
            filetypes=[("PDF files", "*.pdf")],
        )
        if file:
            input_path = pathlib.Path(file)
            self.split_input_var.set(file)
            self.split_output_dir_var.set(str(input_path.with_name(f"{input_path.stem}_pages")))
            self.split_prefix_var.set(input_path.stem)

    def choose_split_output_dir(self) -> None:
        initial_dir = pathlib.Path(self.split_output_dir_var.get()).expanduser()
        folder = filedialog.askdirectory(
            title="Choose output folder",
            initialdir=str(initial_dir.parent if initial_dir.parent.exists() else pathlib.Path.cwd()),
        )
        if folder:
            self.split_output_dir_var.set(folder)

    def run_split(self) -> None:
        self._run_async(
            "Split Pages",
            lambda: self._format_split_result(
                split_pdf_pages(
                    self.split_input_var.get().strip(),
                    self.split_output_dir_var.get().strip() or None,
                    self.split_prefix_var.get().strip() or None,
                )
            ),
        )

    def _format_split_result(self, outputs: list[pathlib.Path]) -> str:
        if not outputs:
            return "No files were created."
        return f"Created {len(outputs)} files in:\n{outputs[0].parent}"

    def choose_watermark_input(self) -> None:
        file = filedialog.askopenfilename(
            title="Choose PDF or image",
            filetypes=[("Supported files", "*.pdf *.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp"), ("All files", "*.*")],
        )
        if file:
            self.watermark_input_var.set(file)
            path = pathlib.Path(file)
            self.watermark_output_var.set(str(path.with_name(path.stem + "_clean.pdf")))

    def choose_watermark_output(self) -> None:
        output = filedialog.asksaveasfilename(
            title="Save cleaned file",
            defaultextension=".pdf",
            initialfile=pathlib.Path(self.watermark_output_var.get()).name,
            filetypes=[("PDF files", "*.pdf"), ("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp")],
        )
        if output:
            self.watermark_output_var.set(output)

    def run_watermark(self) -> None:
        options = WatermarkOptions(
            mode=self.watermark_mode_var.get(),
            dpi=int(self.watermark_dpi_var.get()),
            roi=self.watermark_roi_var.get(),
            roi_height=float(self.watermark_roi_height_var.get()),
            threshold=int(self.watermark_threshold_var.get()),
            dilate=int(self.watermark_dilate_var.get()),
            inpaint_radius=int(self.watermark_inpaint_radius_var.get()),
            jpeg_quality=int(self.watermark_jpeg_quality_var.get()),
        )
        self._run_async(
            "Remove Watermark",
            lambda: str(
                remove_watermark_file(
                    self.watermark_input_var.get().strip(),
                    self.watermark_output_var.get().strip(),
                    options,
                )
            ),
        )

    def choose_compress_input(self) -> None:
        file = filedialog.askopenfilename(
            title="Choose PDF",
            filetypes=[("PDF files", "*.pdf")],
        )
        if file:
            self.compress_input_var.set(file)
            path = pathlib.Path(file)
            self.compress_output_var.set(str(path.with_name(path.stem + "_compressed.pdf")))
            self.compress_input_size_var.set(format_file_size(path.stat().st_size))
            self.compress_output_size_var.set("Not compressed yet")

    def choose_compress_output(self) -> None:
        output = filedialog.asksaveasfilename(
            title="Save compressed PDF",
            defaultextension=".pdf",
            initialfile=pathlib.Path(self.compress_output_var.get()).name,
            filetypes=[("PDF files", "*.pdf")],
        )
        if output:
            self.compress_output_var.set(output)

    def run_compress(self) -> None:
        options = CompressionOptions(
            dpi=int(self.compress_dpi_var.get()),
            jpeg_quality=int(self.compress_quality_var.get()),
        )
        self._run_async(
            "Compress PDF",
            self._compress_with_feedback(options),
        )

    def _compress_with_feedback(self, options: CompressionOptions):
        def work() -> str:
            input_path = pathlib.Path(self.compress_input_var.get().strip()).expanduser().resolve()
            before = format_file_size(input_path.stat().st_size)
            output = compress_pdf(
                input_path,
                self.compress_output_var.get().strip(),
                options,
            )
            after = format_file_size(output.stat().st_size)
            self.after(0, lambda: self.compress_input_size_var.set(before))
            self.after(0, lambda: self.compress_output_size_var.set(after))
            return f"{output}\n\nSize: {before} -> {after}"

        return work


def main() -> None:
    app = PdfToolkitApp()
    app.mainloop()
