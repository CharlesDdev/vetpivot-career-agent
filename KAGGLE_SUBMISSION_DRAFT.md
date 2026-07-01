# Kaggle Submission Draft

## Project Title

VetPivot Career Agent

## Summary

VetPivot Career Agent is a Gemini-powered multi-agent career support prototype that helps veterans translate military experience into civilian resume language, compare that experience against a target job description, and identify gaps or safety risks before applying.

The project is designed for the Kaggle / Google AI Agents Capstone under the **Agents for Good** track. It demonstrates specialized agents, Gemini live behavior, tool use, fallback behavior, and safety-focused evaluation in a small reproducible CLI demo.

## Problem

Transitioning service members and veterans often struggle to explain military experience in terms civilian employers and applicant tracking systems understand. Military roles may include leadership, operations, logistics, safety, maintenance, training, or accountability responsibilities, but those strengths can be hidden behind military terminology.

At the same time, AI-generated career advice can create risk if it exaggerates experience, invents certifications, changes important facts, or overstates job fit.

## Solution

VetPivot accepts:

- Military experience or resume bullet
- Optional MOS/branch context
- Target civilian job description

It returns:

- Professional civilian resume bullet
- ATS-aligned resume bullet
- Match label and analysis
- Matched and missing keywords
- Interview talking points
- Evaluation and safety notes

The prototype uses three focused agents:

- Resume Agent
- Job Fit Agent
- Evaluation Agent

The live workflow uses Gemini for the Resume Agent, Job Fit Agent, and Evaluation Agent. Mock mode remains deterministic and offline for judging, and auto mode tries Gemini first before falling back to mock output if live mode is unavailable.

## Concepts Demonstrated

- Multi-agent decomposition
- Agent orchestration
- Gemini-powered live agent behavior
- Tool use through a backend translation endpoint
- Deterministic fallback behavior
- Google ADK-facing `root_agent` structure
- Function tool wrapper for ADK usage
- Safety-focused evaluation
- Factual drift detection
- Reproducible CLI demos and tests

## Safety / Evaluation

The project includes automated tests and a documented evaluation rubric.

Safety checks focus on:

- Unsupported credentials
- Unsupported degrees
- Changed or omitted dollar amounts
- Changed or omitted team size
- Changed or omitted years of experience
- Risky job-title or overclaim language
- Overstated fit labels

The project also includes three deterministic demo cases:

1. Strong match
2. Partial match
3. Safety-risk / overclaim case

Saved outputs are included so judges can inspect expected behavior without relying on a live backend.

Live-mode behavior is tested with mocked Gemini responses so automated tests do not require real credentials or network calls.

## Limitations

- Mock mode is deterministic and intentionally simple.
- Gemini live mode requires `GEMINI_API_KEY` or `GOOGLE_API_KEY`, the optional `google-genai` dependency, and a supported `VETPIVOT_GEMINI_MODEL`.
- Backend translation depends on network and local Python certificate trust when that helper is used.
- Google ADK-facing structure is included, but the local live workflow uses Gemini directly.
- The project does not include a full MOS database, resume upload parser, database, frontend, dashboard, authentication, job tracking, job board integration, long-term memory, or deployment.
- Fit labels are simple categories, not numeric scores.

## Future Work

- Validate live Google ADK execution with Gemini credentials.
- Improve backend SSL/certificate setup for local Python runs.
- Add more veteran career scenarios across branches and roles.
- Add richer evaluation datasets for factual preservation and job-fit calibration.
- Add optional human review workflows for career coaches.
