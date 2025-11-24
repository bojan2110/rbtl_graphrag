# Contributing

We welcome feature ideas, bug fixes, and documentation improvements. This section will evolve into the canonical contributor experience.

## Workflow

1. Create an issue (or pick one with the `help wanted` label).
2. Branch from `main` using `feat/`, `fix/`, or `docs/` prefixes.
3. Run backend + frontend tests plus `mkdocs build --strict` before opening a PR.
4. Include screenshots or Langfuse trace links when changing UI or prompts.
5. Tag relevant reviewers (backend, frontend, AI, docs).

## Style Notes

- Python: follow Ruff/Black defaults (to be enforced in CI).
- TypeScript/React: stick with ESLint + Prettier defaults from `frontend/`.
- Docs: keep sentences short, use active voice, prefer tables/diagrams when clarity improves.

## Definition of Done

- Tests pass locally.
- Docs updated when behavior changes (use the appropriate page in `docs/`).
- Release notes entry added if the change is user visible (future `docs/changelog.md`).

## Roadmap for This Section

- Add PR template.
- Publish coding standards and branching strategy.
- Document mkdocs contribution guide (how to add new pages, how nav works).

