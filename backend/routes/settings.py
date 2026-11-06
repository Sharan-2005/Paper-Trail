"""Settings route."""
import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_settings():
    """Get current system configuration (non-sensitive)."""
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    tesseract_path = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    
    # Check tesseract
    tesseract_ok = False
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        tesseract_ok = True
    except Exception:
        pass

    # Check CV2
    cv2_ok = False
    try:
        import cv2
        cv2_ok = True
    except ImportError:
        pass

    return {
        "gemini_configured": bool(gemini_key and gemini_key != "your_gemini_api_key_here"),
        "tesseract_available": tesseract_ok,
        "tesseract_path": tesseract_path,
        "opencv_available": cv2_ok,
        "max_file_size_mb": int(os.getenv("MAX_FILE_SIZE_MB", 50)),
        "supported_formats": ["PDF", "PNG", "JPG", "JPEG"],
        "version": "1.0.0",
    }

