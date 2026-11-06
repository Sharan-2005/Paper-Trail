"""
Demo investigation route - preloaded investigation with fictional data.
"""

import uuid
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db, Investigation, Document, Anomaly
from services.analysis_service import calculate_risk_score, build_comparison_table, build_relationship_graph
from services.ai_service import explain_anomaly, explain_investigation_summary

logger = logging.getLogger(__name__)
router = APIRouter()

DEMO_INV_ID = "INV-DEMO0001"

DEMO_DOCUMENTS = [
    {
        "document_id": "DOC-DEMO0001",
        "filename": "Identity_Document_Rahul_Sharma.pdf",
        "file_type": "pdf",
        "document_type": "identity_document",
        "extracted_fields": {
            "full_name": "Rahul Sharma",
            "date_of_birth": "12-05-2002",
            "address": "Flat 304, Andheri West, Mumbai, Maharashtra 400053",
            "document_number": "MH2345678",
            "phone_number": "9876543210",
        },
        "page_count": 1,
        "processing_status": "completed",
        "forensic_results": [],
    },
    {
        "document_id": "DOC-DEMO0002",
        "filename": "PAN_Document_Rahul_Sharma.pdf",
        "file_type": "pdf",
        "document_type": "pan_document",
        "extracted_fields": {
            "full_name": "Rahul Sharma",
            "date_of_birth": "12-05-2002",
            "document_number": "ABCPS1234R",
        },
        "page_count": 1,
        "processing_status": "completed",
        "forensic_results": [],
    },
    {
        "document_id": "DOC-DEMO0003",
        "filename": "Bank_Statement_Rahul_Verma.pdf",
        "file_type": "pdf",
        "document_type": "bank_statement",
        "extracted_fields": {
            "full_name": "Rahul Verma",
            "date_of_birth": "12-05-2001",
            "address": "12 Shivaji Nagar, Pune, Maharashtra 411005",
            "document_number": "ACC-98765432",
            "phone_number": "9876543210",
        },
        "page_count": 3,
        "processing_status": "completed",
        "forensic_results": [],
    },
]

DEMO_ANOMALIES = [
    {
        "anomaly_id": "ANO-DEMO0001",
        "investigation_id": 0,
        "anomaly_type": "full_name_mismatch",
        "field_name": "Full Name",
        "severity": "critical",
        "description": "Name mismatch detected between 'Identity_Document_Rahul_Sharma.pdf' and 'Bank_Statement_Rahul_Verma.pdf'. Values: 'Rahul Sharma' vs 'Rahul Verma'.",
        "source_documents": ["DOC-DEMO0001", "DOC-DEMO0003"],
        "conflicting_values": {"DOC-DEMO0001": "Rahul Sharma", "DOC-DEMO0003": "Rahul Verma"},
        "evidence": "Document 'Identity_Document_Rahul_Sharma.pdf' contains 'Rahul Sharma'; Document 'Bank_Statement_Rahul_Verma.pdf' contains 'Rahul Verma'. These values do not match under normalized comparison.",
        "risk_points": 25,
        "ai_explanation": None,
        "explanation_source": "rules",
        "status": "open",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "anomaly_id": "ANO-DEMO0002",
        "investigation_id": 0,
        "anomaly_type": "date_of_birth_mismatch",
        "field_name": "Date Of Birth",
        "severity": "critical",
        "description": "Date of birth mismatch between 'Identity_Document_Rahul_Sharma.pdf' and 'Bank_Statement_Rahul_Verma.pdf'. Values: '12-05-2002' vs '12-05-2001'.",
        "source_documents": ["DOC-DEMO0001", "DOC-DEMO0003"],
        "conflicting_values": {"DOC-DEMO0001": "12-05-2002", "DOC-DEMO0003": "12-05-2001"},
        "evidence": "Document 'Identity_Document_Rahul_Sharma.pdf' contains DOB '12-05-2002'; Document 'Bank_Statement_Rahul_Verma.pdf' contains DOB '12-05-2001'. One-year discrepancy detected.",
        "risk_points": 25,
        "ai_explanation": None,
        "explanation_source": "rules",
        "status": "open",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "anomaly_id": "ANO-DEMO0003",
        "investigation_id": 0,
        "anomaly_type": "address_mismatch",
        "field_name": "Address",
        "severity": "high",
        "description": "Address mismatch between 'Identity_Document_Rahul_Sharma.pdf' (Mumbai) and 'Bank_Statement_Rahul_Verma.pdf' (Pune).",
        "source_documents": ["DOC-DEMO0001", "DOC-DEMO0003"],
        "conflicting_values": {
            "DOC-DEMO0001": "Flat 304, Andheri West, Mumbai, Maharashtra 400053",
            "DOC-DEMO0003": "12 Shivaji Nagar, Pune, Maharashtra 411005",
        },
        "evidence": "Identity document shows Mumbai address; Bank statement shows Pune address. Cities differ significantly.",
        "risk_points": 15,
        "ai_explanation": None,
        "explanation_source": "rules",
        "status": "open",
        "created_at": datetime.utcnow().isoformat(),
    },
]


def get_or_create_demo(db: Session) -> dict:
    """Return cached demo investigation, creating it if needed."""
    inv = db.query(Investigation).filter(Investigation.investigation_id == DEMO_INV_ID).first()
    if inv:
        return _build_demo_response(inv, db)

    # Create demo investigation
    inv = Investigation(
        investigation_id=DEMO_INV_ID,
        title="[DEMO] Multi-Document Identity Investigation",
        description="Demonstration investigation using fictional sample data. NOT real documents.",
        status="completed",
        risk_score=58.3,
        risk_level="high",
        is_demo=True,
        anomaly_count=3,
        summary=(
            "DEMO INVESTIGATION — Fictional data only. "
            "Analysis of 3 sample documents revealed significant identity discrepancies. "
            "Name mismatch (Rahul Sharma vs Rahul Verma), date of birth discrepancy (2002 vs 2001), "
            "and conflicting address information (Mumbai vs Pune) were detected. "
            "Risk Score: 58/100 (HIGH). These findings require manual verification."
        ),
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # Create documents
    for doc_data in DEMO_DOCUMENTS:
        doc = Document(
            investigation_id=inv.id,
            document_id=doc_data["document_id"],
            filename=doc_data["filename"],
            original_filename=doc_data["filename"],
            file_type=doc_data["file_type"],
            file_path=f"demo/{doc_data['document_id']}",
            document_type=doc_data["document_type"],
            page_count=doc_data["page_count"],
            extracted_fields=doc_data["extracted_fields"],
            processing_status="completed",
        )
        db.add(doc)

    # Create anomalies
    for a_data in DEMO_ANOMALIES:
        a = Anomaly(
            investigation_id=inv.id,
            anomaly_id=a_data["anomaly_id"],
            anomaly_type=a_data["anomaly_type"],
            field_name=a_data["field_name"],
            severity=a_data["severity"],
            description=a_data["description"],
            source_documents=a_data["source_documents"],
            conflicting_values=a_data["conflicting_values"],
            evidence=a_data["evidence"],
            risk_points=a_data["risk_points"],
            status="open",
        )
        db.add(a)

    db.commit()
    db.refresh(inv)

    # Add AI/rule explanations
    for a_data in DEMO_ANOMALIES:
        a_record = db.query(Anomaly).filter(Anomaly.anomaly_id == a_data["anomaly_id"]).first()
        if a_record:
            exp = explain_anomaly(a_data)
            a_record.ai_explanation = exp["explanation"]
            a_record.explanation_source = exp["source"]
    db.commit()

    return _build_demo_response(inv, db)


def _build_demo_response(inv: Investigation, db: Session) -> dict:
    documents = []
    for doc in inv.documents:
        documents.append({
            "document_id": doc.document_id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "document_type": doc.document_type,
            "extracted_fields": doc.extracted_fields or {},
            "page_count": doc.page_count,
            "processing_status": doc.processing_status,
            "forensic_results": [],
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

    comparison_table = build_comparison_table(documents)
    graph_data = build_relationship_graph(documents, anomalies)
    risk_assessment = calculate_risk_score(anomalies)

    return {
        "id": inv.id,
        "investigation_id": inv.investigation_id,
        "title": inv.title,
        "description": inv.description,
        "status": inv.status,
        "risk_score": inv.risk_score or 58.3,
        "risk_level": inv.risk_level or "high",
        "risk_assessment": risk_assessment,
        "anomaly_count": inv.anomaly_count,
        "summary": inv.summary,
        "is_demo": True,
        "demo_notice": "⚠️ DEMO MODE: All data is fictional and for demonstration purposes only.",
        "created_at": inv.created_at.isoformat(),
        "documents": documents,
        "anomalies": anomalies,
        "comparison_table": comparison_table,
        "graph_data": graph_data,
    }


@router.post("/launch")
def launch_demo(db: Session = Depends(get_db)):
    """Launch the demo investigation."""
    result = get_or_create_demo(db)
    return result


@router.get("/")
def get_demo(db: Session = Depends(get_db)):
    """Get demo investigation data."""
    result = get_or_create_demo(db)
    return result

