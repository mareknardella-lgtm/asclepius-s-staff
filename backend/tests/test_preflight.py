from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import day1_preflight as gate


def test_scanner_includes_extensionless_env_and_prunes_dependencies(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("AI_API_KEY=\n", encoding="utf-8")
    (tmp_path / ".env.local").write_text("AI_API_KEY=\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("AI_API_KEY=\n", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    # Build a clearly fake assignment in the temporary ignored directory, not a
    # secret-shaped literal in publication files. The scanner must prune it.
    fake_assignment = "AI_API_KEY=" + "fake-test-value-only" + "\n"
    (tmp_path / "node_modules" / "private.md").write_text(fake_assignment, encoding="utf-8")
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    files = gate.iter_project_files()
    assert {file.name for file in files} == {".env", ".env.local", ".env.example"}
    findings = gate.check_secrets_and_artifacts()
    assert len(findings) == 2
    assert all("file .env" in finding for finding in findings)


def test_intake_real_and_skip_message(capsys: pytest.CaptureFixture[str]) -> None:
    assert gate.main(["--skip-secrets"]) == 0
    output = capsys.readouterr().out
    assert "nessuna valutazione" in output
    assert "nessun candidato rilevato" not in output


def test_duplicate_and_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValueError):
        gate.parse_intake("```text intake\nTRACK: one\nTRACK: two\n```\n")
    fields = gate.parse_intake(gate.INTAKE_DOC.read_text(encoding="utf-8"))
    fields["UNEXPECTED"] = "value"
    assert any("non previste" in issue for issue in gate.check_intake(fields))
