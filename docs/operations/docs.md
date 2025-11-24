# Documentation Ops

This page captures the tooling and automation required to publish the MkDocs site to GitHub Pages.

## Local Tooling

Install (or update) the project dependencies, which now include the documentation toolchain:

```bash
pip install -r requirements.txt
```

Key packages:

- `mkdocs` – static site generator
- `mkdocs-material` – UI theme
- `mkdocs-mermaid2-plugin` – renders Mermaid diagrams (e.g., architecture flowcharts)
- `mkdocs-glightbox` – lightbox support for future screenshots
- `pymdown-extensions` – extra Markdown features (superfences, details blocks, etc.)

Common commands:

```bash
mkdocs serve        # live reload at http://127.0.0.1:8000
mkdocs build        # generate site/ directory
mkdocs gh-deploy    # push to gh-pages (requires repo access)
```

Run `mkdocs build --strict` locally before opening a PR so broken links or warnings fail fast.

## GitHub Pages Workflow

A workflow defined in `.github/workflows/docs.yml` handles validation and deployment:

1. Triggers on pushes to `main` and on pull requests.
2. Installs Python 3.11 and the consolidated `requirements.txt`.
3. Runs `mkdocs build --strict` to catch issues early.
4. On `main`, performs `mkdocs gh-deploy --force` to publish the `gh-pages` branch consumed by GitHub Pages.

Enable Pages in the repo settings with source set to the `gh-pages` branch. Add the published URL to `site_url` (already configured in `mkdocs.yml`) and link it in `README.md` badges when ready.

## Contribution Tips

- Keep content changes close to the code they describe; update docs within the same PR when possible.
- Favor relative links (e.g., `[Testing](operations/testing.md)`) so navigation works locally and on GitHub.
- When adding diagrams, export them to `docs/assets/` and reference with relative paths to benefit from glightbox later.

