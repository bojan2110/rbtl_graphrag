# MCP Architecture

This page distills `MCP_ARCHITECTURE.md` into a concise explanation of how GraphRAG talks to external tools such as the Neo4j GDS Agent.

## What Is MCP?

Model Context Protocol (MCP) standardizes how AI assistants (clients) interact with tool servers. Messages travel over JSON-RPC, typically via stdio pipes, which keeps the integration portable and secure.

```
┌──────────────┐    JSON-RPC / stdio    ┌──────────────┐
│ MCP Client   │ <────────────────────> │ MCP Server   │
│ (our code)   │                        │ (gds-agent)  │
└──────────────┘                        └──────────────┘
        │                                         │
        ▼                                         ▼
  Python services                           Neo4j + GDS
```

## Client Lifecycle

1. **Setup** – `Neo4jGDSAgentClient` (in `ai/mcp_client.py`) loads Neo4j credentials, locates the `uvx gds-agent` command, and prepares environment variables.
2. **Connect** – `stdio_client()` launches the server as a subprocess, wiring stdout/stdin to async memory streams managed by AnyIO.
3. **Initialize** – `ClientSession.initialize()` performs the MCP handshake (server sends `initialize`, client responds, both sides exchange capabilities).
4. **List Tools** – `session.list_tools()` requests metadata (name, description, JSON schema inputs) for algorithms like `article_rank`, `leiden`, etc.
5. **Call Tool** – `session.call_tool()` sends parameters, waits for results, and returns textual or structured content to the caller.
6. **Close** – Streams are closed and the subprocess exits cleanly.

If the server fails to send its initialization payload, the client will hang while waiting for the handshake—this explains earlier connectivity issues filed against `gds-agent`.

## Message Flow

```
Client                        Server
  │   launch subprocess   ───▶ │
  │                           │ start process
  │  wait initialize      ◀───│ send initialize request
  │  send init response   ───▶│
  │  tools/list           ───▶│ enumerate algorithms
  │                      ◀─── │ respond with tool metadata
  │  tools/call           ───▶│ execute algorithm / query Neo4j
  │                      ◀─── │ return result content
```

## Why stdio?

- No open ports or network ACLs required.
- Works across macOS/Linux/Windows without extra services.
- Easier local debugging—just inspect stdout/stderr streams.

## Debugging Tips

- Run `python ai/mcp_client.py --interactive` to step through connection, list tools, and invoke them manually.
- Use `DEBUG=1` (AnyIO capability) or `LANGFUSE` traces to capture MCP request/response payloads.
- If initialization stalls, confirm the gds-agent version and verify it supports standalone stdio clients (some builds originally targeted Claude Desktop only).

The GraphRAG backend reuses this client to power the analytics agent described in the guides section.

