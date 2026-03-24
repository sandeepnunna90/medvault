import pytesseract
from PIL import Image
import io


def image_to_text(image_bytes: bytes) -> str:
    """Run Tesseract OCR on raw image bytes and return extracted text."""
    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image)
