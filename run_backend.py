"""
PaperTrail Backend Launcher
Execute this file from anywhere:
    python run_backend.py
"""

import sys
import os
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"

sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

if __name__ == "__main__":
    import uvicorn
    from config import BACKEND_HOST, BACKEND_PORT

    print("=" * 60)
    print("  🚀 Launching PaperTrail Backend Server...")
    print(f"  Target: http://localhost:{BACKEND_PORT}")
    print("=" * 60)
    uvicorn.run("main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)

