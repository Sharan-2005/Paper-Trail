"""
PaperTrail Central Configuration and Paths
Guarantees consistent file paths regardless of the current working directory.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Find .env in backend/ or papertrail/
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent

if (BACKEND_DIR / ".env").exists():
    load_dotenv(BACKEND_DIR / ".env")
elif (PROJECT_DIR / ".env").exists():
    load_dotenv(PROJECT_DIR / ".env")
else:
    load_dotenv()

# Canonical Directories
UPLOAD_DIR = PROJECT_DIR / "uploads"
REPORTS_DIR = PROJECT_DIR / "generated_reports"
SAMPLE_DIR = PROJECT_DIR / "sample_documents"
DB_PATH = PROJECT_DIR / "papertrail.db"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL or DATABASE_URL == "sqlite:///./papertrail.db":
    DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# Server settings
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

# Tesseract
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Max upload size
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

