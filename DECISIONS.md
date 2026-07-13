# DECISIONS.md

Use this file to record meaningful project decisions.

## Decision Template

### YYYY-MM-DD - Decision Title

**Decision:**

**Why:**

**Alternatives considered:**

**Tradeoffs:**

**Status:** Proposed / Accepted / Rejected / Revisited

## Decisions

### 2026-06-24 - Use Reusable AI-Assisted Development Template

**Decision:**
Start projects with reusable context files before writing application code.

**Why:**
This reduces repeated prompting, improves scope control, and gives Codex persistent project instructions.

**Alternatives considered:**
Prompting manually each session or creating project structure without shared operating instructions.

**Tradeoffs:**
Requires a little setup up front, but improves consistency and evaluation quality later.

**Status:** Accepted

### 2026-06-24 - Use Google ADK With Mock Fallback for Mission 1

**Decision:**
Implement Mission 1 as a CLI-first workflow with deterministic mock agents for tests and an optional Google ADK live path for Gemini.

**Why:**
The Kaggle / Google AI Agents Capstone needs a Google ADK-oriented implementation, while local development and tests need to run reliably without credentials.

**Alternatives considered:**
Building only live Gemini calls, building only mocked agents, or starting with a frontend.

**Tradeoffs:**
The mock path is more reliable for tests but does not prove live model behavior. The live path may need adjustment after installing the current Google ADK package and configuring credentials.

**Status:** Accepted

### 2026-06-24 - Add VetPivot Backend Translation Tool With Fallback

**Decision:**
Connect the Resume Agent to the existing VetPivot backend translation endpoint while preserving deterministic mock mode and fallback behavior.

**Why:**
Mission 2 needs to demonstrate tool use against the existing VetPivot Resume Optimizer backend without making local tests or demos dependent on network availability.

**Alternatives considered:**
Replacing mock mode entirely, adding a new CLI mode, or moving all resume generation into Google ADK immediately.

**Tradeoffs:**
The CLI remains simple and tests stay reliable, but backend behavior is only used in auto/live local workflow when the HTTP call succeeds. Backend output still needs factual drift review because it can alter important details.

**Status:** Accepted

### 2026-06-24 - Prepare Kaggle Evidence Package With Deterministic Demos

**Decision:**
Create a judge-facing evidence package using expanded README documentation, Mermaid architecture diagram, deterministic sample inputs, saved mock outputs, and a Kaggle submission draft.

**Why:**
The capstone should be easy to understand, run, and evaluate without requiring live services, credentials, frontend setup, or deployment.

**Alternatives considered:**
Building a frontend demo, relying only on live backend/ADK execution, or submitting source code without saved outputs.

**Tradeoffs:**
Deterministic mock outputs are easier for judges to reproduce, but they do not demonstrate full live model behavior. Live backend and ADK limitations remain documented for transparency.

**Status:** Accepted

### 2026-06-24 - Add FastAPI Bridge Without Building Frontend

**Decision:**
Expose the existing Career Agent orchestrator through a small FastAPI endpoint at `POST /api/career-agent` while preserving the CLI and deterministic mock mode.

**Why:**
The existing VetPivot frontend will eventually need an API surface, but Mission 4 should avoid frontend, deployment, database, authentication, and job-tracking scope.

**Alternatives considered:**
Building a new frontend, changing the CLI interface, or deploying the API immediately.

**Tradeoffs:**
The API bridge gives the frontend a stable integration target, but the response contract may still need adjustment after frontend wiring begins.

**Status:** Accepted

### 2026-06-24 - Add Offline Kaggle Notebook Walkthrough

**Decision:**
Create a notebook walkthrough that explains the project and runs the three deterministic mock demo cases offline.

**Why:**
Judges should be able to understand and evaluate the project without inspecting every source file or configuring live credentials.

**Alternatives considered:**
Relying only on README documentation or requiring live backend/API execution.

**Tradeoffs:**
The notebook is reproducible and judge-friendly, but it demonstrates mock-mode behavior rather than live Gemini/backend behavior.

**Status:** Accepted

### 2026-07-10 - Add Frontend-Compatible Translate Endpoint

**Decision:**
Add `POST /api/translate` as a thin compatibility adapter over the existing Career Agent workflow.

**Why:**
The repo does not contain frontend source, but the existing VetPivot frontend/backend contract uses a simple translation request shape. Adding a small adapter lets the deployed frontend call this service without replacing the structured `/api/career-agent` endpoint.

**Alternatives considered:**
Building a frontend in this repo, changing the existing `/api/career-agent` contract, or deploying before local smoke tests.

**Tradeoffs:**
The compatibility endpoint returns only `translation` and `mode`, so richer career-agent fields remain available through `/api/career-agent`.

**Status:** Accepted

### 2026-07-13 - Add Credential-Gated Live Smoke Helper

**Decision:**
Add `vetpivot.live_smoke` as a local validation helper for Gemini workflow, API live mode, and Google ADK runner checks.

**Why:**
Live validation depends on external credentials and network-backed model calls. A dedicated helper makes readiness visible, avoids printing secret values, and gives the project one command to run after credentials are configured.

**Alternatives considered:**
Leaving live checks as scattered README commands, running live calls inside the normal test suite, or committing credentials for repeatability.

**Tradeoffs:**
The helper improves operational clarity, but credentialed live behavior still must be run manually because tests should remain offline and deterministic.

**Status:** Accepted

### 2026-07-13 - Keep ADK Live Path Compatible With Installed Google ADK

**Decision:**
Update the Google ADK live runner to support async session creation, use the shared Gemini model configuration, and expose runtime function-tool annotations.

**Why:**
Credentialed live smoke testing showed that the installed Google ADK package requires awaited session creation, rejects stale unavailable model names, and cannot parse stringified tool annotations for automatic function calling.

**Alternatives considered:**
Skipping the ADK smoke check, pinning only older dependencies, or maintaining a separate ADK-only model default.

**Tradeoffs:**
The ADK path is now more aligned with the working Gemini API path, but live ADK behavior still depends on external Google package and model availability.

**Status:** Accepted
