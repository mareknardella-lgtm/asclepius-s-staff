from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from evaluate_care import load_cases, main


def test_corpus_has_preannotated_synthetic_cases() -> None:
    data = load_cases()
    assert len(data["plan_cases"]) == 20
    assert len(data["teach_back_cases"]) == 30
    assert all("SYNTHETIC" in case["text"] for case in data["plan_cases"])


def test_validator_does_not_call_a_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["evaluate_care.py", "--validate-only"])
    assert main() == 0


def test_live_evaluation_rejects_mock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setattr(sys, "argv", ["evaluate_care.py", "--run", "--output", str(tmp_path / "result.json")])
    assert main() == 2
    assert not (tmp_path / "result.json").exists()
