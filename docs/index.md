# RBTL GraphRAG Documentation

RBTL (Reading Between the Lines) leverages a custom GraphRAG implementation to deliver a natural-language interface to Neo4j, combining Retrieval-Augmented Generation with graph analytics tooling. Use this site as the authoritative source for onboarding, architecture decisions, operational playbooks, and contribution guidelines.

## Highlights

- **LLM-powered graph querying** that transforms questions into Cypher via `ai/text_to_cypher.py`.
- **Schema-aware prompts** backed by `ai/schema/` helpers and Langfuse prompt management.
- **Hybrid workflow** with a Next.js frontend, FastAPI backend, MongoDB knowledge base, and optional Neo4j GDS analytics agents.
- **Observability-first approach** using Langfuse, structured logging, and automated tests.

## How to Use These Docs

- Start with [Getting Started](getting-started.md) to stand up the stack locally.
- Explore the [Architecture](architecture/system-overview.md) section for diagrams and service breakdowns.
- Follow the [Guides](guides/graph-analytics.md) when working with prompts, terminology, or analytics agents.
- Consult [Operations](operations/deployment.md) before deploying or running the automated test suites.
- Keep the [Glossary](reference/glossary.md) nearby to stay consistent with project terminology.

## Current Status

This site is still being scaffolded. Existing markdown such as `README.md`, `GRAPH_ANALYTICS_GUIDE.md`, and `MCP_ARCHITECTURE.md` will be merged into the new structure in subsequent passes. Track progress via the `docs` label in the repository issues.

