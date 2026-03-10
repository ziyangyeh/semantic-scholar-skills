from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_SCRIPT = REPO_ROOT / "scripts" / "bundle_skills.py"
DRIFT_SCRIPT = REPO_ROOT / "scripts" / "check_bundle_drift.py"
SKILL_NAMES = ("expand-references", "trace-citations", "paper-triage")


def run_bundle(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BUNDLE_SCRIPT), "--output-dir", str(output_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_drift_check(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DRIFT_SCRIPT), "--output-dir", str(output_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def build_wheel(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "--wheel-dir", str(output_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_bundle_script_materializes_expected_skill_tree(tmp_path) -> None:
    output_dir = tmp_path / "skills"
    completed = run_bundle(output_dir)

    assert completed.returncode == 0, completed.stderr
    for skill_name in SKILL_NAMES:
        skill_dir = output_dir / skill_name
        skill_doc = skill_dir / "SKILL.md"
        run_script = skill_dir / "scripts" / "run.py"
        assert skill_doc.is_file()
        assert (skill_dir / "reference.md").is_file()
        assert (skill_dir / "examples.md").is_file()
        assert (skill_dir / "output_contract.md").is_file()
        assert run_script.is_file()
        assert (skill_dir / "scripts" / "_shared" / "launcher.py").is_file()
        assert (
            skill_dir
            / "scripts"
            / "_vendor"
            / "semantic_scholar_skills"
            / "standalone"
            / "entrypoint.py"
        ).is_file()
        skill_doc_text = skill_doc.read_text(encoding="utf-8")
        run_script_text = run_script.read_text(encoding="utf-8")
        assert "context: fork" in skill_doc_text
        assert "agent: Explore" in skill_doc_text
        assert "disable-model-invocation: true" in skill_doc_text
        assert "asyncio.run(" in run_script_text


def test_bundle_patches_vendored_core_init_to_avoid_transport_exports(tmp_path) -> None:
    output_dir = tmp_path / "skills"
    completed = run_bundle(output_dir)

    assert completed.returncode == 0, completed.stderr
    vendored_core_init = (
        output_dir
        / "expand-references"
        / "scripts"
        / "_vendor"
        / "semantic_scholar_skills"
        / "core"
        / "__init__.py"
    ).read_text(encoding="utf-8")

    assert "transport" not in vendored_core_init
    assert "SupportsRequestJson" in vendored_core_init
    assert "PaperRecommendationsMultiRequest" in vendored_core_init


def test_check_bundle_drift_reports_manual_edits(tmp_path) -> None:
    output_dir = tmp_path / "skills"
    completed = run_bundle(output_dir)

    assert completed.returncode == 0, completed.stderr

    clean = run_drift_check(output_dir)
    assert clean.returncode == 0, clean.stdout + clean.stderr

    edited_file = output_dir / "paper-triage" / "reference.md"
    edited_file.write_text(edited_file.read_text(encoding="utf-8") + "\nManual drift.\n", encoding="utf-8")

    dirty = run_drift_check(output_dir)
    assert dirty.returncode == 1
    assert "paper-triage/reference.md" in (dirty.stdout + dirty.stderr)


def test_wheel_excludes_repo_only_skill_assets(tmp_path) -> None:
    wheel_dir = tmp_path / "wheel"
    completed = build_wheel(wheel_dir)

    assert completed.returncode == 0, completed.stderr

    [wheel_path] = wheel_dir.glob("semantic_scholar_skills-*.whl")
    with ZipFile(wheel_path) as archive:
        names = archive.namelist()

    assert not any(name.startswith("skills/") for name in names)
    assert not any(name.startswith("scripts/") for name in names)
    assert not any(name.startswith("tests/") for name in names)


def test_readme_documents_skills_as_repo_only_assets() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "not included in the published wheel" in readme
    assert "clone the repository or copy a generated bundle" in readme
