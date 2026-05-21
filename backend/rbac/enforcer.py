"""
RBAC Enforcer - VaultRAG AI
Handles authentication and access control enforcement.
"""

from typing import Optional, Dict, Any
from rbac.roles import DEMO_USERS, ROLES


class AccessDeniedError(Exception):
    """Raised when RBAC check fails."""
    pass


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user by email and password."""
    user = DEMO_USERS.get(email)
    if not user:
        return None
    if user["password"] != password:
        return None
    return {
        "email": email,
        "name": user["name"],
        "role": user["role"],
        "employee_id": user["employee_id"],
        "department": user["department"],
        **ROLES[user["role"]]
    }


def get_allowed_sources(role: str) -> list:
    """Return the list of allowed data sources for a role."""
    role_def = ROLES.get(role)
    if not role_def:
        return []
    return role_def.get("allowed_sources", [])


def check_access(role: str, source_name: str) -> bool:
    """Check if a role can access a specific data source."""
    allowed = get_allowed_sources(role)
    return source_name in allowed


def enforce_rbac(role: str, requested_sources: list) -> Dict[str, Any]:
    """
    Filter requested sources through RBAC.
    Returns allowed sources and denied sources.
    """
    allowed = get_allowed_sources(role)
    approved = [s for s in requested_sources if s in allowed]
    denied = [s for s in requested_sources if s not in allowed]
    return {
        "approved_sources": approved,
        "denied_sources": denied,
        "access_granted": len(approved) > 0,
        "policy_applied": f"{role} Access Policy"
    }


def get_metadata_filter(role: str) -> Dict[str, Any]:
    """
    Build ChromaDB-compatible metadata filter for a role.
    Used to restrict vector search results.
    """
    allowed_sources = get_allowed_sources(role)
    return {"source": {"$in": allowed_sources}}
