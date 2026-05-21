"""Query Router - VaultRAG AI"""

from typing import Dict, List, Tuple

INTENT_PATTERNS = {
    "payroll": {
        "keywords": ["payroll", "salary", "payment", "pay", "compensation", "wage"],
        "sources": ["payroll", "server_logs", "incident_report_INC2045", "expenses", "employees"],
        "department": "Finance/HR",
    },
    "incident": {
        "keywords": ["incident", "inc-2045", "inc2045", "outage", "failure", "down", "timeout", "crash"],
        "sources": ["incident_report_INC2045", "server_logs", "server_metrics", "deployment_status", "security_alerts"],
        "department": "Engineering",
    },
    "security": {
        "keywords": ["security", "anomaly", "anomalies", "breach", "attack", "unauthorized",
                     "suspicious", "alert", "threat", "vulnerability", "brute force", "failed login"],
        "sources": ["security_alerts", "access_logs", "server_logs", "security_compliance", "audit_logs"],
        "department": "Compliance/Engineering",
    },
    "compliance": {
        "keywords": ["gdpr", "compliance", "regulation", "policy", "audit", "data protection",
                     "privacy", "retention", "iso 27001", "soc2", "pci"],
        "sources": ["gdpr_policy", "security_compliance", "audit_logs", "security_alerts"],
        "department": "Compliance",
    },
    "hr": {
        "keywords": ["employee", "attendance", "leave", "pto", "vacation", "sick",
                     "staff", "workforce", "hr", "human resources", "recruitment", "benefits"],
        "sources": ["employee_policy", "leave_guidelines", "employee_attendance", "employees"],
        "department": "HR",
    },
    "finance": {
        "keywords": ["budget", "expense", "cost", "financial", "revenue", "ebitda",
                     "overspend", "variance", "vendor", "invoice", "audit report"],
        "sources": ["audit_report_2025", "budget_summary", "department_budget", "expenses"],
        "department": "Finance",
    },
    "deployment": {
        "keywords": ["deploy", "deployment", "release", "rollback", "version", "pipeline", "v2.8"],
        "sources": ["deployment_manual", "deployment_status", "server_logs", "incident_report_INC2045"],
        "department": "Engineering",
    },
}


def detect_intent(query: str) -> Tuple[List[str], str, List[str]]:
    query_lower = query.lower()
    matched_intents, all_sources = [], []

    for intent_name, config in INTENT_PATTERNS.items():
        if any(kw in query_lower for kw in config["keywords"]):
            matched_intents.append(intent_name)
            for src in config["sources"]:
                if src not in all_sources:
                    all_sources.append(src)

    if not matched_intents:
        matched_intents = ["general"]
        all_sources = ["employee_policy", "audit_report_2025", "incident_report_INC2045",
                       "gdpr_policy", "security_compliance", "deployment_manual"]

    dept_votes = {}
    for intent in matched_intents:
        if intent in INTENT_PATTERNS:
            dept = INTENT_PATTERNS[intent]["department"]
            dept_votes[dept] = dept_votes.get(dept, 0) + 1
    primary_dept = max(dept_votes, key=dept_votes.get) if dept_votes else "General"

    return matched_intents, primary_dept, all_sources


def route_query(query: str, role: str, allowed_sources: List[str]) -> Dict:
    from rbac.enforcer import enforce_rbac
    intents, department, suggested_sources = detect_intent(query)
    rbac_result = enforce_rbac(role, suggested_sources)
    final_sources = rbac_result["approved_sources"]

    if not final_sources:
        return {
            "intents": intents, "department": department,
            "routed_sources": [], "denied_sources": suggested_sources,
            "access_granted": False,
            "routing_decision": f"ALL_DENIED: {role} has no access to required sources",
            "policy_applied": rbac_result["policy_applied"]
        }

    return {
        "intents": intents, "department": department,
        "routed_sources": final_sources, "denied_sources": rbac_result["denied_sources"],
        "access_granted": True,
        "routing_decision": f"ROUTED to {len(final_sources)} source(s) via {department}",
        "policy_applied": rbac_result["policy_applied"]
    }
