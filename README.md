# PaperTrail — Follow the Evidence

PaperTrail is a document forensics and contextual intelligence system built for the DataOps Innovation Hackathon 2026.

Most document processing tools stop at extracting text from a single page. In real-world fraud, loan fraud, and identity spoofing cases, the red flags almost never appear on an isolated page. They show up as contradictions **between** documents: an identity document that says 2002, a bank statement that says 2001, an address that silently shifts cities, or two different applications referencing the exact same document number.

PaperTrail correlates every piece of extracted information across all documents submitted in an investigation, flags conflicts on an interactive relationship graph, runs preliminary image forensics, scores fraud risk, and exports an investigation dossier ready for human review.

---

## What It Does

- **Cross-Document Correlation**: Compares names, dates of birth, addresses, IDs, and phone numbers across all documents submitted in a case. Flags exact matches, conflicts, and missing records.
- **Interactive Relationship Graph**: Visualizes documents as nodes connected by colored links (green for verified matches, red with live pulses for conflicts). Click any node or edge to inspect conflicting values directly.
- **Visual Image Forensics**: 
  - **Error Level Analysis (ELA)**: Detects potential JPEG re-compression and localized modifications.
  - **EXIF & Metadata Inspection**: Checks for image-editing software signatures (Photoshop, GIMP) and missing metadata.
  - **Compression Artifacts**: Measures 8x8 DCT block variance and Laplacian edge variance.
  - **Illumination Uniformity**: Checks quadrant brightness variance for composite anomalies.
- **Weighted Risk Assessment**: Transparent 0–100 scoring based on conflicting fields (Name: 25 pts, DOB: 25 pts, Duplicate ID: 25 pts, Address: 15 pts). Categorizes cases into Low, Moderate, High, and Critical.
- **Dual Investigation Assistant**: Generates natural-language case summaries and field-by-field verification guidance. Uses Gemini when an API key is provided, or a local rule engine when offline.
- **Downloadable PDF Dossiers**: Generates multi-page investigation reports using ReportLab with cover sheets, comparison tables, visual forensic metrics, and recommended next steps.
- **Built-in Demo Mode**: Preloaded 3-document case ready to present to judges with a single click.

---

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18, Vite | UI dashboard and state management |
| **Styling** | Tailwind CSS | Dark cybersecurity palette (`#101C2B`, `#45D6E8`) |
| **Graph Visualization** | React Flow | Interactive document relationship and conflict graph |
| **Charts** | Recharts | Risk distribution and activity charts |
| **Icons** | Lucide React | Forensic dashboard icons |
| **Backend** | Python 3.10+, FastAPI | REST API and async request handling |
| **Database** | SQLite + SQLAlchemy | Case records, document metadata, audit history |
| **PDF Processing** | PyMuPDF (fitz) | Page extraction and text parsing |
| **OCR** | Tesseract OCR + Pillow | Image preprocessing and text extraction |
| **Image Forensics** | OpenCV, Pillow, NumPy | ELA, compression analysis, quadrant brightness |
| **Report Engine** | ReportLab | Programmatic PDF dossier generation |
| **AI (Optional)** | Google Gemini API (`gemini-3.8-flash`) | Contextual anomaly explanations (rule fallback built-in) |

---

## Project Structure

```
papertrail/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Central configuration & path anchoring
│   ├── database/
│   │   └── db.py            # SQLite schema (Investigation, Document, Anomaly)
│   ├── services/
│   │   ├── ocr_service.py   # Tesseract OCR & regex structured parser
│   │   ├── analysis_service.py # Cross-doc comparison & risk engine
│   │   ├── ai_service.py    # Gemini API + rule-based fallback
│   │   └── report_service.py# ReportLab PDF dossier generator
│   ├── forensic/
│   │   └── visual_forensics.py # ELA, EXIF, and block variance checks
│   ├── routes/              # Modular API endpoints
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # RelationshipGraph, ComparisonTable, RiskGauge, AnomalyCard
│   │   ├── layouts/         # Collapsible cyber sidebar layout
│   │   ├── pages/           # 9 functional views (Dashboard, History, Evidence, etc.)
│   │   ├── services/api.js  # Axios client
│   │   ├── App.jsx          # Router
│   │   └── index.css        # Glassmorphic styles
│   ├── package.json
│   └── vite.config.js
├── sample_documents/        # Fictional demonstration files
│   ├── Identity_Document_Rahul_Sharma.pdf
│   ├── PAN_Document_Rahul_Sharma.pdf
│   ├── Bank_Statement_Rahul_Verma.pdf
│   └── generate_samples.py
├── run_backend.py           # Universal backend launcher
├── start_all.bat            # One-click launcher for both services (Windows)
├── start_backend.bat        # Backend launch script
├── start_frontend.bat       # Frontend launch script
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher + npm
- (Optional) [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) for scanned image text extraction. Standard text PDFs process without it.

# Setup and Installation

PaperTrail can be installed and run locally using Python, Node.js and open-source document-processing tools.

## 1. Prerequisites

Install the following software before setting up the project:

| Software | Minimum Requirement | Purpose |
|---|---|---|
| Python | 3.10+ | Backend development and processing |
| Node.js | 18+ | Frontend runtime |
| npm | Included with Node.js | Frontend package management |
| Git | Latest version | Clone the project repository |
| Tesseract OCR | Optional | OCR for scanned documents and images |

**Tesseract OCR:** [Download for Windows](https://github.com/UB-Mannheim/tesseract/wiki)

Standard text-based PDFs can be processed without Tesseract OCR.

## 2. Clone the Repository

Open Command Prompt or PowerShell and execute:

```bash
git clone https://github.com/Sharan-2005/Paper-Trail.git
cd Paper-Trail
```

This downloads the PaperTrail source code to your local system.

## 3. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

## 4. Environment Configuration

Create a `.env` file inside the `backend` directory.

Configure the application using the required environment variables:

```env

BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

UPLOAD_DIR=uploads
REPORTS_DIR=generated_reports

TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe

CORS_ORIGINS=http://localhost:5173,http://localhost:3000

DATABASE_URL=sqlite:///./papertrail.db
MAX_FILE_SIZE_MB=50
```

**Note:**
- The Gemini API key is optional. PaperTrail supports a local rule-based fallback.
- Update the Tesseract executable path if it is installed in a different location.
- Keep API keys private and never upload the `.env` file to a public GitHub repository.

## 5. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install the required Node.js dependencies:

```bash
npm install
```

This installs the packages specified in `package.json`.

## 6. Launching PaperTrail

**Option A – One-click startup (Windows)**

From the main project directory, run:

```bash
start_all.bat
```

This launches the backend and frontend services using the project's startup script.

**Option B – Manual startup**

Start the backend:

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend in another terminal:

```bash
cd frontend
npm run dev
```

## 7. Access the Application

Once both services are running, open the following URLs in your browser:

| Service | URL |
|---|---|
| PaperTrail Web Application | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Interactive API Documentation | http://localhost:8000/docs |
| Backend Health Check | http://localhost:8000/api/health |

## 8. Start a Demonstration Investigation

1. Open the PaperTrail web application.
2. Select the built-in Demo Mode or launch the sample investigation.
3. Explore the preloaded fictional documents.
4. Review extracted information and cross-document inconsistencies.
5. Inspect the relationship graph and visual forensic indicators.
6. View the risk assessment and key findings.
7. Generate and download the investigation PDF dossier.

**Setup Complete!**

PaperTrail is now ready to run locally. The application can process uploaded documents and present investigation findings through its web-based interface.

## API Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & component diagnostics (OCR, OpenCV, Gemini, SQLite) |
| `POST` | `/api/investigations/create` | Upload multiple files (PDF/PNG/JPG) and run full pipeline |
| `GET` | `/api/investigations/` | List all investigation history |
| `GET` | `/api/investigations/{id}` | Complete investigation details, matrix & graph data |
| `GET` | `/api/investigations/stats` | Dashboard statistics & risk distribution |
| `PATCH`| `/api/documents/{id}/fields` | Investigator manual correction of OCR mistakes |
| `POST` | `/api/forensics/{doc_id}/analyze` | Trigger OpenCV visual forensics (ELA, compression, brightness) |
| `POST` | `/api/reports/{id}/generate` | Generate formal PDF dossier via ReportLab |
| `GET` | `/api/reports/{id}/download/{file}` | Download generated PDF report |
| `POST` | `/api/demo/launch` | Initialize or retrieve the demonstration investigation |

---

## Technical Considerations & Limitations

- **ELA Interpretation**: Error Level Analysis is an anomaly detection heuristic, not absolute proof of forgery. Re-saving or normal compression variations can yield error levels that require manual verification by an examiner.
- **OCR Scan Quality**: Tesseract OCR performance depends on DPI and skew. Skewed or blurry physical scans may require field corrections using the built-in edit feature.
- **Air-Gapped Design**: PaperTrail evaluates submission consistency internally. It does not ping external government identity databases.
