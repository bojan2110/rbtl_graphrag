# AI & MCP Stack

Everything under `ai/` powers the LLM workflows, few-shot data, terminology normalization, and Model Context Protocol integrations.

## Text-to-Cypher Pipeline

- Entry point: `ai/text_to_cypher.py`
- Inputs: user question, optional flags (`EXECUTE_CYPHER`, `OUTPUT_MODE`, `DEBUG_PROMPT`)
- Steps:
  1. Load schema context from `ai/schema/`.
  2. Render prompt templates from `ai/prompts/*.yaml`.
  3. Inject few-shot examples from `ai/fewshots/`.
  4. Send request to OpenAI (or override via env var).
  5. Optionally execute the generated query via Neo4j driver and summarize results.

## Terminology Management

- `ai/terminology/loader.py` ingests YAML definitions (e.g., `v1.yaml`) to enrich prompts with domain language and synonyms.
- Future work: automate exports into `docs/reference/glossary.md`.

## MCP Client Integration

- `ai/mcp_client.py` provides async helpers to connect to MCP servers (notably the Neo4j GDS Agent).
- Supports interactive mode (`--interactive`) for manual tool testing.
- Shares credentials with the backend through common environment variables.
- See [MCP Architecture](mcp.md) for the full stdio/JSON-RPC handshake sequence.

## Analytics Agent (Optional)

- Implemented in `ai/agent/graph_analytics_agent.py`.
- Routes qualifying questions to graph algorithms (`leiden`, `article_rank`, `bridges`, `count_nodes`).
- Controlled via `ENABLE_ANALYTICS_AGENT`. When disabled, all traffic goes through text-to-Cypher.
- See [Graph Analytics Guide](../guides/graph-analytics.md) for configuration tips.

## Observability

- `ai/llmops/langfuse_client.py` encapsulates Langfuse tracing.
- Prompts are versioned/labeled in Langfuse; the backend selects a label via the `PROMPT_LABEL` env var.

## Roadmap

- Document prompt schemas and response contracts directly from YAML files.
- Add mkdocstrings support to auto-publish function/class docs.
- Provide scripts that regenerate documentation artifacts (schema visualizations, glossary).

