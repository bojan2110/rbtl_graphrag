# Deployment & Environments

Use this guide when promoting GraphRAG beyond local development.

## Environment Matrix

| Target | Backend | Frontend | Neo4j | MongoDB | Langfuse |
|--------|---------|----------|-------|---------|----------|
| Local  | Uvicorn + reload | Next.js dev server | Aura/self-hosted | Atlas/local | docker-compose |
| Staging | Containerized FastAPI | Static export or Next.js server | Managed Aura | Managed Atlas | Self-hosted or Cloud |
| Prod   | Container/orchestrated | Static assets behind CDN | Aura Enterprise | Atlas/DocumentDB | Langfuse Cloud |

## Backend Container Stub

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend backend
COPY ai ai
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Pair with environment variables injected by your orchestration platform (Kubernetes, ECS, etc.).

## Frontend Build

```bash
cd frontend
npm ci
npm run build
npm run export  # optional static export
```

Serve the `.next/standalone` or `out/` directory via your platform of choice (CloudFront, Vercel, etc.). Set `NEXT_PUBLIC_*` env vars for backend URLs and analytics keys.

## Secrets & Config

- Store `.env` values in a secret manager (AWS Secrets Manager, Doppler, 1Password).
- Rotate OpenAI/Langfuse keys regularly; the backend reads them on startup.
- When running analytics agent, ensure both the backend and the MCP server agree on Neo4j credentials.

## Observability & Health Checks

- `GET /health` for FastAPI readiness.
- Langfuse dashboards for LLM traces; configure alerting on latency, failure rate.
- Add metrics/structured logs (planned).

## GitHub Pages + MkDocs

- `mkdocs build` produces static docs for GitHub Pages.
- `mkdocs gh-deploy --force` publishes to `gh-pages`.
- Recommended GitHub Action (to be added) runs on pushes to `main` and pull requests for validation.

