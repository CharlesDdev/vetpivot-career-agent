# Kaggle Submission Draft

## Project Title

VetPivot Career Agent

## Summary

VetPivot Career Agent is a multi-agent career support prototype that helps veterans translate military experience into civilian resume language, compare that experience against a target job description, and identify gaps or safety risks before applying.

The project is designed for the Kaggle / Google AI Agents Capstone under the **Agents for Good** track. It demonstrates specialized agents, tool use, fallback behavior, and safety-focused evaluation in a small reproducible CLI demo.

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

The Resume Agent can use the VetPivot backend translation endpoint as a tool in backend-enabled modes, while mock mode remains deterministic and offline for judging.

## Concepts Demonstrated

- Multi-agent decomposition
- Agent orchestration
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

## Limitations

- Mock mode is deterministic and intentionally simple.
- Backend translation depends on network and local Python certificate trust.
- Google ADK live execution is optional and not required for the offline evidence package.
- The project does not include a full MOS database, resume upload parser, database, frontend, dashboard, authentication, job tracking, job board integration, long-term memory, or deployment.
- Fit labels are simple categories, not numeric scores.

## Future Work

- Add a Kaggle notebook walkthrough.
- Validate live Google ADK execution with Gemini credentials.
- Improve backend SSL/certificate setup for local Python runs.
- Add more veteran career scenarios across branches and roles.
- Add richer evaluation datasets for factual preservation and job-fit calibration.
- Add optional human review workflows for career coaches.
