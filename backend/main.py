"""
PaperTrail - AI-Powered Document Forensics and Contextual Intelligence System
Main FastAPI Application Entry Point
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import (
    UPLOAD_DIR,
    REPORTS_DIR,
    CORS_ORIGINS,
    BACKEND_HOST,
    BACKEND_PORT,
    TESSERACT_CMD,
    GEMINI_API_KEY,
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.db import init_db
from routes import (
    investigations,
    documents,
    forensics,
    reports,
    demo,
    settings as settings_router,
)

# Tesseract path configuration
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
except Exception:
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    init_db()
    print("=" * 60)
    print("  📄 PAPERTRAIL – Follow the Evidence.")
    print("  AI-Powered Document Forensics & Intelligence System")
    print("=" * 60)
    print(f"  API Server:        http://{BACKEND_HOST}:{BACKEND_PORT}")
    print(f"  Interactive Docs:  http://localhost:{BACKEND_PORT}/docs")
    print(f"  Upload Storage:    {UPLOAD_DIR}")
    print(f"  Reports Storage:   {REPORTS_DIR}")
    print("=" * 60)
    yield
    print("🔒 PaperTrail backend shutting down")


app = FastAPI(
    title="PaperTrail API",
    description="AI-Powered Document Forensics and Contextual Intelligence System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads and generated reports
if UPLOAD_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

if REPORTS_DIR.exists():
    app.mount("/reports", StaticFiles(directory=str(REPORTS_DIR)), name="reports")

# Register routers
app.include_router(investigations.router, prefix="/api/investigations", tags=["Investigations"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(forensics.router, prefix="/api/forensics", tags=["Forensics"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(demo.router, prefix="/api/demo", tags=["Demo"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])


@app.get("/")
async def root():
    return {
        "name": "PaperTrail",
        "tagline": "Follow the Evidence",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    checks = {
        "api": True,
        "database": True,
        "tesseract": False,
        "opencv": False,
        "gemini": False,
    }

    # Check tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        checks["tesseract"] = True
    except Exception:
        pass

    # Check opencv
    try:
        import cv2
        checks["opencv"] = True
    except ImportError:
        pass

    # Check gemini
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        checks["gemini"] = True

    return {
        "status": "healthy",
        "components": checks,
        "gemini_available": checks["gemini"],
        "ocr_available": checks["tesseract"],
        "vision_available": checks["opencv"],
    }


if __name__ == "__main__":
    import uvicorn
    # Change working dir to backend directory so relative imports work seamlessly
    os.chdir(BACKEND_DIR)
    uvicorn.run("main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)
