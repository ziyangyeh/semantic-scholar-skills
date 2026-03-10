# semantic-scholar-skills

`semantic-scholar-skills` is a Semantic Scholar research toolkit built around one shared codebase:

- `semantic_scholar_skills.core` exposes typed request models, transport helpers, exceptions, and `S2Client`.
- `semantic_scholar_skills.engine` turns raw API primitives into three higher-level workflows: `expand_references`, `trace_citations`, and `paper_triage`.
- `skills/` tracks self-contained Claude-friendly bundles generated from `skills-src/` for source checkouts.
- `semantic_scholar_skills.mcp` keeps the 16-tool MCP surface and optional HTTP bridge from the older server-first repo.

This repository is the successor to [`semantic-scholar-fastmcp-mcp-server`](https://github.com/zongmin-yu/semantic-scholar-fastmcp-mcp-server). The old repo remains the MCP-server-first implementation; this repo is the package-first continuation for reusable clients, workflows, and skill bundles.

## What Ships

- Async core client with request models for papers, authors, snippets, and recommendations
- Workflow engine for:
  - expanding one to three seed papers into curated reading buckets
  - tracing a paper’s citation neighborhood into foundations, descendants, bridges, and weak edges
  - triaging ambiguous paper queries into a ranked shortlist with follow-up actions
- Packaged MCP server with 16 tools and an optional FastAPI HTTP bridge
- Offline pytest coverage across `contract/`, `core/`, `engine/`, `skills/`, and `standalone/` (`214` collected tests at the time of the initial release)
- Repository-only assets in a source checkout:
  - tracked generated skill bundles under `skills/`
  - bundle-generation and audit scripts under `scripts/`
  - these assets are not included in the published wheel

## Repository Layout

```text
semantic-scholar-skills/
├── src/semantic_scholar_skills/
│   ├── core/
│   ├── engine/
│   ├── standalone/
│   └── mcp/
├── skills-src/
├── skills/
├── scripts/
│   ├── bundle_skills.py
│   ├── check_bundle_drift.py
│   └── spec_audit.py
└── tests/
```

## Installation

### From source

```bash
git clone https://github.com/zongmin-yu/semantic-scholar-skills.git
cd semantic-scholar-skills
python3 -m pip install -e '.[test]'
```

### From PyPI

After the first tagged release:

```bash
python3 -m pip install semantic-scholar-skills
```

`pip install semantic-scholar-skills` installs the Python package under `src/semantic_scholar_skills`.
It does not install the top-level `skills/`, `skills-src/`, `scripts/`, or `tests/` directories.

## Configuration

Set `SEMANTIC_SCHOLAR_API_KEY` for higher rate limits:

```bash
export SEMANTIC_SCHOLAR_API_KEY=your-api-key-here
```

If the key is unset, empty, or a placeholder such as `none`/`null`/`false`, the package falls back to unauthenticated access with stricter limits.

Relevant runtime environment variables:

- `SEMANTIC_SCHOLAR_API_KEY`
- `SEMANTIC_SCHOLAR_TIMEOUT`
- `SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE`
- `SEMANTIC_SCHOLAR_HTTP_BRIDGE_HOST`
- `SEMANTIC_SCHOLAR_HTTP_BRIDGE_PORT`

## Python API

### Core client

```python
import asyncio

from semantic_scholar_skills.core import (
    PaperDetailsRequest,
    cleanup_client,
    get_default_client,
)


async def main() -> None:
    client = get_default_client()
    try:
        paper = await client.get_paper(
            PaperDetailsRequest(
                paper_id="CorpusId:215416146",
                fields=["title", "year", "authors"],
            )
        )
        print(paper["title"])
    finally:
        await cleanup_client()


asyncio.run(main())
```

### Workflow engine

```python
import asyncio

from semantic_scholar_skills.core import cleanup_client, get_default_client
from semantic_scholar_skills.engine import expand_references


async def main() -> None:
    client = get_default_client()
    try:
        result = await expand_references(
            client,
            ["Attention Is All You Need"],
            recommendation_pool="all-cs",
            recommendation_limit=30,
            per_bucket_limit=3,
        )
        print(result.to_dict()["closest_neighbors"][0]["paper"]["title"])
    finally:
        await cleanup_client()


asyncio.run(main())
```

## Bundled Skills

Tracked generated bundles live under `skills/` and are regenerated from `skills-src/`.
These bundles are repository assets rather than wheel contents.
If you installed from PyPI, clone the repository or copy a generated bundle before using the commands below.

Available workflows:

- `skills/expand-references`
- `skills/trace-citations`
- `skills/paper-triage`

Regenerate or verify the tracked bundle:

```bash
python3 scripts/bundle_skills.py
python3 scripts/check_bundle_drift.py
```

Run a bundled skill directly:

```bash
python3 skills/paper-triage/scripts/run.py "retrieval augmented generation"
```

Each bundled skill prints one JSON payload with:

- `schema_version`
- `workflow`
- `status`
- `runtime`
- `arguments`
- `result` or `error`

See `skills-src/_shared/output_contract.md` for the stable output contract.

## MCP Server

The package still ships the full 16-tool MCP surface:

- Papers:
  - `paper_relevance_search`
  - `paper_bulk_search`
  - `paper_title_search`
  - `paper_details`
  - `paper_batch_details`
  - `paper_authors`
  - `paper_citations`
  - `paper_references`
  - `paper_autocomplete`
  - `snippet_search`
- Authors:
  - `author_search`
  - `author_details`
  - `author_papers`
  - `author_batch_details`
- Recommendations:
  - `get_paper_recommendations_single`
  - `get_paper_recommendations_multi`

Start the server with the packaged console entrypoint:

```bash
semantic-scholar-skills-mcp
```

or via the module path:

```bash
python3 -m semantic_scholar_skills.mcp.server
```

The optional HTTP bridge is enabled by default and uses:

- `SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE`
- `SEMANTIC_SCHOLAR_HTTP_BRIDGE_HOST`
- `SEMANTIC_SCHOLAR_HTTP_BRIDGE_PORT`

## Testing and Maintenance

```bash
pytest --collect-only -q tests
pytest -m "not live" -q
python3 scripts/check_bundle_drift.py
python3 scripts/spec_audit.py
```

`spec_audit.py` compares the local field allowlists in `config.py` against the live Semantic Scholar Graph API schema. It returns a non-zero exit code only when real field drift is detected; transient fetch/format failures are logged as warnings and treated as non-blocking.

## Changelog

See `CHANGELOG.md`.

## License

MIT. See `LICENSE`.
