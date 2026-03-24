import fitz  # PyMuPDF
from backend.ocr_service import image_to_text

MAX_PAGES = 3
MIN_TEXT_CHARS = 50  # below this → treat page as scanned


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF (max 3 pages).
    - Digital PDF: use embedded text layer directly.
    - Scanned PDF (< 50 chars of embedded text): render page to image and OCR.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_to_process = min(len(doc), MAX_PAGES)
    parts = []

    for page_num in range(pages_to_process):
        page = doc[page_num]
        text = page.get_text().strip()

        if len(text) >= MIN_TEXT_CHARS:
            parts.append(text)
        else:
            # Render at 2x zoom for better OCR accuracy
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            image_bytes = pix.tobytes("png")
            ocr_text = image_to_text(image_bytes)
            parts.append(ocr_text.strip())

    doc.close()
    return "\n\n".join(parts)
