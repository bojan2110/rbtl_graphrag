# Graph Analytics Agent Guide

Blend Graph Data Science algorithms into the regular GraphRAG chat workflow by enabling the Graph Analytics Agent. Content below distills the legacy `GRAPH_ANALYTICS_GUIDE.md`.

## Overview

The agent extends text-to-Cypher with analytics such as community detection, influence ranking, and bridge analysis. Routing happens automatically based on user intent; when no analytics tool fits, the request falls back to standard Cypher generation.

## Enable the Agent

1. Install the Neo4j GDS Agent (`pip install gds-agent`) or run it as a remote MCP server.
2. Populate `.env` with the same credentials the GDS Agent expects: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, optional `NEO4J_DATABASE`.
3. Set `ENABLE_ANALYTICS_AGENT=true` and restart the backend.
4. Verify connectivity by running `python ai/mcp_client.py --interactive` and listing tools.

## Available Tools

| Tool | Purpose | Example Prompts |
|------|---------|-----------------|
| `article_rank` | Ranks nodes by influence using ArticleRank | “Which influencers are most important?”, “Show me the top creators by ArticleRank score.” |
| `leiden` | Detects communities/clusters via the Leiden algorithm | “Find communities of people who follow similar influencers.” |
| `bridges` | Surfaces critical edges whose removal disconnects the graph | “Which connections are essential for linking neighborhoods?” |
| `count_nodes` | Provides dataset size statistics | “How many people, influencers, and areas are there?” |

Each capability lives in `ai/agent/graph_analytics_agent.py`. Inputs such as `nodeLabels`, `relTypes`, `nodeIdentifierProperty`, or algorithm-specific knobs (e.g., `minCommunitySize`) are inferred from natural language, but you can override them explicitly:

```python
await analytics_agent.run(
    "Find person communities",
    tool_name="leiden",
    inputs={"nodeLabels": ["Person"], "relTypes": ["FOLLOWS"], "minCommunitySize": 10},
)
```

## Routing Logic

1. Chat API receives a user question.
2. Intent classifier (LLM-based with keyword fallback) checks for analytics cues (communities, influence, bridges, graph size).
3. If matched, the backend calls the MCP client, executes the tool, and summarizes the results.
4. Frontend progress cards tell the user which route ran (analytics vs. text-to-Cypher).

Regular Cypher queries still handle counts, aggregations, or lookups that do not require heavy analytics.

## Integration Points

- **Backend** – `backend/app/api/chat.py` wires routing through `services/graphrag.py`, which instantiates the agent once and reuses it per request.  
- **Frontend** – no UX changes required; messages flow through the same UI, but analytics-specific metadata is displayed to set expectations.

## Troubleshooting

- **Tool not found**: ensure the GDS Agent exposes it (`python ai/mcp_client.py --interactive --list-tools`).  
- **Credentials rejected**: confirm TLS-enabled URIs for Aura (`neo4j+s://...`).  
- **Slow responses**: monitor Langfuse traces when algorithms traverse large graphs; consider raising timeouts or narrowing parameters.  
- **Fallback triggered**: set `DEBUG_PROMPT=true` and inspect routing prompts/logs to understand why the LLM avoided analytics.

## Future Tools

The agent reads MCP metadata to discover new tools automatically. To add one:

1. Define a `ToolConfig` in `_build_default_configs()`.
2. Implement a custom summary builder.
3. Regenerate docs to capture the new capability.

Potential additions include `shortest_path`, `betweenness_centrality`, `pagerank`, and `connected_components`.

