"""
OCR and document processing service using Tesseract and PyMuPDF.
"""

import os
import re
import io
import uuid
import logging
from pathlib import Path
from typing import Optional

from config import UPLOAD_DIR, TESSERACT_CMD

logger = logging.getLogger(__name__)

# ─── Tesseract setup ───────────────────────────────────────────────
try:
    import pytesseract
    from PIL import Image
    _TESSERACT_AVAILABLE = True
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    # Quick sanity check
    pytesseract.get_tesseract_version()
except Exception:
    _TESSERACT_AVAILABLE = False
    logger.warning("Tesseract not available – OCR will be skipped")

try:
    import fitz  # PyMuPDF
    _PYMUPDF_AVAILABLE = True
except ImportError:
    _PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF not available – PDF processing limited")

try:
    import cv2
    import numpy as np
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False


# ─── Field extraction patterns ─────────────────────────────────────
FIELD_PATTERNS = {
    "full_name": [
        r"(?:Name|Full Name|Account Holder|Customer Name)\s*[:\-]?\s*([A-Z][a-z]+(?: [A-Z][a-z]+)+)",
        r"^([A-Z][A-Z ]{5,})$",
    ],
    "date_of_birth": [
        r"(?:DOB|Date of Birth|D\.O\.B|Birth Date)\s*[:\-]?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})",
        r"(?:Born|Birth)\s*[:\-]?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})",
    ],
    "address": [
        r"(?:Address|Residential Address|Permanent Address)\s*[:\-]?\s*(.{10,80})",
    ],
    "document_number": [
        r"(?:Document No|Doc No|ID No|Number|Card No|A/C No|Account No)\s*[:\-]?\s*([A-Z0-9]{6,20})",
        r"\b([A-Z]{2,3}[0-9]{6,10})\b",
        r"\b([A-Z]{5}[0-9]{4}[A-Z])\b",   # PAN-style
    ],
    "phone_number": [
        r"(?:Phone|Mobile|Contact|Tel)\s*[:\-]?\s*([\+]?[\d\s\-\(\)]{10,15})",
        r"\b(\d{10})\b",
    ],
    "email": [
        r"[\w\.-]+@[\w\.-]+\.\w{2,}",
    ],
    "issue_date": [
        r"(?:Issue Date|Issued|Date of Issue)\s*[:\-]?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})",
    ],
    "expiry_date": [
        r"(?:Expiry|Expiry Date|Valid Until|Valid Till|Expires)\s*[:\-]?\s*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})",
    ],
}

DOCUMENT_TYPE_KEYWORDS = {
    "identity_document": ["aadhaar", "aadhar", "identity", "national id", "voter id", "driving licence", "passport"],
    "pan_document": ["permanent account number", "pan", "income tax", "pan card"],
    "bank_statement": ["bank statement", "account statement", "transaction", "balance", "debit", "credit", "ifsc"],
    "salary_slip": ["salary", "payslip", "pay slip", "ctc", "basic pay", "allowance", "deduction"],
    "application_form": ["application form", "application no", "applied for"],
    "declaration": ["declaration", "i hereby declare", "affidavit"],
}


def classify_document(text: str) -> str:
    text_lower = text.lower()
    for doc_type, keywords in DOCUMENT_TYPE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return doc_type
    return "supporting_document"


def extract_fields_from_text(text: str) -> dict:
    """Extract structured fields from OCR text using regex patterns."""
    extracted = {}
    for field, patterns in FIELD_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                value = match.group(1).strip() if match.lastindex else match.group(0).strip()
                if value and len(value) > 1:
                    extracted[field] = value
                    break
    return extracted


def preprocess_image_for_ocr(image_path: str):
    """Apply OpenCV preprocessing to improve OCR accuracy."""
    if not _CV2_AVAILABLE:
        from PIL import Image
        return Image.open(image_path)

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Deskew + denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    from PIL import Image
    return Image.fromarray(thresh)


def ocr_image(image_path: str) -> tuple[str, float]:
    """Run OCR on an image file. Returns (text, confidence)."""
    if not _TESSERACT_AVAILABLE:
        return "", 0.0

    try:
        pil_img = preprocess_image_for_ocr(image_path)
        data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
        text = pytesseract.image_to_string(pil_img, config="--oem 3 --psm 6")
        
        confidences = [int(c) for c in data["conf"] if str(c).isdigit() and int(c) > 0]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        return text.strip(), round(avg_conf, 1)
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return "", 0.0


def process_pdf(file_path: str, doc_id: str) -> dict:
    """Extract text and images from a PDF using PyMuPDF."""
    if not _PYMUPDF_AVAILABLE:
        return {"text": "", "pages": [], "page_count": 0, "error": "PyMuPDF not installed"}

    result = {"text": "", "pages": [], "page_count": 0}
    try:
        doc = fitz.open(file_path)
        result["page_count"] = len(doc)
        full_text = []

        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            page_images = []

            # Render page as image for OCR if text is sparse
            if len(page_text.strip()) < 50:
                pix = page.get_pixmap(dpi=200)
                img_path = str(UPLOAD_DIR / f"{doc_id}_page_{page_num + 1}.png")
                pix.save(img_path)
                ocr_text, conf = ocr_image(img_path)
                page_text = ocr_text
                page_images.append({"path": img_path, "ocr_confidence": conf})

            full_text.append(page_text)
            result["pages"].append({
                "page_number": page_num + 1,
                "text": page_text,
                "images": page_images,
            })

        result["text"] = "\n\n".join(full_text)
        doc.close()
    except Exception as e:
        logger.error(f"PDF processing error: {e}")
        result["error"] = str(e)

    return result


def process_image_document(file_path: str, doc_id: str) -> dict:
    """Process an image document through OCR."""
    text, confidence = ocr_image(file_path)
    return {
        "text": text,
        "page_count": 1,
        "pages": [{"page_number": 1, "text": text, "ocr_confidence": confidence}],
        "ocr_confidence": confidence,
    }


def process_document(file_path: str, doc_id: str, file_ext: str) -> dict:
    """Main document processing entry point."""
    file_ext = file_ext.lower().lstrip(".")

    if file_ext == "pdf":
        raw = process_pdf(file_path, doc_id)
    elif file_ext in ("png", "jpg", "jpeg"):
        raw = process_image_document(file_path, doc_id)
    else:
        return {"error": f"Unsupported file type: {file_ext}"}

    text = raw.get("text", "")
    extracted_fields = extract_fields_from_text(text)
    document_type = classify_document(text)

    return {
        **raw,
        "document_type": document_type,
        "extracted_fields": extracted_fields,
        "field_count": len(extracted_fields),
    }

