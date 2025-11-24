# Frontend / UI

The chat experience lives in the `frontend/` Next.js app. This page carries over the details from `FRONTEND_ARCHITECTURE.md`, focusing on structure, Azure-ready deployment, and integration patterns.

## High-Level Architecture

```text
User ↔ Next.js (Azure Static Web Apps / Vercel)
            ↕ REST + WebSockets/SSE
         FastAPI backend (Azure Container Apps)
            ↕
      Neo4j Aura · Langfuse · MongoDB
```

The frontend fetches REST APIs and (optionally) streams updates over WebSockets/SSE. Hosting options include Azure Static Web Apps or any static host/CDN.

## Project Layout

- `app/layout.tsx`, `app/page.tsx` – App Router entry points with chat shell.
- `components/`
  - Conversation: `ChatInterface`, `MessageList`, `MessageInput`.
  - Insights: `GraphInfo`, `CypherViewer`, `ResultsTable`.
  - Knowledge base: `CategoryForm`, `CategoryDetail`, `FavoritesView`, `Sidebar`.
- `lib/api.ts`, `lib/knowledgeBaseApi.ts` – typed fetch helpers.
- `globals.css`, `tailwind.config.js` – design system built on Tailwind CSS; shadcn/ui or similar component primitives can be layered on.
- `public/` – static assets, icons, diagram exports.

State management uses React context with optional libraries like Zustand for chat history persistence. Real-time behavior can leverage browser Fetch streaming, Server-Sent Events, or WebSockets exposed by the backend.

## Developer Workflow

```bash
cd frontend
npm install
npm run dev
```

Add `frontend/.env.local` containing `NEXT_PUBLIC_API_URL=http://localhost:8000`. When deploying, swap in the production FastAPI URL and any telemetry keys.

## Azure Deployment Notes

- **Hosting**: Azure Static Web Apps fronts the compiled Next.js site; alternatively host on Azure App Service, Vercel, or Netlify.
- **Backend connectivity**: Use Azure Container Apps or App Service for FastAPI. Configure CORS to allow the frontend origin.
- **Secrets**: Keep API URLs, Langfuse keys, and feature flags in Azure Key Vault, surfaced as Static Web Apps secrets.
- **Monitoring**: Pair Application Insights (frontend + backend) with Langfuse for LLM traces.

## Feature Checklist

- Streaming responses with typing indicators.
- Cypher visualization (syntax highlight, copy-to-clipboard).
- Tabular or charted results via `ResultsTable`.
- Error and retry states surfaced inline.
- Knowledge-base workflows (favorites, category curation).
- Progress cards describing whether the analytics agent or standard Cypher path handled the question.

Future documentation will include component prop tables, accessibility audit steps, and an end-to-end data-flow diagram linking React hooks to backend services.

