# AGENTS.md

## Development Philosophy

This project uses AI-assisted development.

The human acts as:

- Product owner
- Architect
- Evaluator
- Final decision-maker

The AI acts as:

- Planner
- Engineer
- Documentation assistant
- Testing assistant

The goal is rapid iteration with readable code, clear evaluation, and disciplined scope control.

## Before Any Implementation

Before writing or changing code, Codex should provide:

### Plan

- What will be built or changed
- Why this approach is appropriate
- What files are likely to change

### Risks

- Technical risks
- Ambiguities
- Assumptions
- Data, privacy, or safety concerns if relevant

### Scope Creep Check

- Identify anything that should not be added yet
- Recommend the smallest viable implementation
- Avoid adding systems that were not requested

### Implementation Steps

- Clear ordered steps
- Small, reviewable changes
- Verification steps before calling work complete

If the task is ambiguous, ask for clarification before implementing.

## Project Constraints

Prefer:

- Simple solutions
- Readable code
- Small focused changes
- Working software
- Clear documentation
- Testable behavior
- Explicit tradeoffs

Avoid:

- Overbuilding
- Premature optimization
- Unrequested features
- Excessive abstractions
- Hidden behavior
- Large rewrites unless requested

## Required Documentation

Keep these files updated when relevant:

- `README.md`
- `PROJECT_STATUS.md`
- `EVALS.md`
- `DECISIONS.md`

`PROJECT_STATUS.md` should always include:

- Completed
- In Progress
- Remaining
- Risks
- Next Recommended Step

## Evaluation Requirements

For every meaningful feature, define:

- What success looks like
- How it will be tested
- Expected behavior
- Failure cases
- Safety concerns, if any

Prefer automated tests when practical. Use manual review checklists when automation is not yet justified.

## Scope Control

Do not add the following unless explicitly requested:

- Authentication
- Databases
- Analytics
- Dashboards
- Payment systems
- User accounts
- Frontend redesigns
- Large infrastructure changes
- Background jobs
- Complex deployment pipelines

## After Implementation

After coding, Codex should report:

### Summary

- What changed

### Files Changed

- Major files changed

### Tests Run

- Commands run
- Results

### Remaining Work

- What is still incomplete

### Next Recommended Step

- One clear next action

## Documentation Log Policy

Use one running file per documentation category by default:

- `PROJECT_STATUS.md` is the current project snapshot. Keep it short and update it as work changes.
- `DECISIONS.md` is the running decision log. Append dated decisions instead of replacing older ones.
- `EVALS.md` is the running evaluation and testing file. Add or update test cases as features are built.
- `PROJECT_BRIEF.md` is the core project brief. Update it only when the project direction changes.

Do not create new status, decision, or evaluation files unless the project has grown enough that the existing file is hard to scan.

If the project becomes large, recommend a split such as:

- `docs/decisions/0001-decision-title.md`
- `docs/evals/feature-or-workflow-name.md`

Prefer the single-file approach until there is a clear reason to split.

## File Visibility While Editing

When changing a Markdown file or any other project file, Codex should make the changed file easy for the human to inspect.

Preferred behavior:

- Open or present the changed file in the browser sidebar or VS Code, whichever is most efficient for the situation.
- For Markdown files, prefer a readable rendered view when available, or a source view if that is faster and clearer.
- If browser or editor access is blocked, unavailable, or would require starting services unnecessarily, report the changed path and show the relevant excerpt in chat.
- Do not start servers, launch unrelated apps, or perform extra setup just to display a file unless the human approves it.
