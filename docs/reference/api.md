# API Surface (Placeholder)

The backend exposes FastAPI routes grouped under `/api`. This page will eventually be generated with `mkdocstrings` once the dependency is added.

## Current Endpoints

- `GET /health` – readiness probe.
- `POST /api/chat` – main chat interface; accepts user message + session metadata, returns streamed or batched responses.
- `GET /api/graph-info` – Graph schema and capabilities.
- `GET /api/knowledge-base` – Paginated knowledge base entries.
- `POST /api/knowledge-base` – Create/update entries (admin-only).

## Planned Automation

- Auto-generate schema tables for request/response models from Pydantic definitions in `backend/app/models/`.
- Include curl examples and authentication notes if/when auth is added.

