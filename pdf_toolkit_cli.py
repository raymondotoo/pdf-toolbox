#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import sys

from pdf_toolkit.runtime import bootstrap_local_site_packages

bootstrap_local_site_packages(pathlib.Path(__file__).resolve())

from pdf_toolkit.gui import main as launch_gui
from pdf_toolkit.operations import (
    CompressionOptions,
    WatermarkOptions,
    compress_pdf,
    images_to_pdf,
    merge_pdfs_sorted_by_date_prefix,
    merge_pdfs,
    merge_two_pdfs,
    remove_watermark_file,
    split_pdf_pages,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PDF Toolbox CLI for merge, cleanup, and compression tasks."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gui_parser = subparsers.add_parser("gui", help="Launch the desktop app.")
    gui_parser.set_defaults(func=run_gui)

    merge_parser = subparsers.add_parser("merge", help="Merge 2 or more PDFs.")
    merge_parser.add_argument("files", nargs="+", help="PDF files to merge.")
    merge_parser.add_argument("--output", default="merged.pdf", help="Output PDF path.")
    merge_parser.set_defaults(func=run_merge)

    merge_two_parser = subparsers.add_parser("merge-two", help="Merge exactly two PDFs.")
    merge_two_parser.add_argument("pdf_a")
    merge_two_parser.add_argument("pdf_b")
    merge_two_parser.add_argument("--output", default="merged.pdf", help="Output PDF path.")
    merge_two_parser.set_defaults(func=run_merge_two)

    dated_parser = subparsers.add_parser(
        "dated-merge",
        aliases=["bank-merge"],
        help="Merge PDFs ordered by the YYYYMMDD date at the start of each filename.",
    )
    dated_parser.add_argument("paths", nargs="*", help="PDF paths. If omitted, scan a folder.")
    dated_parser.add_argument(
        "--input-dir",
        default=".",
        help="Folder to scan when no files are passed.",
    )
    dated_parser.add_argument(
        "--pattern",
        default="*.pdf",
        help="Glob pattern when scanning a folder.",
    )
    dated_parser.add_argument(
        "--output",
        default="merged_by_date.pdf",
        help="Output PDF path.",
    )
    dated_parser.set_defaults(func=run_dated_merge)

    images_parser = subparsers.add_parser(
        "images-to-pdf",
        help="Convert one or more images into a single PDF.",
    )
    images_parser.add_argument("files", nargs="+", help="Image files to convert in order.")
    images_parser.add_argument("--output", default="images.pdf", help="Output PDF path.")
    images_parser.add_argument("--dpi", type=int, default=300)
    images_parser.set_defaults(func=run_images_to_pdf)

    watermark_parser = subparsers.add_parser(
        "remove-watermark",
        help="Remove scanner watermarks from PDFs or images.",
    )
    watermark_parser.add_argument("input")
    watermark_parser.add_argument("output")
    watermark_parser.add_argument("--dpi", type=int, default=300)
    watermark_parser.add_argument(
        "--mode", choices=["auto", "overlay", "inpaint"], default="auto"
    )
    watermark_parser.add_argument(
        "--roi", choices=["bottom", "top", "full"], default="bottom"
    )
    watermark_parser.add_argument("--roi-height", type=float, default=0.25)
    watermark_parser.add_argument("--threshold", type=int, default=16)
    watermark_parser.add_argument("--dilate", type=int, default=2)
    watermark_parser.add_argument("--inpaint-radius", type=int, default=3)
    watermark_parser.add_argument("--jpeg-quality", type=int, default=85)
    watermark_parser.set_defaults(func=run_watermark)

    compress_parser = subparsers.add_parser(
        "compress",
        help="Compress a scanned PDF by rasterizing to a smaller image PDF.",
    )
    compress_parser.add_argument("input")
    compress_parser.add_argument("output")
    compress_parser.add_argument("--dpi", type=int, default=200)
    compress_parser.add_argument("--jpeg-quality", type=int, default=75)
    compress_parser.set_defaults(func=run_compress)

    split_parser = subparsers.add_parser(
        "split-pages",
        help="Split a PDF into one single-page PDF per page.",
    )
    split_parser.add_argument("input", help="Input PDF path.")
    split_parser.add_argument(
        "--output-dir",
        default=None,
        help="Folder to write split pages into. Defaults to <input>_pages.",
    )
    split_parser.add_argument(
        "--prefix",
        default=None,
        help="Filename prefix for the split pages. Defaults to the input filename stem.",
    )
    split_parser.set_defaults(func=run_split_pages)

    return parser


def run_gui(_: argparse.Namespace) -> None:
    launch_gui()


def run_merge(args: argparse.Namespace) -> None:
    output = merge_pdfs(args.files, args.output)
    print(output)


def run_merge_two(args: argparse.Namespace) -> None:
    output = merge_two_pdfs(args.pdf_a, args.pdf_b, args.output)
    print(output)


def run_dated_merge(args: argparse.Namespace) -> None:
    output = merge_pdfs_sorted_by_date_prefix(
        args.paths,
        args.output,
        input_dir=args.input_dir,
        pattern=args.pattern,
    )
    print(output)


def run_images_to_pdf(args: argparse.Namespace) -> None:
    output = images_to_pdf(args.files, args.output, dpi=args.dpi, jpeg_quality=None)
    print(output)


def run_watermark(args: argparse.Namespace) -> None:
    options = WatermarkOptions(
        dpi=args.dpi,
        mode=args.mode,
        roi=args.roi,
        roi_height=args.roi_height,
        threshold=args.threshold,
        dilate=args.dilate,
        inpaint_radius=args.inpaint_radius,
        jpeg_quality=args.jpeg_quality,
    )
    output = remove_watermark_file(args.input, args.output, options)
    print(output)


def run_compress(args: argparse.Namespace) -> None:
    options = CompressionOptions(dpi=args.dpi, jpeg_quality=args.jpeg_quality)
    output = compress_pdf(args.input, args.output, options)
    print(output)


def run_split_pages(args: argparse.Namespace) -> None:
    outputs = split_pdf_pages(args.input, args.output_dir, args.prefix)
    for output in outputs:
        print(output)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.exit(str(exc))
