import json
from typing import Any, Literal, Protocol

import httpx

from app.config import Settings
from app.ai.fixtures import CORRECT_ANSWER, DEMO_SOURCE, EDITORIAL_SOURCE, INCORRECT_ANSWER, SECOND_SOURCE
from app.ai.rules import build_plan, compare_answer
from app.ai.schemas import Focus, SourceSegment

# Which engine produced a result. Surfaced in the API and in the UI so nobody
# reads deterministic output as a model assessment.
Origin = Literal["scripted_fixture", "local_rules", "model"]


class ProviderError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class AIProvider(Protocol):
    async def generate(self, system_prompt: str, user_prompt: str) -> str: ...

    def origin(self, task: str, source_text: str) -> Origin: ...


def _segments(payload: dict[str, Any]) -> list[SourceSegment]:
    return [SourceSegment(id=item["id"], text=item["text"]) for item in payload["source_segments"]]


class MockProvider:
    """Offline engine: labeled fixtures for the demo, transparent rules otherwise.

    Nothing here is an AI assessment. Free-text output comes from
    `app.ai.rules`, which only rewrites and compares text it was given.
    """

    def origin(self, task: str, source_text: str) -> Origin:
        if source_text in {DEMO_SOURCE, EDITORIAL_SOURCE, SECOND_SOURCE}:
            return "scripted_fixture"
        return "local_rules"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = json.loads(user_prompt)
        segments = _segments(payload)
        source = "\n".join(segment.text for segment in segments)
        if payload["task"] == "teach_back":
            focus = Focus.model_validate(payload["focus"])
            preset: tuple[str, str] | None = None
            expected_id = "s4" if source == EDITORIAL_SOURCE else "s2"
            if source in {DEMO_SOURCE, EDITORIAL_SOURCE} and [reference.model_dump() for reference in focus.evidence] == [{"segment_id": expected_id, "quote": "Arrange a follow-up within seven days, even if you feel better."}]:
                if payload["untrusted_answer"] == INCORRECT_ANSWER:
                    preset = ("needs_clarification", "The note says to arrange the follow-up within seven days even if you feel better, not only if you feel unwell. This example was written in advance; no AI looked at it.")
                elif payload["untrusted_answer"] == CORRECT_ANSWER:
                    preset = ("matched", "You kept the seven days and the ‘even if you feel better’ part. This example was written in advance; no AI looked at it, and wording is not the same as understanding the advice.")
            if preset is not None:
                status, feedback = preset
                return json.dumps({"focus_id": focus.id, "status": status, "feedback": feedback, "evidence": [reference.model_dump() for reference in focus.evidence]})
            return json.dumps(compare_answer(focus, payload["untrusted_answer"]))
        steps = {
            DEMO_SOURCE: [("Arrange a follow-up within seven days, even if you feel better.", "Arrange your follow-up within seven days, including if you feel better."), ("Bring your discharge instructions to that visit.", "Take your discharge instructions to the follow-up visit.")],
            EDITORIAL_SOURCE: [("Arrange a follow-up within seven days, even if you feel better.", "Arrange your follow-up within seven days, even if you feel better."), ("Bring your discharge instructions to that visit.", "Take your discharge instructions to the follow-up visit.")],
            SECOND_SOURCE: [("Call the clinic on Monday to confirm the appointment time.", "Call the clinic on Monday to check the appointment time."), ("Bring your appointment letter to the visit.", "Take your appointment letter to the visit.")],
        }.get(source)
        if steps is None:
            return json.dumps(build_plan(segments))
        items: list[dict[str, Any]] = []
        for index, (quote, instruction) in enumerate(steps):
            segment = next(segment for segment in segments if quote in segment.text)
            items.append({"id": f"step-{index + 1}", "instruction": instruction, "evidence": [{"segment_id": segment.id, "quote": quote}]})
        clarifications: list[dict[str, Any]] = []
        if source == EDITORIAL_SOURCE:
            clarifications.extend([
                {"description": "The appointment date and time are not given. Ask the follow-up service to confirm them.", "evidence": [{"segment_id": "s6", "quote": "The follow-up service will confirm the appointment date."}]},
                {"description": "The note names a medicine and some test results, but it does not say how much to take or when. Asclepius cannot work that out. Ask the care team.", "evidence": [{"segment_id": "s7", "quote": "Medication listed in this fictional record: atorvastatin 20 mg. No dosing schedule is provided."}]},
            ])
        else:
            clarifications.append({"description": "This is a practice example, not real advice. It does not give an appointment time.", "evidence": []})
        return json.dumps({"summary": "A practice example. Each step is a line from the note, shown next to its original wording. No AI model looked at this document.", "items": items, "clarifications": clarifications, "questions_for_care_team": ["How can I confirm my appointment details?"]})


class OpenAICompatibleProvider:
    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client

    def origin(self, task: str, source_text: str) -> Origin:
        return "model"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = await self.client.post(
                f"{self.settings.ai_base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.ai_api_key.get_secret_value()}"},
                json={
                    "model": self.settings.ai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0,
                    "max_tokens": self.settings.ai_max_output_tokens,
                    "response_format": {"type": "json_object"},
                },
                timeout=self.settings.ai_timeout_seconds,
            )
        except httpx.TimeoutException as exc:
            raise ProviderError("provider_timeout", "The provider did not respond in time.", 504) from exc
        except httpx.HTTPError as exc:
            raise ProviderError("provider_unavailable", "The provider could not be reached.") from exc
        if response.status_code == 429:
            raise ProviderError("provider_rate_limit", "Provider rate limit reached. Try again later.", 429)
        if response.is_error:
            raise ProviderError("provider_failure", "The provider could not complete the request.")
        # Limit the JSON envelope before parsing; max_tokens limits model output too.
        if len(response.content) > 100_000:
            raise ProviderError("invalid_response", "The provider response was too large.")
        try:
            data = response.json()
            choice = data["choices"][0]
            if choice.get("finish_reason") not in {None, "stop"}:
                raise ValueError("Incomplete response")
            content = choice["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Missing text content")
        except (ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
            raise ProviderError("invalid_response", "The provider returned an invalid or incomplete response.") from exc
        return content