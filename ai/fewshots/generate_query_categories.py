"""Generate query categories using query-category-builder prompt from Langfuse.

This script calls the query-category-builder prompt in Langfuse with the schema
to generate categories of query types that can be used to organize few-shot examples.
"""

from pathlib import Path
import os
import sys

# Ensure project root is on sys.path for absolute imports
# From ai/fewshots/generate_query_categories.py, go up 2 levels to reach project root
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.schema.schema_utils import get_cached_schema, fetch_schema_from_neo4j
from ai.llmops.langfuse_client import get_prompt_from_langfuse, create_completion
from dotenv import load_dotenv


def main() -> None:
    """Generate query categories using query-category-builder prompt."""
    # Load .env from project root
    if load_dotenv is not None:
        try:
            load_dotenv(dotenv_path=str(ROOT / ".env"))
        except Exception:
            pass

    # Fetch schema (from cache or Neo4j)
    print("Fetching schema...")
    schema_string = get_cached_schema(
        force_update=False,  # Controlled by UPDATE_NEO4J_SCHEMA env var
        fetch_schema_fn=fetch_schema_from_neo4j,
    )
    print(f"✓ Schema loaded ({len(schema_string)} characters)")

    # Load query-category-builder prompt from Langfuse
    print("\nFetching query-category-builder prompt from Langfuse...")
    try:
        prompt_label = os.environ.get("PROMPT_LABEL", "production")
        prompt = get_prompt_from_langfuse("query-category-builder", langfuse_client=None, label=prompt_label)
        params = prompt.config or {}
        print("✓ Prompt loaded from Langfuse")
    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch prompt from Langfuse: {e}. "
            "Ensure Langfuse is configured (LANGFUSE_HOST, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY) "
            "and the prompt 'query-category-builder' has been synced."
        ) from e

    # Compile prompt with schema variable
    print("\nCompiling prompt with schema...")
    rendered = prompt.compile(schema=schema_string)
    
    # Optionally debug-print the rendered prompt
    if os.environ.get("DEBUG_PROMPT", "").lower() in {"1", "true", "yes"}:
        print("\n" + "="*80)
        print("RENDERED PROMPT:")
        print("="*80)
        print(rendered)
        print("="*80 + "\n")

    # Check if OpenAI/Azure OpenAI is available
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    if not (azure_endpoint and azure_api_key) and not openai_api_key:
        print("\n⚠️  No OpenAI API key found. Showing rendered prompt only.")
        print("\n" + "="*80)
        print(rendered)
        print("="*80)
        return

    # Get model configuration
    model = (
        os.environ.get("OPEN_AI_MODEL")
        or os.environ.get("OPENAI_MODEL")
        or "gpt-4o"
    )
    # For Azure OpenAI GPT-5-mini, temperature must be 1.0 (default) or omitted
    # Use default 0.7 for standard OpenAI, but will be handled by create_completion
    temperature = float(params.get("temperature", 0.7))
    max_tokens = int(params.get("max_tokens", 2000))

    # Use simple JSON object output (ensures valid JSON response)
    response_format = {"type": "json_object"}
    
    # Call the model
    print(f"\nCalling model: {model}...")
    print("Using structured JSON output format")
    output = create_completion(
        rendered,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        langfuse_prompt=prompt,  # Link prompt to observation
        response_format=response_format,
    )

    # Output the result
    print("\n" + "="*80)
    print("GENERATED QUERY CATEGORIES:")
    print("="*80)
    print(output)
    print("="*80)

    # Save to file (default: graph_categories.json in fewshots folder)
    output_file = os.environ.get("OUTPUT_FILE")
    if output_file:
        output_path = Path(output_file)
    else:
        # Default to graph_categories.json in the fewshots folder
        fewshots_dir = Path(__file__).resolve().parent
        output_path = fewshots_dir / "graph_categories.json"
    
    output_path.write_text(output, encoding="utf-8")
    print(f"\n✓ Query categories saved to: {output_path}")


if __name__ == "__main__":
    main()

