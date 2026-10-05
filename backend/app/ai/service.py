import json
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.ai.prompts import SYSTEM_PROMPT, TEACH_BACK_PROMPT, build_teach_back_prompt, build_user_prompt
from app.ai.provider import AIProvider, Origin, ProviderError
from app.ai.schemas import (
    AnalyzeRequest, CarePlan, PlanDraft, TeachBackRequest, TeachBackResult,
    evidence_matches, segment_source,
)

Result = TypeVar("Result", bound=BaseModel)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("Non-finite JSON number")


def parse_result(raw: str, schema: type[Result]) -> Result:
    if len(raw) > 20_000:
        raise ProviderError("invalid_ai_output", "The model output exceeded the allowed limit.")
    try:
        payload = json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
        return schema.model_validate(payload, strict=True)
    except (ValueError, TypeError, ValidationError, RecursionError) as exc:
        raise ProviderError("invalid_ai_output", "The model returned an invalid structured result.") from exc


class AIService:
    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    def origin(self, task: str, source_text: str) -> Origin:
        return self.provider.origin(task, source_text)

    async def analyze(self, request: AnalyzeRequest) -> CarePlan:
        raw = await self.provider.generate(SYSTEM_PROMPT, build_user_prompt(request))
        draft = parse_result(raw, PlanDraft)
        segments = segment_source(request.text)
        evidence = [reference for item in draft.items for reference in item.evidence]
        evidence.extend(reference for clarification in draft.clarifications for reference in clarification.evidence)
        if not evidence_matches(evidence, segments):
            raise ProviderError("ungrounded_output", "The engine cited text not found in the original instructions. No plan was accepted.")
        return CarePlan(**draft.model_dump(), source_segments=segments)

    async def teach_back(self, request: TeachBackRequest) -> TeachBackResult:
        raw = await self.provider.generate(TEACH_BACK_PROMPT, build_teach_back_prompt(request))
        result = parse_result(raw, TeachBackResult)
        if result.focus_id != request.focus.id or not evidence_matches(result.evidence, segment_source(request.text)):
            raise ProviderError("ungrounded_output", "The feedback did not match the selected source. No assessment was accepted.")
        # Assessments must cite the selected passages, not unrelated source lines.
        if any(not any(reference.segment_id == focus.segment_id and reference.quote in focus.quote
                       for focus in request.focus.evidence) for reference in result.evidence):
            raise ProviderError("ungrounded_output", "The feedback cited text outside the selected step.")
        return result
