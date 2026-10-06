# Devpost submission copy

Ready-to-paste text for the AI + Healthcare track. Every claim below is backed by
something in this repository; nothing here asserts clinical benefit or a win.

## Project name

**Asclepius — the care instructions desk**

## Tagline

Understand the next step. Keep the original close.

## One-line pitch

Asclepius turns a discharge note into a short list of steps you can explain back
in your own words, and shows you where a misunderstanding would come from.

## What it does

A patient or caregiver pastes written discharge instructions. Asclepius returns:

1. **Cited steps.** Every step sits next to the exact source line it came from,
   numbered the same way on both sides. Click a citation to jump to the wording.
2. **A teach-back check.** The reader explains one step in their own words.
   Asclepius compares the explanation with that specific source passage and
   reports what it could not match.
3. **What is still unknown.** Missing dates, unclear lines and anything the
   document does not specify stay visible instead of being filled in.
4. **A reviewed take-away.** Each suggestion needs an explicit human decision —
   accept, edit or set aside with a reason — before a JSON record can be saved.

It does not diagnose, triage, prescribe, calculate doses or contact anyone.

## Why this is not a summariser

A summary hides the part that causes harm. The failure mode this targets is a
correct-looking paraphrase of a conditional instruction: a note that says
*book the follow-up within seven days, even if you feel better*, read as
*book it only if you still feel unwell*.

So the product is built around the round trip, not the read: **read → explain
back → see the difference → decide**. The comparison is deliberately narrow —
timing, conditions, negation, polarity and numbers — because those are the parts
that invert the meaning of a sentence.

## Human in the loop, visible

- Every suggestion has Accept / Edit / Set aside; editing and setting aside
  require a written reason.
- The export is blocked until every suggestion has a recorded decision.
- Model suggestions and human decisions are stored in separate fields of the
  export, so the audit record shows who changed what.
- Editing the source or the explanation invalidates the results derived from it.

## How the AI is used, honestly

Asclepius supports three engines and always states which one produced a result:

| Engine | What it is | Where it comes from |
| --- | --- | --- |
| `scripted_fixture` | A labeled synthetic demo note | The bundled demo document |
| `local_rules` | Deterministic rules over your text | [rules.py](../backend/app/ai/rules.py) |
| `model` | A configured LLM via an OpenAI-compatible API | `AI_PROVIDER=openai` |

The offline engine is not a mock that pretends: it is a transparent rule engine
that segments the note, classifies each line by clinical cues (red flags,
deadlines, medication, actions), orders them by priority, quotes the source
verbatim and abstains on anything it cannot ground. A note that mentions a
medicine becomes a limitation to raise with the care team, never a dosing step.

Configuring a real model changes that sentence to say an AI model wrote it. With
no key and no network, the demo still works on any text. The exact engine code
(`scripted_fixture`, `local_rules`, `model`) is not hidden: it stays in the
"How this was made" disclosure and in the exported JSON, so a judge can audit
the claim rather than take it on trust.

## Measured, not asserted

`python scripts/evaluate_rules.py` over the bundled synthetic corpus:

- 20/20 plan cases produce a schema-valid, fully grounded plan.
- 20/20 keep medication wording out of operational steps.
- 25/30 teach-back cases match the annotated label.
- **0 of 30** produce a false `matched`: every error is a correct explanation
  being sent back for clarification, which is the safe direction to fail.

The remaining 5 misses are valid paraphrases ("seven days" → "a week") that
need semantics a rule engine does not have. They are listed by case id so the
limit is auditable rather than hidden.

## Built with

React 19, Vite 6, TypeScript, hand-written CSS with design tokens; Python
FastAPI, Pydantic, HTTPX. No database, no vector store, no agent framework, no
UI kit. Self-hosted OFL fonts. Tests: pytest, mypy, Vitest, Testing Library,
plus a GitHub Actions workflow that runs them on every push.

## Try it

```sh
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
npm --prefix frontend ci
python scripts/dev.py
```

Open http://127.0.0.1:5173. No account, no key, no data leaves the machine.
Only synthetic documents are accepted.

## Limitations we are not hiding

- Not a medical device. No clinical validation, no accuracy claim, no measured
  effect on adherence or readmission.
- A citation proves where wording came from, not that it is medically correct.
- `matched` describes text correspondence, not comprehension or understanding.
- The offline engine cannot resolve meaning, contradiction or ambiguity. It
  abstains rather than guesses, and asks the care team instead.
- No user study has been run. The problem is grounded in published work on
  health literacy and teach-back, not in our own measurements.
- Only synthetic documents are accepted by design.

## Links

- Repository: https://github.com/mareknardella-lgtm/asclepius-s-staff
- Video Demo (MP4): https://github.com/mareknardella-lgtm/asclepius-s-staff/blob/main/public/video/asclepius_demo_3min.mp4
- Live demo: _add when deployed_

---

## Video script, 3 minutes

**0:00–0:25 · The problem.** Show a printed discharge note. Read out: *"Arrange
a follow-up within seven days, even if you feel better."* Say: the words are
simple, the condition is easy to drop, and the person leaving hospital has about
ten minutes with a nurse. Say plainly that we did not measure how often this
happens — we are not claiming a statistic.

**0:25–0:50 · What we built.** Three sentences: source stays visible, one step at
a time, explain it back in your own words. No product screenshots yet, just the
promise.

**0:50–2:00 · Live demo, real clicks.**
1. Open the app. The note is already there, numbered S1–S9, with the fictional
   patient panel. Say the record is synthetic and the person is fictional.
2. Tick the confirmation, press **Show me my steps**. Read the plain line at the
   top of the result: *Written by a prepared demo example. No AI looked at this
   note.*
3. Point at the first step and its `Source S4` citation. Click it — the view
   jumps to the original wording. That is the whole product: nothing on screen
   without its source.
4. Pick the step, press **Example that misses something**, then **Check what I
   said**. The feedback says the note says seven days *even if you feel
   better*.
5. Go to **Check it and save**. Edit one step, set another aside with a
   reason. Note that the source evidence does not change when you edit.
6. Confirm and download. Open the JSON: the note, the provenance, and the human
   decisions are separate fields.
7. **Second run, no scripted anything.** Edit the note, paste a note that
   mentions a medicine and a fever threshold. Press the button. New steps,
   ordered with the fever first, each cited. The medicine became a limitation,
   not a dosing instruction. The sentence at the top now reads *simple rules
   that copy words from your own text. No AI model was used*. This is the moment
   that shows it is not a template.

**2:00–2:40 · Under the hood.** Fast tour: deterministic source segments,
strict Pydantic schema, citation validation that rejects any quote not present
in the original, and the rule engine that works offline. Mention the three
engines and that a real model swaps in through configuration, with the label
changing accordingly.

**2:40–3:00 · Limits and close.** Say what it does not do: no diagnosis, no
dosing, no clinical validation, no user study. Say the corpus result: 20/20
grounded, 25/30 comparisons correct, and zero false reassurances. Close with the
repository URL.

## Recording checklist

- [ ] Key configured or offline engine labelled honestly on screen
- [ ] No `.env`, key or terminal output in frame
- [ ] Window at 1280px, browser zoom 100%
- [ ] Second demo run uses text that is not a bundled example
- [ ] Say "synthetic record" and "fictional patient" out loud at least once
- [ ] State the limits; do not claim clinical benefit or a win probability