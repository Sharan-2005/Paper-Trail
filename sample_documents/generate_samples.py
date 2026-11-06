"""
Generate fictional sample documents for PaperTrail demonstration.
Creates 3 sample PDFs with intentional discrepancies:
- Document 1: Identity Document (Rahul Sharma, DOB: 12-05-2002, Mumbai)
- Document 2: PAN Card (Rahul Sharma, DOB: 12-05-2002)
- Document 3: Bank Statement (Rahul Verma, DOB: 12-05-2001, Pune)
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER

SAMPLE_DIR = Path(__file__).parent
SAMPLE_DIR.mkdir(exist_ok=True)

NAVY = colors.HexColor("#101C2B")
CYAN = colors.HexColor("#45D6E8")
WHITE = colors.white
LIGHT_GRAY = colors.HexColor("#F8FAFC")


def generate_identity_document():
    path = str(SAMPLE_DIR / "Identity_Document_Rahul_Sharma.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=40, bottomMargin=40, leftMargin=40, rightMargin=40)
    styles = getSampleStyleSheet()

    story = [
        Paragraph("<b>DEMO DATA — FICTIONAL DOCUMENT FOR HACKATHON DEMONSTRATION ONLY</b>", 
                  ParagraphStyle("demo", fontName="Helvetica-Bold", fontSize=8, textColor=colors.red, alignment=TA_CENTER)),
        Spacer(1, 10),
        Paragraph("<b>GOVERNMENT IDENTITY CARD</b>", 
                  ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=18, textColor=NAVY, alignment=TA_CENTER)),
        Paragraph("NATIONAL IDENTITY AUTHORITY OF INDIA", 
                  ParagraphStyle("sub", fontName="Helvetica", fontSize=10, textColor=colors.HexColor("#64748B"), alignment=TA_CENTER)),
        Spacer(1, 15),
        HRFlowable(width="100%", thickness=2, color=CYAN),
        Spacer(1, 15),
    ]

    fields = [
        ["Field", "Details"],
        ["Full Name:", "Rahul Sharma"],
        ["Date of Birth:", "12-05-2002"],
        ["Gender:", "Male"],
        ["Document Number:", "MH2345678"],
        ["Address:", "Flat 304, Andheri West, Mumbai, Maharashtra 400053"],
        ["Phone Number:", "9876543210"],
        ["Issue Date:", "15-08-2020"],
    ]

    t = Table(fields, colWidths=[200, 300])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)

    story.append(Spacer(1, 30))
    story.append(Paragraph("This is a fictional identity document generated for testing document forensic systems.", 
                           ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=8, textColor=colors.gray, alignment=TA_CENTER)))

    doc.build(story)
    print(f"Generated: {path}")


def generate_pan_document():
    path = str(SAMPLE_DIR / "PAN_Document_Rahul_Sharma.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=40, bottomMargin=40, leftMargin=40, rightMargin=40)
    styles = getSampleStyleSheet()

    story = [
        Paragraph("<b>DEMO DATA — FICTIONAL DOCUMENT FOR HACKATHON DEMONSTRATION ONLY</b>", 
                  ParagraphStyle("demo", fontName="Helvetica-Bold", fontSize=8, textColor=colors.red, alignment=TA_CENTER)),
        Spacer(1, 10),
        Paragraph("<b>INCOME TAX DEPARTMENT</b>", 
                  ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=18, textColor=NAVY, alignment=TA_CENTER)),
        Paragraph("PERMANENT ACCOUNT NUMBER CARD", 
                  ParagraphStyle("sub", fontName="Helvetica-Bold", fontSize=12, textColor=colors.HexColor("#2563EB"), alignment=TA_CENTER)),
        Spacer(1, 15),
        HRFlowable(width="100%", thickness=2, color=CYAN),
        Spacer(1, 15),
    ]

    fields = [
        ["Field", "Details"],
        ["Full Name:", "Rahul Sharma"],
        ["Father's Name:", "Suresh Sharma"],
        ["Date of Birth:", "12-05-2002"],
        ["Document Number:", "ABCPS1234R"],
        ["Card Type:", "Individual"],
        ["Issue Date:", "10-01-2021"],
    ]

    t = Table(fields, colWidths=[200, 300])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)

    story.append(Spacer(1, 30))
    story.append(Paragraph("This is a fictional PAN card generated for testing document forensic systems.", 
                           ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=8, textColor=colors.gray, alignment=TA_CENTER)))

    doc.build(story)
    print(f"Generated: {path}")


def generate_bank_statement():
    path = str(SAMPLE_DIR / "Bank_Statement_Rahul_Verma.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=40, bottomMargin=40, leftMargin=40, rightMargin=40)
    styles = getSampleStyleSheet()

    story = [
        Paragraph("<b>DEMO DATA — FICTIONAL DOCUMENT FOR HACKATHON DEMONSTRATION ONLY</b>", 
                  ParagraphStyle("demo", fontName="Helvetica-Bold", fontSize=8, textColor=colors.red, alignment=TA_CENTER)),
        Spacer(1, 10),
        Paragraph("<b>GLOBAL TRUST BANK</b>", 
                  ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=18, textColor=NAVY, alignment=TA_CENTER)),
        Paragraph("STATEMENT OF ACCOUNT", 
                  ParagraphStyle("sub", fontName="Helvetica", fontSize=11, textColor=colors.HexColor("#64748B"), alignment=TA_CENTER)),
        Spacer(1, 15),
        HRFlowable(width="100%", thickness=2, color=CYAN),
        Spacer(1, 15),
    ]

    fields = [
        ["Account Holder Details", ""],
        ["Full Name:", "Rahul Verma"],  # INTENTIONAL NAME MISMATCH: Verma instead of Sharma
        ["Date of Birth:", "12-05-2001"],  # INTENTIONAL DOB MISMATCH: 2001 instead of 2002
        ["Address:", "12 Shivaji Nagar, Pune, Maharashtra 411005"],  # INTENTIONAL ADDRESS MISMATCH: Pune instead of Mumbai
        ["Document Number:", "ACC-98765432"],
        ["Phone Number:", "9876543210"],
        ["Branch:", "Pune Main Branch"],
        ["IFSC Code:", "GTBK0001234"],
    ]

    t = Table(fields, colWidths=[200, 300])
    t.setStyle(TableStyle([
        ("SPAN", (0, 0), (1, 0)),
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)

    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Recent Transactions:</b>", ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11)))
    story.append(Spacer(1, 5))

    tx_data = [
        ["Date", "Description", "Debit", "Credit", "Balance"],
        ["01-10-2023", "Salary Credit", "-", "75,000.00", "85,420.00"],
        ["05-10-2023", "ATM Withdrawal", "10,000.00", "-", "75,420.00"],
        ["12-10-2023", "Electricity Bill", "2,340.00", "-", "73,080.00"],
        ["20-10-2023", "Online Transfer", "15,000.00", "-", "58,080.00"],
    ]
    t2 = Table(tx_data, colWidths=[80, 180, 80, 80, 80])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t2)

    story.append(Spacer(1, 20))
    story.append(Paragraph("This is a fictional bank statement generated for testing document forensic systems.", 
                           ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=8, textColor=colors.gray, alignment=TA_CENTER)))

    doc.build(story)
    print(f"Generated: {path}")


if __name__ == "__main__":
    generate_identity_document()
    generate_pan_document()
    generate_bank_statement()
    print("All sample documents generated successfully!")

