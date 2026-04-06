from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "CompressionOptions": ("pdf_toolkit.operations", "CompressionOptions"),
    "WatermarkOptions": ("pdf_toolkit.operations", "WatermarkOptions"),
    "collect_statement_pdfs": ("pdf_toolkit.operations", "collect_statement_pdfs"),
    "collect_pdfs_sorted_by_date_prefix": ("pdf_toolkit.operations", "collect_pdfs_sorted_by_date_prefix"),
    "compress_pdf": ("pdf_toolkit.operations", "compress_pdf"),
    "extract_date_prefix": ("pdf_toolkit.operations", "extract_date_prefix"),
    "extract_statement_date": ("pdf_toolkit.operations", "extract_statement_date"),
    "format_file_size": ("pdf_toolkit.operations", "format_file_size"),
    "images_to_pdf": ("pdf_toolkit.operations", "images_to_pdf"),
    "merge_pdfs": ("pdf_toolkit.operations", "merge_pdfs"),
    "merge_pdfs_sorted_by_date_prefix": ("pdf_toolkit.operations", "merge_pdfs_sorted_by_date_prefix"),
    "merge_two_pdfs": ("pdf_toolkit.operations", "merge_two_pdfs"),
    "remove_watermark_file": ("pdf_toolkit.operations", "remove_watermark_file"),
    "split_pdf_pages": ("pdf_toolkit.operations", "split_pdf_pages"),
    "run_gui": ("pdf_toolkit.gui", "main"),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attribute_name = _EXPORTS[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value
