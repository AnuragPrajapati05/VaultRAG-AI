"""
VaultRAG AI - FastAPI Backend
Enterprise Secure RAG Intelligence Platform
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import time

load_dotenv()

from rbac.roles import DEMO_USERS, ROLES
from rbac.enforcer import authenticate_user, get_allowed_sources
from routing.query_router import route_query
from retrieval.retriever import retrieve
from llm.generator import generate_response
from database.db import init_db, query_incidents, query_employees, get_db_context
from ingestion.ingest import ingest_all

# App Setup

app = FastAPI(
    title="VaultRAG AI",
    description="Enterprise Secure RAG Intelligence Platform",
    version="1.0.0"
)

def _get_cors_origins() -> list[str]:
    origins = os.getenv("CORS_ORIGINS") or os.getenv("FRONTEND_URL") or "http://localhost:5173"
    return [origin.strip().rstrip("/") for origin in origins.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup

@app.on_event("startup")
async def startup():
    print("[START] VaultRAG AI starting up...")
    init_db()
    print("[INFO] Ingesting enterprise documents...")
    ingest_all()
    print("[OK] VaultRAG AI ready.")

# Request Models

class LoginRequest(BaseModel):
    email: str
    password: str

class QueryRequest(BaseModel):
    query: str
    email: str
    role: str

# In-memory access log

_access_log = []

def log_access(email: str, role: str, query: str, result: str, sources: list):
    _access_log.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "email": email,
        "role": role,
        "query": query[:80],
        "result": result,
        "sources_accessed": sources
    })
    if len(_access_log) > 100:
        _access_log.pop(0)

# Endpoints

@app.get("/")
def root():
    return {"status": "online", "system": "VaultRAG AI", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


@app.post("/login")
def login(req: LoginRequest):
    user = authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    role_info = ROLES.get(user["role"], {})
    return {
        "success": True,
        "user": {
            "email": req.email,
            "name": user["name"],
            "role": user["role"],
            "display_role": role_info.get("display", user["role"]),
            "employee_id": user["employee_id"],
            "department": user["department"],
            "badge_color": role_info.get("badge_color", "#6366f1"),
            "icon": role_info.get("icon", "USR"),
            "allowed_sources": get_allowed_sources(user["role"])
        }
    }


@app.post("/query")
def query_endpoint(req: QueryRequest):
    t_start = time.time()

    # Validate user exists
    if req.email not in DEMO_USERS:
        raise HTTPException(status_code=401, detail="Unauthorized")

    role = req.role
    allowed_sources = get_allowed_sources(role)

    # Route query
    routing = route_query(req.query, role, allowed_sources)

    # Access denied: no approved sources
    if not routing["access_granted"]:
        log_access(req.email, role, req.query, "ACCESS_DENIED", [])
        return {
            "access_denied": True,
            "answer": "ACCESS DENIED: Insufficient privileges under enterprise RBAC policy.",
            "policy_applied": routing["policy_applied"],
            "denied_sources": routing["denied_sources"],
            "routing": routing,
            "confidence": 0,
            "citations": [],
            "retrieval_trace": [],
            "elapsed_ms": int((time.time() - t_start) * 1000)
        }

    # Retrieve
    retrieved = retrieve(req.query, role, routing["routed_sources"])

    # SQL context
    db_context = get_db_context(req.query, role)
    if db_context:
        retrieved["chunks"].append({
            "text": db_context,
            "score": 0.88,
            "meta": {"source": "sql_database", "filename": "enterprise.db", "type": "sql"}
        })
        retrieved["citations"].append("enterprise.db [SQL]")

    # Generate
    user_info = DEMO_USERS.get(req.email, {})
    llm_result = generate_response(req.query, retrieved["chunks"], routing,
                                   role, user_info.get("name", "User"))

    # Retrieval trace for UI
    trace = []
    for chunk in retrieved["chunks"]:
        trace.append({
            "source": chunk["meta"].get("filename", chunk["meta"].get("source", "?")),
            "type": chunk["meta"].get("type", "document"),
            "score": chunk.get("score", 0),
            "department": chunk["meta"].get("department", "System"),
            "snippet": chunk["text"][:150] + "..."
        })

    log_access(req.email, role, req.query, "SUCCESS", retrieved["citations"])

    return {
        "access_denied": False,
        "answer": llm_result["answer"],
        "confidence": llm_result["confidence"],
        "citations": retrieved["citations"],
        "policy_applied": routing["policy_applied"],
        "routing": routing,
        "retrieval_trace": trace,
        "sources_queried": routing["routed_sources"],
        "sources_denied": routing["denied_sources"],
        "model": llm_result["model"],
        "elapsed_ms": int((time.time() - t_start) * 1000)
    }


@app.get("/documents")
def list_documents(role: str = "Admin"):
    from ingestion.ingest import PDF_FILES, CSV_FILES, JSON_FILES
    allowed = get_allowed_sources(role)
    docs = []
    for key, (path, fname, dept) in {**PDF_FILES, **CSV_FILES, **JSON_FILES}.items():
        docs.append({
            "source": key,
            "filename": fname,
            "department": dept,
            "type": "pdf" if "pdf" in path else ("csv" if "csv" in path else "json"),
            "accessible": key in allowed
        })
    return {"documents": docs, "total": len(docs)}


@app.get("/logs")
def get_logs(role: str = "Admin"):
    allowed = get_allowed_sources(role)
    if "audit_logs" not in allowed and role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied to audit logs")
    return {"logs": list(reversed(_access_log))}


@app.get("/incidents")
def get_incidents(role: str = "Admin"):
    allowed = get_allowed_sources(role)
    if "incidents" not in allowed and role != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return {"incidents": query_incidents()}


@app.get("/permissions")
def get_permissions(role: str = "Admin"):
    if role != "Admin":
        raise HTTPException(status_code=403, detail="Only Admin can view all permissions")
    return {"roles": ROLES}


@app.post("/reingest")
def reingest():
    ingest_all(force=True)
    return {"status": "Reingestion complete"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "false").lower() == "true",
    )
