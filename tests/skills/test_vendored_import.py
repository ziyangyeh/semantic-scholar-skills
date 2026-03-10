from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import types

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_SCRIPT = REPO_ROOT / "scripts" / "bundle_skills.py"


def build_bundle(output_dir: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(BUNDLE_SCRIPT), "--output-dir", str(output_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def load_module(module_path: Path, module_name: str):
    for name in (module_name, "_shared", "_shared.launcher"):
        sys.modules.pop(name, None)
    sys.path[:] = [
        entry
        for entry in sys.path
        if not entry.replace("\\", "/").endswith("/_vendor")
    ]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_import_vendored_runtime_loads_from_bundle(tmp_path) -> None:
    output_dir = tmp_path / "skills"
    build_bundle(output_dir)

    launcher = load_module(
        output_dir / "trace-citations" / "scripts" / "_shared" / "launcher.py",
        "trace_citations_launcher_vendored",
    )
    module = launcher._import_vendored_runtime()

    module_path = Path(module.__file__).resolve()
    assert module.__name__ == "semantic_scholar_skills.standalone"
    assert "_vendor" in module_path.as_posix()
    assert module_path == (
        output_dir
        / "trace-citations"
        / "scripts"
        / "_vendor"
        / "semantic_scholar_skills"
        / "standalone"
        / "__init__.py"
    ).resolve()


def test_launch_uses_vendored_runtime_when_bundle_is_present(monkeypatch, tmp_path) -> None:
    output_dir = tmp_path / "skills"
    build_bundle(output_dir)

    launcher = load_module(
        output_dir / "paper-triage" / "scripts" / "_shared" / "launcher.py",
        "paper_triage_launcher_prefers_vendored",
    )

    class FakeResult:
        def to_dict(self) -> dict[str, object]:
            return {"shortlist": [{"paper": {"paper_id": "p-1", "title": "Example Paper"}}]}

    async def fake_run_workflow(workflow: str, **kwargs):
        return FakeResult()

    vendored_module = types.SimpleNamespace(
        __name__="semantic_scholar_skills.standalone",
        __file__="/tmp/fake-vendor/semantic_scholar_skills/standalone/__init__.py",
        run_workflow=fake_run_workflow,
    )

    def fail_installed():
        raise AssertionError("_import_installed_runtime should not be called when vendored bundle exists")

    monkeypatch.setattr(launcher, "_import_vendored_runtime", lambda: vendored_module)
    monkeypatch.setattr(launcher, "_import_installed_runtime", fail_installed)

    outcome = launcher.launch("paper-triage", query="bert")

    assert outcome.exit_code == 0
    assert outcome.payload["status"] == "ok"
    assert outcome.payload["runtime"]["mode"] == "vendored"
    assert outcome.payload["runtime"]["path"] == vendored_module.__file__
    assert outcome.payload["result"]["shortlist"][0]["paper"]["paper_id"] == "p-1"


def test_load_runtime_raises_when_vendored_bundle_exists_but_is_broken(monkeypatch, tmp_path) -> None:
    output_dir = tmp_path / "skills"
    build_bundle(output_dir)

    launcher = load_module(
        output_dir / "paper-triage" / "scripts" / "_shared" / "launcher.py",
        "paper_triage_launcher_broken_vendor",
    )

    def fail_vendored():
        raise ImportError("broken vendored runtime")

    installed_module = types.SimpleNamespace(
        __name__="semantic_scholar_skills.standalone",
        __file__="/tmp/fake-installed/semantic_scholar_skills/standalone/__init__.py",
    )

    monkeypatch.setattr(launcher, "_import_vendored_runtime", fail_vendored)
    monkeypatch.setattr(launcher, "_import_installed_runtime", lambda: installed_module)

    with pytest.raises(RuntimeError) as excinfo:
        launcher.load_runtime()

    assert "Vendored Semantic Scholar standalone runtime is present but failed to import" in str(
        excinfo.value
    )
