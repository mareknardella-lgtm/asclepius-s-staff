"""Start the local synthetic-data demo: python scripts/dev.py.

Uses the existing backend venv and frontend node_modules, never installs packages.
Checks both ports before starting and terminates only its own subprocesses.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
# The backend uses PEP 604 annotations at runtime and the toolchain targets 3.12,
# so an older venv fails with an unrelated-looking TypeError instead of a clear message.
MIN_PYTHON = (3, 12)


def port_available(port: int) -> bool:
    with socket.socket() as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def interpreter_version(python: Path) -> tuple[int, int] | None:
    try:
        completed = subprocess.run([str(python), "-c", "import sys; print(sys.version_info[0], sys.version_info[1])"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    fields = completed.stdout.split()
    if completed.returncode != 0 or len(fields) != 2 or not all(field.isdigit() for field in fields):
        return None
    return int(fields[0]), int(fields[1])


def supports_backend(version: tuple[int, int]) -> bool:
    return version >= MIN_PYTHON


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--web-port", type=int, default=5173)
    parser.add_argument("--smoke-test", action="store_true", help="start, verify HTTP readiness, then stop both owned servers")
    args = parser.parse_args(argv)
    if args.api_port == args.web_port or any(not 1 <= port <= 65535 for port in (args.api_port, args.web_port)):
        parser.error("Use two different ports between 1 and 65535")
    for port in (args.api_port, args.web_port):
        if not port_available(port):
            print(f"Port {port} is occupied. No existing process was stopped.", file=sys.stderr)
            return 1
    python = ROOT / "backend" / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    node = shutil.which("node")
    vite = ROOT / "frontend" / "node_modules" / "vite" / "bin" / "vite.js"
    if not python.is_file() or not node or not vite.is_file():
        print("Install project-local dependencies using README instructions first.", file=sys.stderr)
        return 1
    version = interpreter_version(python)
    if version is None:
        print(f"backend/.venv interpreter could not be started: {python}. Recreate it with the README steps.", file=sys.stderr)
        return 1
    if not supports_backend(version):
        print(
            f"backend/.venv uses Python {version[0]}.{version[1]}; Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required. "
            f"Recreate the virtual environment with a {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ interpreter (README, Local setup), "
            f"for example on Windows: py -{MIN_PYTHON[0]}.{MIN_PYTHON[1]} -m venv backend/.venv",
            file=sys.stderr,
        )
        return 1
    env = {**os.environ, "API_PROXY_TARGET": f"http://127.0.0.1:{args.api_port}", "FRONTEND_ORIGIN": f"http://127.0.0.1:{args.web_port}"}
    processes: list[subprocess.Popen[bytes]] = []
    try:
        processes.append(subprocess.Popen([str(python), "-m", "uvicorn", "app.main:create_app", "--factory", "--host", "127.0.0.1", "--port", str(args.api_port)], cwd=ROOT / "backend", env=env))
        processes.append(subprocess.Popen([node, str(vite), "--host", "127.0.0.1", "--port", str(args.web_port)], cwd=ROOT / "frontend", env=env))
        print(f"Local demo: http://127.0.0.1:{args.web_port} — Ctrl+C stops only these servers.", flush=True)
        if args.smoke_test:
            deadline = time.monotonic() + 25
            urls = [f"http://127.0.0.1:{args.api_port}/health", f"http://127.0.0.1:{args.web_port}/", f"http://127.0.0.1:{args.web_port}/api/health"]
            pending = set(urls)
            while pending and time.monotonic() < deadline and all(process.poll() is None for process in processes):
                for url in list(pending):
                    try:
                        with urlopen(url, timeout=2) as response:
                            if response.status == 200:
                                pending.remove(url)
                    except OSError:
                        # Servers can be unavailable during startup; bounded polling,
                        # not a swallowed success. Remaining URLs fail the smoke test.
                        pass
                time.sleep(0.25)
            if pending:
                print(f"Readiness failed: {sorted(pending)}", file=sys.stderr)
                return 1
            print("PASS: backend, frontend and API proxy returned HTTP 200.")
            return 0
        while all(process.poll() is None for process in processes):
            time.sleep(0.5)
        print("A development server exited; stopping its companion.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
