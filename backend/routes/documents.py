"""Documents routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db, Document

router = APIRouter()

@router.get("/{document_id}")
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "document_id": doc.document_id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "document_type": doc.document_type,
        "extracted_fields": doc.extracted_fields or {},
        "ocr_text": doc.ocr_text,
        "page_count": doc.page_count,
        "processing_status": doc.processing_status,
    }

@router.patch("/{document_id}/fields")
def update_document_fields(document_id: str, fields: dict, db: Session = Depends(get_db)):
    """Allow investigators to correct OCR mistakes."""
    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    existing = doc.extracted_fields or {}
    existing.update(fields)
    doc.extracted_fields = existing
    db.commit()
    return {"message": "Fields updated", "extracted_fields": doc.extracted_fields}

