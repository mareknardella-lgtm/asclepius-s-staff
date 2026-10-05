from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

SourceText = Annotated[str, StringConstraints(strict=True, min_length=20, max_length=4000)]
Identifier = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=40)]
Instruction = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=600)]
ShortText = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=300)]
Feedback = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=1000)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceSegment(StrictModel):
    id: Identifier
    text: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=4000)]


def segment_source(text: str) -> list[SourceSegment]:
    lines = [line for line in text.split("\n") if line.strip()]
    return [SourceSegment(id=f"s{index + 1}", text=line) for index, line in enumerate(lines)]


class AnalyzeRequest(StrictModel):
    text: SourceText
    synthetic_data_confirmed: bool = Field(strict=True)

    @field_validator("text", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return value.replace("\r\n", "\n").replace("\r", "\n").strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_consent_and_segments(self) -> "AnalyzeRequest":
        if not self.synthetic_data_confirmed:
            raise ValueError("Only synthetic data is allowed; confirmation is required")
        if len(segment_source(self.text)) > 80:
            raise ValueError("Use at most 80 non-empty lines")
        return self


class Evidence(StrictModel):
    segment_id: Identifier
    quote: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=4000)]

    @field_validator("quote")
    @classmethod
    def non_blank_quote(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Quote must not be blank")
        return value


class CareItem(StrictModel):
    id: Identifier
    instruction: Instruction
    evidence: list[Evidence] = Field(min_length=1, max_length=3)


class Clarification(StrictModel):
    description: Instruction
    evidence: list[Evidence] = Field(max_length=3)


class PlanDraft(StrictModel):
    summary: Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=1200)]
    items: list[CareItem] = Field(max_length=6)
    clarifications: list[Clarification] = Field(max_length=6)
    questions_for_care_team: list[ShortText] = Field(max_length=3)

    @model_validator(mode="after")
    def unique_ids(self) -> "PlanDraft":
        ids = [item.id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Care item IDs must be unique")
        return self


class CarePlan(PlanDraft):
    source_segments: list[SourceSegment] = Field(min_length=1, max_length=80)


class Focus(StrictModel):
    id: Identifier
    evidence: list[Evidence] = Field(min_length=1, max_length=3)


def evidence_matches(evidence: list[Evidence], segments: list[SourceSegment]) -> bool:
    sources = {segment.id: segment.text for segment in segments}
    return all(item.segment_id in sources and item.quote in sources[item.segment_id] for item in evidence)


class TeachBackRequest(AnalyzeRequest):
    focus: Focus
    answer: Feedback

    @model_validator(mode="after")
    def validate_focus(self) -> "TeachBackRequest":
        if not evidence_matches(self.focus.evidence, segment_source(self.text)):
            raise ValueError("Focus must quote the original source exactly")
        return self


class TeachBackResult(StrictModel):
    focus_id: Identifier
    status: Literal["matched", "needs_clarification", "unable_to_assess"]
    feedback: Feedback
    evidence: list[Evidence] = Field(max_length=3)

    @model_validator(mode="after")
    def require_evidence(self) -> "TeachBackResult":
        if self.status != "unable_to_assess" and not self.evidence:
            raise ValueError("An assessment requires source evidence")
        return self


class ResponseMetadata(StrictModel):
    schema_version: Literal["care-v1"] = "care-v1"
    prompt_version: str
    request_id: UUID
    provider: Literal["mock", "openai"]
    model: str | None
    is_mock: bool
    # Which engine actually produced this result, so the interface can state it.
    origin: Literal["scripted_fixture", "local_rules", "model"]
    elapsed_ms: int = Field(ge=0)


class AnalyzeResponse(ResponseMetadata):
    result: CarePlan


class TeachBackResponse(ResponseMetadata):
    result: TeachBackResult
