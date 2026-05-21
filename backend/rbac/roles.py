"""
RBAC Role Definitions - VaultRAG AI
Defines all enterprise roles and their data source permissions.
"""

from typing import Set, Dict

# Role Definitions

ROLES = {
    "Admin": {
        "display": "System Administrator",
        "level": 5,
        "departments": ["HR", "Finance", "Engineering", "Compliance", "Admin"],
        "allowed_sources": [
            "employee_policy", "leave_guidelines",
            "audit_report_2025", "budget_summary",
            "incident_report_INC2045", "deployment_manual",
            "gdpr_policy", "security_compliance",
            "employee_attendance", "payroll",
            "department_budget", "expenses",
            "server_metrics", "deployment_status", "audit_logs",
            "security_alerts", "server_logs", "access_logs",
            "employees", "incidents", "departments", "user_roles", "permissions"
        ],
        "badge_color": "#9333ea",
        "icon": "ADM"
    },
    "HR_Manager": {
        "display": "HR Manager",
        "level": 3,
        "departments": ["HR"],
        "allowed_sources": [
            "employee_policy", "leave_guidelines",
            "employee_attendance", "payroll",
            "employees", "departments"
        ],
        "denied_sources": [
            "audit_report_2025", "budget_summary", "expenses", "department_budget",
            "incident_report_INC2045", "deployment_manual", "server_metrics",
            "deployment_status", "gdpr_policy", "security_compliance", "audit_logs",
            "security_alerts", "server_logs", "access_logs", "incidents", "permissions"
        ],
        "badge_color": "#0ea5e9",
        "icon": "HR"
    },
    "Finance_Analyst": {
        "display": "Finance Analyst",
        "level": 3,
        "departments": ["Finance"],
        "allowed_sources": [
            "audit_report_2025", "budget_summary",
            "department_budget", "expenses",
            "employees", "departments", "incidents"
        ],
        "denied_sources": [
            "employee_policy", "leave_guidelines", "payroll", "employee_attendance",
            "incident_report_INC2045", "deployment_manual", "server_metrics",
            "deployment_status", "gdpr_policy", "security_compliance",
            "security_alerts", "server_logs", "access_logs", "permissions"
        ],
        "badge_color": "#f59e0b",
        "icon": "FIN"
    },
    "Engineer": {
        "display": "Engineer",
        "level": 3,
        "departments": ["Engineering"],
        "allowed_sources": [
            "incident_report_INC2045", "deployment_manual",
            "server_metrics", "deployment_status",
            "server_logs", "access_logs", "security_alerts",
            "employees", "departments", "incidents"
        ],
        "denied_sources": [
            "employee_policy", "leave_guidelines", "payroll", "employee_attendance",
            "audit_report_2025", "budget_summary", "department_budget", "expenses",
            "gdpr_policy", "security_compliance", "audit_logs", "permissions"
        ],
        "badge_color": "#10b981",
        "icon": "ENG"
    },
    "Compliance_Officer": {
        "display": "Compliance Officer",
        "level": 4,
        "departments": ["Compliance"],
        "allowed_sources": [
            "gdpr_policy", "security_compliance",
            "audit_logs", "security_alerts", "access_logs",
            "employees", "departments", "incidents", "permissions",
            "incident_report_INC2045"
        ],
        "denied_sources": [
            "employee_policy", "leave_guidelines", "payroll", "employee_attendance",
            "audit_report_2025", "budget_summary", "department_budget", "expenses",
            "deployment_manual", "server_metrics", "deployment_status", "server_logs"
        ],
        "badge_color": "#ef4444",
        "icon": "GRC"
    }
}

# Demo Users

DEMO_USERS = {
    "admin@vaultrag.ai": {
        "password": "admin123",
        "name": "Marcus Whitfield",
        "role": "Admin",
        "employee_id": "EMP-9999",
        "department": "Executive"
    },
    "hr@vaultrag.ai": {
        "password": "hr123",
        "name": "Sarah Mitchell",
        "role": "HR_Manager",
        "employee_id": "EMP-1002",
        "department": "HR"
    },
    "finance@vaultrag.ai": {
        "password": "fin123",
        "name": "Carol Watts",
        "role": "Finance_Analyst",
        "employee_id": "EMP-1003",
        "department": "Finance"
    },
    "engineer@vaultrag.ai": {
        "password": "eng123",
        "name": "Kevin Huang",
        "role": "Engineer",
        "employee_id": "EMP-1038",
        "department": "Engineering"
    },
    "compliance@vaultrag.ai": {
        "password": "comp123",
        "name": "David Okafor",
        "role": "Compliance_Officer",
        "employee_id": "EMP-1004",
        "department": "Compliance"
    }
}
