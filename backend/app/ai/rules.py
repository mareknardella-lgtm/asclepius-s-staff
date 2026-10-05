"""Deterministic care-instruction planner and teach-back comparator.

This module is deliberately *not* an AI system. It is a transparent rule engine:
every output sentence is a transformation of text already present in the source,
and every claim carries the exact source line it came from. That makes it usable
offline, auditable and honest: the API labels results as `local_rules` so nobody
mistakes it for model output.

What it does well: deadline, frequency, negation, red-flag and medication cues,
plus a plain-language rewrite driven by an explicit phrase table. What it cannot
do: understand clinical meaning. Anything it cannot ground becomes a limitation
question for the care team instead of a guess.
"""
from __future__ import annotations

import re
from typing import Any, Literal

from app.ai.schemas import Focus, SourceSegment

MAX_ITEMS = 6
MAX_CLARIFICATIONS = 6
MAX_QUESTIONS = 3

# Lines that describe the document rather than care the reader must act on:
# headers such as "Patient: ..." and recorded test values such as "Haemoglobin
# 13.4 g/dl". A bare lab result carries no instruction, and turning it into one
# would ask a patient to act on a number nobody explained to them.
DOCUMENT_NOISE = re.compile(
    r"(patient\s*:|age\s+\d|\bissued\s*:|\bservice\s*:|^document\s*:|reference interval|"
    r"fictional|not medical advice|synthetic demo|"
    r"h[ae]moglobin|haematocrit|hematocrit|sodium|potassium|creatinine|glucose|"
    r"white cell|wbc|platelet|tsh|mmol/l|mg/dl|g/dl)",
    re.IGNORECASE,
)
# Medication must never become an operational step; it becomes a limitation.
MEDICATION_CUE = re.compile(
    r"\b(medication|medicine|tablet|tablets|capsule|capsules|mg|mcg|microgram|milligram|dose|dosage|"
    r"prescribed|prescription|twice daily|once daily|per day|daily|nightly|in the evening|in the morning)\b",
    re.IGNORECASE,
)
RED_FLAG_CUE = re.compile(
    r"\b(call|contact|seek|go to|return|urgent|emergency|999|911|999\w*|immediately|"
    r"if you (?:have|feel|develop|notice)|fever|bleeding|breathless|chest pain|worsen|deteriorat)\w*",
    re.IGNORECASE,
)
DEADLINE_CUE = re.compile(
    r"\b(\d+\s*(?:day|days|week|weeks|hour|hours|month|months|minute|minutes)|"
    r"(?:within|before|after|no later than|up to)\s+\w+|monday|tuesday|wednesday|thursday|friday|"
    r"saturday|sunday|today|tomorrow|next week|as soon as)\b",
    re.IGNORECASE,
)
FOLLOW_UP_CUE = re.compile(r"\b(follow[- ]?up|appointment|review|clinic|visit|surgery|procedure)\b", re.IGNORECASE)
NEGATION_CUE = re.compile(r"\b(not|never|no|without|avoid|do not|don'?t|must not|stop)\b", re.IGNORECASE)
CONDITION_CUE = re.compile(r"\b(even if|if you|unless|while|when|after|before|despite|only if|should)\b", re.IGNORECASE)
ACTION_CUE = re.compile(
    r"^\s*(take|bring|call|contact|return|continue|stop|avoid|keep|use|wear|check|measure|record|"
    r"attend|arrange|book|ask|do not|don'?t|please|you (?:should|must|may|can|will))\b",
    re.IGNORECASE,
)


# Plain-language rewrites. Longest phrases first so "even if you feel better"
# is replaced before "if you".
REWRITES: tuple[tuple[str, str], ...] = (
    (r"\barrange a follow-up\b", "book your follow-up"),
    (r"\bfollow-up appointment\b", "follow-up appointment"),
    (r"\bdischarge instructions\b", "discharge instructions"),
    (r"\bmedication listed\b", "medicine listed"),
    (r"\bprior to\b", "before"),
    (r"\bsubsequent to\b", "after"),
    (r"\bin the event that\b", "if"),
    (r"\bin the absence of\b", "without"),
    (r"\bno later than\b", "no later than"),
    (r"\bcommence\b", "start"),
    (r"\bterminate\b", "stop"),
    (r"\butilise\b", "use"),
    (r"\badditional\b", "extra"),
    (r"\bregarding\b", "about"),
    (r"\bapproximately\b", "about"),
    (r"\bshould you\b", "if you"),
    (r"\byou should\b", "you need to"),
    (r"\bit is important that you\b", "you need to"),
    (r"\bdo not forget to\b", "remember to"),
    (r"\bif you have any questions\b", "if you have questions"),
)


def _evidence(segment: SourceSegment) -> list[dict[str, str]]:
    return [{"segment_id": segment.id, "quote": segment.text}]


def simplify(text: str) -> str:
    """Rewrite an instruction into plainer English without changing its meaning.

    Conditions, negations and deadlines are deliberately left intact: they are
    the parts patients most often lose, and a rewrite that dropped them would
    create exactly the misunderstanding this tool exists to catch.
    """
    plain = text.strip()
    for pattern, replacement in REWRITES:
        plain = re.sub(pattern, replacement, plain, flags=re.IGNORECASE)
    plain = re.sub(r"\s+", " ", plain)
    plain = re.sub(r"\s+([,.;:])", r"\1", plain)
    if plain and plain[0].islower():
        plain = plain[0].upper() + plain[1:]
    return plain


LineKind = Literal["deadline", "action", "red_flag", "medication", "noise", "unclear"]
# A time word alone does not make a sentence an instruction: "it is cold today"
# is not a care step. Something must also address the reader or command them.
SECOND_PERSON = re.compile(r"\b(you|your|yours|yourself)\b", re.IGNORECASE)


def classify(text: str) -> LineKind:
    """Label a source line by the cues it contains, in clinical-priority order."""
    if DOCUMENT_NOISE.search(text):
        return "noise"
    # Medication never becomes an operational step, whatever else the line says.
    if MEDICATION_CUE.search(text):
        return "medication"
    addressed = bool(ACTION_CUE.search(text) or SECOND_PERSON.search(text))
    if not addressed:
        return "unclear"
    if RED_FLAG_CUE.search(text):
        return "red_flag"
    if DEADLINE_CUE.search(text) or FOLLOW_UP_CUE.search(text):
        return "deadline"
    if ACTION_CUE.search(text):
        return "action"
    return "unclear"


def _order_key(kind: str) -> int:
    return {"red_flag": 0, "deadline": 1, "action": 2}.get(kind, 3)


def build_plan(segments: list[SourceSegment]) -> dict[str, Any]:
    """Build a PlanDraft-shaped dict from arbitrary text using rules only."""
    items: list[dict[str, Any]] = []
    clarifications: list[dict[str, Any]] = []
    seen_instructions: set[str] = set()
    medication_lines: list[SourceSegment] = []
    unclear_lines: list[SourceSegment] = []

    ranked: list[tuple[int, int, SourceSegment, LineKind]] = []
    for index, segment in enumerate(segments):
        kind = classify(segment.text)
        ranked.append((_order_key(kind), index, segment, kind))
    ranked.sort(key=lambda entry: (entry[0], entry[1]))

    for _, _, segment, kind in ranked:
        if kind == "noise":
            continue
        if kind == "medication":
            medication_lines.append(segment)
            continue
        if kind == "unclear":
            unclear_lines.append(segment)
            continue
        instruction = simplify(segment.text)
        fingerprint = instruction.lower()
        if len(items) >= MAX_ITEMS or fingerprint in seen_instructions:
            continue
        seen_instructions.add(fingerprint)
        items.append({
            "id": f"step-{len(items) + 1}",
            "instruction": instruction,
            "evidence": _evidence(segment),
        })

    for segment in medication_lines[:2]:
        clarifications.append({
            "description": "The document mentions a medicine. This tool does not give dosing instructions; ask the care team how and when to take it.",
            "evidence": _evidence(segment),
        })
    for segment in unclear_lines[:2]:
        clarifications.append({
            "description": "This line could not be read as an instruction, so it was not turned into a step. Review the wording with the care team.",
            "evidence": _evidence(segment),
        })
    if not items:
        clarifications.insert(0, {
            "description": "No clear instruction was found in this text. Ask the care team to read the document with you.",
            "evidence": [],
        })
    if len(clarifications) > MAX_CLARIFICATIONS:
        clarifications = clarifications[:MAX_CLARIFICATIONS]

    questions: list[str] = []
    if any("follow-up" in item["instruction"].lower() or "appointment" in item["instruction"].lower() for item in items):
        questions.append("What date and time is my follow-up, and who confirms it?")
    if medication_lines:
        questions.append("How and when should I take the medicine named in this document?")
    if unclear_lines:
        questions.append("Can someone explain the lines that were not clear to me?")
    if not questions:
        questions.append("Which of these instructions matter most in the next 48 hours?")

    summary = (
        f"{len(items)} step{'s' if len(items) != 1 else ''} taken directly from this document, "
        "each one linked to its original wording. "
        "Produced by local rules on the text itself, not by an AI model: it does not judge whether the guidance is correct."
    )
    return {
        "summary": summary,
        "items": items,
        "clarifications": clarifications,
        "questions_for_care_team": questions[:MAX_QUESTIONS],
    }


# A few genuine equivalents, kept short and explicit so the table stays auditable.
SYNONYMS = {
    "medicine": "medication",
    "tablet": "medication",
    "tablets": "medication",
    "pill": "medication",
    "pills": "medication",
    "drug": "medication",
    "meds": "medication",
    "appointment": "visit",
    "letter": "document",
    "letters": "document",
    "correspondence": "document",
    "paperwork": "document",
    "jab": "injection",
    "phone": "call",
    "ring": "call",
    "phoned": "call",
    "where": "location",
    "place": "location",
    "check": "confirm",
    "checks": "confirm",
    "verify": "confirm",
    "contact": "call",
}


def normalize_token(token: str) -> str:
    return SYNONYMS.get(token, token)


STOPWORDS = frozenset("""
a an and are as at be been but by can could did do does for from had has have he her him his how i if in into is
it its may me might more most must my no nor not of on once one only or other our out she should so some such than
that the their them then there these they this those to too under until up very was we were what when where which
while who whom why will with would you your about after again before being below between both during each few
further here itself just more most same then these those through too under until very
""".split())


def content_tokens(text: str) -> set[str]:
    """Lowercase word tokens with stopwords, one-character noise and plurals folded."""
    words = re.findall(r"[a-z0-9']+", text.lower())
    kept = {word.strip("'") for word in words if len(word.strip("'")) > 2 and word.strip("'") not in STOPWORDS}
    tokens = {normalize_token(word) for word in kept}
    # Fold simple plurals so "questions" and "question" are the same word.
    return tokens | {token[:-1] for token in tokens if token.endswith("s") and len(token) > 3}


PHONE_LIKE = re.compile(r"\b\d[\d\s().-]{5,}\d\b")


def _numbers(text: str) -> set[str]:
    """Numbers a person is expected to carry in their explanation.

    Phone numbers and similar contact strings are excluded: nobody repeats a
    number back, and flagging its absence would train people to distrust
    correct explanations.
    """
    return set(re.findall(r"\b\d+(?:[.,]\d+)?\b", PHONE_LIKE.sub(" ", text.lower())))


NUMBER_WORDS = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|twelve|couple|few|several)"
# A time limit stated in digits, in words, or as a named day.
DEADLINE_MENTION = re.compile(
    rf"\b(?:within|no later than|before|after|in)\s+{NUMBER_WORDS}\s*(?:day|days|week|weeks|hour|hours|month|months|minute|minutes)\b"
    rf"|\b{NUMBER_WORDS}\s*(?:day|days|week|weeks|hour|hours|month|months|minute|minutes)\b"
    rf"|\b(?:within|no later than|before|after)\s+\w+"
    rf"|\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tomorrow|tonight|next week)\b",
    re.IGNORECASE,
)


def _missing(source: str, answer: str, pattern: re.Pattern[str]) -> str | None:
    """Report the first source cue that the answer does not preserve at all."""
    match = pattern.search(source)
    if not match:
        return None
    phrase = match.group(0).strip()
    key = phrase.lower().strip(" ,.")
    if key and key not in answer.lower():
        return phrase
    return None


def _has_condition(text: str) -> bool:
    """Does the text state a condition, in any wording?"""
    return bool(re.search(r"\b(if|unless|only if|when|whenever|while|until|after|before|in case|even if|should)\b", text, re.IGNORECASE))


def _has_negation(text: str) -> bool:
    return bool(NEGATION_CUE.search(text))


def _has_time_limit(text: str) -> bool:
    return bool(DEADLINE_MENTION.search(text))


WEEKDAYS = re.compile(r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.IGNORECASE)


def _weekday_conflict(source: str, answer: str) -> bool:
    """True when both name days and they disagree, e.g. Monday against Friday."""
    source_days = {day.lower() for day in WEEKDAYS.findall(source)}
    answer_days = {day.lower() for day in WEEKDAYS.findall(answer)}
    return bool(source_days and answer_days and not source_days & answer_days)


def compare_answer(focus: Focus, answer: str) -> dict[str, Any]:
    """Compare a free-form answer with the selected source line using cues only.

    Returns a TeachBackResult-shaped dict. The comparison is about preserved
    meaning cues (timing, conditions, polarity), never about the person.
    Cue classes are compared as classes, not as literal strings, so a valid
    paraphrase ("unless" -> "only after") is not mistaken for an omission.
    Evidence is the focus's own citations, so every claim stays grounded in a
    real source segment rather than an invented identifier.
    """
    source_text = focus.evidence[0].quote
    source = source_text.lower()
    normalized_answer = answer.lower()
    answer_tokens = content_tokens(answer)
    source_tokens = content_tokens(source_text)
    evidence = [reference.model_dump() for reference in focus.evidence]

    def result(status: str, feedback: str, cited: list[dict[str, str]] | None = None) -> dict[str, Any]:
        return {"focus_id": focus.id, "status": status, "feedback": feedback, "evidence": evidence if cited is None else cited}

    if len(answer_tokens) < 2:
        return result(
            "unable_to_assess",
            "There is not enough here to compare with the instructions. Try describing what you plan to do, in your own words.",
            cited=[],
        )

    if not answer_tokens & source_tokens:
        return result(
            "unable_to_assess",
            "This does not refer to the step you selected, so it cannot be compared. Look at the original wording and try again.",
            cited=[],
        )

    # Polarity first: an explanation that reverses the instruction is the most
    # consequential difference, whatever else it preserves.
    if not _has_negation(source) and _has_negation(normalized_answer):
        return result(
            "needs_clarification",
            "Your explanation says this does not apply, but the instructions ask for it. Read the original wording again, and raise the difference with the care team.",
        )
    if _has_negation(source) and not _has_negation(normalized_answer):
        return result(
            "needs_clarification",
            "The instructions include something to avoid or stop, which your explanation leaves out. Worth checking with the care team.",
        )

    if _has_time_limit(source) and not _has_time_limit(normalized_answer):
        phrase = _missing(source, normalized_answer, DEADLINE_MENTION) or "a time limit"
        return result(
            "needs_clarification",
            f"The instructions say '{phrase}', and that limit is missing from your explanation. Check what should happen, and by when.",
        )

    if _weekday_conflict(source, normalized_answer):
        return result(
            "needs_clarification",
            "The days in your explanation are not the days in the instructions. Check which day the document means.",
        )

    invented_days = {day.lower() for day in WEEKDAYS.findall(normalized_answer)} - {
        day.lower() for day in WEEKDAYS.findall(source)
    }
    if invented_days:
        named = ", ".join(sorted(day.capitalize() for day in invented_days))
        return result(
            "needs_clarification",
            f"Your explanation names {named}, which the instructions do not mention. Check the wording again before relying on that day.",
        )

    if _has_condition(source) and not _has_condition(normalized_answer):
        phrase = _missing(source, normalized_answer, CONDITION_CUE) or "a condition"
        return result(
            "needs_clarification",
            f"The instructions are conditional ('{phrase}'), and your explanation does not cover that case. Ask what to do when it happens.",
        )

    if _numbers(source) - _numbers(normalized_answer):
        return result(
            "needs_clarification",
            "A number from the instructions is not in your explanation. Numbers such as days or times are easy to mix up; read them again.",
        )

    coverage = len(source_tokens & answer_tokens) / max(1, len(source_tokens))
    if coverage >= 0.5:
        return result(
            "matched",
            "Your explanation keeps the main points of this step, including its conditions and timing. Local rules checked wording only; the care team confirms what is right for you.",
        )
    return result(
        "needs_clarification",
        "Part of this step is missing from your explanation. Compare your words with the original wording above, and note anything that reads differently.",
    )