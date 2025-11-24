# Graph Analytics Agent - User Guide

## Overview

The Graph Analytics Agent extends your existing text-to-Cypher functionality with advanced graph algorithms. Users can ask questions that require community detection, influence ranking, bridge analysis, and more.

## Available Tools

### 1. **Article Rank** (`article_rank`)
**Purpose**: Ranks nodes by influence using ArticleRank (a PageRank variant).

**Example Questions**:
- "Which influencers are most important in the network?"
- "Rank the most central influencers by their influence score"
- "Who are the top influencers that people follow?"
- "Show me the most influential content creators"
- "Which influencers have the highest ArticleRank score?"

**What it does**: Calculates influence scores based on how many connections a node has and the importance of those connections. Higher scores = more influential.

---

### 2. **Leiden Community Detection** (`leiden`)
**Purpose**: Detects communities/clusters in the graph using the Leiden algorithm.

**Example Questions**:
- "Find communities of people who follow similar influencers"
- "What are the different groups of influencers in the network?"
- "Cluster people by their social connections"
- "Show me communities of youth in Rotterdam"
- "Identify groups of influencers with similar audiences"

**What it does**: Groups nodes into communities where nodes within a community are more connected to each other than to nodes outside. Useful for finding natural groupings in your social network.

---

### 3. **Bridges** (`bridges`)
**Purpose**: Detects critical connection edges (bridges) that connect different parts of the graph.

**Example Questions**:
- "Which connections are critical for connecting different neighborhoods?"
- "Find bridge influencers that connect different communities"
- "What are the bottleneck connections in the network?"
- "Show me critical links between areas"
- "Which relationships are essential for network connectivity?"

**What it does**: Identifies edges whose removal would disconnect parts of the graph. These are often important "bridge" nodes (like influencers who connect different communities).

---

### 4. **Count Nodes** (`count_nodes`)
**Purpose**: Counts nodes in the graph (useful for dataset size questions).

**Example Questions**:
- "How many nodes are in the graph?"
- "What's the total size of the dataset?"
- "Count all nodes by type"
- "How many people, influencers, and areas are there?"

**What it does**: Provides basic statistics about your graph size. May take time on very large databases.

---

## How Questions Are Routed

The system uses an **LLM-based router** that analyzes your question and decides:

1. **If it's a graph analytics question** (mentions communities, influence, bridges, etc.) → Routes to Graph Analytics Agent
2. **If it's a regular data query** (counts, aggregations, lookups) → Routes to text-to-Cypher

### Examples of Routing:

**Graph Analytics** (uses MCP tools):
- "Find communities among people in Rotterdam" → `leiden` tool
- "Which influencers are most central?" → `article_rank` tool
- "Show me bridge connections" → `bridges` tool

**Regular Queries** (uses Cypher):
- "How many female participants are in the dataset?" → Cypher query
- "Count the top popular YouTube videos" → Cypher query
- "Show me all influencers in Rotterdam" → Cypher query

---

## Integration Points

### Backend API

The analytics agent can be integrated into your existing chat API:

```python
# In backend/app/api/chat.py or a new router
from ai.agent import GraphAnalyticsAgent

# Initialize agent (reuse across requests)
analytics_agent = GraphAnalyticsAgent(
    allowed_tool_names=["article_rank", "leiden", "bridges"],  # Limit to specific tools
    use_llm_selector=True,  # Use LLM to choose tools
)

# In your chat endpoint:
async def chat(request: ChatRequest):
    question = request.question
    
    # Simple router: check if question needs analytics
    if _is_analytics_question(question):
        result = await analytics_agent.run(question)
        return {
            "summary": result.summary,
            "tool_name": result.tool_name,
            "results": result.raw_result,
        }
    else:
        # Use existing text-to-Cypher
        return await graphrag_service.process_question(question)
```

### Frontend

Users can ask questions naturally in the chat interface. The system automatically routes to the appropriate tool.

---

## Tool Parameters

The LLM automatically extracts parameters from questions, but you can also specify them:

### Common Parameters:

- **`nodeLabels`**: Array of node labels to filter (e.g., `["Person", "Influencer"]`)
- **`relTypes`**: Array of relationship types (e.g., `["FOLLOWS", "LIVES_IN_AREA"]`)
- **`nodeIdentifierProperty`**: Property to use for node identification (default: `"name"`)

### Example with Explicit Parameters:

```python
result = await agent.run(
    "Find communities",
    tool_name="leiden",
    inputs={
        "nodeLabels": ["Person"],
        "relTypes": ["FOLLOWS"],
        "minCommunitySize": 10,
    }
)
```

---

## Limitations & Notes

1. **Performance**: Some algorithms (like `count_nodes` on large graphs) may timeout. The system handles this gracefully.

2. **Tool Selection**: The LLM uses the graph schema to make informed decisions about which node labels and relationship types to use.

3. **Schema Awareness**: The agent has access to your full graph schema (node labels, relationships, properties) to construct correct tool arguments.

4. **Fallback**: If the LLM can't determine a tool, it falls back to keyword-based matching.

---

## Future Tools

Additional tools can be added by:
1. Adding a `ToolConfig` to `_build_default_configs()`
2. Implementing a summary builder function
3. The LLM will automatically discover and use it via MCP metadata

Potential additions:
- `shortest_path` - Find paths between nodes
- `betweenness_centrality` - Measure node importance as bridges
- `pagerank` - Alternative influence ranking
- `connected_components` - Find disconnected groups

