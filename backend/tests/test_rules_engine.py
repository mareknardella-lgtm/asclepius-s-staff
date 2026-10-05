"""Behaviour tests for the deterministic engine.

These assert what the rules actually do on free text: grounded quotes, no
operational medication steps, priority ordering, and the comparison outcomes a
patient is likely to produce. They are behaviour contracts, not snapshots.
"""
from fastapi.testclient import TestClient

from app.ai import rules
from app.ai.schemas import CarePlan, Evidence, Focus, PlanDraft, TeachBackResult, segment_source
from app.config import Settings
from app.main import create_app

FREE_TEXT = """Patient: Marta Kowalski, age 71 years. Issued: 02 Oct 2026 at 08:00 UTC.
Take your water tablet twice daily with food.
Call the ward on 555 0100 if you have a fever above 38 C.
Book the follow-up review within seven days, even if you feel better.
Do not lift anything heavier than 5 kg for two weeks.
Haemoglobin: 11.4 g/dL; reference interval in this fictional record: 12.0-16.0 g/dL.
Bring your discharge letter to the appointment."""


def mock_settings() -> Settings:
    return Settings(ai_provider="mock")


def request_body(text: str) -> dict[str, object]:
    return {"text": text, "synthetic_data_confirmed": True}


def test_free_text_plan_is_contract_valid_and_grounded() -> None:
    segments = segment_source(FREE_TEXT)
    draft = rules.build_plan(segments)
    PlanDraft.model_validate(draft, strict=True)
    plan = CarePlan(**draft, source_segments=segments)
    sources = {segment.id: segment.text for segment in segments}
    for item in plan.items:
        for reference in item.evidence:
            assert reference.quote in sources[reference.segment_id]
    for clarification in plan.clarifications:
        for reference in clarification.evidence:
            assert reference.quote in sources[reference.segment_id]


def test_medication_and_lab_lines_never_become_operational_steps() -> None:
    segments = segment_source(FREE_TEXT)
    items = rules.build_plan(segments)["items"]
    instructions = " ".join(item["instruction"] for item in items).lower()
    assert "water tablet" not in instructions
    assert "twice daily" not in instructions
    assert "haemoglobin" not in instructions
    # The medication line survives as a limitation with its own citation.
    medication = [c for c in rules.build_plan(segments)["clarifications"] if "medicine" in c["description"]]
    assert medication and medication[0]["evidence"]


def test_red_flag_and_deadline_lines_outrank_routine_actions() -> None:
    items = rules.build_plan(segment_source(FREE_TEXT))["items"]
    assert "fever" in items[0]["instruction"].lower()
    assert "seven days" in items[1]["instruction"].lower()


def test_document_metadata_lines_are_not_turned_into_steps() -> None:
    instructions = " ".join(item["instruction"] for item in rules.build_plan(segment_source(FREE_TEXT))["items"])
    assert "Kowalski" not in instructions
    assert "08:00" not in instructions


def test_text_without_instructions_yields_limitation_not_invention() -> None:
    draft = rules.build_plan(segment_source("The weather is cold today and the tea is ready."))
    PlanDraft.model_validate(draft, strict=True)
    assert draft["items"] == []
    assert draft["clarifications"][0]["evidence"] == []
    assert "questions_for_care_team"


def test_rewrite_preserves_conditions_and_deadlines() -> None:
    plain = rules.simplify("It is important that you prior to the procedure, you should commence your medication.")
    assert "before" in plain
    assert "start" in plain
    preserved = rules.simplify("Arrange a follow-up within seven days, even if you feel better.")
    assert "seven days" in preserved
    assert "even if you feel better" in preserved


def test_duplicate_instructions_are_not_repeated_as_steps() -> None:
    repeated = "Call the ward on 555 0100.\nCall the ward on 555 0100."
    items = rules.build_plan(segment_source(repeated))["items"]
    assert len(items) == 1


def focus_for(quote: str, segment_id: str = "s1", focus_id: str = "step-1") -> Focus:
    return Focus(id=focus_id, evidence=[Evidence(segment_id=segment_id, quote=quote)])


def test_comparison_flags_missing_deadline_condition_and_negation() -> None:
    deadline_source = "Arrange a follow-up within seven days, even if you feel better."
    assert rules.compare_answer(focus_for(deadline_source), "I will book it soon when I feel ready.")["status"] == "needs_clarification"
    assert rules.compare_answer(focus_for(deadline_source), "I will arrange the follow-up within seven days.")["status"] == "needs_clarification"
    assert "seven days" in rules.compare_answer(focus_for(deadline_source), "I will book it soon when I feel ready.")["feedback"]
    negation_source = "Do not lift anything heavier than 5 kg for two weeks."
    assert rules.compare_answer(focus_for(negation_source), "I can lift up to 5 kg for two weeks.")["status"] == "needs_clarification"
    assert rules.compare_answer(focus_for(negation_source), "For two weeks I should not lift anything heavier than 5 kg.")["status"] == "matched"


def test_comparison_catches_reversed_instruction() -> None:
    # The most consequential error type: saying the opposite of the note.
    source = "Bring your appointment letter to the visit."
    assert rules.compare_answer(focus_for(source), "I do not need to bring the letter.")["status"] == "needs_clarification"
    assert "does not apply" in rules.compare_answer(focus_for(source), "I do not need to bring the letter.")["feedback"]


def test_comparison_catches_a_conflicting_day() -> None:
    source = "Call the clinic on Monday to confirm the appointment time."
    assert rules.compare_answer(focus_for(source), "I will call on Friday to check the time.")["status"] == "needs_clarification"
    assert rules.compare_answer(focus_for(source), "I will call on Monday to check the time.")["status"] == "matched"


def test_comparison_ignores_contact_numbers_but_keeps_clinical_ones() -> None:
    # Nobody repeats a ward phone number back; demanding it would teach people
    # to distrust correct explanations. A temperature must still be preserved.
    source = "Call the ward on 555 0100 if you have a fever above 38 C."
    assert rules.compare_answer(focus_for(source), "I will call the ward if I have a fever above 38 C.")["status"] == "matched"
    assert rules.compare_answer(focus_for(source), "I will call the ward if I have a fever.")["status"] == "needs_clarification"


def test_comparison_flags_a_day_the_note_never_mentions() -> None:
    source = "Call the ward on 555 0100 if you have a fever above 38 C."
    result = rules.compare_answer(focus_for(source), "I will call the ward on Friday if I have a fever above 38 C.")
    assert result["status"] == "needs_clarification"
    assert "Friday" in result["feedback"]


def test_comparison_abstains_instead_of_guessing() -> None:
    focus = focus_for("Arrange a follow-up within seven days, even if you feel better.")
    assert rules.compare_answer(focus, "Yes.")["status"] == "unable_to_assess"
    assert rules.compare_answer(focus, "My sister will drive me to the hospital on Sunday.")["status"] == "unable_to_assess"


def test_comparison_result_satisfies_public_contract() -> None:
    result = TeachBackResult.model_validate(
        rules.compare_answer(focus_for("Bring your discharge instructions to that visit."), "I will bring the discharge instructions to the visit."), strict=True
    )
    assert result.focus_id == "step-1"
    assert result.evidence
    assert result.status == "matched"


def test_synonyms_do_not_change_grounding_of_the_quote() -> None:
    # Equivalents widen the comparison, never the citation: the returned quote
    # and segment id must be the focus's own evidence.
    focus = focus_for("Bring your discharge letter to the visit.", segment_id="s7")
    result = rules.compare_answer(focus, "I will bring the document to the visit.")
    assert result["evidence"][0]["quote"] == "Bring your discharge letter to the visit."
    assert result["evidence"][0]["segment_id"] == "s7"
    assert result["focus_id"] == "step-1"


def test_api_reports_origin_and_answers_free_text() -> None:
    with TestClient(create_app(mock_settings())) as client:
        response = client.post("/analyze", json=request_body(FREE_TEXT)).json()
        assert response["origin"] == "local_rules"
        assert response["is_mock"] is True
        assert response["result"]["items"]
        focus = response["result"]["items"][0]
        taught = client.post("/teach-back", json={
            "text": FREE_TEXT, "synthetic_data_confirmed": True,
            "focus": {"id": focus["id"], "evidence": focus["evidence"]},
            "answer": "I have no idea what this means.",
        }).json()
        assert taught["origin"] == "local_rules"
        assert taught["result"]["status"] in {"unable_to_assess", "needs_clarification"}