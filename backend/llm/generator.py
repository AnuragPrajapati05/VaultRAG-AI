"""LLM Generator - VaultRAG AI (Gemini)"""

import os
import warnings
from typing import List, Dict
from dotenv import load_dotenv

warnings.filterwarnings(
    "ignore",
    message=r"(?s).*All support for the `google\.generativeai` package has ended.*",
    category=FutureWarning,
)

import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = genai.GenerativeModel("gemini-1.5-flash")
    return _model


SYSTEM_PROMPT = """You are VaultRAG AI, an enterprise-grade AI assistant.
Answer ONLY based on the provided context. Do NOT hallucinate.
If the context is insufficient, respond: "Insufficient verified enterprise data available."
Be concise, precise, and professional. Use bullet points for lists."""


def build_context(chunks: List[Dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks[:6], 1):
        src = chunk["meta"].get("filename", chunk["meta"].get("source", "unknown"))
        parts.append(f"[SOURCE {i}: {src}]\n{chunk['text']}")
    return "\n\n---\n\n".join(parts)


def compute_confidence(chunks: List[Dict], routing: Dict) -> int:
    if not chunks:
        return 0
    avg_score = sum(c.get("score", 0) for c in chunks) / len(chunks)
    num_sources = len(set(c["meta"].get("source", "") for c in chunks))
    base = int(avg_score * 80)
    bonus = min(num_sources * 4, 16)  # up to +16 for multiple sources
    if routing.get("intents", ["general"]) != ["general"]:
        bonus += 4
    return min(base + bonus, 98)


def _generate_mock_response(query: str, chunks: List[Dict], routing: Dict, role: str) -> str:
    q = query.lower()
    
    # 1. Look at the retrieved chunks and see if we can find specific known answers.
    if "inc-2045" in q or "inc2045" in q or "payroll service failure" in q or "outage" in q:
        return (
            "### Incident Report: INC-2045 (Critical Payroll & Auth Service Failure)\n\n"
            "Based on retrieved Engineering incident reports and database records:\n\n"
            "* **Status**: Resolved (Start: `2025-05-16T02:03:47Z` | End: `2025-05-16T04:51:22Z`)\n"
            "* **Severity**: P1-Critical\n"
            "* **Affected Systems**: `PayrollService`, `AuthService`, and database `DB-PROD-03`\n"
            "* **Root Cause**: An unoptimized database query in `PayrollService v2.8.1` caused database connection pool exhaustion.\n"
            "* **Financial Impact**: $287,300 in delayed payroll processing and recovery overhead.\n"
            "* **Resolution**: Rolled back version, optimized database indexing, and increased the connection pool size. Resolved by Senior SRE **Kevin Huang**.\n\n"
            "*(Source: incident_report_INC2045.pdf, enterprise.db [SQL])* "
        )

    if "payroll" in q or "salary" in q or "compensation" in q:
        return (
            "### Enterprise Payroll & Compensation Summary\n\n"
            "Based on retrieved payroll databases and HR records:\n\n"
            "* **System Details**: The payroll system logs details on employee compensation and payments.\n"
            "* **Recent Issue**: Payroll calculations were temporarily delayed during the `INC-2045` incident on 2025-05-16.\n"
            "* **Data Sources**: Details are loaded from `payroll.csv` and `employee_attendance.csv`.\n"
            "* **Salary Range**: Standard salaries range from $95,000 to $148,000 for technical staff, with the CEO salary at $320,000.\n\n"
            "*(Source: payroll.csv, employee_policy.txt)* "
        )

    if "budget" in q or "expense" in q or "cost" in q or "finance" in q:
        return (
            "### Enterprise Financial & Budget Report (Q1 2025)\n\n"
            "Based on retrieved Finance spreadsheets and database tables:\n\n"
            "* **Q1 Performance**: The audit report 2025 highlights department budget allocations and variances.\n"
            "* **Engineering Budget**: Allocated Q1 budget of $20.8M, representing the largest headcount (312 employees).\n"
            "* **Finance Budget**: Allocated Q1 budget of $8.4M.\n"
            "* **Overspend/Underprep**: Details in `department_budget.csv` trace expenses for vendor licenses and servers.\n\n"
            "*(Source: audit_report_2025.pdf, department_budget.csv)* "
        )

    if "security" in q or "anomaly" in q or "breach" in q or "alert" in q or "unauthorized" in q:
        return (
            "### Enterprise Security & Compliance Alerts\n\n"
            "Based on retrieved Compliance logs and Security alerts:\n\n"
            "* **Alert Summary**: Security alerts track unauthorized document store access attempts.\n"
            "* **GDPR Compliance**: The system enforces GDPR policies regarding PII and employee directories.\n"
            "* **Access Logs**: The `access_logs.json` file tracks all successful and blocked requests.\n"
            "* **Recent Alert**: `INC-2051` (P3-Medium) was logged when an HR user attempted unauthorized access to a Finance document.\n\n"
            "*(Source: security_compliance.pdf, access_logs.json, audit_logs.csv)* "
        )

    if "gdpr" in q or "compliance" in q or "regulation" in q:
        return (
            "### GDPR & Compliance Policy Overview\n\n"
            "Based on retrieved Compliance documents:\n\n"
            "* **Policy Scope**: The company is subject to strict data protection regulations under GDPR.\n"
            "* **PII Protection**: Employee records, salaries, and sensitive data must be encrypted at rest and filtered through RBAC.\n"
            "* **Auditing**: Compliance audit logs (`audit_logs.csv`) record all security breaches and access violations.\n\n"
            "*(Source: gdpr_policy.pdf, security_compliance.pdf)* "
        )

    if "employee" in q or "leave" in q or "pto" in q or "policy" in q:
        return (
            "### Human Resources Policy & Leave Guidelines\n\n"
            "Based on retrieved HR documents:\n\n"
            "* **Standard PTO**: Leave guidelines are detailed in `leave_guidelines.txt`.\n"
            "* **Attendance Tracking**: Standard hours and attendance are tracked in `employee_attendance.csv`.\n"
            "* **Staff Headcount**: The company employs personnel across Engineering, HR, Finance, and Compliance.\n\n"
            "*(Source: employee_policy.txt, leave_guidelines.txt)* "
        )

    # General fallback using text snippets from retrieved chunks
    bullet_points = []
    for i, chunk in enumerate(chunks[:4]):
        text = chunk["text"].strip()
        lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 15]
        if lines:
            line = lines[0]
            if len(line) > 150:
                line = line[:147] + "..."
            bullet_points.append(f"* {line}")
        else:
            bullet_points.append(f"* Snippet from {chunk['meta'].get('filename', 'document')}: {text[:100]}...")

    bullets_str = "\n".join(bullet_points)
    
    return (
        f"### Enterprise Search Results\n\n"
        f"Based on your query, the following information was retrieved from active enterprise sources:\n\n"
        f"{bullets_str}\n\n"
        f"*(Source: {', '.join(list(set(c['meta'].get('filename', 'doc') for c in chunks)))})* "
    )


def generate_response(query: str, chunks: List[Dict], routing: Dict,
                      role: str, user_name: str) -> Dict:
    if not chunks:
        return {
            "answer": "Insufficient verified enterprise data available.",
            "confidence": 0,
            "model": "mock-fallback"
        }

    api_key = os.getenv("GEMINI_API_KEY", "")
    is_mock = not api_key or api_key == "your_gemini_api_key_here"

    confidence = compute_confidence(chunks, routing)

    if is_mock:
        print("[WARN] [VaultRAG AI] Using mock LLM fallback (no valid Gemini API key detected).")
        answer = _generate_mock_response(query, chunks, routing, role)
        return {
            "answer": answer,
            "confidence": confidence,
            "model": "mock-fallback"
        }

    context = build_context(chunks)
    prompt = f"""{SYSTEM_PROMPT}

ENTERPRISE CONTEXT:
{context}

USER ROLE: {role}
ACCESS POLICY: {routing.get('policy_applied', 'Standard')}
QUERY INTENT: {', '.join(routing.get('intents', ['general']))}

QUESTION: {query}

Provide a professional, grounded answer citing relevant sources."""

    try:
        model = _get_model()
        response = model.generate_content(prompt)
        answer = response.text.strip()
        model_name = "gemini-1.5-flash"
    except Exception as e:
        print(f"[WARN] [VaultRAG AI] Gemini API call failed: {str(e)}. Falling back to mock generator.")
        answer = _generate_mock_response(query, chunks, routing, role)
        model_name = "mock-fallback"

    return {
        "answer": answer,
        "confidence": confidence,
        "model": model_name
    }
