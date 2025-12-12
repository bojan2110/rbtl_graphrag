# API Reference

The GraphRAG backend exposes a FastAPI REST API for querying Neo4j graph databases using natural language. All endpoints are prefixed with `/api` except for the root and health endpoints.

## Interactive API Documentation

FastAPI automatically generates interactive API documentation that you can use to explore and test endpoints:

- **Swagger UI**: Available at `/docs` when the backend is running
  - Local: http://localhost:8000/docs
  - Docker: http://localhost:8001/docs
- **ReDoc**: Available at `/redoc` when the backend is running
  - Local: http://localhost:8000/redoc
  - Docker: http://localhost:8001/redoc

The interactive docs include:
- Complete request/response schemas
- Try-it-out functionality to test endpoints directly
- Authentication requirements (if configured)
- Example payloads

## Base URL

- **Local Development**: `http://localhost:8000`
- **Docker**: `http://localhost:8001`
- **Production**: Configured per deployment environment

## Endpoints

### Health Check

#### `GET /api/health`

Health check endpoint for monitoring and deployment probes.

**Response:**
```json
{
  "status": "healthy",
  "service": "graphrag-api"
}
```

---

### Chat Endpoints

#### `POST /api/chat`

Main chat interface for processing natural language questions and returning Cypher queries with results.

**Request Body:**
```json
{
  "username": "bojan",
  "question": "How many TikTok users have over 1 million followers?",
  "execute_cypher": true,
  "output_mode": "chat"
}
```

**Parameters:**
- `username` (string, required): Tester username (must be in allowed list)
- `question` (string, required): Natural language question
- `execute_cypher` (boolean, default: `true`): Whether to execute the generated Cypher query
- `output_mode` (string, default: `"chat"`): Output format - `"json"`, `"chat"`, or `"both"`

**Response:**
```json
{
  "username": "bojan",
  "question": "How many TikTok users have over 1 million followers?",
  "route_type": "cypher",
  "cypher": "MATCH (t:TikTokUser) WHERE t.follower_count > 1000000 RETURN count(t) as count",
  "results": [{"count": 42}],
  "summary": "There are 42 TikTok users with over 1 million followers.",
  "examples_used": [...],
  "timings": {
    "similar_queries": 0.5,
    "generate_cypher": 2.3,
    "query_knowledge_base": 0.8,
    "generate_final_response": 1.2
  },
  "message_id": "uuid-here"
}
```

**Response Fields:**
- `route_type`: Either `"analytics"` or `"cypher"` indicating which processing route was used
- `cypher`: Generated Cypher query (if route_type is "cypher")
- `tool_name`: Analytics tool name (if route_type is "analytics")
- `tool_inputs`: Analytics tool parameters (if route_type is "analytics")
- `results`: Query results from Neo4j
- `summary`: Natural language summary of results
- `examples_used`: Similar query examples used for few-shot learning
- `timings`: Performance metrics for each processing step
- `message_id`: Unique identifier for the stored message

#### `GET /api/chat/users`

Return list of available tester usernames.

**Response:**
```json
{
  "users": ["bojan", "roel", "famke", "scarlett"]
}
```

#### `GET /api/chat/history/{username}`

Retrieve stored chat history for a specific user.

**Path Parameters:**
- `username` (string): Tester username

**Response:**
```json
{
  "username": "bojan",
  "messages": [
    {
      "id": "message-id",
      "role": "user",
      "content": "Question text",
      "timestamp": "2024-01-01T12:00:00",
      "is_favorite": false
    },
    {
      "id": "message-id",
      "role": "assistant",
      "content": "Response text",
      "cypher": "MATCH ...",
      "results": [...],
      "summary": "Summary text",
      "timestamp": "2024-01-01T12:00:01",
      "is_favorite": false
    }
  ]
}
```

#### `DELETE /api/chat/history/{username}/{message_id}`

Delete a specific message from a user's chat history.

**Path Parameters:**
- `username` (string): Tester username
- `message_id` (string): Message ID to delete

**Response:**
```json
{
  "message": "Message deleted"
}
```

#### `POST /api/chat/favorites/{username}/{message_id}`

Mark or unmark a message as favorite.

**Path Parameters:**
- `username` (string): Tester username
- `message_id` (string): Message ID

**Request Body:**
```json
{
  "is_favorite": true
}
```

**Response:**
```json
{
  "message": "Favorite updated"
}
```

#### `GET /api/chat/favorites/{username}`

Retrieve all favorite messages for a user.

**Path Parameters:**
- `username` (string): Tester username

**Response:**
```json
{
  "username": "bojan",
  "favorites": [
    {
      "message": {
        "id": "message-id",
        "role": "assistant",
        "content": "Response text",
        "cypher": "MATCH ...",
        "timestamp": "2024-01-01T12:00:00",
        "is_favorite": true
      },
      "question": "Original question",
      "question_id": "question-id"
    }
  ]
}
```

#### `GET /api/chat/analytics-tools`

Return available graph analytics tools and their descriptions.

**Response:**
```json
{
  "tools": [
    {
      "name": "leiden",
      "description": "Community detection using Leiden algorithm",
      "keywords": ["community", "cluster", "group"],
      "defaults": {...}
    },
    {
      "name": "article_rank",
      "description": "Influence ranking using ArticleRank",
      "keywords": ["influence", "rank", "important"],
      "defaults": {...}
    }
  ],
  "note": "These tools are available for graph analytics questions..."
}
```

#### `WS /api/chat/stream`

WebSocket endpoint for streaming chat responses in real-time.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8001/api/chat/stream');
```

**Send Message:**
```json
{
  "username": "bojan",
  "question": "How many people are there?",
  "execute_cypher": true,
  "output_mode": "chat"
}
```

**Receive Messages:**
```json
{"type": "status", "message": "Processing question..."}
{"type": "cypher", "cypher": "MATCH (p:Person) RETURN count(p)"}
{"type": "results", "results": [{"count": 1000}]}
{"type": "summary", "summary": "There are 1000 people in the graph."}
{"type": "complete"}
```

---

### Graph Information Endpoints

#### `GET /api/graph-info`

Return cached graph schema overview including nodes, relationships, and terminology.

**Response:**
```json
{
  "schema_text": "Node properties:\n:`Person` {...}",
  "terminology_text": "Terminology definitions...",
  "nodes": [
    {
      "label": "Person",
      "properties": [
        {"property": "age", "type": "String"},
        {"property": "gender", "type": "String"}
      ],
      "description": "A person in the graph"
    }
  ],
  "relationships": [
    {
      "start": "Person",
      "type": "FOLLOWS",
      "end": "Influencer",
      "description": "Person follows an influencer"
    }
  ],
  "graph_ready": true,
  "summary": "This overview is generated from the cached schema..."
}
```

#### `GET /api/graph-visualization`

Return the static schema visualization JSON file for rendering graph diagrams.

**Response:**
```json
{
  "nodes": [...],
  "relationships": [...],
  "visualization": {...}
}
```

---

### Knowledge Base Endpoints

#### `GET /api/knowledge-base/categories`

Retrieve all query categories from the knowledge base.

**Response:**
```json
[
  {
    "category_name": "Entity lookup and profiling",
    "category_description": "Queries that retrieve entity information..."
  }
]
```

#### `GET /api/knowledge-base/queries?category={category_name}`

Retrieve query examples for a specific category.

**Query Parameters:**
- `category` (string, required): Category name

**Response:**
```json
[
  {
    "question": "Return all Person nodes with their properties",
    "cypher": "MATCH (p:Person) RETURN p LIMIT 100",
    "added_at": "2024-01-01T12:00:00",
    "created_by": "user"
  }
]
```

#### `POST /api/knowledge-base/queries`

Add a new query example to a category.

**Request Body:**
```json
{
  "category_name": "Entity lookup and profiling",
  "question": "Find all verified TikTok users",
  "cypher": "MATCH (t:TikTokUser) WHERE t.is_verified = true RETURN t",
  "created_by": "user"
}
```

**Response:**
```json
{
  "message": "Query added successfully",
  "example": {
    "question": "Find all verified TikTok users",
    "cypher": "MATCH (t:TikTokUser) WHERE t.is_verified = true RETURN t",
    "added_at": "2024-01-01T12:00:00",
    "created_by": "user"
  }
}
```

#### `PUT /api/knowledge-base/queries?category={category_name}`

Update an existing query example.

**Query Parameters:**
- `category` (string, required): Category name

**Request Body:**
```json
{
  "old_question": "Original question",
  "old_cypher": "MATCH ...",
  "new_question": "Updated question",
  "new_cypher": "MATCH ..."
}
```

#### `DELETE /api/knowledge-base/queries?category={category_name}`

Delete a query example from a category.

**Query Parameters:**
- `category` (string, required): Category name

**Request Body:**
```json
{
  "question": "Question to delete",
  "cypher": "Cypher to delete"
}
```

#### `GET /api/knowledge-base/categories`

Retrieve all categories (same as `/api/knowledge-base/categories`).

#### `POST /api/knowledge-base/categories`

Create a new category.

**Request Body:**
```json
{
  "category_name": "New Category",
  "category_description": "Description of the category"
}
```

#### `PUT /api/knowledge-base/categories`

Update an existing category.

**Request Body:**
```json
{
  "category_name": "Category Name",
  "category_description": "Updated description"
}
```

#### `DELETE /api/knowledge-base/categories?category={category_name}`

Delete a category and all its query examples.

**Query Parameters:**
- `category` (string, required): Category name

---

## Error Responses

All endpoints may return standard HTTP error responses:

- `400 Bad Request`: Invalid request parameters
- `403 Forbidden`: Username not in allowed list
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Authentication

Currently, the API uses username-based access control. Only usernames in the allowed tester list can access chat endpoints. This is configured in `backend/app/services/chat_sessions.py`.

Future versions may include:
- API key authentication
- OAuth2 integration
- Role-based access control

---

## Rate Limiting

Rate limiting is not currently implemented but may be added in future versions.

---

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at `/openapi.json` when the backend is running. This can be used to:
- Generate client SDKs
- Import into API testing tools (Postman, Insomnia)
- Generate additional documentation
