"""Reports routes - PDF generation and download."""
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.db import get_db, Investigation, Document, Anomaly, GeneratedReport
from services.report_service import generate_investigation_report
from services.analysis_service import build_comparison_table, calculate_risk_score
from config import REPORTS_DIR

router = APIRouter()

@router.post("/{investigation_id}/generate")
def generate_report(investigation_id: str, db: Session = Depends(get_db)):
    """Generate a PDF investigation dossier."""
    inv = db.query(Investigation).filter(Investigation.investigation_id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    documents = []
    for doc in inv.documents:
        documents.append({
            "document_id": doc.document_id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "document_type": doc.document_type,
            "extracted_fields": doc.extracted_fields or {},
            "processing_status": doc.processing_status,
        })

    anomalies = []
    for a in inv.anomalies:
        anomalies.append({
            "anomaly_id": a.anomaly_id,
            "anomaly_type": a.anomaly_type,
            "field_name": a.field_name,
            "severity": a.severity,
            "description": a.description,
            "source_documents": a.source_documents,
            "conflicting_values": a.conflicting_values,
            "evidence": a.evidence,
            "risk_points": a.risk_points,
            "ai_explanation": a.ai_explanation,
            "explanation_source": a.explanation_source,
        })

    comparison_table = build_comparison_table(documents)
    risk_assessment = calculate_risk_score(anomalies)

    investigation_data = {
        "investigation_id": inv.investigation_id,
        "title": inv.title,
        "risk_score": inv.risk_score or 0,
        "risk_level": inv.risk_level or "low",
        "risk_assessment": risk_assessment,
        "summary": inv.summary,
        "documents": documents,
        "anomalies": anomalies,
        "comparison_table": comparison_table,
        "forensic_results": [],
    }

    try:
        report_path = generate_investigation_report(investigation_data)
        filename = Path(report_path).name
        
        # Save report record
        report_record = GeneratedReport(
            investigation_id=investigation_id,
            report_path=report_path,
            file_size=os.path.getsize(report_path),
        )
        db.add(report_record)
        db.commit()

        return {
            "message": "Report generated",
            "report_path": report_path,
            "download_url": f"/api/reports/{investigation_id}/download/{filename}",
            "filename": filename,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/{investigation_id}/download/{filename}")
def download_report(investigation_id: str, filename: str):
    """Download a generated report."""
    report_path = REPORTS_DIR / filename
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(
        str(report_path),
        media_type="application/pdf",
        filename=filename,
    )

