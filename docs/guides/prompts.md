# Prompt & Few-Shot Management

Prompt quality drives GraphRAG accuracy. This guide tracks where templates live and how to evolve them safely.

## File Layout

- `ai/prompts/*.yaml` – Langfuse-compatible templates (e.g., `text_to_cypher_v1.yaml`, `result_summarizer_v1.yaml`).
- `ai/fewshots/` – scripts and JSON files for query categories and examples.
- `ai/terminology/` – YAML dictionaries that enrich prompts with domain-specific terms.

## Workflow

1. **Draft Locally** – edit the YAML template, keeping variables consistent with what backend services expect.
2. **Sync to Langfuse** – use Langfuse UI or API to update the prompt, applying the same label as in `.env` (`PROMPT_LABEL` default `production`).
3. **Record Changes** – document rationale and testing evidence in the PR description or future `docs/changelog.md`.
4. **Backfill Few-Shot Data** – regenerate categories/examples via:

   ```bash
   python ai/fewshots/generate_query_categories.py
   python ai/fewshots/generate_examples.py
   ```

5. **Verify** – run smoke tests (`DEBUG_PROMPT=true`) and capture Langfuse traces for reviewers.

## Tips

- Use `response_format={"type": "json_object"}` when possible for structured outputs.
- Keep terminology JSON/YAML small and composable to avoid bloated prompts.
- When introducing new instructions, update the documentation page that references the behavior (e.g., analytics routing, summarization).

## Backlog

- Automate prompt diffing inside CI.
- Add linting for YAML placeholders.
- Mirror final Langfuse prompt text back into this repo for change tracking.

