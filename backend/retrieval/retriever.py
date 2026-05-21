"""Multi-source Retriever - VaultRAG AI"""

import os, json, csv
from typing import List, Dict
from retrieval.vector_store import search


DATASETS_DIR = os.path.join(os.path.dirname(__file__), "../../datasets")


def retrieve(query: str, role: str, routed_sources: List[str], n_results: int = 5) -> Dict:
    """
    Retrieve from vector store (RBAC-filtered) + structured data.
    Returns chunks, citations, and trace info.
    """
    # 1. Vector search
    vec_results = search(query, role, n_results, sources=routed_sources)
    docs = vec_results.get("documents", [[]])[0]
    metas = vec_results.get("metadatas", [[]])[0]
    dists = vec_results.get("distances", [[]])[0]

    chunks = []
    citations = []

    for doc, meta, dist in zip(docs, metas, dists):
        score = round(1.0 - dist, 3)
        chunks.append({"text": doc, "score": score, "meta": meta})
        source_name = meta.get("source", "unknown")
        file_name = meta.get("filename", source_name)
        if file_name not in citations:
            citations.append(file_name)

    # 2. Structured data injection (CSV/JSON summaries)
    structured_context = _get_structured_context(query, routed_sources)
    if structured_context:
        chunks.append({
            "text": structured_context,
            "score": 0.85,
            "meta": {"source": "structured_data", "filename": "enterprise_database"}
        })
        citations.append("enterprise_database [CSV/JSON]")

    return {
        "chunks": chunks,
        "citations": list(dict.fromkeys(citations)),  # preserve order, dedupe
        "num_chunks": len(chunks)
    }


def _get_structured_context(query: str, sources: List[str]) -> str:
    q = query.lower()
    parts = []

    # Payroll CSV
    if any(s in sources for s in ["payroll"]):
        rows = _read_csv("csv/payroll.csv")
        delayed = [r for r in rows if r.get("payment_status") == "DELAYED"]
        if delayed:
            parts.append(f"PAYROLL DATA: {len(delayed)} employees had DELAYED payments on 2025-05-16 due to INC-2045.")
            for r in delayed[:3]:
                parts.append(f"  - {r['name']} ({r['employee_id']}): ${r['total_compensation']} - {r['notes']}")

    # Server metrics CSV
    if any(s in sources for s in ["server_metrics"]):
        rows = _read_csv("csv/server_metrics.csv")
        critical = [r for r in rows if r.get("incident_ref") == "INC-2045" and r.get("alert_triggered") == "true"]
        if critical:
            parts.append(f"SERVER METRICS: {len(critical)} critical metric alerts triggered during INC-2045.")
            for r in critical[:3]:
                parts.append(f"  - {r['timestamp']} | {r['server_id']} | {r['metric']}: {r['value']}{r['unit']}")

    # Security alerts JSON
    if any(s in sources for s in ["security_alerts"]):
        alerts = _read_json("json/security_alerts.json")
        crit = [a for a in alerts if a.get("severity") in ["CRITICAL", "HIGH"]]
        if crit:
            parts.append(f"SECURITY ALERTS: {len(crit)} HIGH/CRITICAL alerts found.")
            for a in crit[:3]:
                parts.append(f"  - [{a['alert_id']}] {a['type']} | {a['severity']} | {a['description'][:120]}...")

    # Deployment status CSV
    if any(s in sources for s in ["deployment_status"]):
        rows = _read_csv("csv/deployment_status.csv")
        failed = [r for r in rows if r.get("rollback_triggered") == "true"]
        if failed:
            parts.append(f"DEPLOYMENT STATUS: {len(failed)} deployments required rollback.")
            for r in failed:
                parts.append(f"  - {r['deployment_id']} | {r['service']} v{r['version']} | {r['notes'][:100]}")

    # Budget CSV
    if any(s in sources for s in ["department_budget"]):
        rows = _read_csv("csv/department_budget.csv")
        over = [r for r in rows if r.get("budget_status", "").startswith("OVER")]
        if over:
            parts.append(f"BUDGET DATA: {len(over)} departments over budget in Q1 2025.")
            for r in over:
                parts.append(f"  - {r['department']}: allocated ${r['allocated_q1']}, spent ${r['spent_q1']} ({r['notes']})")

    return "\n".join(parts) if parts else ""


def _read_csv(relative_path: str) -> List[Dict]:
    path = os.path.join(DATASETS_DIR, relative_path)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _read_json(relative_path: str) -> list:
    path = os.path.join(DATASETS_DIR, relative_path)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)
