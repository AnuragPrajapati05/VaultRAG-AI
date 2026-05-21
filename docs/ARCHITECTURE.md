# VaultRAG AI Architecture

## System Architecture

```mermaid
flowchart TD
    U[User Browser] --> FE[React + Tailwind Frontend]
    FE -->|HTTPS JSON API| API[FastAPI Backend]
    API --> AUTH[Authentication + Demo User Resolver]
    API --> RBAC[RBAC Enforcer]
    RBAC --> ROUTER[Query Router]
    ROUTER --> RET[Multi-Source Retriever]
    RET --> VDB[ChromaDB Vector Store]
    RET --> SQL[SQLite Enterprise DB]
    RET --> FILES[CSV / JSON / Policy Text]
    VDB --> GEN[LLM Generator]
    SQL --> GEN
    FILES --> GEN
    GEN --> FE
```

## Backend Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as FastAPI
    participant RBAC
    participant Router
    participant Retriever
    participant LLM

    User->>Frontend: Submit enterprise query
    Frontend->>API: POST /query
    API->>RBAC: Resolve allowed sources
    API->>Router: Detect intent and candidate sources
    Router->>RBAC: Filter candidate sources
    API->>Retriever: Retrieve approved context
    Retriever->>Retriever: Vector + structured + SQL context
    API->>LLM: Generate grounded answer
    LLM->>API: Answer + confidence
    API->>Frontend: Citations + trace + policy result
```

## Deployment Architecture

```mermaid
flowchart LR
    GH[GitHub Repository] --> V[Vercel Frontend]
    GH --> R[Render Backend]
    V -->|VITE_API_URL| R
    R --> C[(Runtime ChromaDB)]
    R --> D[(Bundled SQLite Dataset)]
    R --> G[Gemini API]
```

## Data Boundaries

- The frontend never receives API keys.
- Render stores backend secrets as environment variables.
- Vercel stores only the public backend URL.
- RBAC filtering is applied before retrieval.
- ChromaDB is regenerated from bundled demo datasets at startup when needed.
