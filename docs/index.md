# RBTL GraphRAG Documentation

## Introduction

RBTL GraphRAG is a web-based portal that provides a natural language interface for querying Neo4j graph databases, enabling users to explore complex graph data without needing to be technical experts themselves. The system delivers an intuitive chat-based experience where users can ask questions in plain English and receive both structured query results and conversational summaries. The AI does its magic in the background - deciding on the intent of the user questions, and calling the applicable tools(agents) that handle: cypher-to-text queries, data visualization or advanced graph algorithms. The portal includes features such as personal chat interface, query result visualization, a knowledge base for organizing query examples (for improving the AI capabilities), and real-time agent tracking that shows where queries are routed in the agentic system.

The platform is designed for analysts, researchers, and business users who need to extract insights from graph databases but may not have expertise in graph query languages. By abstracting away the complexity of Cypher syntax, the system democratizes access to graph data, allowing domain experts to focus on asking the right questions rather than learning database-specific query languages. The multi-user architecture supports separate chat sessions for different testers or team members, with each user maintaining their own conversation history and favorite queries, making it suitable for collaborative environments where multiple stakeholders need to explore the same graph data from different perspectives.

At its core, RBTL GraphRAG leverages several sophisticated AI capabilities to deliver intelligent query generation and analysis. The system uses large language models (LLMs) to convert natural language questions into accurate Cypher queries, with schema-aware prompt engineering that ensures generated queries respect the Neo4j database structure. An Graph Analytics Agent extends this functionality by intelligently routing certain questions to graph data science algorithms—such as community detection (Leiden), influence ranking (ArticleRank) or visualizing the Cypher obtained data. The platform also maintains a knowledge base of categorized query examples stored in MongoDB and synchronized with Neo4j's vector store, enabling few-shot learning that helps the LLM generate more accurate queries by referencing similar past questions. Full observability is provided through Langfuse integration, which traces all LLM calls, prompt versions, and tool invocations, giving administrators visibility into system performance and query patterns.

## How to Use These Docs

- Start with [Getting Started](getting-started.md) to run the dockerized application locally.
- Explore the [Architecture](architecture/system-overview.md) section for diagrams and service breakdowns.
- Review [Docker Deployment](DOCKER_DEPLOYMENT.md) for local and cloud container deployment.
- Consult [Operations](operations/deployment.md) for environment-specific deployment guides.
- See [Azure Production Deployment](operations/azure-deployment.md) for cloud deployment with Docker containers.

