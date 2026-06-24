"""Google ADK agent definitions for VetPivot.

The CLI can run without Google ADK in mock mode. Live mode imports these
objects only when credentials and the google-adk package are available.
"""

from __future__ import annotations

import os

from vetpivot.tools.vetpivot_translate_tool import vetpivot_translate

DEFAULT_MODEL = os.getenv("VETPIVOT_GEMINI_MODEL", "gemini-2.0-flash-lite")

try:
    from google.adk.agents.llm_agent import Agent
except Exception:  # pragma: no cover - exercised only when ADK is installed
    try:
        from google.adk.agents import Agent
    except Exception:
        Agent = None  # type: ignore[assignment]


RESUME_AGENT_INSTRUCTION = (
    "Translate the provided military experience into truthful civilian resume language. "
    "Use the vetpivot_translate tool when a backend translation is useful. "
    "Create one professional bullet and one ATS-aligned bullet. Do not invent facts, "
    "metrics, credentials, tools, or certifications."
)

JOB_FIT_AGENT_INSTRUCTION = (
    "Compare the candidate experience to the target job description. Use only these fit labels: "
    "Strong Match, Partial Match, Weak Match. Identify matched keywords, missing keywords, "
    "and interview talking points. Do not use numeric scoring."
)

EVALUATION_AGENT_INSTRUCTION = (
    "Review the generated resume and job-fit output. Flag unsupported claims, exaggeration, "
    "risky wording, invented credentials, ATS keyword stuffing, and factual drift in dollar amounts, "
    "team size, certifications, degrees, job titles, or years of experience."
)

ROOT_AGENT_INSTRUCTION = (
    "Coordinate a three-step workflow: resume translation, job fit analysis, then evaluation. "
    "Return a concise structured report with professional_resume_bullet, ats_optimized_bullet, "
    "fit_label, match_analysis, missing_keywords, interview_talking_points, evaluation_notes, "
    "and safety_flags."
)


def _require_adk() -> None:
    if Agent is None:
        raise RuntimeError("Google ADK is not installed. Install with: pip install -e .[live]")


def build_resume_agent():
    _require_adk()
    return Agent(
        name="resume_agent",
        model=DEFAULT_MODEL,
        description="Translates military experience into civilian resume bullets.",
        instruction=RESUME_AGENT_INSTRUCTION,
        tools=[vetpivot_translate],
    )


def build_job_fit_agent():
    _require_adk()
    return Agent(
        name="job_fit_agent",
        model=DEFAULT_MODEL,
        description="Evaluates fit against a target civilian job description.",
        instruction=JOB_FIT_AGENT_INSTRUCTION,
    )


def build_evaluation_agent():
    _require_adk()
    return Agent(
        name="evaluation_agent",
        model=DEFAULT_MODEL,
        description="Reviews output for accuracy, usefulness, and safety.",
        instruction=EVALUATION_AGENT_INSTRUCTION,
    )


def build_root_agent():
    _require_adk()
    return Agent(
        name="vetpivot_career_agent",
        model=DEFAULT_MODEL,
        description="Coordinates VetPivot Mission 1 resume translation, job fit, and evaluation agents.",
        instruction=ROOT_AGENT_INSTRUCTION,
        sub_agents=[build_resume_agent(), build_job_fit_agent(), build_evaluation_agent()],
    )


root_agent = build_root_agent() if Agent is not None else None
