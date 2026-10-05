from pathlib import Path
import shutil
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import dev as launcher

VENV_PYTHON = Path("backend/.venv/Scripts/python.exe" if sys.platform == "win32" else "backend/.venv/bin/python")


def test_minimum_python_matches_backend_requirements() -> None:
    assert launcher.MIN_PYTHON == (3, 12)


@pytest.mark.parametrize(
    ("version", "expected"),
    [((3, 11), False), ((3, 12), True), ((3, 14), True), ((4, 0), True)],
)
def test_supports_backend(version: tuple[int, int], expected: bool) -> None:
    assert launcher.supports_backend(version) is expected


def test_interpreter_version_reads_project_venv() -> None:
    version = launcher.interpreter_version(Path(__file__).resolve().parents[2] / VENV_PYTHON)
    assert version is not None
    assert launcher.supports_backend(version)


def test_interpreter_version_reports_none_for_non_interpreter(tmp_path: Path) -> None:
    fake = tmp_path / "not-python.txt"
    fake.write_text("plain text, not an interpreter", encoding="utf-8")
    assert launcher.interpreter_version(fake) is None


def test_launcher_refuses_old_venv_with_actionable_message(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    venv_python = tmp_path / "backend" / ".venv" / "Scripts" / "python.exe"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("", encoding="utf-8")
    vite = tmp_path / "frontend" / "node_modules" / "vite" / "bin" / "vite.js"
    vite.parent.mkdir(parents=True)
    vite.write_text("", encoding="utf-8")
    monkeypatch.setattr(launcher, "ROOT", tmp_path)
    monkeypatch.setattr(launcher, "interpreter_version", lambda _path: (3, 9))
    monkeypatch.setattr(shutil, "which", lambda _name: "node")
    monkeypatch.setattr(launcher, "port_available", lambda _port: True)
    assert launcher.main(["--api-port", "8301", "--web-port", "5371"]) == 1
    error = capsys.readouterr().err
    assert "Python 3.9" in error
    assert "3.12" in error
    assert "py -3.12 -m venv backend/.venv" in error


def test_launcher_reports_unreadable_interpreter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    venv_python = tmp_path / "backend" / ".venv" / "Scripts" / "python.exe"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("", encoding="utf-8")
    vite = tmp_path / "frontend" / "node_modules" / "vite" / "bin" / "vite.js"
    vite.parent.mkdir(parents=True)
    vite.write_text("", encoding="utf-8")
    monkeypatch.setattr(launcher, "ROOT", tmp_path)
    monkeypatch.setattr(launcher, "interpreter_version", lambda _path: None)
    monkeypatch.setattr(shutil, "which", lambda _name: "node")
    monkeypatch.setattr(launcher, "port_available", lambda _port: True)
    assert launcher.main(["--api-port", "8302", "--web-port", "5372"]) == 1
    assert "could not be started" in capsys.readouterr().err


def test_launcher_rejects_equal_ports_without_touching_them(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(launcher, "port_available", lambda _port: True)
    with pytest.raises(SystemExit):
        launcher.main(["--api-port", "8303", "--web-port", "8303"])


def test_launcher_refuses_occupied_port(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(launcher, "port_available", lambda port: port != 8304)
    assert launcher.main(["--api-port", "8304", "--web-port", "5374"]) == 1
    assert "occupied" in capsys.readouterr().err