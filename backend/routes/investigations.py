"""
Investigation routes - create, list, retrieve, analyze investigations.
"""

import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db import get_db, Investigation, Document, Anomaly, ForensicResult
from services.ocr_service import process_document
from services.analysis_service import detect_anomalies, calculate_risk_score, build_comparison_table, build_relationship_graph
from services.ai_service import explain_anomaly, explain_investigation_summary
from forensic.visual_forensics import run_visual_forensics
from config import UPLOAD_DIR, MAX_FILE_SIZE_BYTES

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = MAX_FILE_SIZE_BYTES


@router.post("/create")
async def create_investigation(
    title: str = Form(...),
    description: str = Form(""),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Create a new investigation with uploaded documents."""
    if not files:
        raise HTTPException(status_code=400, detail="At least one document is required")

    # Validate files
    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Allowed: PDF, PNG, JPG, JPEG")

    # Create investigation record
    inv_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
    investigation = Investigation(
        investigation_id=inv_id,
        title=title,
        description=description,
        status="processing",
    )
    db.add(investigation)
    db.commit()
    db.refresh(investigation)

    documents_data = []

    # Process each uploaded document
    for uploaded_file in files:
        doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
        ext = Path(uploaded_file.filename).suffix.lower().lstrip(".")
        safe_name = f"{doc_id}.{ext}"
        file_path = str(UPLOAD_DIR / safe_name)

        # Save file
        content = await uploaded_file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File {uploaded_file.filename} exceeds 50MB limit")
        
        with open(file_path, "wb") as fp:
            fp.write(content)

        # Create document record
        doc_record = Document(
            investigation_id=investigation.id,
            document_id=doc_id,
            filename=uploaded_file.filename,
            original_filename=uploaded_file.filename,
            file_type=ext,
            file_path=file_path,
            file_size=len(content),
            processing_status="processing",
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        try:
            # Process document
            proc_result = process_document(file_path, doc_id, ext)
            
            doc_record.ocr_text = proc_result.get("text", "")
            doc_record.extracted_fields = proc_result.get("extracted_fields", {})
            doc_record.document_type = proc_result.get("document_type", "supporting_document")
            doc_record.page_count = proc_result.get("page_count", 1)
            doc_record.processing_status = "completed"
            db.commit()

            documents_data.append({
                "document_id": doc_id,
                "filename": uploaded_file.filename,
                "file_type": ext,
                "document_type": doc_record.document_type,
                "extracted_fields": doc_record.extracted_fields or {},
                "page_count": doc_record.page_count,
            })

            # Visual forensics for image files
            if ext in ("jpg", "jpeg", "png"):
                try:
                    forensic_result = run_visual_forensics(file_path, ext)
                    summary = forensic_result.get("summary", {})
                    
                    fr = ForensicResult(
                        document_id=doc_record.id,
                        result_type="full_analysis",
                        finding=summary.get("overall_assessment", "normal"),
                        severity="info" if summary.get("suspicious_findings", 0) == 0 else "warning",
                        details=forensic_result,
                    )
                    db.add(fr)
                    db.commit()
                except Exception as fe:
                    logger.warning(f"Forensic analysis failed for {doc_id}: {fe}")

        except Exception as e:
            logger.error(f"Document processing failed for {doc_id}: {e}")
            doc_record.processing_status = "failed"
            db.commit()

    # Cross-document analysis
    if len(documents_data) >= 1:
        anomaly_dicts = detect_anomalies(documents_data, investigation.id)
        
        for a in anomaly_dicts:
            # Get AI/rule explanation
            explanation_result = explain_anomaly(a)
            
            anomaly_record = Anomaly(
                investigation_id=investigation.id,
                anomaly_id=a["anomaly_id"],
                anomaly_type=a["anomaly_type"],
                field_name=a["field_name"],
                severity=a["severity"],
                description=a["description"],
                source_documents=a["source_documents"],
                conflicting_values=a["conflicting_values"],
                evidence=a["evidence"],
                risk_points=a["risk_points"],
                ai_explanation=explanation_result["explanation"],
                explanation_source=explanation_result["source"],
                status="open",
            )
            db.add(anomaly_record)

        db.commit()

        # Calculate risk
        risk_data = calculate_risk_score(anomaly_dicts)
        
        # Get summary
        inv_summary_data = {
            "risk_score": risk_data["score"],
            "risk_level": risk_data["level"],
            "anomalies": anomaly_dicts,
            "documents": documents_data,
        }
        summary_result = explain_investigation_summary(inv_summary_data)

        investigation.risk_score = risk_data["score"]
        investigation.risk_level = risk_data["level"]
        investigation.anomaly_count = len(anomaly_dicts)
        investigation.summary = summary_result["summary"]
        investigation.status = "completed"
        db.commit()

    db.refresh(investigation)

    return {
        "investigation_id": inv_id,
        "id": investigation.id,
        "status": "completed",
        "documents_processed": len(documents_data),
        "anomalies_detected": investigation.anomaly_count,
        "risk_score": investigation.risk_score,
        "risk_level": investigation.risk_level,
    }


@router.get("/")
def list_investigations(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all investigations."""
    investigations = db.query(Investigation).order_by(Investigation.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(Investigation).count()
    
    return {
        "total": total,
        "investigations": [
            {
                "id": inv.id,
                "investigation_id": inv.investigation_id,
                "title": inv.title,
                "status": inv.status,
                "risk_score": inv.risk_score,
                "risk_level": inv.risk_level,
                "anomaly_count": inv.anomaly_count,
                "document_count": len(inv.documents),
                "is_demo": inv.is_demo,
                "created_at": inv.created_at.isoformat(),
            }
            for inv in investigations
        ],
    }


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    total_investigations = db.query(Investigation).count()
    total_documents = db.query(Document).count()
    total_anomalies = db.query(Anomaly).count()
    
    critical = db.query(Investigation).filter(Investigation.risk_level == "critical").count()
    high = db.query(Investigation).filter(Investigation.risk_level == "high").count()
    moderate = db.query(Investigation).filter(Investigation.risk_level == "moderate").count()
    low = db.query(Investigation).filter(Investigation.risk_level == "low").count()

    return {
        "total_investigations": total_investigations,
        "total_documents": total_documents,
        "total_anomalies": total_anomalies,
        "documents_requiring_review": db.query(Investigation).filter(Investigation.risk_score > 20).count(),
        "risk_distribution": {
            "critical": critical,
            "high": high,
            "moderate": moderate,
            "low": low,
        },
        "recent_investigations": [
            {
                "id": inv.id,
                "investigation_id": inv.investigation_id,
                "title": inv.title,
                "status": inv.status,
                "risk_score": inv.risk_score,
                "risk_level": inv.risk_level,
                "anomaly_count": inv.anomaly_count,
                "document_count": len(inv.documents),
                "is_demo": inv.is_demo,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
            }
            for inv in db.query(Investigation).order_by(Investigation.created_at.desc()).limit(5).all()
        ],
    }


@router.get("/{investigation_id}")
def get_investigation(investigation_id: str, db: Session = Depends(get_db)):
    """Get full investigation details."""
    inv = db.query(Investigation).filter(Investigation.investigation_id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    documents = []
    for doc in inv.documents:
        forensic_data = []
        for fr in doc.forensic_results:
            forensic_data.append({
                "result_type": fr.result_type,
                "finding": fr.finding,
                "severity": fr.severity,
                "details": fr.details,
                "image_path": fr.image_path,
            })
        
        documents.append({
            "document_id": doc.document_id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "document_type": doc.document_type,
            "extracted_fields": doc.extracted_fields or {},
            "page_count": doc.page_count,
            "processing_status": doc.processing_status,
            "forensic_results": forensic_data,
            "file_path": doc.file_path,
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
            "status": a.status,
            "created_at": a.created_at.isoformat(),
        })

    # Build comparison table and graph
    comparison_table = build_comparison_table(documents)
    graph_data = build_relationship_graph(documents, anomalies)
    
    # Build risk assessment
    risk_assessment = calculate_risk_score(anomalies)

    return {
        "id": inv.id,
        "investigation_id": inv.investigation_id,
        "title": inv.title,
        "description": inv.description,
        "status": inv.status,
        "risk_score": inv.risk_score or 0,
        "risk_level": inv.risk_level or "low",
        "risk_assessment": risk_assessment,
        "anomaly_count": inv.anomaly_count,
        "summary": inv.summary,
        "is_demo": inv.is_demo,
        "created_at": inv.created_at.isoformat(),
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
        "documents": documents,
        "anomalies": anomalies,
        "comparison_table": comparison_table,
        "graph_data": graph_data,
    }


@router.delete("/{investigation_id}")
def delete_investigation(investigation_id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.investigation_id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    db.delete(inv)
    db.commit()
    return {"message": "Investigation deleted"}

