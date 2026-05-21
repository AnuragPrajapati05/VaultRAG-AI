"""Vector Store - VaultRAG AI (ChromaDB + sentence-transformers)"""

import os
import hashlib
import math
import re
import chromadb
from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions

PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../chroma_db"))
)
EMBEDDING_DIM = 384

_client = None
_collection = None
_ef = None


class LocalHashEmbeddingFunction(EmbeddingFunction):
    """Offline embedding fallback for deterministic local demo search."""

    def __init__(self, dimensions: int = EMBEDDING_DIM):
        self.dimensions = dimensions

    def __call__(self, input):
        return [self._embed(text) for text in input]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    @staticmethod
    def name() -> str:
        return "local_hash"

    def default_space(self) -> str:
        return "cosine"

    def supported_spaces(self) -> list[str]:
        return ["cosine", "l2", "ip"]

    @staticmethod
    def build_from_config(config: dict):
        return LocalHashEmbeddingFunction(config.get("dimensions", EMBEDDING_DIM))

    def get_config(self) -> dict:
        return {"dimensions": self.dimensions}


def _get_ef():
    global _ef
    if _ef is None:
        try:
            _ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2",
                local_files_only=True,
            )
            print("[OK] Using cached sentence-transformer embeddings.")
        except Exception as exc:
            print(f"[WARN] Sentence-transformer model unavailable locally: {exc}")
            print("[WARN] Using offline local hash embeddings.")
            _ef = LocalHashEmbeddingFunction()
    return _ef


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=PERSIST_DIR)
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name="vaultrag_enterprise",
            embedding_function=_get_ef(),
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def delete_collection():
    global _collection
    try:
        get_client().delete_collection("vaultrag_enterprise")
    except Exception:
        pass
    _collection = None


def add_documents(docs: list, metadatas: list, ids: list):
    col = get_collection()
    col.add(documents=docs, metadatas=metadatas, ids=ids)


def search(query: str, role: str, n_results: int = 6, sources: list | None = None) -> dict:
    """Semantic search with RBAC metadata filtering."""
    from rbac.enforcer import get_allowed_sources
    allowed = get_allowed_sources(role)
    if sources is not None:
        allowed = [source for source in sources if source in allowed]

    col = get_collection()
    total = col.count()
    if total == 0:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    # Build where filter for allowed sources
    if len(allowed) == 1:
        where = {"source": allowed[0]}
    elif len(allowed) > 1:
        where = {"source": {"$in": allowed}}
    else:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    results = col.query(
        query_texts=[query],
        n_results=min(n_results, total),
        where=where,
        include=["documents", "metadatas", "distances"]
    )
    return results


def is_populated() -> bool:
    try:
        col = get_collection()
        return col.count() > 0
    except Exception:
        return False
