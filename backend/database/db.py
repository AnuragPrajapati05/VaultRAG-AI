"""SQLite Database Setup & Queries - VaultRAG AI"""

import sqlite3
import os

DB_PATH = os.getenv(
    "DATABASE_URL",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../datasets/sql/enterprise.db"))
)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed data."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY, code TEXT UNIQUE, name TEXT, head TEXT, budget REAL, headcount INTEGER
    );
    CREATE TABLE IF NOT EXISTS employees (
        id TEXT PRIMARY KEY, name TEXT, email TEXT, department TEXT, role TEXT,
        title TEXT, salary REAL, hire_date TEXT, status TEXT
    );
    CREATE TABLE IF NOT EXISTS incidents (
        id TEXT PRIMARY KEY, title TEXT, severity TEXT, status TEXT,
        start_time TEXT, end_time TEXT, affected_systems TEXT,
        root_cause TEXT, financial_impact REAL, reporter TEXT, department TEXT
    );
    CREATE TABLE IF NOT EXISTS user_roles (
        email TEXT PRIMARY KEY, role TEXT, department TEXT, access_level INTEGER
    );
    CREATE TABLE IF NOT EXISTS permissions (
        role TEXT, resource TEXT, action TEXT, granted INTEGER
    );

    INSERT OR IGNORE INTO departments VALUES
      (1,'ENG','Engineering','Priya Nair',20800000,312),
      (2,'HR','Human Resources','Sarah Mitchell',7200000,48),
      (3,'FIN','Finance','Diana Forsythe',8400000,67),
      (4,'COMP','Compliance','Alexandra Reeves',3800000,29);

    INSERT OR IGNORE INTO employees VALUES
      ('EMP-1001','Alice Chen','a.chen@vaultcorp.ai','Engineering','Engineer','Senior Software Engineer',145000,'2021-03-15','Active'),
      ('EMP-1002','Bob Singh','b.singh@vaultcorp.ai','HR','HR_Manager','HR Business Partner',95000,'2019-07-01','Active'),
      ('EMP-1003','Carol Watts','c.watts@vaultcorp.ai','Finance','Finance_Analyst','Senior Financial Analyst',118000,'2020-01-10','Active'),
      ('EMP-1004','David Okafor','d.okafor@vaultcorp.ai','Compliance','Compliance_Officer','Compliance Analyst',102000,'2022-05-01','Active'),
      ('EMP-1005','Emma Liu','e.liu@vaultcorp.ai','Engineering','Engineer','DevOps Engineer',138000,'2021-09-20','Active'),
      ('EMP-1038','Kevin Huang','k.huang@vaultcorp.ai','Engineering','Engineer','Senior SRE',148000,'2020-11-01','Active'),
      ('EMP-9999','Marcus Whitfield','admin@vaultcorp.ai','Executive','Admin','CEO',320000,'2015-01-01','Active');

    INSERT OR IGNORE INTO incidents VALUES
      ('INC-2045','Critical Payroll & Auth Service Failure','P1-Critical','Resolved',
       '2025-05-16T02:03:47Z','2025-05-16T04:51:22Z',
       'PayrollService,AuthService,DB-PROD-03',
       'Unoptimized query in PayrollService v2.8.1 caused DB connection pool exhaustion',
       287300,'Kevin Huang','Engineering'),
      ('INC-2040','API Gateway Latency Spike','P2-High','Resolved',
       '2025-05-10T14:22:00Z','2025-05-10T15:45:00Z',
       'APIGateway','Rate limiter misconfiguration',5000,'Emma Liu','Engineering'),
      ('INC-2051','Unauthorized Finance Doc Access Attempt','P3-Medium','Resolved',
       '2025-05-19T14:22:00Z','2025-05-19T14:23:00Z',
       'DocumentStore','RBAC policy violation attempt by HR user',0,'David Okafor','Compliance');

    INSERT OR IGNORE INTO user_roles VALUES
      ('admin@vaultrag.ai','Admin','Executive',5),
      ('hr@vaultrag.ai','HR_Manager','HR',3),
      ('finance@vaultrag.ai','Finance_Analyst','Finance',3),
      ('engineer@vaultrag.ai','Engineer','Engineering',3),
      ('compliance@vaultrag.ai','Compliance_Officer','Compliance',4);

    INSERT OR IGNORE INTO permissions VALUES
      ('Admin','*','*',1),
      ('HR_Manager','employee_policy','read',1),('HR_Manager','payroll','read',1),
      ('HR_Manager','audit_report_2025','read',0),('HR_Manager','server_logs','read',0),
      ('Finance_Analyst','audit_report_2025','read',1),('Finance_Analyst','budget_summary','read',1),
      ('Finance_Analyst','payroll','read',0),('Finance_Analyst','server_logs','read',0),
      ('Engineer','incident_report_INC2045','read',1),('Engineer','server_logs','read',1),
      ('Engineer','payroll','read',0),('Engineer','audit_report_2025','read',0),
      ('Compliance_Officer','gdpr_policy','read',1),('Compliance_Officer','audit_logs','read',1),
      ('Compliance_Officer','payroll','read',0),('Compliance_Officer','department_budget','read',0);
    """)

    conn.commit()
    conn.close()
    print("[OK] Database initialized.")


def query_incidents(incident_id: str = None) -> list:
    conn = get_connection()
    cur = conn.cursor()
    if incident_id:
        cur.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
    else:
        cur.execute("SELECT * FROM incidents ORDER BY start_time DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def query_employees(department: str = None) -> list:
    conn = get_connection()
    cur = conn.cursor()
    if department:
        cur.execute("SELECT * FROM employees WHERE department = ?", (department,))
    else:
        cur.execute("SELECT * FROM employees")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_db_context(query: str, role: str) -> str:
    """Build SQL context string to inject into LLM prompt."""
    from rbac.enforcer import get_allowed_sources
    allowed = get_allowed_sources(role)
    context_parts = []

    if "incidents" in allowed or role == "Admin":
        rows = query_incidents()
        if rows:
            context_parts.append("=== INCIDENTS DATABASE ===")
            for r in rows:
                context_parts.append(
                    f"[{r['id']}] {r['title']} | Severity: {r['severity']} | "
                    f"Status: {r['status']} | Root Cause: {r['root_cause']} | "
                    f"Impact: ${r['financial_impact']:,.0f}"
                )

    if "employees" in allowed or role == "Admin":
        rows = query_employees()
        if rows:
            context_parts.append("=== EMPLOYEES DATABASE ===")
            for r in rows:
                context_parts.append(
                    f"[{r['id']}] {r['name']} | {r['title']} | {r['department']} | Status: {r['status']}"
                )

    return "\n".join(context_parts)
