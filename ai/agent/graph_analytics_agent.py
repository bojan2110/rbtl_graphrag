"""Graph analytics agent that routes natural language queries to MCP tools."""

from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from ai.llmops.langfuse_client import create_completion
from ai.mcp_client import MCPClient, create_client
from ai.schema.schema_utils import load_cached_schema


class GraphAnalyticsAgentError(RuntimeError):
    """Base exception for graph analytics agent errors."""


@dataclass
class ToolConfig:
    """Configuration metadata for an MCP tool."""

    name: str
    description: str
    keywords: Tuple[str, ...]
    defaults: Dict[str, Any] = field(default_factory=dict)
    summary_builder: Optional[
        Callable[[List[Dict[str, Any]]], str]
    ] = None  # Takes tool result content, returns summary text.


@dataclass
class GraphAnalyticsResult:
    """Structured result returned by the graph analytics agent."""

    tool_name: str
    inputs: Dict[str, Any]
    raw_result: List[Dict[str, Any]]
    summary: str


class GraphAnalyticsAgent:
    """Routes user questions to MCP graph analytics tools."""

    def __init__(
        self,
        tool_configs: Optional[List[ToolConfig]] = None,
        default_identifier_property: str = "name",
        allowed_tool_names: Optional[List[str]] = None,
        use_llm_selector: bool = True,
        llm_model: Optional[str] = None,
    ) -> None:
        self._client: Optional[MCPClient] = None
        self._client_lock = asyncio.Lock()
        self._default_identifier_property = default_identifier_property
        self._allowed_tool_names = set(allowed_tool_names or [])
        self._use_llm_selector = use_llm_selector
        self._llm_model = (
            llm_model
            or os.environ.get("GRAPH_AGENT_MODEL")
            or os.environ.get("OPENAI_MODEL")
            or "gpt-4o-mini"
        )

        configs = tool_configs if tool_configs is not None else self._build_default_configs()
        if self._allowed_tool_names:
            configs = [cfg for cfg in configs if cfg.name in self._allowed_tool_names]
        self._tool_configs: Dict[str, ToolConfig] = {config.name: config for config in configs}

        if not self._tool_configs:
            raise ValueError("No graph analytics tools configured or allowed.")

        self._tool_metadata: Dict[str, Dict[str, Any]] = {}
        self._tool_metadata_loaded = False

    async def _get_client(self) -> MCPClient:
        if self._client is None:
            async with self._client_lock:
                if self._client is None:
                    self._client = await create_client()
        return self._client

    async def close(self) -> None:
        """Close MCP client and stop the underlying server."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def run(
        self,
        question: str,
        tool_name: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> GraphAnalyticsResult:
        """Execute the best-fit analytics tool for a question."""
        llm_suggested_inputs: Dict[str, Any] = {}
        if tool_name is None and self._use_llm_selector:
            selection = await self._select_tool_with_llm(question)
            if selection:
                tool_name = selection.get("tool")
                llm_suggested_inputs = selection.get("inputs", {})

        # Only use keyword fallback if LLM selector is disabled
        # If LLM selector is enabled but returned None, that means LLM couldn't find a tool
        if tool_name is None:
            if self._use_llm_selector:
                # LLM selector was used but didn't find a tool - raise error
                raise GraphAnalyticsAgentError(
                    "Could not infer a graph analytics tool for this question. "
                    "The LLM tool selector did not find a suitable tool."
                )
            else:
                # LLM selector disabled - use keyword fallback
                tool_name = self._infer_tool(question)
                if tool_name is None:
                    raise GraphAnalyticsAgentError(
                        "Could not infer a graph analytics tool for this question."
                    )

        if tool_name not in self._tool_configs:
            raise GraphAnalyticsAgentError(f"Unsupported tool: {tool_name}")

        config = self._tool_configs[tool_name]
        combined_inputs = dict(llm_suggested_inputs)
        if inputs:
            combined_inputs.update(inputs)

        prepared_inputs = self._prepare_inputs(config, question, combined_inputs)
        client = await self._get_client()

        try:
            result_content = await client.call_tool(tool_name, prepared_inputs)
        except Exception as exc:
            raise GraphAnalyticsAgentError(
                f"Tool call failed for '{tool_name}': {exc}"
            ) from exc

        summary = self._build_summary(config, result_content, question)

        return GraphAnalyticsResult(
            tool_name=tool_name,
            inputs=prepared_inputs,
            raw_result=result_content,
            summary=summary,
        )

    def list_tools(self) -> List[ToolConfig]:
        """Return supported tool configurations."""
        return list(self._tool_configs.values())
    
    def _summarize_schema_for_tool_selection(self, full_schema: str) -> str:
        """Create a concise schema summary with just node labels and relationship types.
        
        This reduces prompt size while keeping essential information for tool selection.
        """
        if not full_schema or full_schema == "Graph schema not available.":
            return full_schema
        
        # Extract node labels and relationship types from the schema
        # The schema format is:
        # Node properties:
        # :`Label` {props...}
        # ...
        # Relationship properties:
        # :`REL_TYPE` {props...}
        # ...
        # The relationships:
        # (:Label)-[:REL_TYPE]->(:Label)
        
        lines = full_schema.split('\n')
        node_labels = []
        rel_types = []
        relationships = []
        
        in_node_props = False
        in_rel_props = False
        in_rels = False
        
        for line in lines:
            if 'Node properties:' in line:
                in_node_props = True
                in_rel_props = False
                in_rels = False
                continue
            elif 'Relationship properties:' in line:
                in_node_props = False
                in_rel_props = True
                in_rels = False
                continue
            elif 'The relationships:' in line:
                in_node_props = False
                in_rel_props = False
                in_rels = True
                continue
            
            if in_node_props and line.strip().startswith(':`'):
                # Extract label: :`Label` {props...}
                label = line.split('`')[1] if '`' in line else None
                if label:
                    node_labels.append(label)
            elif in_rel_props and line.strip().startswith(':`'):
                # Extract relationship type: :`REL_TYPE` {props...}
                rel_type = line.split('`')[1] if '`' in line else None
                if rel_type:
                    rel_types.append(rel_type)
            elif in_rels and ')-[:' in line:
                # Extract relationship: (:Label)-[:REL_TYPE]->(:Label)
                relationships.append(line.strip())
        
        # Build concise summary
        summary_parts = []
        if node_labels:
            summary_parts.append(f"Node labels: {', '.join(sorted(set(node_labels)))}")
        if rel_types:
            summary_parts.append(f"Relationship types: {', '.join(sorted(set(rel_types)))}")
        if relationships:
            summary_parts.append(f"Key relationships:\n" + "\n".join(relationships[:10]))  # Limit to first 10
        
        return "\n".join(summary_parts) if summary_parts else "Graph schema summary not available."

    def _infer_tool(self, question: str) -> Optional[str]:
        normalized = question.lower()
        import logging
        logger = logging.getLogger("GraphAnalyticsAgent")
        logger.debug(f"Keyword fallback: checking question '{question}' (normalized: '{normalized}') against keywords")
        
        # Get all available keywords for debugging
        all_keywords = {kw.lower(): cfg.name for cfg in self._tool_configs.values() for kw in cfg.keywords}
        logger.debug(f"Available keywords: {all_keywords}")
        
        for config in self._tool_configs.values():
            # Check if any keyword appears in the normalized question
            # Simple substring match: "community" should match "communities"
            for kw in config.keywords:
                kw_lower = kw.lower()
                # Direct substring match
                if kw_lower in normalized:
                    logger.info(f"Keyword match found: '{kw}' in '{normalized}' -> {config.name}")
                    return config.name
                # Also check if any word in the question contains the keyword
                # e.g., "communities" contains "community"
                for word in normalized.split():
                    if kw_lower in word or word.startswith(kw_lower):
                        logger.info(f"Keyword match found: '{kw}' in word '{word}' -> {config.name}")
                        return config.name
        
        logger.info(f"No keyword matches found for: {question}")
        return None

    async def _get_tool_metadata(self) -> Dict[str, Dict[str, Any]]:
        if self._tool_metadata_loaded and self._tool_metadata:
            return self._tool_metadata

        client = await self._get_client()
        tools = await client.list_tools()
        metadata: Dict[str, Dict[str, Any]] = {}
        for tool in tools:
            name = tool.get("name")
            if not name:
                continue
            if self._allowed_tool_names and name not in self._allowed_tool_names:
                continue
            if name in self._tool_configs:
                metadata[name] = tool

        # Only mark as loaded if we got at least one tool; otherwise keep trying later.
        if metadata:
            self._tool_metadata = metadata
            self._tool_metadata_loaded = True
        return self._tool_metadata

    async def _select_tool_with_llm(self, question: str) -> Optional[Dict[str, Any]]:
        if not self._llm_model:
            import logging
            logger = logging.getLogger("GraphAnalyticsAgent")
            logger.debug("LLM model not set, skipping LLM tool selection")
            return None

        try:
            metadata = await self._get_tool_metadata()
            import logging
            logger = logging.getLogger("GraphAnalyticsAgent")
            logger.debug(f"Loaded {len(metadata)} tool metadata entries")
        except Exception as e:
            import logging
            logger = logging.getLogger("GraphAnalyticsAgent")
            logger.warning(f"Failed to load tool metadata: {e}")
            metadata = {}

        if not metadata:
            import logging
            logger = logging.getLogger("GraphAnalyticsAgent")
            logger.warning("No tool metadata available for LLM selection")
            return None

        tool_sections = []
        for name, meta in metadata.items():
            config = self._tool_configs.get(name)
            description = meta.get("description") or (config.description if config else "")
            schema_summary = _summarize_input_schema(meta.get("inputSchema"))
            defaults = config.defaults if config else {}
            tool_sections.append(
                {
                    "name": name,
                    "description": description,
                    "schema": schema_summary,
                    "default_args": defaults,
                }
            )

        tools_text_lines = []
        for idx, tool in enumerate(tool_sections, start=1):
            lines = [
                f"{idx}. {tool['name']}",
                f"   Description: {tool['description']}",
            ]
            if tool["schema"]:
                lines.append(f"   Input schema: {tool['schema']}")
            if tool["default_args"]:
                lines.append(f"   Default args: {json.dumps(tool['default_args'], ensure_ascii=False)}")
            tools_text_lines.append("\n".join(lines))
        tools_text = "\n".join(tools_text_lines)

        # Load graph schema for context - use summarized version to reduce prompt size
        full_schema = load_cached_schema() or "Graph schema not available."
        schema_text = self._summarize_schema_for_tool_selection(full_schema)

        prompt = f"""
You are a routing assistant that selects the best graph analytics tool for a question.

Graph Schema (for reference when constructing tool arguments):
{schema_text}

Available tools (only choose from these):
{tools_text}

For the given user question, choose the single most appropriate tool and optional JSON arguments.
When constructing arguments, use the graph schema above to determine valid node labels and relationship types.
If no tool applies, set tool to null.

Respond STRICTLY with JSON using this schema:
{{
  "tool": "<tool-name or null>",
  "inputs": {{ "key": "value", ... }},
  "reason": "<short explanation>"
}}

Question: {question}
"""

        try:
            import logging
            logger = logging.getLogger("GraphAnalyticsAgent")
            logger.debug(f"Calling LLM for tool selection with model: {self._llm_model}")
            
            # Try with response_format first, fallback if it fails
            try:
                completion = create_completion(
                    prompt.strip(),
                    model=self._llm_model,
                    temperature=0.0,
                    max_tokens=600,
                    response_format={"type": "json_object"},
                )
            except Exception as e:
                import logging
                logger = logging.getLogger("GraphAnalyticsAgent")
                logger.warning(f"LLM call with response_format failed: {e}, trying without it")
                # Fallback: try without response_format and parse JSON manually
                completion = create_completion(
                    prompt.strip(),
                    model=self._llm_model,
                    temperature=0.0,
                    max_tokens=600,
                    # No response_format - will need to extract JSON from response
                )
            
            if not completion or not completion.strip():
                logger.error(f"LLM returned empty response (model: {self._llm_model})")
                logger.error(f"Prompt length: {len(prompt)}, tools: {len(tool_sections)}")
                logger.error(f"Prompt preview (first 1000 chars):\n{prompt[:1000]}")
                # This is a critical error - LLM should always return something
                # Return None to trigger fallback or error
                return None
            
            # Try to parse JSON, handle potential issues
            completion = completion.strip()
            logger.debug(f"LLM response (first 200 chars): {completion[:200]}")
            
            # Remove markdown code blocks if present
            if completion.startswith("```"):
                lines = completion.split("\n")
                completion = "\n".join(lines[1:-1]) if len(lines) > 2 else completion
            
            data = json.loads(completion)
            import logging
            logger = logging.getLogger("GraphAnalyticsAgent")
            logger.debug(f"LLM tool selection response: {data}")
        except json.JSONDecodeError as e:
            import logging
            logger = logging.getLogger("GraphAnalyticsAgent")
            logger.warning(f"LLM tool selection JSON parse failed: {e}, response: {completion[:200]}")
            return None
        except Exception as e:
            import logging
            logger = logging.getLogger("GraphAnalyticsAgent")
            logger.warning(f"LLM tool selection failed: {e}")
            return None

        tool_name = data.get("tool") or data.get("tool_name")
        if tool_name is None:
            import logging
            logger = logging.getLogger("GraphAnalyticsAgent")
            logger.info(f"LLM returned null tool for question: {question}")
            return None
        if tool_name not in self._tool_configs:
            import logging
            logger = logging.getLogger("GraphAnalyticsAgent")
            logger.warning(f"LLM selected unknown tool: {tool_name}, available: {list(self._tool_configs.keys())}")
            return None

        inputs = data.get("inputs") or data.get("arguments") or {}
        if not isinstance(inputs, dict):
            inputs = {}
        return {"tool": tool_name, "inputs": inputs, "reason": data.get("reason")}

    def _prepare_inputs(
        self,
        config: ToolConfig,
        question: str,
        overrides: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        inputs = dict(config.defaults)

        # Always set identifier property if supported.
        if "nodeIdentifierProperty" not in inputs:
            inputs["nodeIdentifierProperty"] = self._default_identifier_property

        # Simple pattern: extract area/municipality names for filtering.
        geos = self._extract_geo_filters(question)
        if geos:
            inputs.setdefault("nodeLabels", ["Area", "Municipality"])
            inputs.setdefault("filterNames", geos)

        if overrides:
            inputs.update(overrides)
        return inputs

    def _extract_geo_filters(self, question: str) -> List[str]:
        # Naive extraction: any quoted text after "in".
        matches = re.findall(r"in ([A-Z][A-Za-z0-9_ -]+)", question)
        cleaned = [name.strip(" ,.") for name in matches]
        return cleaned

    def _build_summary(
        self,
        config: ToolConfig,
        content: List[Dict[str, Any]],
        question: str,
    ) -> str:
        if config.summary_builder:
            try:
                return config.summary_builder(content)
            except Exception:
                pass  # Fall back to default summary.

        if not content:
            return f"Tool '{config.name}' returned no results."

        if len(content) == 1 and "text" in content[0]:
            return content[0]["text"]

        snippet = json.dumps(content[:1], ensure_ascii=False)
        return (
            f"Tool '{config.name}' returned {len(content)} rows. "
            f"First entry: {snippet}"
        )

    def _build_default_configs(self) -> List[ToolConfig]:
        return [
            ToolConfig(
                name="article_rank",
                description="Ranks nodes by influence using ArticleRank (PageRank variant).",
                keywords=("influencer", "important", "central", "rank", "pagerank"),
                defaults={"maxIterations": 20, "tolerance": 0.0001},
                summary_builder=_summarize_rankings,
            ),
            ToolConfig(
                name="leiden",
                description="Community detection using the Leiden algorithm.",
                keywords=("community", "cluster", "group", "modularity"),
                defaults={"minCommunitySize": 5, "tolerance": 0.0001},
                summary_builder=_summarize_leiden,
            ),
            ToolConfig(
                name="bridges",
                description="Detects bridge edges connecting graph components.",
                keywords=("bridge", "bottleneck", "critical connection", "cut edge"),
                defaults={},
                summary_builder=_summarize_bridges,
            ),
            ToolConfig(
                name="count_nodes",
                description="Counts nodes per label.",
                keywords=("count nodes", "size", "how many nodes", "dataset size"),
                defaults={},
                summary_builder=_summarize_text_result,
            ),
        ]


def _summarize_rankings(content: List[Dict[str, Any]]) -> str:
    if not content:
        return "No influential nodes found."

    rows = content[0].get("json", content)
    if isinstance(rows, list):
        top_rows = rows[:5]
        formatted = ", ".join(
            f"{row.get('nodeName') or row.get('name', 'Unknown')} "
            f"(score={row.get('score') or row.get('articleRank')})"
            for row in top_rows
        )
        return f"Top ranked nodes: {formatted}"
    text = content[0].get("text")
    return text or "Influence ranking computed."


def _summarize_leiden(content: List[Dict[str, Any]]) -> str:
    if not content:
        return "No communities detected."
    payload = content[0]
    if "json" in payload:
        data = payload["json"]
        if isinstance(data, dict):
            return (
                f"Detected {data.get('communityCount', 'multiple')} communities. "
                f"Largest size: {data.get('largestCommunitySize')}, "
                f"modularity: {data.get('modularity')}"
            )
    return payload.get("text", "Leiden algorithm completed.")


def _summarize_bridges(content: List[Dict[str, Any]]) -> str:
    if not content:
        return "No bridge edges found."
    payload = content[0]
    if "json" in payload and isinstance(payload["json"], list):
        bridges = payload["json"]
        examples = ", ".join(
            f"{row.get('source')}→{row.get('target')}" for row in bridges[:5]
        )
        return f"Found {len(bridges)} bridge edges. Examples: {examples}"
    return payload.get("text", "Bridge detection completed.")


def _summarize_text_result(content: List[Dict[str, Any]]) -> str:
    if not content:
        return "No data returned."
    if "text" in content[0]:
        return content[0]["text"]
    return json.dumps(content[0], ensure_ascii=False)


def _summarize_input_schema(schema: Any) -> str:
    if not isinstance(schema, dict):
        return ""
    schema_type = schema.get("type")
    if schema_type == "object" and "properties" in schema:
        props = list(schema["properties"].keys())
        if props:
            return f"object with properties {props}"
    if "description" in schema:
        return schema["description"]
    return ""

