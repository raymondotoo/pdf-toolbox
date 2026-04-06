from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

try:
    import cv2  # type: ignore
except ModuleNotFoundError:
    cv2 = None  # type: ignore[assignment]

try:
    import fitz  # type: ignore
except ModuleNotFoundError:
    try:
        import pymupdf as fitz  # type: ignore
    except ModuleNotFoundError:
        fitz = None  # type: ignore[assignment]

try:
    import numpy as np
except ModuleNotFoundError:
    np = None  # type: ignore[assignment]

DATE_PREFIX_RE = re.compile(r"^(?P<date>\d{8})")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


@dataclass
class WatermarkOptions:
    dpi: int = 300
    password: str | None = None
    mode: str = "auto"
    max_overlay_area: float = 0.03
    overlay_margin: float = 0.15
    roi: str = "bottom"
    roi_height: float = 0.25
    roi_box: tuple[float, float, float, float] | None = None
    threshold: int = 16
    dilate: int = 2
    inpaint_radius: int = 3
    jpeg_quality: int = 85


@dataclass
class CompressionOptions:
    dpi: int = 200
    password: str | None = None
    jpeg_quality: int = 75


def format_file_size(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"
        size /= 1024


def load_pdf_backend():
    try:
        from pypdf import PdfReader, PdfWriter

        return PdfReader, PdfWriter
    except ModuleNotFoundError:
        try:
            from PyPDF2 import PdfReader, PdfWriter  # type: ignore[assignment]

            return PdfReader, PdfWriter
        except ModuleNotFoundError:
            return None, None


def require_pdf_backend():
    pdf_reader, pdf_writer = load_pdf_backend()
    if pdf_reader is None or pdf_writer is None:
        raise RuntimeError(
            "No PDF library was found. Install one with `python3 -m pip install pypdf`."
        )
    return pdf_reader, pdf_writer


def require_cv2():
    if cv2 is None:
        raise RuntimeError(
            "OpenCV is required for raster processing. Install `opencv-python-headless`."
        )
    return cv2


def require_fitz():
    if fitz is None:
        raise RuntimeError(
            "PyMuPDF is required for PDF raster processing. Install `pymupdf`."
        )
    return fitz


def require_numpy():
    if np is None:
        raise RuntimeError("NumPy is required for raster processing. Install `numpy`.")
    return np


def resolve_pdf_paths(files: Iterable[pathlib.Path | str], minimum: int = 1) -> list[pathlib.Path]:
    paths = [pathlib.Path(file).expanduser().resolve() for file in files]
    if len(paths) < minimum:
        noun = "file" if minimum == 1 else "files"
        raise ValueError(f"Please provide at least {minimum} PDF {noun}.")

    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("These files were not found:\n" + "\n".join(missing))

    non_pdfs = [path.name for path in paths if path.suffix.lower() != ".pdf"]
    if non_pdfs:
        raise ValueError("These files are not PDFs:\n" + "\n".join(non_pdfs))

    return paths


def resolve_image_paths(
    files: Iterable[pathlib.Path | str], minimum: int = 1
) -> list[pathlib.Path]:
    paths = [pathlib.Path(file).expanduser().resolve() for file in files]
    if len(paths) < minimum:
        noun = "file" if minimum == 1 else "files"
        raise ValueError(f"Please provide at least {minimum} image {noun}.")

    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("These files were not found:\n" + "\n".join(missing))

    unsupported = [path.name for path in paths if path.suffix.lower() not in IMAGE_EXTENSIONS]
    if unsupported:
        allowed = ", ".join(sorted(IMAGE_EXTENSIONS))
        raise ValueError(
            "These files are not supported images:\n"
            + "\n".join(unsupported)
            + f"\n\nSupported types: {allowed}"
        )

    return paths


def merge_pdfs(pdf_paths: Iterable[pathlib.Path | str], output_path: pathlib.Path | str) -> pathlib.Path:
    resolved_inputs = resolve_pdf_paths(pdf_paths, minimum=2)
    pdf_reader_cls, pdf_writer_cls = require_pdf_backend()
    writer = pdf_writer_cls()

    for pdf_path in resolved_inputs:
        reader = pdf_reader_cls(str(pdf_path))
        if getattr(reader, "is_encrypted", False):
            raise RuntimeError(f"{pdf_path.name} is encrypted and cannot be merged as-is.")
        for page in reader.pages:
            writer.add_page(page)

    output = pathlib.Path(output_path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as merged_file:
        writer.write(merged_file)
    return output


def merge_two_pdfs(
    pdf_a: pathlib.Path | str, pdf_b: pathlib.Path | str, output_path: pathlib.Path | str
) -> pathlib.Path:
    return merge_pdfs([pdf_a, pdf_b], output_path)


def extract_date_prefix(path: pathlib.Path) -> datetime:
    match = DATE_PREFIX_RE.match(path.name)
    if match is None:
        raise ValueError(
            f"{path.name} does not start with an 8-digit date like YYYYMMDD."
        )
    return datetime.strptime(match.group("date"), "%Y%m%d")


def collect_pdfs_sorted_by_date_prefix(
    paths: Iterable[pathlib.Path | str],
    input_dir: pathlib.Path | str = pathlib.Path("."),
    pattern: str = "*.pdf",
) -> list[pathlib.Path]:
    provided_paths = [pathlib.Path(path).expanduser() for path in paths]
    if provided_paths:
        pdfs = provided_paths
    else:
        input_directory = pathlib.Path(input_dir).expanduser()
        pdfs = sorted(input_directory.glob(pattern))

    resolved = [pdf.resolve() for pdf in pdfs if pdf.suffix.lower() == ".pdf"]
    if not resolved:
        raise FileNotFoundError(
            "No PDF files found. Pass PDFs directly or adjust the folder/pattern."
        )

    missing = [str(pdf) for pdf in resolved if not pdf.exists()]
    if missing:
        raise FileNotFoundError("These files were not found:\n" + "\n".join(missing))

    return sorted(resolved, key=extract_date_prefix)


def merge_pdfs_sorted_by_date_prefix(
    paths: Iterable[pathlib.Path | str],
    output_path: pathlib.Path | str,
    input_dir: pathlib.Path | str = pathlib.Path("."),
    pattern: str = "*.pdf",
) -> pathlib.Path:
    pdf_paths = collect_pdfs_sorted_by_date_prefix(paths, input_dir, pattern)
    return merge_pdfs(pdf_paths, output_path)


def split_pdf_pages(
    input_path: pathlib.Path | str,
    output_dir: pathlib.Path | str | None = None,
    prefix: str | None = None,
) -> list[pathlib.Path]:
    input_file = resolve_pdf_paths([input_path])[0]
    pdf_reader_cls, pdf_writer_cls = require_pdf_backend()
    reader = pdf_reader_cls(str(input_file))

    if getattr(reader, "is_encrypted", False):
        raise RuntimeError(f"{input_file.name} is encrypted and cannot be split as-is.")

    if output_dir is None:
        target_dir = input_file.with_name(f"{input_file.stem}_pages").resolve()
    else:
        target_dir = pathlib.Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    filename_prefix = (prefix or input_file.stem).strip() or input_file.stem
    page_count = len(reader.pages)
    if page_count == 0:
        raise RuntimeError(f"{input_file.name} has no pages to split.")

    pad_width = max(2, len(str(page_count)))
    outputs: list[pathlib.Path] = []
    for page_number, page in enumerate(reader.pages, start=1):
        writer = pdf_writer_cls()
        writer.add_page(page)
        output_path = target_dir / f"{filename_prefix}_page_{page_number:0{pad_width}d}.pdf"
        with output_path.open("wb") as output_file:
            writer.write(output_file)
        outputs.append(output_path)

    return outputs


def load_image_file(image_path: pathlib.Path):
    cv2_mod = require_cv2()
    image = cv2_mod.imread(str(image_path), cv2_mod.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Unable to read {image_path}")
    return image


def images_to_pdf(
    image_paths: Iterable[pathlib.Path | str],
    output_path: pathlib.Path | str,
    dpi: int = 300,
    jpeg_quality: int | None = None,
) -> pathlib.Path:
    resolved_inputs = resolve_image_paths(image_paths, minimum=1)
    images = [load_image_file(path) for path in resolved_inputs]
    return save_images_as_pdf(images, pathlib.Path(output_path), dpi, jpeg_quality)


def extract_statement_date(path: pathlib.Path) -> datetime:
    return extract_date_prefix(path)


def collect_statement_pdfs(
    paths: Iterable[pathlib.Path | str],
    input_dir: pathlib.Path | str = pathlib.Path("."),
    pattern: str = "*-Bank statement.pdf",
) -> list[pathlib.Path]:
    return collect_pdfs_sorted_by_date_prefix(paths, input_dir, pattern)


def load_pdf_images(pdf_path: pathlib.Path, dpi: int, password: str | None = None):
    fitz_mod = require_fitz()
    np_mod = require_numpy()
    document = fitz_mod.open(pdf_path)
    if document.needs_pass:
        if not password or not document.authenticate(password):
            raise RuntimeError("PDF is encrypted; reopen with the correct password.")

    images = []
    zoom = dpi / 72.0
    matrix = fitz_mod.Matrix(zoom, zoom)
    for page in document:
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image = np_mod.frombuffer(pix.samples, dtype=np_mod.uint8)
        image = image.reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            image = image[:, :, :3]
        image = image[:, :, ::-1].copy()
        images.append(image)
    document.close()
    return images


def load_image_any(
    path: pathlib.Path, dpi: int, password: str | None = None
) -> tuple[list[np.ndarray], bool]:
    if path.suffix.lower() == ".pdf":
        return load_pdf_images(path, dpi, password), True

    cv2_mod = require_cv2()
    image = cv2_mod.imread(str(path), cv2_mod.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Unable to read {path}")
    return [image], False


def _encode_jpeg(image, jpeg_quality: int) -> bytes:
    cv2_mod = require_cv2()
    success, encoded = cv2_mod.imencode(
        ".jpg",
        image,
        [int(cv2_mod.IMWRITE_JPEG_QUALITY), int(jpeg_quality)],
    )
    if not success:
        raise RuntimeError("Unable to encode image for PDF output.")
    return encoded.tobytes()


def _image_to_rgb_bytes(image) -> bytes:
    if len(image.shape) != 3 or image.shape[2] != 3:
        raise RuntimeError("Expected a 3-channel image for PDF output.")
    return image[:, :, ::-1].copy().tobytes()


def save_images_as_pdf(
    images: list[np.ndarray],
    out_path: pathlib.Path,
    dpi: int,
    jpeg_quality: int | None = None,
) -> pathlib.Path:
    fitz_mod = require_fitz()
    document = fitz_mod.open()
    for image in images:
        height, width = image.shape[:2]
        page = document.new_page(width=width * 72 / dpi, height=height * 72 / dpi)
        if jpeg_quality is None:
            pix = fitz_mod.Pixmap(
                fitz_mod.csRGB,
                width,
                height,
                _image_to_rgb_bytes(image),
                False,
            )
            page.insert_image(page.rect, pixmap=pix, overlay=False)
        else:
            page.insert_image(page.rect, stream=_encode_jpeg(image, jpeg_quality))

    out_path = out_path.expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(out_path, deflate=True, garbage=3)
    document.close()
    return out_path


def region_slice(h: int, w: int, roi: str, roi_height: float, roi_box):
    if roi == "bottom":
        y0 = int(h * (1 - roi_height))
        y1 = h
        x0, x1 = 0, w
    elif roi == "top":
        y0 = 0
        y1 = int(h * roi_height)
        x0, x1 = 0, w
    elif roi == "full":
        x0, y0, x1, y1 = 0, 0, w, h
    else:
        if not roi_box:
            raise ValueError("roi=box requires x0 y0 x1 y1 coordinates.")
        x0 = int(w * roi_box[0])
        y0 = int(h * roi_box[1])
        x1 = int(w * roi_box[2])
        y1 = int(h * roi_box[3])
    return x0, y0, x1, y1


def build_mask(gray: np.ndarray, threshold: int) -> np.ndarray:
    cv2_mod = require_cv2()
    background = cv2_mod.medianBlur(gray, 31)
    diff_dark = background.astype("int16") - gray.astype("int16")
    diff_light = gray.astype("int16") - background.astype("int16")
    mask = (diff_dark >= threshold) | (diff_light >= threshold)
    return mask.astype("uint8") * 255


def remove_watermark_from_image(image: np.ndarray, options: WatermarkOptions) -> np.ndarray:
    cv2_mod = require_cv2()
    np_mod = require_numpy()

    height, width = image.shape[:2]
    x0, y0, x1, y1 = region_slice(
        height, width, options.roi, options.roi_height, options.roi_box
    )
    roi = image[y0:y1, x0:x1]
    gray = cv2_mod.cvtColor(roi, cv2_mod.COLOR_BGR2GRAY)

    mask = build_mask(gray, options.threshold)
    if options.dilate > 0:
        kernel = np_mod.ones((3, 3), np_mod.uint8)
        mask = cv2_mod.dilate(mask, kernel, iterations=options.dilate)

    inpainted = cv2_mod.inpaint(
        roi, mask, options.inpaint_radius, cv2_mod.INPAINT_TELEA
    )
    result = image.copy()
    result[y0:y1, x0:x1] = inpainted
    return result


def overlay_candidate_rects(page, options: WatermarkOptions):
    fitz_mod = require_fitz()
    page_width, page_height = page.rect.width, page.rect.height
    area_limit = page_width * page_height * options.max_overlay_area
    margin_width = page_width * options.overlay_margin
    margin_height = page_height * options.overlay_margin
    rects = []

    raw = page.get_text("rawdict")
    for block in raw.get("blocks", []):
        if block.get("type") != 1:
            continue
        x0, y0, x1, y1 = block["bbox"]
        block_width = x1 - x0
        block_height = y1 - y0
        center_x = x0 + block_width / 2
        center_y = y0 + block_height / 2
        near_edge = (
            center_x < margin_width
            or center_x > page_width - margin_width
            or center_y < margin_height
            or center_y > page_height - margin_height
        )
        if block_width * block_height <= area_limit and near_edge:
            rects.append(fitz_mod.Rect(x0, y0, x1, y1))

    return rects


def count_overlay_candidates_pdf(
    input_path: pathlib.Path, options: WatermarkOptions
) -> int:
    fitz_mod = require_fitz()
    document = fitz_mod.open(input_path)
    if document.needs_pass and not (
        options.password and document.authenticate(options.password)
    ):
        raise RuntimeError("PDF is encrypted; supply the correct password.")

    candidate_count = 0
    for page in document:
        candidate_count += len(overlay_candidate_rects(page, options))

    document.close()
    return candidate_count


def overlay_remove_pdf(
    input_path: pathlib.Path, output_path: pathlib.Path, options: WatermarkOptions
) -> pathlib.Path:
    if input_path.suffix.lower() != ".pdf":
        raise RuntimeError("Overlay mode works only for PDFs.")

    fitz_mod = require_fitz()
    document = fitz_mod.open(input_path)
    if document.needs_pass and not (
        options.password and document.authenticate(options.password)
    ):
        raise RuntimeError("PDF is encrypted; supply the correct password.")

    for page in document:
        rects = overlay_candidate_rects(page, options)
        for rect in rects:
            page.add_redact_annot(rect, fill=(1, 1, 1))
        if rects:
            page.apply_redactions()

    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(output_path, deflate=True, garbage=3)
    document.close()
    return output_path


def save_processed_watermark_output(
    processed: list[np.ndarray],
    output_file: pathlib.Path,
    options: WatermarkOptions,
    is_pdf: bool,
) -> pathlib.Path:
    if output_file.suffix.lower() == ".pdf" or is_pdf:
        return save_images_as_pdf(processed, output_file, options.dpi, None)

    if len(processed) > 1:
        raise RuntimeError("Multiple pages require PDF output.")

    cv2_mod = require_cv2()
    success = cv2_mod.imwrite(str(output_file), processed[0])
    if not success:
        raise RuntimeError(f"Unable to save image to {output_file}")
    return output_file


def remove_watermark_file(
    input_path: pathlib.Path | str,
    output_path: pathlib.Path | str,
    options: WatermarkOptions | None = None,
) -> pathlib.Path:
    input_file = pathlib.Path(input_path).expanduser().resolve()
    output_file = pathlib.Path(output_path).expanduser().resolve()
    options = options or WatermarkOptions()

    if options.mode == "auto":
        if input_file.suffix.lower() == ".pdf":
            overlay_candidates = count_overlay_candidates_pdf(input_file, options)
            if overlay_candidates > 0:
                return overlay_remove_pdf(input_file, output_file, options)
        images, is_pdf = load_image_any(input_file, options.dpi, options.password)
        processed = [remove_watermark_from_image(image, options) for image in images]
        return save_processed_watermark_output(processed, output_file, options, is_pdf)

    if options.mode == "overlay":
        return overlay_remove_pdf(input_file, output_file, options)

    images, is_pdf = load_image_any(input_file, options.dpi, options.password)
    processed = [remove_watermark_from_image(image, options) for image in images]
    return save_processed_watermark_output(processed, output_file, options, is_pdf)


def compress_pdf(
    input_path: pathlib.Path | str,
    output_path: pathlib.Path | str,
    options: CompressionOptions | None = None,
) -> pathlib.Path:
    input_file = pathlib.Path(input_path).expanduser().resolve()
    output_file = pathlib.Path(output_path).expanduser().resolve()
    options = options or CompressionOptions()

    if input_file.suffix.lower() != ".pdf":
        raise ValueError("Compression currently supports PDF input files only.")

    images = load_pdf_images(input_file, options.dpi, options.password)
    return save_images_as_pdf(images, output_file, options.dpi, options.jpeg_quality)
