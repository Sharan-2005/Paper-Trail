"""Forensics routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db, Document, ForensicResult
from forensic.visual_forensics import run_visual_forensics

router = APIRouter()

@router.get("/{document_id}")
def get_forensic_results(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    results = db.query(ForensicResult).filter(ForensicResult.document_id == doc.id).all()
    return {
        "document_id": document_id,
        "filename": doc.filename,
        "results": [
            {
                "result_type": r.result_type,
                "finding": r.finding,
                "severity": r.severity,
                "details": r.details,
            }
            for r in results
        ],
    }

@router.post("/{document_id}/analyze")
def run_forensics(document_id: str, db: Session = Depends(get_db)):
    """Run/rerun forensic analysis on a document."""
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if doc.file_type not in ("jpg", "jpeg", "png"):
        return {"message": "Visual forensics available for image documents only", "results": {}}
    
    result = run_visual_forensics(doc.file_path, doc.file_type)
    return {"document_id": document_id, "forensic_results": result}

