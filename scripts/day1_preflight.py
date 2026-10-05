"""Gate del Day 1 per Asclepius.

Verifica, senza rete e senza dipendenze, che l'intake in docs/day-1.md sia
completo prima di scrivere codice di prodotto, e che nel workspace non siano
presenti segreti o artefatti da non pubblicare.

Uso:
    python scripts/day1_preflight.py

Codici di uscita:
    0 intake completo e nessun segreto rilevato
    1 intake incompleto (stampa i campi mancanti)
    2 intake illeggibile o intake non conforme alla struttura prevista

    Opzioni:
    --intake PATH    valida un altro documento intake (es. una bozza da revisionare)
    --skip-secrets   valida solo l'intake, senza scansione dei segreti
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INTAKE_DOC = REPO_ROOT / "docs" / "day-1.md"
INTAKE_FENCE_RE = re.compile(r"^```text intake\s*$(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
PLACEHOLDER_VALUES = {"", "-", "n/a", "na", "tbd", "todo", "da compilare", "non ancora", "?"}

REQUIRED_FIELDS: tuple[str, ...] = (
    "TRACK",
    "PROMPT_SOURCE",
    "PROMPT_SUMMARY",
    "PROBLEM",
    "TARGET_USER",
    "CURRENT_WORKFLOW",
    "PAIN_POINT",
    "INPUT_DATA",
    "AI_ROLE",
    "WHY_AI",
    "OUTPUT",
    "DECISION_OR_ACTION",
    "IMPACT_MEASURED",
    "MVP_SCOPE",
    "WOW_MOMENT",
    "REQUISITES_TRACE",
    "DATA_PERMISSION",
    "ALTERNATIVES",
    "SELECTION_RATIONALE",
    "API_CONTRACT",
    "DATA_MODEL",
    "TEST_STRATEGY",
    "RISKS",
)

# Campi che devono restare strutturati: una risposta sola e breve non basta.
MIN_LENGTH: dict[str, int] = {
    "PROMPT_SUMMARY": 80,
    "PROBLEM": 60,
    "TARGET_USER": 30,
    "WHY_AI": 80,
    "ALTERNATIVES": 200,
    "SELECTION_RATIONALE": 120,
    "REQUISITES_TRACE": 80,
    "TEST_STRATEGY": 60,
    "RISKS": 40,
}

SKIP_DIRS = {
    ".git", ".venv", "node_modules", "dist", ".npm-cache", ".pip-cache",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".freebuff", "coverage",
}
SECRET_NAME_RE = re.compile(r"^\.env(?!\.example$)")
# I prefissi come AI_API_KEY o X-ACCESS-TOKEN contengono separatori che impediscono
# a \b di trovare l'inizio del nome, quindi il prefisso viene consumato esplicitamente.
SECRET_CONTENT_RE = re.compile(
    r"(?i)(?:[A-Za-z0-9]+[_-])*"
    r"(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passwd)"
    r"\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"
)
TEXT_SUFFIXES = {
    ".py", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".json", ".md", ".txt",
    ".yml", ".yaml", ".toml", ".cfg", ".ini", ".sh", ".env", ".example",
}
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".pdf", ".zip"}


def parse_intake(doc_text: str) -> dict[str, str]:
    """Estrae il blocco ```text intake``` come dizionario chiave -> valore."""
    match = INTAKE_FENCE_RE.search(doc_text)
    if match is None:
        raise ValueError("docs/day-1.md non contiene un blocco '```text intake'")
    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError(f"riga non conforme all'intake: {raw_line!r}")
        key, _, value = line.partition(":")
        key = key.strip().upper()
        if not key or key in fields:
            raise ValueError(f"chiave intake vuota o duplicata: {key!r}")
        fields[key] = value.strip()
    return fields


def check_intake(fields: dict[str, str]) -> list[str]:
    problems: list[str] = []
    for name in REQUIRED_FIELDS:
        if name not in fields:
            problems.append(f"{name}: campo mancante dal blocco intake")
            continue
        value = fields[name]
        if value.lower() in PLACEHOLDER_VALUES:
            problems.append(f"{name}: ancora da compilare")
            continue
        minimum = MIN_LENGTH.get(name)
        if minimum is not None and len(value) < minimum:
            problems.append(f"{name}: troppo breve ({len(value)} caratteri, minimo {minimum})")
    unknown = sorted(set(fields) - set(REQUIRED_FIELDS))
    if unknown:
        problems.append(f"chiavi non previste nell'intake: {', '.join(unknown)}")
    return problems


def iter_project_files() -> list[Path]:
    files: list[Path] = []
    for directory, names, filenames in os.walk(REPO_ROOT):
        names[:] = [name for name in names if name not in SKIP_DIRS]
        for name in filenames:
            path = Path(directory) / name
            if SECRET_NAME_RE.match(name) or path.suffix.lower() in TEXT_SUFFIXES:
                files.append(path)
    return files


def check_secrets_and_artifacts() -> list[str]:
    findings: list[str] = []
    for path in iter_project_files():
        try:
            relative = path.relative_to(REPO_ROOT)
        except ValueError:  # pragma: no cover - difensivo
            continue
        if SECRET_NAME_RE.match(path.name):
            findings.append(f"{relative}: file .env presente nel workspace, non deve essere pubblicato")
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_number, line in enumerate(content.splitlines(), start=1):
            match = SECRET_CONTENT_RE.search(line)
            if match is None:
                continue
            # Le chiavi documentate come segreto devono restare vuote o con placeholder.
            if "<" in line or "SecretStr" in line or "get_secret_value" in line:
                continue
            findings.append(
                f"{relative}:{line_number}: possibile segreto ({match.group(1)} valorizzato)"
            )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate Day 1 per Asclepius.")
    parser.add_argument(
        "--skip-secrets",
        action="store_true",
        help="valida solo l'intake, senza scansione dei segreti",
    )
    parser.add_argument(
        "--intake",
        type=Path,
        default=INTAKE_DOC,
        help="percorso alternativo del documento intake (default: docs/day-1.md)",
    )
    arguments = parser.parse_args(argv)
    intake_doc: Path = arguments.intake

    if not intake_doc.is_file():
        print(f"ERRORE: intake non trovato in {intake_doc}", file=sys.stderr)
        return 2

    try:
        fields = parse_intake(intake_doc.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"ERRORE: intake non conforme: {error}", file=sys.stderr)
        return 2

    intake_problems = check_intake(fields)
    secret_findings = [] if arguments.skip_secrets else check_secrets_and_artifacts()

    if intake_problems or secret_findings:
        print("DAY 1 NON COMPLETATO")
        if intake_problems:
            print(f"\nIntake ({intake_doc}): {len(intake_problems)} problemi")
            for problem in intake_problems:
                print(f"  - {problem}")
            print(
                "\nCompila docs/day-1.md con dati reali del prompt ufficiale.\n"
                "Non iniziare il codice di prodotto finche questo gate non e' verde."
            )
        if secret_findings:
            print(f"\nSegreti rilevati: {len(secret_findings)}")
            for finding in secret_findings:
                print(f"  - {finding}")
            print(
                "\nNon pubblicare segreti. I file .env locali devono restare ignorati; revisiona i file effettivamente condivisi.\n"
                "Se un valore e' un segnaposto, usa un placeholder vuoto o <...> invece."
            )
        return 1

    print("DAY 1: intake strutturalmente completo.")
    print(f"  campi validati: {len(REQUIRED_FIELDS)}")
    if arguments.skip_secrets:
        print("  scansione dei segreti saltata (--skip-secrets); nessuna valutazione dei segreti eseguita")
    else:
        print("  scansione euristica: nessun candidato rilevato; non certifica assenza di segreti")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())