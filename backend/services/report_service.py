"""
PDF Report generation using ReportLab.
"""

import os
import io
import uuid
import logging
from datetime import datetime
from pathlib import Path

from config import REPORTS_DIR

logger = logging.getLogger(__name__)

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not installed – PDF generation unavailable")

# ─── Color palette ─────────────────────────────────────────────────
NAVY = colors.HexColor("#101C2B")
CYAN = colors.HexColor("#45D6E8")
BLUE = colors.HexColor("#2563EB")
RED = colors.HexColor("#EF4444")
GREEN = colors.HexColor("#22C55E")
YELLOW = colors.HexColor("#F59E0B")
PURPLE = colors.HexColor("#8B5CF6")
GRAY = colors.HexColor("#64748B")
LIGHT_GRAY = colors.HexColor("#F1F5F9")
WHITE = colors.white

RISK_COLORS = {
    "low": GREEN,
    "moderate": YELLOW,
    "high": colors.HexColor("#F97316"),
    "critical": RED,
}


def _build_styles():
    styles = getSampleStyleSheet()
    custom = {
        "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24, textColor=WHITE, alignment=TA_CENTER, spaceAfter=6),
        "subtitle": ParagraphStyle("subtitle", fontName="Helvetica", fontSize=12, textColor=CYAN, alignment=TA_CENTER, spaceAfter=4),
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=16, textColor=NAVY, spaceBefore=12, spaceAfter=6, borderPad=4),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13, textColor=BLUE, spaceBefore=10, spaceAfter=4),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11, textColor=NAVY, spaceBefore=8, spaceAfter=3),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10, textColor=colors.black, spaceAfter=4, leading=14),
        "bold": ParagraphStyle("bold", fontName="Helvetica-Bold", fontSize=10, textColor=colors.black, spaceAfter=4),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8, textColor=GRAY, spaceAfter=3),
        "mono": ParagraphStyle("mono", fontName="Courier", fontSize=9, textColor=colors.black, spaceAfter=3),
        "risk_low": ParagraphStyle("risk_low", fontName="Helvetica-Bold", fontSize=12, textColor=GREEN, alignment=TA_CENTER),
        "risk_moderate": ParagraphStyle("risk_moderate", fontName="Helvetica-Bold", fontSize=12, textColor=YELLOW, alignment=TA_CENTER),
        "risk_high": ParagraphStyle("risk_high", fontName="Helvetica-Bold", fontSize=12, textColor=colors.HexColor("#F97316"), alignment=TA_CENTER),
        "risk_critical": ParagraphStyle("risk_critical", fontName="Helvetica-Bold", fontSize=12, textColor=RED, alignment=TA_CENTER),
        "disclaimer": ParagraphStyle("disclaimer", fontName="Helvetica-Oblique", fontSize=8, textColor=GRAY, spaceAfter=4, leading=12),
    }
    return custom


def _header_footer(canvas, doc):
    """Draw header and footer on each page."""
    canvas.saveState()
    page_width, page_height = A4

    # Header bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, page_height - 40, page_width, 40, fill=1, stroke=0)

    canvas.setFillColor(CYAN)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(30, page_height - 25, "PaperTrail")

    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(120, page_height - 25, "Document Forensics & Intelligence")

    canvas.setFillColor(GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(page_width - 30, page_height - 25, "CONFIDENTIAL – FOR AUTHORIZED USE ONLY")

    # Footer
    canvas.setFillColor(LIGHT_GRAY)
    canvas.rect(0, 0, page_width, 25, fill=1, stroke=0)
    canvas.setFillColor(GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(30, 8, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    canvas.drawCentredString(page_width / 2, 8, "PaperTrail — Follow the Evidence")
    canvas.drawRightString(page_width - 30, 8, f"Page {doc.page}")

    canvas.restoreState()


def generate_investigation_report(investigation_data: dict) -> str:
    """
    Generate a full PDF investigation dossier.
    Returns the path to the generated PDF.
    """
    if not _REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab is not installed. Run: pip install reportlab")

    inv_id = investigation_data.get("investigation_id", f"INV-{uuid.uuid4().hex[:8].upper()}")
    report_filename = f"PaperTrail_Report_{inv_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    report_path = str(REPORTS_DIR / report_filename)

    pdf_doc = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        topMargin=60,
        bottomMargin=40,
        leftMargin=30,
        rightMargin=30,
    )

    styles = _build_styles()
    story = []
    page_width = A4[0] - 60  # usable width

    # ── COVER PAGE ─────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * inch))

    # Title box
    cover_data = [[
        Paragraph("INVESTIGATION DOSSIER", styles["title"]),
    ]]
    cover_table = Table(cover_data, colWidths=[page_width])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Document Forensics & Contextual Intelligence", styles["subtitle"]))
    story.append(Spacer(1, 0.3 * inch))

    # Investigation meta
    risk_score = investigation_data.get("risk_score", 0)
    risk_level = investigation_data.get("risk_level", "low")
    risk_color = RISK_COLORS.get(risk_level, GRAY)

    meta_data = [
        ["Investigation ID:", inv_id],
        ["Date:", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")],
        ["Documents Analyzed:", str(len(investigation_data.get("documents", [])))],
        ["Anomalies Detected:", str(len(investigation_data.get("anomalies", [])))],
        ["Risk Score:", f"{risk_score}/100"],
        ["Risk Level:", risk_level.upper()],
    ]

    meta_table = Table(meta_data, colWidths=[2 * inch, page_width - 2 * inch])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TEXTCOLOR", (1, 5), (1, 5), risk_color),
        ("FONTNAME", (1, 5), (1, 5), "Helvetica-Bold"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.3 * inch))

    # Summary
    summary = investigation_data.get("summary", "")
    if summary:
        story.append(Paragraph("Investigation Summary", styles["h2"]))
        story.append(Paragraph(summary, styles["body"]))
        story.append(Spacer(1, 0.2 * inch))

    # Disclaimer
    story.append(HRFlowable(width=page_width, thickness=0.5, color=GRAY))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(
        "⚠️  DISCLAIMER: This report is generated by an automated forensic analysis system. "
        "Risk scores are preliminary indicators only and do not constitute proof of fraud or document manipulation. "
        "All findings require manual verification by qualified investigators before any action is taken. "
        "This system is a decision-support tool, not a replacement for human judgment.",
        styles["disclaimer"]
    ))
    story.append(PageBreak())

    # ── SECTION 1: DOCUMENT OVERVIEW ──────────────────────────────
    story.append(Paragraph("1. Document Overview", styles["h1"]))
    story.append(HRFlowable(width=page_width, thickness=1, color=CYAN))
    story.append(Spacer(1, 0.1 * inch))

    for i, doc in enumerate(investigation_data.get("documents", []), 1):
        story.append(Paragraph(f"Document {i}: {doc.get('filename', 'Unknown')}", styles["h3"]))
        
        doc_meta = [
            ["Document ID:", doc.get("document_id", "-")],
            ["File Type:", doc.get("file_type", "-").upper()],
            ["Document Type:", doc.get("document_type", "-").replace("_", " ").title()],
            ["Processing Status:", doc.get("processing_status", "-").title()],
        ]
        
        doc_table = Table(doc_meta, colWidths=[1.5 * inch, page_width - 1.5 * inch])
        doc_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(doc_table)

        # Extracted fields
        fields = doc.get("extracted_fields", {})
        if fields:
            story.append(Spacer(1, 0.08 * inch))
            story.append(Paragraph("Extracted Information:", styles["bold"]))
            field_rows = [["Field", "Extracted Value"]]
            for key, val in fields.items():
                field_rows.append([key.replace("_", " ").title(), str(val)])
            
            field_table = Table(field_rows, colWidths=[2 * inch, page_width - 2 * inch])
            field_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(field_table)

        story.append(Spacer(1, 0.2 * inch))

    # ── SECTION 2: CROSS-DOCUMENT COMPARISON ──────────────────────
    story.append(PageBreak())
    story.append(Paragraph("2. Cross-Document Comparison", styles["h1"]))
    story.append(HRFlowable(width=page_width, thickness=1, color=CYAN))
    story.append(Spacer(1, 0.1 * inch))

    comparison_table_data = investigation_data.get("comparison_table", [])
    if comparison_table_data:
        docs = investigation_data.get("documents", [])
        doc_names = [d.get("filename", f"Doc {i+1}")[:20] for i, d in enumerate(docs)]
        doc_ids = [d.get("document_id") for d in docs]

        header_row = ["Field"] + doc_names + ["Status"]
        col_widths = [1.5 * inch] + [1.2 * inch] * len(doc_names) + [0.8 * inch]

        table_rows = [header_row]
        for row in comparison_table_data:
            status = row.get("status", "unknown")
            status_text = {"match": "✓ Match", "conflict": "⚠ Conflict", "missing": "– Missing", "single": "○ Single"}.get(status, status)
            
            values = row.get("values", {})
            data_row = [row.get("field", "")]
            for doc_id in doc_ids:
                val = values.get(doc_id, "—")
                data_row.append(str(val)[:25] if val else "—")
            data_row.append(status_text)
            table_rows.append(data_row)

        comp_table = Table(table_rows, colWidths=col_widths)
        style_cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("ALIGN", (-1, 0), (-1, -1), "CENTER"),
        ]
        
        for row_idx, row in enumerate(comparison_table_data, 1):
            status = row.get("status", "")
            if status == "match":
                style_cmds.append(("TEXTCOLOR", (-1, row_idx), (-1, row_idx), GREEN))
            elif status == "conflict":
                style_cmds.append(("TEXTCOLOR", (-1, row_idx), (-1, row_idx), RED))
                style_cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#FEF2F2")))
            elif status == "missing":
                style_cmds.append(("TEXTCOLOR", (-1, row_idx), (-1, row_idx), YELLOW))

        comp_table.setStyle(TableStyle(style_cmds))
        story.append(comp_table)

    # ── SECTION 3: IDENTIFIED ANOMALIES ───────────────────────────
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("3. Identified Anomalies", styles["h1"]))
    story.append(HRFlowable(width=page_width, thickness=1, color=CYAN))
    story.append(Spacer(1, 0.1 * inch))

    anomalies = investigation_data.get("anomalies", [])
    if not anomalies:
        story.append(Paragraph("No anomalies detected in this investigation.", styles["body"]))
    else:
        for i, anomaly in enumerate(anomalies, 1):
            severity = anomaly.get("severity", "medium")
            sev_color = {"critical": RED, "high": colors.HexColor("#F97316"), "medium": YELLOW, "low": GREEN}.get(severity, GRAY)

            sev_badge = [[Paragraph(severity.upper(), ParagraphStyle("sev", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, alignment=TA_CENTER))]]
            sev_table = Table(sev_badge, colWidths=[0.7 * inch])
            sev_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), sev_color),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))

            story.append(KeepTogether([
                Paragraph(f"Anomaly {i}: {anomaly.get('field_name', 'Unknown')} Discrepancy", styles["h3"]),
                Paragraph(f"Type: {anomaly.get('anomaly_type', '').replace('_', ' ').title()} | ID: {anomaly.get('anomaly_id', '-')}", styles["small"]),
                Spacer(1, 0.05 * inch),
                Paragraph(anomaly.get("description", ""), styles["body"]),
                Spacer(1, 0.05 * inch),
                Paragraph("<b>Evidence:</b> " + anomaly.get("evidence", ""), styles["body"]),
                Spacer(1, 0.05 * inch),
            ]))

            # AI explanation
            explanation = anomaly.get("ai_explanation", "")
            if explanation:
                story.append(Paragraph("Investigation Notes:", styles["bold"]))
                # Strip markdown
                clean_exp = explanation.replace("**", "").replace("*", "").replace("#", "")
                story.append(Paragraph(clean_exp[:800], styles["body"]))

            story.append(HRFlowable(width=page_width, thickness=0.5, color=LIGHT_GRAY))
            story.append(Spacer(1, 0.1 * inch))

    # ── SECTION 4: RISK ASSESSMENT ─────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("4. Risk Assessment", styles["h1"]))
    story.append(HRFlowable(width=page_width, thickness=1, color=CYAN))
    story.append(Spacer(1, 0.15 * inch))

    risk_assessment = investigation_data.get("risk_assessment", {})
    risk_level = risk_assessment.get("level", investigation_data.get("risk_level", "low"))
    risk_score = risk_assessment.get("score", investigation_data.get("risk_score", 0))
    risk_color = RISK_COLORS.get(risk_level, GRAY)

    # Risk score display
    risk_display = [[
        Paragraph(f"{risk_score}", ParagraphStyle("rs", fontName="Helvetica-Bold", fontSize=48, textColor=risk_color, alignment=TA_CENTER)),
        Paragraph(f"/100\n\n{risk_level.upper()}", ParagraphStyle("rl", fontName="Helvetica-Bold", fontSize=14, textColor=risk_color, alignment=TA_LEFT)),
    ]]
    risk_disp_table = Table(risk_display, colWidths=[1.5 * inch, page_width - 1.5 * inch])
    risk_disp_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(risk_disp_table)
    story.append(Spacer(1, 0.15 * inch))

    factors = risk_assessment.get("factors", [])
    if factors:
        story.append(Paragraph("Risk Factor Breakdown:", styles["h2"]))
        factor_rows = [["Risk Factor", "Points Assigned"]]
        for f in factors:
            factor_rows.append([f.get("field", "-"), str(f.get("points", 0))])
        factor_rows.append(["TOTAL (normalized to 100)", f"{risk_score}/100"])

        factor_table = Table(factor_rows, colWidths=[3 * inch, page_width - 3 * inch])
        factor_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), LIGHT_GRAY),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(factor_table)

    # ── SECTION 5: FORENSIC OBSERVATIONS ──────────────────────────
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("5. Visual Forensic Observations", styles["h1"]))
    story.append(HRFlowable(width=page_width, thickness=1, color=CYAN))
    story.append(Spacer(1, 0.1 * inch))

    forensic_results = investigation_data.get("forensic_results", [])
    if not forensic_results:
        story.append(Paragraph("Visual forensic analysis was not performed or no image documents were submitted.", styles["body"]))
    else:
        for fr in forensic_results:
            story.append(Paragraph(f"Document: {fr.get('document_name', 'Unknown')}", styles["h3"]))
            checks = fr.get("checks", {})
            for check_name, check_data in checks.items():
                if isinstance(check_data, dict) and check_data.get("available"):
                    interp = check_data.get("interpretation", "")
                    if interp:
                        status = "⚠️" if check_data.get("potentially_suspicious") else "✓"
                        story.append(Paragraph(f"{status} <b>{check_name.upper()}:</b> {interp}", styles["body"]))
            story.append(Spacer(1, 0.1 * inch))

    # ── SECTION 6: SYSTEM LIMITATIONS ─────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("6. System Limitations and Recommendations", styles["h1"]))
    story.append(HRFlowable(width=page_width, thickness=1, color=CYAN))
    story.append(Spacer(1, 0.1 * inch))

    limitations = [
        "OCR accuracy depends on document scan quality. Low-resolution or skewed documents may yield incomplete extraction.",
        "ELA and visual forensic checks are heuristic tools and cannot conclusively prove document manipulation.",
        "Risk scores are preliminary indicators based on cross-document field comparison, not certified forensic analysis.",
        "The system requires Tesseract OCR to be installed for image-based text extraction.",
        "AI-generated explanations (when Gemini API is available) are supplementary observations, not definitive conclusions.",
        "All findings in this report require manual verification by qualified investigators.",
        "The system does not access external databases or verify documents against government records.",
    ]

    for lim in limitations:
        story.append(Paragraph(f"• {lim}", styles["body"]))

    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Recommended Verification Steps:", styles["h2"]))
    recs = [
        "Obtain original physical documents for examination where possible.",
        "Cross-verify identity information with the issuing authority.",
        "Request supporting documentation from the applicant to explain discrepancies.",
        "Consult a certified document forensic examiner for contested findings.",
        "Document all verification steps taken for the audit trail.",
    ]
    for rec in recs:
        story.append(Paragraph(f"• {rec}", styles["body"]))

    # Final disclaimer
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width=page_width, thickness=1, color=GRAY))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(
        "This document was generated by PaperTrail — Document Forensics & Intelligence System. "
        "It is intended for authorized investigators only. The findings herein are preliminary and "
        "should not be used as sole basis for any adverse action. PaperTrail — Follow the Evidence.",
        styles["disclaimer"]
    ))

    # Build PDF
    pdf_doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    logger.info(f"Generated report: {report_path}")
    return report_path

