"""
Database initialization and SQLAlchemy models for PaperTrail.
"""

import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text,
    DateTime, Boolean, ForeignKey, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─────────────────────────── ORM Models ───────────────────────────

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")          # pending | processing | completed | failed
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)          # low | moderate | high | critical
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    summary = Column(Text, nullable=True)
    anomaly_count = Column(Integer, default=0)

    documents = relationship("Document", back_populates="investigation", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="investigation", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"))
    document_id = Column(String, unique=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)          # pdf | image
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    document_type = Column(String, nullable=True)       # identity | pan | bank_statement | etc.
    page_count = Column(Integer, default=1)
    ocr_text = Column(Text, nullable=True)
    extracted_fields = Column(JSON, nullable=True)
    processing_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="documents")
    forensic_results = relationship("ForensicResult", back_populates="document", cascade="all, delete-orphan")


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"))
    anomaly_id = Column(String, unique=True, index=True)
    anomaly_type = Column(String, nullable=False)       # name_mismatch | dob_mismatch | etc.
    field_name = Column(String, nullable=False)
    severity = Column(String, default="medium")         # low | medium | high | critical
    description = Column(Text, nullable=False)
    source_documents = Column(JSON, nullable=True)      # list of document IDs
    conflicting_values = Column(JSON, nullable=True)    # {doc_id: value}
    evidence = Column(Text, nullable=True)
    risk_points = Column(Integer, default=0)
    ai_explanation = Column(Text, nullable=True)
    explanation_source = Column(String, default="rules") # ai | rules
    status = Column(String, default="open")             # open | reviewed | dismissed
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="anomalies")


class ForensicResult(Base):
    __tablename__ = "forensic_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    result_type = Column(String, nullable=False)        # ela | metadata | compression | etc.
    finding = Column(Text, nullable=True)
    severity = Column(String, default="info")
    details = Column(JSON, nullable=True)
    image_path = Column(String, nullable=True)          # path to forensic image
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="forensic_results")


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(String, index=True)
    report_path = Column(String, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer, nullable=True)


# ─────────────────────────── Helpers ───────────────────────────

def init_db():
    Base.metadata.create_all(bind=engine)

# Auto-initialize database tables on module load
init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

