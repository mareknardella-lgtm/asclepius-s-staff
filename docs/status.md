# Asclepius — implementation and verification status

## Plain-language screen — latest checkpoint

The main screen was rewritten for the person actually using it: a patient or caregiver leaving hospital, not a clinician and not a judge. The guarantees were kept; the language was not simplified at their expense.

Changed:

- One plain question as the heading ("What should I do at home?"), one primary action ("Show me my steps"), and one sentence of framing instead of a strip of uppercase editorial labels. The `.overline` class was removed from the components entirely, loading state included: 0 instances in the source and 0 in the production CSS bundle.
- Engine provenance is now plain on screen — "Written by simple rules that copy words from your own text. No AI model was used." The exact `origin` code, prompt version, request id and timings moved to a "How this was made" disclosure at the bottom of the column, and stay in the exported JSON unchanged. Nothing was hidden; it was moved below the fold.
- Teach-back uses a radio list of steps with the whole sentence visible, replacing a `<select>` whose contents had to be remembered while scrolling. Changing the step clears the explanation and the feedback, as before.
- Backend fixture copy rewritten in everyday language: the scripted teach-back feedback, the medication limitation and the demo summary no longer say "Scripted mock feedback", "recorded context only" or "fixed mock fixture".
- The clarification panel only appears when there is something to clarify, and the review screen mirrors the same wording.

Verification for this pass:

| Check | Result |
| --- | --- |
| Backend `pytest -q` | **93 passed**, exit 0 |
| Backend `mypy` | **Success, 20 files**, exit 0 |
| Frontend `npm run typecheck` | **Pass**, exit 0 |
| Frontend `npm test` | **21 passed**, exit 0 |
| Frontend `npm run build` | **Pass**, exit 0 |
| `scripts/evaluate_rules.py` | Grounding and safety 20/20; 25/30 labels; exit 0 |
| Browser 1280px, seeded note | Consent → 2 cited steps → engine sentence → example that misses something → feedback with S4 evidence → 6 decisions → confirm → download |
| Browser 1280px, free text | `local_rules` sentence, 2 steps, invented "Friday" flagged with S1 evidence, no preset buttons offered |
| Export payload via trusted click | `care-export-v1`, 5,801 bytes, `origin: scripted_fixture`, 6 human decisions, 5 limitations |
| Mobile 390px | No horizontal overflow on any element; step radios inside 44px labels |
| Console | No application errors; Vite/React development messages only |

Known limits of this pass: screenshots could not be captured (the preview webview stopped compositing), so layout was checked through DOM geometry and computed overflow rather than pixels. Nothing else changed in behaviour: source links, Accept/Edit/Set aside, the download gate and the skeleton/empty/error/uncertain states all behave as before.

## Deterministic engine — previous checkpoint

The offline engine now answers **any** synthetic note, not only the three bundled examples. This closes the largest demo risk: a judge pasting their own text previously got no result.

Delivered:

- New [rules.py](../backend/app/ai/rules.py): a transparent, non-AI rule engine. It segments the note, classifies each line by clinical cue (red flag, deadline, action, medication, document metadata), orders steps by clinical priority, rewrites jargon with an explicit phrase table that never touches conditions, negations or deadlines, and cites the exact source line verbatim.
- Teach-back comparison on free text: timing, conditions, negation polarity, weekday agreement and preserved numbers, compared as cue classes so valid paraphrases are not mistaken for omissions. Abstains instead of guessing.
- Safety rules enforced by construction: medication lines never become operational steps, lab/reference lines become limitations, document metadata is never a step, duplicates collapse.
- `origin` field (`scripted_fixture` / `local_rules` / `model`) in every API response, exported in the take-away record, shown in the interface so a user always knows which engine produced the text.
- [evaluate_rules.py](../scripts/evaluate_rules.py): offline measurement over the synthetic corpus with a printed confusion matrix.
- [devpost.md](../docs/devpost.md): submission copy and a 3-minute video script.

Measured over the 20 plan / 30 comparison synthetic cases:

| Check | Result |
| --- | --- |
| Plan cases schema-valid | 20/20 |
| Plan cases fully grounded | 20/20 |
| Plan cases with no medication wording in a step | 20/20 |
| Comparison exact-label match | 25/30 |
| **False `matched` (dangerous direction)** | **0/30** |

The five misses are valid paraphrases needing semantics a rule engine lacks (`seven days` → `a week`, `unless` → `only after`); each is reported by case id by the evaluator rather than hidden. The engine errs towards asking the care team.

Defects found by measurement and browser testing, and fixed at the source:

- A prompt-injection style line produced a step. Now any line must address the reader or command them; a bare time word is not an instruction.
- "within **seven** days" written in words was not detected as a deadline.
- A reversed instruction ("I do not need to bring the letter") was reported as `matched`. Polarity is now checked first, in both directions.
- A conflicting day (note says Monday, answer says Friday) was reported as `matched`.
- A day invented by the answer and absent from the note was not flagged.
- Ward phone numbers were treated as facts the patient must recall, causing false alarms on correct answers.
- Teach-back returned a placeholder segment id, so every free-text comparison was rejected as ungrounded. Found by running the real browser path, not by unit tests.
- The launcher accepted a Python 3.9 virtual environment that fails at import time; it now refuses it with the required version.

Verification for this checkpoint:

| Check | Result |
| --- | --- |
| Backend `pytest -q` | **93 passed**, exit 0 |
| Backend `mypy` | **Success, 20 files**, exit 0 |
| Frontend `npm run typecheck` | **Pass**, exit 0 |
| Frontend `npm test` | **21 passed**, exit 0 |
| Frontend `npm run build` | **Pass**, exit 0 |
| `scripts/evaluate_rules.py` | Grounding and safety 20/20; 25/30 labels; exit 0 |
| Browser, typed free text (no fixture) | Consent → 4 cited steps ordered fever-first → medicine demoted to limitation → teach-back flagged the invented Friday with S2 evidence → 6 decisions + 1 comparison → export |
| Export payload via trusted click | `care-export-v1`, 5,120 bytes, `origin: local_rules`, 7 human decisions |
| Mobile 390px | No horizontal overflow; only the wrapped 20px checkbox is under 44px, inside a 67px label |
| Console | No application errors after the fixes; the earlier 502 was the ungrounded-evidence defect, since corrected |

Deliberately not done, and why:

- No AI account was created and no paid call was made: that needs the user's explicit authorisation, and the offline engine already makes the demo complete without it.
- No deployment or submission: no account was provisioned and no repository URL is available yet.
- The rule engine was not tuned to inflate the corpus score. Fixes were limited to genuine semantic classes; the residual misses are reported.

## Editorial interface redesign — previous checkpoint

Direction committed: **calm clinical editorial**, patient and caregiver language only. Two screens (understand/explain, review/take-away) replace the previous single generic panel.

Delivered in this pass:

- Design tokens in one `:root` block: five base colours (paper, ink, primary, alert plus a muted text tone derived for AA), 9-step type scale, 10-step spacing scale, shared radius/hairline/motion tokens. Rules and washes derive from the base colours.
- Self-hosted OFL fonts: Source Serif 4 (display), Public Sans (interface), IBM Plex Mono (values, identifiers, timings). No system default, Inter or Roboto; `document.fonts.check` confirms all three load.
- Seeded fictional case with plausible identifiers, ISO timestamp, medication strength, and lab values with units and record intervals. Every number carries units and context; values are copied from the fictional record and never interpreted.
- Evidence, human review and export in reusable components ([components.tsx](../frontend/src/components.tsx)) used by both screens; design decisions measured rather than asserted.
- States: skeleton for plan and comparison, empty source, neutral error preserving the original text, explicit "I could not check this one", and "Please check this" on unreviewed steps.
- Human-in-the-loop is now explicit for every suggestion: accept, edit, or set aside with a required reason; confirmation and download unlock only when all decisions are recorded, and the export separates AI evidence from human decisions.
- Tailwind CSS and its Vite plugin were removed after the redesign (12 packages); styles are hand-written CSS. The production CSS bundle is byte-identical before and after removal, and typecheck, tests and build were rerun. Two locked native binaries of the removed packages remain in the local `node_modules` (EPERM while the dev server holds them); they are untracked and not part of the build.

Verification for this pass:

| Check | Result |
| --- | --- |
| Frontend `npm run typecheck`, `npm test`, `npm run build` | **Pass** (19 tests, 2 suites; build emitted) |
| Backend `pytest -q` + `mypy` + corpus validation | **66 passed** at that time, mypy clean, corpus pass |
| Two-type mypy failure and a `getByRole` option typo from the interrupted pass | Fixed at the source (typed fixture lists; regex matcher), not suppressed |
| Real local stack | Launcher `scripts/dev.py` owns both ports; `/api/health` 200 through the Vite proxy; seeded fixture returns two cited steps at S4/S5, two limitations at S6/S7, 9 source segments, mock flag |
| Browser 60-second path | Consent → plan → preset misunderstanding → clarification with S4 evidence → review → 6 decisions → confirm; verified by snapshot, screenshots and DOM assertions |
| Export payload via trusted click | `care-export-v1`, 5,680 bytes, SHA-256 `a263917c5189757dbbe6809f7d70e2ea8bd1ea800f9e1a00a3463c8240c06899`, six human decisions, S4 evidence, `needs_clarification`, mock provenance, ISO review timestamp |
| Contrast (computed in-browser) | Body 12.21, secondary 5.38, primary 6.71, on-primary 6.71, secondary on wash 4.86, hairline 3.54, alert on paper 6.39 — all AA or better |
| Target sizes | Only the 20px checkbox input is under 44px; it is wrapped in a 44px label, so the effective target is compliant. Provenance links were enlarged from 13–15px to 44px hit areas |
| Focus visibility | 3px primary outline, 6.71:1, verified on a focused control |
| Responsive | 1280px two-column, 390px single column, no horizontal overflow, table 308px wide |
| Font loading and console | All three faces loaded; no application errors in console |

Limitations for this pass:

- The browser in this environment no longer persists blob downloads to disk, so the export was validated by capturing the exact blob payload during a trusted click (size, SHA-256, parsed content) rather than by reopening a saved file. Unit tests cover the blob, filename and JSON content directly.
- The alert token is intentionally unused: this product does not assess clinical urgency, so no red state is fabricated. Measured alert contrast (6.39:1 on paper) is recorded for future use only.
- Live AI, semantic benchmark, deployment and submission remain open as before.

## Earlier checkpoint

## Current checkpoint

**Healthcare MVP implemented and verified locally with explicitly labeled synthetic mock fixtures. Not a clinically validated product or submission-ready live AI demo.** The user authorized continuing development and pushing to the repository they are creating, `asclepius's-staff`. Repository URL/access and real-model credentials remain unavailable at this checkpoint.

No Git repository was present at inspection. No commit, push, account creation, public deployment or submission has occurred. Existing downloaded export from the previous session was left untouched.

## Delivered

- Healthcare `care-v1` API: source normalization/segmentation, strict input and synthetic-data confirmation, plan schema, exact-quote validation, uncertainty and teach-back.
- Stateless semantic comparison prompts with selected original passages; no generated client summary treated as truth. Unknown focus/quotes are rejected before a provider call; unrelated output evidence is rejected.
- English React UI: source references, steps, clarifications, questions, explicit explanation submission, review states and consent.
- Review-gated `care-export-v1` JSON download with source, current explanation/feedback, model/mock/prompt provenance and limitations. Editing source/answer/step state invalidates relevant review/results.
- Honest offline fixtures: two exact synthetic documents, two labeled preset explanations; custom documents yield zero items and free answers abstain. No pretend semantic AI.
- Synthetic evaluation corpus: 20 plan rubrics and 30 pre-annotated comparisons, ten per label. Evaluator validates offline or makes 50 explicit real-provider requests, preserving error outcomes and requiring manual plan semantic review.
- Multipiattaforma stdlib launcher in [dev.py](../scripts/dev.py): checks ports, never stops unrelated processes, starts/stops only its own children.
- Launcher refuses a `backend/.venv` built with Python older than 3.12 and names the required version. Found on this machine: `python` on PATH is 3.9.13 while the project venv is 3.14.7, so the previously documented `python -m venv` command would have produced an environment that fails at import time. README now selects a 3.12+ interpreter explicitly (`py -3.14`).
- GitHub Actions verification workflow added, **not run remotely yet**.
- Intake scanner repaired to include extensionless `.env`/`.env.local`, prune dependency/cache directories and report skipped scans honestly; tests added. Still heuristic, not a publication/security audit.

## Final checks at this checkpoint

| Check | Result / scope |
| --- | --- |
| Backend `pytest -q` | **77 passed**, including schema, quotes, consent, Unicode, focus forgery, invalid JSON, provider faults, corpus, preflight and launcher version/port gates. |
| Backend `mypy` | **Pass**, 17 source files, including scripts. |
| Frontend `npm run typecheck` | **Pass** after migrating Day 0 tests to care-v1. |
| Frontend `npm test` | **16 passed**, API/export and UI journey. |
| Frontend `npm run build` | **Pass**, static bundle generated; not public deployment. |
| Launcher `dev.py --api-port 8100 --web-port 5273 --smoke-test` | **Pass on Windows:** both servers and proxy returned 200, owned listeners stopped afterward. One initial proxy connection refusal while backend started, bounded retry succeeded. Other OS paths not executed. |
| Launcher Python-version gate | **Pass:** a copied 3.9.13 interpreter in `backend/.venv` is rejected with exit 1 and the message `Python 3.12+ is required ... py -3.12 -m venv backend/.venv`; the real 3.14.7 venv still passes. |
| `evaluate_care.py --validate-only` | **Pass**, 20 plan cases / 30 grounded comparison cases; no AI request. |
| `day1_preflight.py` | **Exit 0**, 23 intake fields; heuristic scan has no findings, not an absence-of-secrets guarantee. |
| HTTP server/proxy readiness | **200** for backend `/health`, frontend and `/api/health`. First proxy readiness probe timed out at 5 seconds; later 15-second probe passed after startup. |
| Browser journey, real local servers | **Pass with mock:** example → consent → plan → preset misunderstanding → clarification → review → download. API routes returned 200. |
| Actual browser download | **Inspected:** `asclepius-fc590252-d2da-4c30-a463-1860901cbbdf.json`, ignored local file (intentionally no repository link to an unpublished artifact). UTF-8 JSON, `care-export-v1`, source, two cited steps, feedback needs_clarification, confirmed review, mock provenance. Not intended for GitHub. |
| Invalidation/free explanation | **Pass in browser:** editing explanation clears feedback/review and blocks download; non-preset answer gives unable_to_assess; changing source removes plan and resets consent. |
| Desktop/mobile | **Pass:** 1280px two-column / 390px one-column, no horizontal overflow, controls fit. |
| Visual screenshots | **Viewed successfully** at desktop/mobile and feedback/export; not saved as submission artifacts. Historical screenshot-tool failure no longer applies. |
| Browser logs | No errors; Vite/React development messages only. Successful plan/teach-back network calls. |
| AI live correctness/timing | **Not run:** no credentials. Mocks and transport tests do not prove model behavior. |
| Clinical validation / usability | **Not run.** Corpus labels measure text correspondence, not clinical safety or understanding. |
| GitHub CI | Workflow authored; not executed on GitHub before push. |

Checks were rerun after relevant repairs. Initial frontend typecheck failed because old tests referenced the retired v0; tests were migrated to the real new contract. A preflight false positive matched a clearly fake test literal; the temporary test data is now assembled without a publication-file secret-shaped literal, and the scanner assertions remain intact. Nothing was suppressed or skipped to pass.

One warning remains: installed Starlette deprecates HTTPX TestClient integration. Tests pass; dependency locking/version review remains a freeze task. No vulnerability or supply-chain audit claimed.

## Local preview

Owned background services restarted for this task, readiness/logs inspected:

- Frontend **http://127.0.0.1:5173**, launcher PID 26232, registered in Preview.
- Backend **http://127.0.0.1:8000**, launcher PID 1192, server child PID 21644.
- Provider **mock**. `/health` checks liveness/configuration only.

These processes are session-local and may stop on restart; inspect ports/PIDs before reuse. No other process was stopped. [Launcher](../scripts/dev.py) supports a reproducible future start.

## Remaining release gates

1. **Real provider:** candidate researched through Gravity; no credentials/account/billing action. Configure `AI_PROVIDER`, `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL` locally, verify compatibility/policy, run allowed synthetic input. Do not claim free-form AI or prompt safety based on mock success.
2. **Semantic evaluation:** run the versioned corpus with real model; inspect incorrect labels, false matched, omissions, unsupported additions and medication-scope behavior. Runner single run is not the three-run/baseline/usability protocol. No measured quality/latency/improvement yet.
3. **GitHub:** exact URL, access and remote history must be inspected. Stage only relevant source/docs/tests/config, excluding env, dependencies, caches, logs, local exports and unreviewed reports. No username or remote inferred.
4. **Public deployment:** auth/access, rate limits, budgets/concurrency, body limits, HTTPS/API routing and privacy policy before exposing a paid endpoint. Push authorization is not deployment authorization.
5. **Hackathon:** actual team/elegibility, pre-existing-work disclosure and deadline timezone. Devpost banner says 12:00 EDT, rules body EST, October 10, 2026; confirm and plan against earlier 16:00 UTC. No team facts invented.
6. **Submission:** saved screenshots, 2–4 minute live video, genuine URL links, user review/submission. No clinical outcome, originality ranking or probability of winning promised.

[Product decision](day-1.md) · [API/architecture](architecture.md) · [Demo](demo-script.md) · [Audit](submission-checklist.md) · [README](../README.md).
