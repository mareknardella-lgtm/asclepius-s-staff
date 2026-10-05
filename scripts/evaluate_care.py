"""Validate synthetic corpus or explicitly run a real-provider evaluation.

From the workspace root:
    backend/.venv/Scripts/python.exe scripts/evaluate_care.py --validate-only
    backend/.venv/Scripts/python.exe scripts/evaluate_care.py --run --output reports/live-evaluation.json

--run makes 50 paid/provider requests (20 plans, 30 comparisons), without retries.
Plan semantic correctness requires human review; this script does not score it.
"""
from __future__ import annotations

import argparse
import asyncio
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

import httpx
from app.ai.prompts import PROMPT_VERSION, TEACH_BACK_VERSION
from app.ai.provider import OpenAICompatibleProvider, ProviderError
from app.ai.schemas import AnalyzeRequest, TeachBackRequest
from app.ai.service import AIService
from app.config import Settings

CORPUS = ROOT / "backend" / "tests" / "care_cases.json"


def load_cases(path: Path = CORPUS) -> dict[str, Any]:
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != "care-eval-v1":
        raise ValueError("Unsupported evaluation schema")
    plans, comparisons = data["plan_cases"], data["teach_back_cases"]
    if len(plans) != 20 or len(comparisons) != 30:
        raise ValueError("Expected 20 plan cases and 30 teach-back cases")
    ids = [case["id"] for case in plans + comparisons]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate case IDs")
    for case in plans:
        AnalyzeRequest.model_validate({"text": case["text"], "synthetic_data_confirmed": True})
        if not case["required"] or not case["forbidden"]:
            raise ValueError("Every plan case needs a predeclared semantic rubric")
    for case in comparisons:
        TeachBackRequest.model_validate({
            "text": case["source"], "synthetic_data_confirmed": True,
            "focus": {"id": case["id"], "evidence": [{"segment_id": "s1", "quote": case["quote"]}]},
            "answer": case["answer"],
        })
    counts = Counter(case["expected"] for case in comparisons)
    if counts != {"matched": 10, "needs_clarification": 10, "unable_to_assess": 10}:
        raise ValueError("Expected ten cases for each assessment status")
    return data


async def evaluate(data: dict[str, Any], config: Settings) -> dict[str, Any]:
    outcomes: list[dict[str, Any]] = []
    async with httpx.AsyncClient(follow_redirects=False) as client:
        service = AIService(OpenAICompatibleProvider(config, client))
        for kind, cases in (("plan", data["plan_cases"]), ("teach_back", data["teach_back_cases"])):
            for case in cases:
                start = perf_counter()
                row: dict[str, Any] = {"id": case["id"], "kind": kind}
                try:
                    if kind == "plan":
                        plan_request = AnalyzeRequest.model_validate({"text": case["text"], "synthetic_data_confirmed": True})
                        row["result"] = (await service.analyze(plan_request)).model_dump()
                        row["semantic_review"] = {"status": "not_reviewed", "required": case["required"], "forbidden": case["forbidden"]}
                    else:
                        comparison_request = TeachBackRequest.model_validate({"text": case["source"], "synthetic_data_confirmed": True, "focus": {"id": case["id"], "evidence": [{"segment_id": "s1", "quote": case["quote"]}]}, "answer": case["answer"]})
                        result = await service.teach_back(comparison_request)
                        row["result"] = result.model_dump()
                        row["expected"] = case["expected"]
                        row["label_matches"] = result.status == case["expected"]
                    row["outcome"] = "accepted"
                except ProviderError as exc:
                    row.update(outcome="error", error_code=exc.code)
                    print(f'{case["id"]}: {exc.code}', file=sys.stderr)
                row["elapsed_ms"] = round((perf_counter() - start) * 1000)
                outcomes.append(row)
                print(f'{case["id"]}: {row["outcome"]} ({row["elapsed_ms"]} ms)')
    comparisons = [row for row in outcomes if row["kind"] == "teach_back"]
    correct = sum(row.get("label_matches") is True for row in comparisons)
    false_matches = sum(row.get("result", {}).get("status") == "matched" and row.get("expected") != "matched" for row in comparisons)
    return {
        "schema_version": "care-eval-report-v1", "created_at": datetime.now(timezone.utc).isoformat(),
        "provider": config.ai_provider, "model": config.ai_model, "is_mock": False,
        "prompt_versions": [PROMPT_VERSION, TEACH_BACK_VERSION], "corpus_version": data["schema_version"],
        "summary": {"requests": len(outcomes), "provider_or_validation_errors": sum(row["outcome"] == "error" for row in outcomes), "teach_back_correct": correct, "teach_back_total": 30, "false_matched": false_matches, "plan_semantics": "not reviewed"},
        "limitations": "Single run on authored synthetic cases. No baseline, usability or clinical validation. Plan semantics need human review. Schema/citation acceptance is not semantic correctness.",
        "cases": outcomes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--validate-only", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "live-evaluation.json")
    args = parser.parse_args()
    try:
        data = load_cases()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Invalid corpus: {exc}", file=sys.stderr)
        return 2
    if args.validate_only:
        print("PASS: 20 synthetic plan rubrics, 30 grounded teach-back requests, 10 labels per status. No provider called.")
        return 0
    try:
        config = Settings()
    except ValueError:
        print("Invalid provider configuration; check backend environment settings.", file=sys.stderr)
        return 2
    if config.ai_provider != "openai":
        print("Live evaluation requires a configured real provider. Mock fixtures cannot measure AI quality.", file=sys.stderr)
        return 2
    if args.output.exists():
        print("Output already exists; choose a new path to preserve earlier measurements.", file=sys.stderr)
        return 2
    report = asyncio.run(evaluate(data, config))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {args.output}")
    summary = report["summary"]
    return 1 if summary["provider_or_validation_errors"] or summary["teach_back_correct"] != 30 else 0


if __name__ == "__main__":
    raise SystemExit(main())
