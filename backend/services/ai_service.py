"""
AI explanation service using Gemini API with rule-based fallback.
"""

import os
import logging
from typing import Optional
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)
_GEMINI_AVAILABLE = False

if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        from google import genai
        _genai_client = genai.Client(api_key=GEMINI_API_KEY)
        _GEMINI_AVAILABLE = True
        logger.info("✅ Gemini API initialized")
    except Exception as e:
        logger.warning(f"Gemini API unavailable: {e}")
        _genai_client = None
else:
    _genai_client = None
    logger.info("ℹ️  No Gemini API key – using rule-based explanations")


# ─── Gemini explanation ───────────────────────────────────────────

SYSTEM_PROMPT = """You are PaperTrail's forensic investigation assistant. 
Your role is to explain document anomalies found during investigation in clear, 
professional language for investigators. 

Rules:
- Be factual and grounded in the provided evidence
- Never invent data, documents, or findings not provided to you
- Explain what was found, why it matters, and what should be verified
- Keep explanations concise (3-5 sentences per section)
- Do not make definitive fraud conclusions — flag for manual review
"""


def get_gemini_explanation(anomaly: dict, context: dict) -> Optional[str]:
    """Get AI explanation from Gemini API."""
    if not _GEMINI_AVAILABLE or _genai_client is None:
        return None

    prompt = f"""
Explain this document anomaly for an investigation report:

ANOMALY TYPE: {anomaly.get('anomaly_type', 'unknown')}
FIELD: {anomaly.get('field_name', 'unknown')}
SEVERITY: {anomaly.get('severity', 'medium')}
DESCRIPTION: {anomaly.get('description', '')}
EVIDENCE: {anomaly.get('evidence', '')}
CONFLICTING VALUES: {anomaly.get('conflicting_values', {})}
SOURCE DOCUMENTS: {', '.join(anomaly.get('source_documents', []))}

Please provide:
1. What was detected
2. Why this requires investigation
3. What the investigator should verify next
"""

    try:
        interaction = _genai_client.interactions.create(
            model="gemini-3.8-flash",
            system_instruction=SYSTEM_PROMPT,
            input=prompt,
            store=False,
        )
        return interaction.output_text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None


# ─── Rule-based fallback ──────────────────────────────────────────

RULE_TEMPLATES = {
    "full_name_mismatch": """
**What was detected:** A discrepancy in the name field was found between documents in this investigation. The name recorded differs across two or more submitted documents.

**Why this requires investigation:** Consistent identity information is critical in document verification. A name mismatch may indicate typographical errors, the use of aliases, different legal name formats, or potentially fraudulent document substitution.

**What the investigator should verify next:**
- Confirm the legal name on the applicant's primary government-issued identity document
- Check whether the variation is a spelling difference, abbreviation, or completely different name
- Request a name explanation letter from the applicant if the discrepancy cannot be resolved through documents
""",
    "date_of_birth_mismatch": """
**What was detected:** A date of birth discrepancy was identified across documents in this investigation.

**Why this requires investigation:** Date of birth is a core identity verification field. Even a single-digit difference may indicate data entry errors, age manipulation, or use of documents belonging to different individuals.

**What the investigator should verify next:**
- Cross-reference the date of birth against the primary identity document
- Look for the possibility of day/month transposition (common OCR error: 12-05 vs 05-12)
- Verify whether the discrepancy affects age-dependent eligibility criteria in this case
""",
    "address_mismatch": """
**What was detected:** The address information does not match consistently across all submitted documents.

**Why this requires investigation:** Address consistency is an indicator of residential stability and document authenticity. Mismatches may reflect a genuine change of address, document forgery, or use of documents from different time periods.

**What the investigator should verify next:**
- Identify which document carries the more recent address
- Request recent utility bills or government-issued correspondence to confirm current address
- Determine if the address difference is material to the purpose of this investigation
""",
    "document_number_mismatch": """
**What was detected:** Document numbers do not match across two or more documents that should reference the same underlying credential.

**Why this requires investigation:** Document numbers are unique identifiers. A mismatch may indicate separate legitimate documents, typographical errors during data entry, or potentially forged documents.

**What the investigator should verify next:**
- Verify the document number against the issuing authority's records
- Determine whether both documents are genuinely issued for the same individual
- Check document issuance dates to establish chronological context
""",
    "duplicate_document_number": """
**What was detected:** The same document number appears on multiple different documents within this investigation.

**Why this requires investigation:** Duplicate document numbers are a significant anomaly. Each document should carry a unique identifier. This may indicate photocopied documents, forged documents, or database duplication errors.

**What the investigator should verify next:**
- Immediately escalate to verify document authenticity with the issuing authority
- Determine if both documents are physically present and examined
- Check whether the documents are copies of the same original or represent two different issuances
""",
    "default": """
**What was detected:** An inconsistency was identified in the document comparison analysis.

**Why this requires investigation:** This discrepancy requires manual verification to ensure document authenticity and information consistency.

**What the investigator should verify next:**
- Review the original source documents carefully
- Cross-reference the conflicting information against additional supporting documents
- Contact the applicant or relevant authority to clarify the discrepancy
""",
}


def get_rule_based_explanation(anomaly: dict) -> str:
    """Generate a structured explanation using predefined rules."""
    anomaly_type = anomaly.get("anomaly_type", "default")
    template = RULE_TEMPLATES.get(anomaly_type, RULE_TEMPLATES["default"])

    # Inject actual values into the template
    conflicting = anomaly.get("conflicting_values", {})
    if conflicting:
        values_str = ", ".join([f"'{v}' (Document {k[-8:]})" for k, v in conflicting.items()])
        header = f"\n**Conflicting Values:** {values_str}\n"
        template = header + template

    return template.strip()


# ─── Public interface ─────────────────────────────────────────────

def explain_anomaly(anomaly: dict, context: dict = None) -> dict:
    """
    Get explanation for an anomaly.
    Returns {explanation, source} where source is 'ai' or 'rules'.
    """
    context = context or {}

    # Try Gemini first
    ai_explanation = get_gemini_explanation(anomaly, context)
    if ai_explanation:
        return {"explanation": ai_explanation, "source": "ai"}

    # Fall back to rules
    rule_explanation = get_rule_based_explanation(anomaly)
    return {"explanation": rule_explanation, "source": "rules"}


def explain_investigation_summary(investigation_data: dict) -> dict:
    """Get an AI or rule-based summary of the whole investigation."""
    anomaly_count = len(investigation_data.get("anomalies", []))
    risk_score = investigation_data.get("risk_score", 0)
    risk_level = investigation_data.get("risk_level", "low")

    if _GEMINI_AVAILABLE and _genai_client:
        prompt = f"""
Provide a brief investigation summary for this document forensics case:

Risk Score: {risk_score}/100 ({risk_level.upper()})
Total Anomalies: {anomaly_count}
Documents Analyzed: {len(investigation_data.get('documents', []))}

Key findings: {', '.join([a.get('description', '')[:100] for a in investigation_data.get('anomalies', [])[:3]])}

Write a 2-3 sentence professional summary for an investigation dossier.
"""
        try:
            interaction = _genai_client.interactions.create(
                model="gemini-3.8-flash",
                system_instruction=SYSTEM_PROMPT,
                input=prompt,
                store=False,
            )
            return {"summary": interaction.output_text, "source": "ai"}
        except Exception:
            pass

    # Rule-based summary
    if anomaly_count == 0:
        summary = f"Analysis of {len(investigation_data.get('documents', []))} document(s) revealed no cross-document inconsistencies. Risk score: {risk_score}/100 ({risk_level.upper()}). No immediate manual verification flags were raised."
    elif risk_level == "low":
        summary = f"Investigation identified {anomaly_count} minor anomaly(ies) across the submitted documents. Risk score: {risk_score}/100 (LOW). These discrepancies appear low-risk but should be reviewed before final approval."
    elif risk_level == "moderate":
        summary = f"Investigation identified {anomaly_count} anomaly(ies) requiring attention. Risk score: {risk_score}/100 (MODERATE). One or more significant field mismatches were detected and require manual verification before proceeding."
    elif risk_level == "high":
        summary = f"Investigation identified {anomaly_count} anomaly(ies) with significant risk indicators. Risk score: {risk_score}/100 (HIGH). Multiple field mismatches across documents warrant immediate escalation and verification with issuing authorities."
    else:
        summary = f"Investigation identified {anomaly_count} critical anomaly(ies). Risk score: {risk_score}/100 (CRITICAL). Serious inconsistencies across key identity fields have been detected. This case requires immediate review and potential escalation."

    return {"summary": summary, "source": "rules"}

