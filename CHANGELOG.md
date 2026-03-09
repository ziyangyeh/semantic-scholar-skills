# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.1.0] - 2026-03-10

### Added

- Typed Semantic Scholar core client under `src/semantic_scholar_skills/core/`, including request models, transport helpers, exception types, and compatibility adapters.
- Workflow engine under `src/semantic_scholar_skills/engine/` with `expand_references`, `trace_citations`, and `paper_triage`.
- Standalone stdlib runtime under `src/semantic_scholar_skills/standalone/` for bundle-friendly execution.
- Tracked generated Claude skill bundles under `skills/`, built from `skills-src/` via `scripts/bundle_skills.py`.
- MCP server and optional FastAPI HTTP bridge under `src/semantic_scholar_skills/mcp/`, preserving the 16-tool surface from the earlier server-first repo.
- Offline pytest coverage across `tests/contract/`, `tests/core/`, `tests/engine/`, `tests/skills/`, and `tests/standalone/` (`214` collected tests at the time of the initial release).
- GitHub Actions workflows for CI, weekly spec audit, and tagged PyPI release publishing.
- `scripts/spec_audit.py` to compare local field allowlists against the live Semantic Scholar API schema.

### Changed

- Repositioned the project from a core-only extraction to the package-first successor of `semantic-scholar-fastmcp-mcp-server`.
- Rewrote the README to document the full package surface: core client, workflow engine, skill bundles, and MCP server.
