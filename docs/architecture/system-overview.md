# System Overview

GraphRAG spans four major subsystems:

1. **User Experience** – Next.js app (see `frontend/`) that manages chat flows, query results, and knowledge base navigation.
2. **Application Layer** – FastAPI backend (`backend/app`) that orchestrates conversations, routes graph operations, and exposes REST APIs.
3. **Graph & Knowledge Stores** – Neo4j for graph data, MongoDB for knowledge base content, plus optional Langfuse PostgreSQL/ClickHouse stack for observability.
4. **AI & Automation** – Prompt pipelines, MCP integrations, and graph analytics agents housed under `ai/`.

```mermaid
flowchart LR
    User(UI) -->|HTTPS| Frontend
    Frontend -->|REST/WebSocket| Backend
    Backend -->|Cypher| Neo4j[(Neo4j)]
    Backend -->|Mongo driver| Mongo[(MongoDB)]
    Backend -->|Langfuse SDK| Langfuse[(Langfuse)]
    Backend -->|MCP| GDS[(Neo4j GDS Agent)]
    Backend -->|LLM APIs| OpenAI[(OpenAI)]
```

## Key Responsibilities

- **Frontend**: Collects user input, streams backend responses, visualizes Cypher results, and surfaces progress/status cards for analytics routing.
- **Backend**: Hosts chat endpoints (`backend/app/api/chat.py`), exposes graph metadata (`graph_info.py`), and coordinates agent routing via `backend/app/services/graphrag.py`.
- **AI Layer**: Generates prompts (YAML files in `ai/prompts/`), manages few-shot examples (`ai/fewshots/`), and facilitates MCP sessions (`ai/mcp_client.py`).
- **Observability**: Langfuse traces capture LLM calls, prompt versions, and tool invocations; logs integrate with whichever platform you deploy.

## Deployment Targets

- **Local Dev**: Docker + Uvicorn + Next.js dev server; Langfuse runs via `docker-compose.langfuse.yml`.
- **Staging/Prod**: Recommended approach is containerize backend/frontend separately, deploy Neo4j (Aura or self-hosted) plus MongoDB (Atlas). GitHub Actions will build docs and site assets.

See the dedicated pages for deep dives into each subsystem.

