"""
Cross-document intelligence and anomaly detection engine.
"""

import re
import uuid
import logging
from typing import Any
from datetime import datetime

logger = logging.getLogger(__name__)

# ─── Normalizers ───────────────────────────────────────────────────

def normalize_name(name: str) -> str:
    if not name:
        return ""
    return re.sub(r"\s+", " ", name.strip().upper())


def normalize_date(date_str: str) -> str:
    """Normalize date strings to YYYY-MM-DD where possible."""
    if not date_str:
        return ""
    cleaned = re.sub(r"[^\d/\-\.]", "", date_str.strip())
    for fmt_pattern in [
        (r"(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})", "dmy"),
        (r"(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})", "ymd"),
        (r"(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2})", "dmy2"),
    ]:
        m = re.match(fmt_pattern[0], cleaned)
        if m:
            if fmt_pattern[1] == "dmy":
                return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
            elif fmt_pattern[1] == "ymd":
                return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
            elif fmt_pattern[1] == "dmy2":
                year = int(m.group(3))
                year = 2000 + year if year < 50 else 1900 + year
                return f"{year}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    return cleaned


def normalize_address(addr: str) -> str:
    if not addr:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"[,\.\-]", " ", addr.strip().upper()))


def values_match(v1: str, v2: str, field: str) -> bool:
    """Compare two field values with field-appropriate normalization."""
    if not v1 or not v2:
        return False
    if field in ("full_name",):
        return normalize_name(v1) == normalize_name(v2)
    if field in ("date_of_birth", "issue_date", "expiry_date"):
        n1, n2 = normalize_date(v1), normalize_date(v2)
        return n1 == n2 if (n1 and n2) else v1.strip() == v2.strip()
    if field == "address":
        # partial match – at least 60% word overlap
        words1 = set(normalize_address(v1).split())
        words2 = set(normalize_address(v2).split())
        if not words1 or not words2:
            return False
        overlap = len(words1 & words2) / max(len(words1), len(words2))
        return overlap >= 0.6
    return v1.strip().upper() == v2.strip().upper()


# ─── Scoring ──────────────────────────────────────────────────────

FIELD_RISK_WEIGHTS = {
    "full_name": 25,
    "date_of_birth": 25,
    "document_number": 25,
    "address": 15,
    "phone_number": 5,
    "email": 5,
}

RISK_THRESHOLDS = {
    "low": (0, 20),
    "moderate": (21, 50),
    "high": (51, 75),
    "critical": (76, 100),
}


def get_risk_level(score: float) -> str:
    for level, (lo, hi) in RISK_THRESHOLDS.items():
        if lo <= score <= hi:
            return level
    return "critical"


# ─── Core analysis ─────────────────────────────────────────────────

COMPARABLE_FIELDS = ["full_name", "date_of_birth", "address", "document_number", "phone_number", "email"]


def build_comparison_matrix(documents: list[dict]) -> dict:
    """
    Build a cross-document field comparison matrix.
    Returns a dict of {field: {doc_id: value}} and detected conflicts.
    """
    matrix = {}
    for field in COMPARABLE_FIELDS:
        matrix[field] = {}
        for doc in documents:
            fields = doc.get("extracted_fields", {})
            val = fields.get(field)
            if val:
                matrix[field][doc["document_id"]] = val

    return matrix


def detect_anomalies(documents: list[dict], investigation_id: int) -> list[dict]:
    """
    Compare extracted fields across documents and emit anomaly records.
    """
    anomalies = []
    matrix = build_comparison_matrix(documents)
    seen_conflicts = set()          # avoid double-counting

    for field, doc_values in matrix.items():
        if len(doc_values) < 2:
            continue                # only one document has this field – skip

        doc_ids = list(doc_values.keys())
        for i in range(len(doc_ids)):
            for j in range(i + 1, len(doc_ids)):
                id1, id2 = doc_ids[i], doc_ids[j]
                v1, v2 = doc_values[id1], doc_values[id2]

                if not values_match(v1, v2, field):
                    conflict_key = tuple(sorted([id1, id2, field]))
                    if conflict_key in seen_conflicts:
                        continue
                    seen_conflicts.add(conflict_key)

                    doc1_name = next((d["filename"] for d in documents if d["document_id"] == id1), id1)
                    doc2_name = next((d["filename"] for d in documents if d["document_id"] == id2), id2)

                    anomaly_type = f"{field}_mismatch"
                    risk_points = FIELD_RISK_WEIGHTS.get(field, 10)
                    severity = "critical" if risk_points >= 25 else ("high" if risk_points >= 15 else "medium")

                    anomalies.append({
                        "anomaly_id": f"ANO-{uuid.uuid4().hex[:8].upper()}",
                        "investigation_id": investigation_id,
                        "anomaly_type": anomaly_type,
                        "field_name": field.replace("_", " ").title(),
                        "severity": severity,
                        "description": (
                            f"{field.replace('_', ' ').title()} mismatch detected between "
                            f"'{doc1_name}' and '{doc2_name}'. "
                            f"Values: '{v1}' vs '{v2}'."
                        ),
                        "source_documents": [id1, id2],
                        "conflicting_values": {id1: v1, id2: v2},
                        "evidence": (
                            f"Document '{doc1_name}' contains '{v1}'; "
                            f"Document '{doc2_name}' contains '{v2}'. "
                            f"These values do not match under normalized comparison."
                        ),
                        "risk_points": risk_points,
                        "status": "open",
                    })

    # Check for duplicate document numbers across different documents
    doc_numbers = {}
    for doc in documents:
        num = doc.get("extracted_fields", {}).get("document_number")
        if num:
            if num in doc_numbers:
                other_id = doc_numbers[num]
                if other_id != doc["document_id"]:
                    anomalies.append({
                        "anomaly_id": f"ANO-{uuid.uuid4().hex[:8].upper()}",
                        "investigation_id": investigation_id,
                        "anomaly_type": "duplicate_document_number",
                        "field_name": "Document Number",
                        "severity": "critical",
                        "description": f"Duplicate document number '{num}' found in multiple documents.",
                        "source_documents": [other_id, doc["document_id"]],
                        "conflicting_values": {other_id: num, doc["document_id"]: num},
                        "evidence": f"Document number '{num}' appears in more than one document.",
                        "risk_points": 25,
                        "status": "open",
                    })
            else:
                doc_numbers[num] = doc["document_id"]

    return anomalies


def calculate_risk_score(anomalies: list[dict]) -> dict:
    """Calculate normalized risk score from anomaly list."""
    if not anomalies:
        return {"score": 0, "level": "low", "factors": [], "breakdown": {}}

    # Sum unique risk contributions (avoid double-counting same field)
    seen_fields = {}
    total_raw = 0
    factors = []
    breakdown = {}

    for a in anomalies:
        field = a.get("field_name", "unknown")
        pts = a.get("risk_points", 0)
        if field not in seen_fields or pts > seen_fields[field]:
            seen_fields[field] = pts

    for field, pts in seen_fields.items():
        total_raw += pts
        factors.append({"field": field, "points": pts})
        breakdown[field] = pts

    # Normalize to 100
    max_possible = sum(FIELD_RISK_WEIGHTS.values()) + 10  # +10 for forensics
    score = min(100, round((total_raw / max_possible) * 100, 1))
    level = get_risk_level(score)

    return {
        "score": score,
        "level": level,
        "factors": sorted(factors, key=lambda x: x["points"], reverse=True),
        "breakdown": breakdown,
        "raw_points": total_raw,
        "max_possible": max_possible,
    }


def build_comparison_table(documents: list[dict]) -> list[dict]:
    """
    Return comparison table rows: [{field, values: {doc_id: value}, status}]
    """
    matrix = build_comparison_matrix(documents)
    rows = []
    for field, doc_values in matrix.items():
        if not doc_values:
            continue
        all_values = list(doc_values.values())
        # Determine status
        if len(all_values) == 1:
            status = "single"
        else:
            first = all_values[0]
            if all(values_match(first, v, field) for v in all_values[1:]):
                status = "match"
            else:
                status = "conflict"

        rows.append({
            "field": field.replace("_", " ").title(),
            "field_key": field,
            "values": doc_values,
            "status": status,
        })

    # Also show missing fields
    all_fields = set(COMPARABLE_FIELDS)
    present_fields = set(matrix.keys())
    for field in all_fields - present_fields:
        rows.append({
            "field": field.replace("_", " ").title(),
            "field_key": field,
            "values": {},
            "status": "missing",
        })

    return rows


def build_relationship_graph(documents: list[dict], anomalies: list[dict]) -> dict:
    """
    Build React Flow compatible nodes and edges for the relationship graph.
    """
    nodes = []
    edges = []
    edge_set = set()

    for i, doc in enumerate(documents):
        doc_type = doc.get("document_type", "unknown").replace("_", " ").title()
        nodes.append({
            "id": doc["document_id"],
            "type": "documentNode",
            "position": {"x": 100 + i * 300, "y": 200},
            "data": {
                "label": doc.get("filename", f"Document {i+1}"),
                "documentType": doc_type,
                "documentId": doc["document_id"],
                "fields": doc.get("extracted_fields", {}),
            },
        })

    for anomaly in anomalies:
        src_docs = anomaly.get("source_documents", [])
        if len(src_docs) >= 2:
            edge_id = f"{src_docs[0]}-{src_docs[1]}-{anomaly['field_name']}"
            if edge_id not in edge_set:
                edge_set.add(edge_id)
                edges.append({
                    "id": edge_id,
                    "source": src_docs[0],
                    "target": src_docs[1],
                    "type": "conflictEdge",
                    "animated": True,
                    "style": {"stroke": "#ef4444", "strokeWidth": 2},
                    "label": anomaly["field_name"],
                    "data": {
                        "anomalyType": anomaly["anomaly_type"],
                        "fieldName": anomaly["field_name"],
                        "conflictingValues": anomaly.get("conflicting_values", {}),
                        "severity": anomaly["severity"],
                    },
                })

    # Add green edges for matching fields
    matrix = build_comparison_matrix(documents)
    for field, doc_values in matrix.items():
        doc_ids = list(doc_values.keys())
        if len(doc_ids) < 2:
            continue
        for i in range(len(doc_ids)):
            for j in range(i + 1, len(doc_ids)):
                id1, id2 = doc_ids[i], doc_ids[j]
                v1, v2 = doc_values[id1], doc_values[id2]
                if values_match(v1, v2, field):
                    edge_id = f"{id1}-{id2}-match-{field}"
                    if edge_id not in edge_set:
                        edge_set.add(edge_id)
                        edges.append({
                            "id": edge_id,
                            "source": id1,
                            "target": id2,
                            "type": "matchEdge",
                            "animated": False,
                            "style": {"stroke": "#22c55e", "strokeWidth": 1.5},
                            "label": f"✓ {field.replace('_', ' ').title()}",
                            "data": {"match": True, "field": field, "value": v1},
                        })

    return {"nodes": nodes, "edges": edges}

