# Glossary (Draft)

This glossary will eventually be auto-generated from `ai/terminology/*.yaml`. For now, it mirrors key concepts the team uses in prompts and discussions.

- **GraphRAG** – Graph Retrieval-Augmented Generation system that converts natural language to Cypher.
- **Langfuse** – Observability and prompt management platform used for tracing and versioning LLM calls.
- **MCP (Model Context Protocol)** – Standard for tool/agent interoperability; GraphRAG uses it to talk to the Neo4j GDS Agent.
- **Analytics Agent** – Optional routing path that invokes GDS algorithms (community detection, influence, etc.) instead of plain Cypher.
- **Knowledge Base** – MongoDB-backed store for curated insights, categories, and favorites surfaced in the UI.
- **Few-shot Examples** – JSON snippets that prime the LLM with representative queries per category.

> **Todo:** Add script that imports `ai/terminology/v1.yaml` and renders a table here during docs build.

