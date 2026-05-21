"""Data Ingestion Pipeline - VaultRAG AI"""

import os, json, csv
from retrieval.vector_store import add_documents, is_populated, get_collection

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "../../datasets")

# Source metadata map
PDF_FILES = {
    "employee_policy":        ("pdfs/employee_policy.txt",        "employee_policy.txt",   "HR"),
    "leave_guidelines":       ("pdfs/leave_guidelines.txt",       "leave_guidelines.txt",  "HR"),
    "audit_report_2025":      ("pdfs/audit_report_2025.txt",      "audit_report_2025.pdf", "Finance"),
    "budget_summary":         ("pdfs/budget_summary.txt",         "budget_summary.pdf",    "Finance"),
    "incident_report_INC2045":("pdfs/incident_report_INC2045.txt","incident_report_INC2045.pdf","Engineering"),
    "deployment_manual":      ("pdfs/deployment_manual.txt",      "deployment_manual.pdf", "Engineering"),
    "gdpr_policy":            ("pdfs/gdpr_policy.txt",            "gdpr_policy.pdf",       "Compliance"),
    "security_compliance":    ("pdfs/security_compliance.txt",    "security_compliance.pdf","Compliance"),
}

CSV_FILES = {
    "employee_attendance": ("csv/employee_attendance.csv", "employee_attendance.csv", "HR"),
    "payroll":             ("csv/payroll.csv",              "payroll.csv",             "Finance"),
    "department_budget":   ("csv/department_budget.csv",   "department_budget.csv",   "Finance"),
    "expenses":            ("csv/expenses.csv",             "expenses.csv",            "Finance"),
    "server_metrics":      ("csv/server_metrics.csv",      "server_metrics.csv",      "Engineering"),
    "deployment_status":   ("csv/deployment_status.csv",   "deployment_status.csv",   "Engineering"),
    "audit_logs":          ("csv/audit_logs.csv",          "audit_logs.csv",          "Compliance"),
}

JSON_FILES = {
    "security_alerts": ("json/security_alerts.json", "security_alerts.json", "Compliance"),
    "server_logs":     ("json/server_logs.json",     "server_logs.json",     "Engineering"),
    "access_logs":     ("json/access_logs.json",     "access_logs.json",     "Compliance"),
}


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def ingest_all(force: bool = False):
    if is_populated() and not force:
        print("[OK] Vector store already populated. Skipping ingestion.")
        return

    if force:
        try:
            from retrieval.vector_store import delete_collection
            delete_collection()
        except Exception:
            pass

    docs, metas, ids = [], [], []
    idx = 0

    # Ingest text files (PDFs)
    for source_key, (rel_path, filename, dept) in PDF_FILES.items():
        full_path = os.path.join(DATASETS_DIR, rel_path)
        if not os.path.exists(full_path):
            print(f"[WARN] Missing: {full_path}")
            continue
        with open(full_path, encoding="utf-8") as f:
            text = f.read()
        for chunk in chunk_text(text):
            docs.append(chunk)
            metas.append({"source": source_key, "filename": filename,
                          "department": dept, "type": "pdf"})
            ids.append(f"doc_{source_key}_{idx}")
            idx += 1
        print(f"  [PDF] {filename}")

    # Ingest CSV files (as text rows)
    for source_key, (rel_path, filename, dept) in CSV_FILES.items():
        full_path = os.path.join(DATASETS_DIR, rel_path)
        if not os.path.exists(full_path):
            continue
        with open(full_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # Convert to text chunks
        text = f"FILE: {filename}\n"
        text += ", ".join(rows[0].keys()) + "\n" if rows else ""
        for row in rows:
            text += " | ".join(f"{k}: {v}" for k, v in row.items()) + "\n"
        for chunk in chunk_text(text, chunk_size=800):
            docs.append(chunk)
            metas.append({"source": source_key, "filename": filename,
                          "department": dept, "type": "csv"})
            ids.append(f"doc_{source_key}_{idx}")
            idx += 1
        print(f"  [CSV] {filename}")

    # Ingest JSON files
    for source_key, (rel_path, filename, dept) in JSON_FILES.items():
        full_path = os.path.join(DATASETS_DIR, rel_path)
        if not os.path.exists(full_path):
            continue
        with open(full_path, encoding="utf-8") as f:
            data = json.load(f)
        text = f"FILE: {filename}\n"
        for entry in data:
            text += json.dumps(entry) + "\n"
        for chunk in chunk_text(text, chunk_size=800):
            docs.append(chunk)
            metas.append({"source": source_key, "filename": filename,
                          "department": dept, "type": "json"})
            ids.append(f"doc_{source_key}_{idx}")
            idx += 1
        print(f"  [JSON] {filename}")

    if docs:
        add_documents(docs, metas, ids)
        print(f"[OK] Ingested {len(docs)} chunks into ChromaDB.")
    else:
        print("[ERROR] No documents found to ingest.")
