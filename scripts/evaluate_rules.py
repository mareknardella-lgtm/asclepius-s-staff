"""Measure the deterministic engine on the synthetic corpus.

    python scripts/evaluate_rules.py [--json]

Reports grounding, safety and label outcomes for the rule engine alone. It makes
no network call, so it separates "the rules work on these documents" from "a
model would agree" — a different claim that still needs real-model review.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.ai import rules  # noqa: E402
from app.ai.schemas import Evidence, Focus, PlanDraft, TeachBackResult, segment_source  # noqa: E402

CASES = ROOT / "backend" / "tests" / "care_cases.json"
MEDICATION = ("mg", "mcg", "milligram", "twice daily", "once daily", "dosage", "dose of")


def load_cases(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "care-eval-v1":
        raise SystemExit(f"unexpected corpus schema in {path}")
    return data


def evaluate_plans(data: dict[str, Any]) -> dict[str, Any]:
    total = grounded = contract_valid = no_medication_steps = 0
    details: list[dict[str, Any]] = []
    for case in data["plan_cases"]:
        total += 1
        segments = segment_source(case["text"])
        draft = rules.build_plan(segments)
        problems: list[str] = []
        try:
            PlanDraft.model_validate(draft, strict=True)
            contract_valid += 1
        except ValueError as exc:
            problems.append(f"contract: {exc}")
        sources = {segment.id: segment.text for segment in segments}
        cited = [reference for item in draft["items"] for reference in item["evidence"]]
        cited += [reference for clarification in draft["clarifications"] for reference in clarification["evidence"]]
        if all(reference["quote"] in sources.get(reference["segment_id"], "") for reference in cited):
            grounded += 1
        else:
            problems.append("ungrounded citation")
        instructions = " ".join(item["instruction"] for item in draft["items"]).lower()
        if not any(cue in instructions for cue in MEDICATION):
            no_medication_steps += 1
        else:
            problems.append("medication wording became a step")
        details.append({"id": case["id"], "category": case["category"], "steps": len(draft["items"]), "problems": problems})
    return {
        "cases": total,
        "contract_valid": contract_valid,
        "grounded": grounded,
        "no_medication_steps": no_medication_steps,
        "details": details,
    }


def evaluate_comparisons(data: dict[str, Any]) -> dict[str, Any]:
    labels = ("matched", "needs_clarification", "unable_to_assess")
    matrix = {expected: {predicted: 0 for predicted in labels} for expected in labels}
    misses: list[dict[str, str]] = []
    for case in data["teach_back_cases"]:
        quote = case.get("quote") or case["source"]
        result = TeachBackResult.model_validate(
            rules.compare_answer(Focus(id="step-1", evidence=[Evidence(segment_id="s1", quote=quote)]), case["answer"]), strict=True
        )
        matrix[case["expected"]][result.status] += 1
        if result.status != case["expected"]:
            misses.append({"id": case["id"], "expected": case["expected"], "got": result.status})
    correct = sum(matrix[label][label] for label in labels)
    return {"cases": sum(sum(row.values()) for row in matrix.values()), "correct": correct, "matrix": matrix, "misses": misses}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable results")
    parser.add_argument("--corpus", type=Path, default=CASES)
    args = parser.parse_args(argv)
    data = load_cases(args.corpus)
    plans = evaluate_plans(data)
    comparisons = evaluate_comparisons(data)
    if args.json:
        print(json.dumps({"plans": plans, "comparisons": comparisons}, indent=2))
    else:
        print(f"Plan cases: {plans['cases']}")
        print(f"  contract valid     {plans['contract_valid']}/{plans['cases']}")
        print(f"  grounded quotes    {plans['grounded']}/{plans['cases']}")
        print(f"  no medication steps {plans['no_medication_steps']}/{plans['cases']}")
        print(f"Comparison cases: {comparisons['cases']}  exact-label match {comparisons['correct']}")
        for expected, row in comparisons["matrix"].items():
            print(f"  expected {expected:20} " + " ".join(f"{predicted}={count}" for predicted, count in row.items()))
        for miss in comparisons["misses"]:
            print(f"  miss {miss['id']}: expected {miss['expected']}, got {miss['got']}")
    return 0 if plans["grounded"] == plans["cases"] and plans["no_medication_steps"] == plans["cases"] else 1


if __name__ == "__main__":
    raise SystemExit(main())