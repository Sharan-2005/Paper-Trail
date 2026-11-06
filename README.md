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

### 1. Setup Backend

```powershell
cd backend
pip install -r requirements.txt
```

*(Optional)* Create a `.env` file in `backend/` or `papertrail/` if you want to enable Gemini AI explanations:
```env
GEMINI_API_KEY=your_key_here
```
If skipped, PaperTrail will run the built-in rule-based investigation engine with zero degradation in functionality.

### 2. Setup Frontend

```powershell
cd frontend
npm install
```

### 3. Running the App

You can start both services with the Windows batch script:
```powershell
.\start_all.bat
```

Or start them individually in separate terminals:

**Backend:**
```powershell
python run_backend.py
# Server runs on http://localhost:8000
# API Docs at http://localhost:8000/docs
```

**Frontend:**
```powershell
cd frontend
npm run dev
# Web app runs on http://localhost:5173
```

---

## Demo Walkthrough for Judges

1. Open `http://localhost:5173` in any browser.
2. Click **"Launch Demo Investigation"** on the dashboard.
3. The system loads three synthetic test documents with intentional inconsistencies:
   - **Document 1 (Govt Identity)**: `Rahul Sharma`, DOB: `12-05-2002`, Address: `Mumbai, Maharashtra`
   - **Document 2 (PAN Card)**: `Rahul Sharma`, DOB: `12-05-2002`, PAN: `ABCPS1234R`
   - **Document 3 (Bank Statement)**: `Rahul Verma` *(name conflict)*, DOB: `12-05-2001` *(1-year discrepancy)*, Address: `Pune, Maharashtra` *(city conflict)*
4. Explore the views:
   - **Cross-Document Matrix**: Green checkmarks for confirmed matching fields; high-contrast red alerts for conflicting names, birthdates, and residential addresses.
   - **Relationship Graph**: Interactive React Flow canvas showing corroborated document paths and conflict edges. Click any edge to review raw conflicting values.
   - **Risk Gauge**: Real-time score of **58/100 (HIGH RISK)** with full point attribution.
   - **Forensic Assistant**: Concrete investigation notes outlining what was detected, why it matters, and recommended verification steps.
   - **Download PDF**: Hit the **"Download PDF Dossier"** button to export a complete, multi-page ReportLab investigation report.

---

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
