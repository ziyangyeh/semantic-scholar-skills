from __future__ import annotations

from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_ci_workflow_tests_all_supported_python_versions() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert re.search(r'python-version:\s*\["3\.10",\s*"3\.11",\s*"3\.12"\]', workflow)
    assert "Set up Python ${{ matrix.python-version }}" in workflow
    assert "python-version: ${{ matrix.python-version }}" in workflow
