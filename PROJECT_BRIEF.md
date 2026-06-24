# PROJECT_BRIEF.md

## Project Name

VetPivot Career Agent

## One-Sentence Description

VetPivot Career Agent helps veterans translate military experience into civilian resume language, evaluate job fit against a target role, and identify gaps or risks before applying.

## Problem

Transitioning service members and military veterans often have valuable experience that is difficult to communicate in civilian hiring language.

Common pain points:

- Military terminology may not map clearly to civilian job requirements.
- Resume bullets may undersell leadership, operations, logistics, technical, or safety experience.
- Applicants may not know whether their experience matches a target role.
- Missing keywords can reduce ATS visibility.
- Veterans may need help turning experience into interview-ready talking points.
- Career advice can become inaccurate or unsafe if it exaggerates experience or invents qualifications.

## Target User

Primary user:

Transitioning service members and military veterans seeking civilian employment.

Secondary users:

Veteran career coaches and mentors who help veterans prepare resumes, evaluate roles, and practice interview positioning.

## Solution

This project will:

1. Translate military experience into clear civilian resume language.
2. Evaluate job fit against a target civilian job description.
3. Identify missing keywords, gaps, risks, and interview talking points.
4. Evaluate generated outputs for accuracy, usefulness, and safety.

## Success Criteria

The project is successful when:

- A user can provide a military bullet or experience description and receive a professional civilian resume bullet.
- The system can generate an ATS-optimized version without inventing facts.
- The system can compare the experience against a target job description and summarize match strength.
- The system can identify missing keywords or likely gaps.
- The system can suggest interview talking points grounded in the provided experience.
- The system can produce evaluation and safety notes that flag exaggeration, unsupported claims, or risky wording.

## Core Workflow

```text
User provides military experience or resume bullet
    ↓
User optionally provides MOS/branch and target job description
    ↓
Resume Agent translates the experience into civilian resume language
    ↓
Job Fit Agent analyzes the target role and compares fit
    ↓
Evaluation Agent reviews accuracy, safety, and usefulness
    ↓
System returns resume bullets, fit analysis, missing keywords, interview talking points, and safety notes
```

## Required Features

- Input for military experience or resume bullet
- Optional MOS/branch context
- Input for target job description
- Resume Agent for civilian translation
- ATS-optimized resume bullet generation
- Job Fit Agent for role analysis and match evaluation
- Missing keyword identification
- Interview talking point suggestions
- Evaluation Agent for accuracy, safety, and quality review
- Final structured output that is easy to inspect in a demo

## Explicit Non-Goals

Do not build yet:

- Authentication
- User accounts
- Payments
- Job application tracking
- Database storage
- Full recruiter dashboard
- Full MOS database
- Long-term memory
- Social features
- Frontend redesign
- Mobile application

## Architecture

Main components:

- Resume Agent: translates military experience into civilian resume language and ATS-focused bullets.
- Job Fit Agent: analyzes a target job description, extracts requirements and keywords, and evaluates fit.
- Evaluation Agent: reviews outputs for accuracy, safety, unsupported claims, clarity, and usefulness.
- Orchestrator: coordinates the agents and assembles the final response.
- Demo interface or script: provides a focused Kaggle capstone demonstration of the workflow.

## Tools / APIs

Potential tools/APIs:

- LLM API for agent reasoning and generation
- Keyword extraction or structured parsing helper
- Evaluation rubric for output review
- Optional local fixtures for sample military bullets and job descriptions

Final tool/API choices are not yet decided.

## Data

Inputs:

- Military experience or resume bullet
- Optional MOS/branch
- Target civilian job description

Outputs:

- Professional civilian resume bullet
- ATS-optimized resume bullet
- Match analysis
- Missing keywords
- Interview talking points
- Evaluation and safety notes

Stored data, if any:

- None for the first version. The capstone demo should avoid database storage unless explicitly added later.

## Safety / Risk Notes

Potential risks:

- Inventing qualifications, metrics, tools, certifications, or experience not provided by the user.
- Translating military terms too loosely and changing the meaning of the original experience.
- Overstating job fit or giving misleading application advice.
- Producing ATS keyword stuffing instead of truthful resume language.
- Mishandling sensitive personal, service, or employment information.
- Expanding into a full career platform before the core workflow is proven.

Guardrails:

- Do not invent facts that are not present or reasonably implied by the user input.
- Clearly distinguish strong matches, partial matches, gaps, and unknowns.
- Flag unsupported claims and risky wording.
- Keep recommendations grounded in the provided experience and target job description.
- Avoid storing user data in the first version.
- Keep the first version focused on the capstone demo workflow.

## Demo Plan

The first successful demo should show:

1. A veteran pastes a military bullet and a civilian job description.
2. The Resume Agent translates the experience into civilian resume language.
3. The Job Fit Agent analyzes the target role and compares the user experience against it.
4. The Evaluation Agent reviews the output for accuracy, safety, and usefulness.
5. The final result includes a professional resume bullet, ATS version, match analysis, missing keywords, interview talking points, and evaluation/safety notes.

## Project Context

This project is a focused Kaggle capstone demonstrating multi-agent design, tool use, evaluation, and safety.
