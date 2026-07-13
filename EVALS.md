# EVALS.md

## Evaluation Purpose

This file defines how the project is judged.

The goal is not only to ask whether the CLI runs, but whether the system translates experience truthfully, evaluates job fit conservatively, uses Gemini/live mode safely, falls back correctly in auto mode, and flags risky output. For Kaggle capstone evidence, the project also includes deterministic demo cases and saved outputs.

## Success Criteria

The project should be evaluated against:

1. Correctness
2. Usefulness
3. Clarity
4. Robustness
5. Safety
6. Scope discipline
7. Backend fallback reliability
8. Factual preservation
9. Judge readability
10. Demo reproducibility
11. Gemini live-mode reliability

## Evaluation Rubric

| Category | 1 - Weak | 3 - Acceptable | 5 - Strong |
|---|---|---|---|
| Correctness | Frequently changes meaning | Mostly preserves meaning | Reliably preserves user-provided facts |
| Usefulness | Not actionable | Somewhat useful | Clear resume and interview value |
| Clarity | Confusing | Understandable | Easy to scan and use |
| Robustness | Breaks on normal input | Handles sample inputs | Handles normal, backend, and risk cases |
| Safety | Invents claims | Flags obvious risks | Consistently avoids unsupported claims and factual drift |
| Scope Discipline | Overbuilt | Mostly focused | CLI-only and capstone focused |
| Backend Fallback | Backend failures break workflow | Some failures fall back | Timeout, invalid response, and backend errors fall back cleanly |
| Factual Preservation | Loses key facts | Flags some drift | Flags dollar amounts, team size, years, credentials, degrees, and job titles |
| Judge Readability | Hard to understand | Docs explain basics | README, diagram, and draft explain the project clearly |
| Demo Reproducibility | Demo depends on live services | Some local demo coverage | All core demos run offline in mock mode |
| Gemini Live Mode | Live mode is untested or changes response shape | Mocked Gemini tests cover basic output | Live, auto fallback, invalid JSON, and API mode behavior are covered without requiring real API calls |

## Test Cases

### Case 1: Normal Input

Input:

- Military leadership/equipment maintenance bullet
- Operations coordinator job description

Expected behavior:

- Generates professional and ATS-aligned bullets
- Produces Strong, Partial, or Weak Match label
- Identifies matched and missing keywords
- Produces interview talking points
- Includes safety notes

Pass/fail notes:

- Covered by `tests/test_mission_1_flow.py`

### Case 2: Mock Mode Isolation

Input:

- Valid Mission input
- Translator function that would fail if called

Expected behavior:

- Mock mode does not call backend
- Deterministic output is returned

Pass/fail notes:

- Covered by `tests/test_mission_2_backend_tool.py`

### Case 3: Backend Success

Input:

- Valid Mission input
- Backend tool returns a translation

Expected behavior:

- Resume Agent uses backend translation for the professional bullet
- Workflow continues through job fit and evaluation

Pass/fail notes:

- Covered by `tests/test_mission_2_backend_tool.py`

### Case 4: Backend Failure Fallback

Input:

- Valid Mission input
- Backend timeout or request failure

Expected behavior:

- Workflow falls back to deterministic mock resume output

Pass/fail notes:

- Covered by `tests/test_mission_2_backend_tool.py`

### Case 5: Invalid Backend Response

Input:

- Backend returns JSON without a usable `translation`

Expected behavior:

- Resume Agent falls back to deterministic mock output

Pass/fail notes:

- Covered by `tests/test_mission_2_backend_tool.py`

### Case 6: Unsupported Credential Risk

Input:

- Generated output containing unsupported credential language such as "certified"

Expected behavior:

- Evaluation Agent flags unsupported claim risk

Pass/fail notes:

- Covered by `tests/test_safety_eval.py`

### Case 7: Factual Drift Risk

Input:

- Original input includes `$2.3M`, team size, and job title
- Generated output changes or omits important facts

Expected behavior:

- Evaluation Agent flags factual drift and identifies changed or omitted facts

Pass/fail notes:

- Covered by `tests/test_mission_2_backend_tool.py`

### Case 8: Strong Match Demo

Input:

- `examples/strong_match.json`

Expected behavior:

- Produces a strong operations-coordinator match and saved output

Pass/fail notes:

- Saved output: `examples/outputs/strong_match_output.json`

### Case 9: Partial Match Demo

Input:

- `examples/partial_match.json`

Expected behavior:

- Produces partial role alignment with gaps and interview talking points

Pass/fail notes:

- Saved output: `examples/outputs/partial_match_output.json`

### Case 10: Safety-Risk / Overclaim Demo

Input:

- `examples/safety_risk_overclaim.json`

Expected behavior:

- Shows a senior target role with requirements that should not be invented from junior experience

Pass/fail notes:

- Saved output: `examples/outputs/safety_risk_overclaim_output.json`

### Case 11: Gemini Live Workflow With Mocked Responses

Input:

- Valid Mission input
- Mocked Gemini responses for Resume Agent, Job Fit Agent, and Evaluation Agent

Expected behavior:

- `mode="live"` returns a structured `MissionReport`
- Resume, job-fit, and evaluation fields are populated
- API response shape remains unchanged

Pass/fail notes:

- Covered by `tests/test_live_workflow.py` and `tests/test_api.py`

### Case 12: Strict Live Failure

Input:

- Valid Mission input
- Gemini dependency, credentials, API call, or JSON parsing unavailable

Expected behavior:

- `mode="live"` fails clearly
- It does not silently fall back to mock
- CLI live mode reports missing credentials without a Python traceback

Pass/fail notes:

- Covered by `tests/test_live_workflow.py` and `tests/test_mission_1_flow.py`

### Case 13: Auto Fallback

Input:

- Valid Mission input
- Gemini unavailable

Expected behavior:

- `mode="auto"` falls back to deterministic mock output

Pass/fail notes:

- Covered by `tests/test_live_workflow.py`

### Case 14: Live Smoke Readiness

Input:

- Local environment with or without Gemini credentials

Expected behavior:

- Readiness check reports optional dependency availability and whether credential env vars are set
- Secret values are not printed
- Missing live credentials return exit code `2` before network-backed checks run
- When credentials are configured, the smoke command runs Gemini workflow, `/api/translate` in live mode, and Google ADK runner checks

Pass/fail notes:

- No-credential behavior covered by `tests/test_live_smoke.py`
- Credentialed live behavior passed on 2026-07-13 with `PYTHONPATH=src python3 -m vetpivot.live_smoke`
- The credentialed run validated the Gemini workflow, live `/api/translate`, and Google ADK runner

## Manual Review Checklist

Before calling capstone evidence ready:

- [ ] Mock CLI runs
- [ ] Tests pass
- [ ] All three demo cases run in mock mode
- [ ] Saved outputs exist for all three demo cases
- [ ] README explains problem, track, architecture, agent roles, tool use, ADK alignment, safety, run commands, and limitations
- [ ] Mermaid diagram renders or is readable as text
- [ ] `KAGGLE_SUBMISSION_DRAFT.md` covers title, summary, problem, solution, concepts, safety/evaluation, limitations, and future work
- [ ] No database, frontend, auth, upload parsing, job tracking, MOS database, dashboard, long-term memory, job board integration, or deployment added
- [ ] Safety notes identify unsupported claims or factual drift
- [ ] Gemini live mode, auto fallback, backend helper, and Google ADK limitations are disclosed clearly

## Mission 4 API Bridge Evaluation

API bridge success criteria:

- `POST /api/career-agent` accepts military experience, optional MOS/branch, and target job description.
- `POST /api/translate` accepts the older frontend-compatible `{ "text": "..." }` request shape.
- API response exposes resume bullets, job-fit assessment, missing keywords, interview talking points, evaluation notes, safety flags, unsupported claims, and mode metadata.
- Default API mode is deterministic/offline mock.
- Existing CLI behavior remains unchanged.
- No frontend, deployment, database, auth, dashboard, job tracking, long-term memory, job board integration, or upload parsing is added.

API tests:

- Valid request returns `200` and required fields.
- Explicit mock mode returns a mock report.
- Explicit live mode is accepted and preserves the response shape.
- Unavailable live mode returns a clear error.
- Missing `military_experience` returns validation error.
- Missing `target_job_description` uses discovery mode.
- Frontend-compatible translate request returns `translation` and `mode`.
- Missing translate `text` returns validation error.

## Kaggle Notebook Walkthrough Evaluation

Notebook success criteria:

- `notebooks/vetpivot_career_agent_demo.ipynb` is valid notebook JSON.
- It explains the problem, Agents for Good track, architecture, agent roles, tool usage, Google ADK alignment, safety/evaluation approach, and known limitations.
- It runs all three deterministic mock demo cases offline.
- It displays compact summaries and full structured JSON outputs.
- It does not require live API credentials.
