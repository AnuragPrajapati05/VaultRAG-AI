import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))

from database.db import init_db, query_incidents
from ingestion.ingest import ingest_all
from retrieval.vector_store import get_collection
from routing.query_router import route_query
from llm.generator import generate_response
from retrieval.retriever import retrieve

print("1. Initializing SQLite Database...")
init_db()
print("2. Ingesting documents into ChromaDB...")
ingest_all(force=True)

print("3. Checking ChromaDB count...")
col = get_collection()
print(f"Collection count: {col.count()}")

print("4. Testing query: INC-2045 outage root cause for Engineer role")
query = "What caused the INC-2045 outage and what was the root cause?"
role = "Engineer"
allowed_sources = ["incident_report_INC2045", "server_logs", "server_metrics", "deployment_status", "security_alerts", "employees", "departments", "incidents"]

routing = route_query(query, role, allowed_sources)
print(f"Routing result: {routing}")

retrieved = retrieve(query, role, routing["routed_sources"])
print(f"Retrieved {len(retrieved['chunks'])} chunks.")

response = generate_response(query, retrieved["chunks"], routing, role, "Test User")
print("Response:")
print(response["answer"])
print(f"Confidence: {response['confidence']}%")
print(f"Model: {response['model']}")
