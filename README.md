VetPivot Career Agent

VetPivot Career Agent is a multi-agent career assistant designed to help transitioning service members and veterans translate military experience into civilian career opportunities.

Rather than acting as a simple resume translator, VetPivot now coordinates multiple specialized AI agents that work together to:

* Translate military experience into professional civilian resume language
* Generate an ATS-optimized version of the same experience
* Evaluate job fit against a target civilian position
* Identify missing keywords and transferable skills
* Generate interview talking points
* Detect unsupported claims and potential factual drift before an application is submitted

The project demonstrates modern agent orchestration using Google ADK-inspired architecture while maintaining a simple web experience for end users.

⸻

Problem

Military experience is often difficult to communicate in civilian hiring language.

Veterans may have years of leadership, logistics, maintenance, operations, safety, communications, or technical experience that is described using military terminology unfamiliar to civilian recruiters or Applicant Tracking Systems (ATS).

This creates several challenges:

* Valuable experience is overlooked.
* Resume bullets miss important civilian terminology.
* Applicants overstate or understate job fit.
* AI-generated resumes can accidentally invent certifications, degrees, metrics, or responsibilities.

VetPivot Career Agent focuses on helping veterans present truthful, understandable, and competitive resumes while providing additional career guidance.

⸻

Kaggle Track

Agents for Good

VetPivot Career Agent supports veterans during the military-to-civilian transition by combining resume translation, job-fit evaluation, and AI safety into a single workflow.

⸻

Current Status

Current implementation includes:

* ✅ React web application
* ✅ FastAPI Career Agent API
* ✅ Multi-agent orchestration
* ✅ Resume Agent
* ✅ Job Fit Agent
* ✅ Evaluation Agent
* ✅ VetPivot Translation Tool
* ✅ Google ADK-compatible architecture
* ✅ Offline mock mode
* ✅ Local API integration
* ✅ Job Fit visualization
* ✅ Safety evaluation
* ✅ 17 automated tests

⸻

What VetPivot Career Agent Does

The user provides:

* Military experience
* Optional MOS / Branch
* Target civilian job description

The Career Agent returns:

* Professional resume bullet
* ATS-optimized resume bullet
* Job Fit assessment
* Matched keywords
* Missing keywords
* Interview talking points
* Safety and evaluation notes
* Unsupported claim detection

The experience is presented through the existing VetPivot web interface while the Career Agent API coordinates the underlying workflow.

⸻

Current Architecture

React VetPivot UI
        │
        ▼
Career Agent API (FastAPI)
        │
        ▼
Orchestrator
        │
 ┌──────┼──────────────┐
 ▼      ▼              ▼
Resume  Job Fit    Evaluation
Agent   Agent      Agent
        │
        ▼
VetPivot Translation Tool
        │
        ▼
Structured Career Guidance

⸻

Agent Responsibilities

Resume Agent

Responsible for:

* Translating military experience into civilian language
* Producing:
    * Professional Resume Bullet
    * ATS-Optimized Resume Bullet
* Calling the VetPivot Translation Tool when available
* Falling back to deterministic mock behavior if needed

⸻

Job Fit Agent

Responsible for:

* Comparing experience against a target job
* Determining:
    * Strong Match
    * Partial Match
    * Weak Match
* Identifying:
    * Matched keywords
    * Missing keywords
    * Interview talking points

⸻

Evaluation Agent

Responsible for reviewing AI output before presenting it to the user.

Checks include:

* Unsupported claims
* Factual drift
* Risky wording
* Dollar amounts
* Team size
* Certifications
* Degrees
* Years of experience
* Job titles

⸻

Tool Usage

Mission 2 introduced the VetPivot Translation Tool.

The Resume Agent may call the existing VetPivot backend instead of relying entirely on prompt generation.

When unavailable, the workflow automatically falls back to deterministic mock mode.

This allows:

* Offline development
* Reliable testing
* Consistent demonstrations
* Graceful failure handling

⸻

Google ADK Alignment

The project follows Google ADK design principles.

Included:

* Root Agent
* Specialized sub-agents
* Tool registration
* Orchestration layer
* Typed schemas
* Evaluation layer
* Deterministic testing

Live Gemini execution is optional and can be enabled later without changing the overall architecture.

⸻

Evaluation & Safety

VetPivot treats evaluation as part of the workflow rather than something performed afterward.

Safety checks include:

* Unsupported credentials
* Unsupported certifications
* Unsupported education
* Unsupported years of experience
* Factual drift detection
* Resume honesty validation

Evaluation artifacts include:

* Automated tests
* Demo scenarios
* Evaluation rubric
* Manual review checklist

⸻

Running the Project

Recommended — Web Application

1. Start the Career Agent API

cd vetpivot-career-agent
PYTHONPATH=src uvicorn vetpivot.api:app --host 127.0.0.1 --port 8000

2. Start the VetPivot Frontend

cd vetpivot-frontend
npm install
npm run dev

3. Open the application

http://127.0.0.1:3000

The frontend communicates with:

POST /api/career-agent

running locally.

⸻

CLI (Developer Mode)

The CLI remains available for development, testing, and reproducible demonstrations.

Run a demo:

PYTHONPATH=src python3 -m vetpivot.main \
--mode mock \
--input examples/strong_match.json

⸻

Running Tests

Career Agent:

PYTHONPATH=src python3 -m pytest -p no:cacheprovider

Frontend:

npm run build

Current status:

* ✅ 17 tests passing
* ✅ Frontend build passing

⸻

Demo Scenarios

Three deterministic demo cases are included.

Strong Match

Demonstrates:

* Resume translation
* Strong job alignment
* Minimal skill gaps

⸻

Partial Match

Demonstrates:

* Transferable skills
* Missing keywords
* Interview preparation guidance

⸻

Safety Risk

Demonstrates:

* Unsupported claim detection
* Degree requirements
* Certification requirements
* Years of experience validation

⸻

Current Limitations

Current limitations include:

* Job Fit uses qualitative labels rather than a validated scoring model.
* Mock mode remains the default demonstration path.
* Live Google ADK/Gemini integration is optional and not required for local use.
* Backend SSL configuration may vary by local Python environment.
* No persistent user accounts.
* No database.
* No recruiter dashboard.
* No job application tracking.
* No long-term memory.
* No deployment pipeline.

⸻

Future Roadmap

Planned enhancements include:

* Live Google ADK execution
* Gemini-powered production workflow
* Deployment of the Career Agent API
* Enhanced job-fit reasoning
* STAR interview response generation
* Resume version comparison
* MOS knowledge integration
* Production authentication
* Persistent user sessions

⸻

Repository Structure

React Frontend
        │
        ▼
Career Agent API
        │
        ▼
Multi-Agent System
        ├── Resume Agent
        ├── Job Fit Agent
        ├── Evaluation Agent
        └── VetPivot Translation Tool
Supporting Assets
├── Demo Notebook
├── Evaluation Rubrics
├── Sample Inputs
├── Sample Outputs
├── Automated Tests
└── Documentation

⸻

Vision

The original VetPivot project translated military experience into civilian resume language.

VetPivot Career Agent expands that idea into a complete AI-assisted career guidance system.

Instead of simply rewriting resume bullets, the application helps veterans understand how their experience aligns with civilian careers, identify gaps before applying, prepare for interviews, and verify that generated content remains truthful and defensible.

The long-term goal is to provide veterans with an AI career advisor that is transparent, trustworthy, and grounded in accurate representation of their military experience.
