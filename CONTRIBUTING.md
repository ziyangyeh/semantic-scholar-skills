# Contributing

Thanks for your interest in contributing.

## Setup

```bash
git clone https://github.com/zongmin-yu/semantic-scholar-skills.git
cd semantic-scholar-skills
pip install -e '.[test]'
```

## Running Tests

```bash
# All offline tests
pytest -m "not live" -q

# Specific test suite
pytest tests/engine/ -q
pytest tests/contract/ -q
```

## Skill Bundles

If you modify `engine/`, `standalone/`, or `skills-src/`, regenerate the bundles:

```bash
python scripts/bundle_skills.py
python scripts/check_bundle_drift.py  # CI runs this too
```

## Pull Requests

1. Fork and create a feature branch
2. Make your changes
3. Ensure `pytest -m "not live" -q` passes
4. Ensure `python scripts/check_bundle_drift.py` passes
5. Open a PR against `main`

## Reporting Issues

Please include:
- What you tried (command, code snippet, or skill invocation)
- What happened vs. what you expected
- Python version and OS
