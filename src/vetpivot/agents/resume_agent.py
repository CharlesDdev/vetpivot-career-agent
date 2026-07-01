"""Resume Agent for translating military experience."""

from __future__ import annotations

import json
from collections.abc import Callable

from vetpivot.gemini_client import GeminiGenerator, GeminiUnavailableError, generate_json
from vetpivot.schemas import MissionInput, ResumeOutput
from vetpivot.tools.vetpivot_translate_tool import VetPivotTranslateError, translate_text

Translator = Callable[[str], str]

RESUME_LIVE_SYSTEM_INSTRUCTION = (
    "You are the VetPivot Resume Agent. Translate military experience into truthful civilian resume language. "
    "Do not invent facts, metrics, credentials, tools, certifications, degrees, job titles, or years of experience. "
    "Return only valid JSON with keys professional_resume_bullet and ats_optimized_bullet."
)


def _require_text(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise GeminiUnavailableError(f"Gemini resume response missing usable {key}.")
    return value.strip()


def run_mock_resume_agent(data: MissionInput) -> ResumeOutput:
    """Return deterministic Mission 1 resume bullets for local tests and demos."""
    source = data.military_experience.strip().rstrip(".")
    context = f" ({data.mos_branch.strip()})" if data.mos_branch.strip() else ""

    professional = (
        f"Translated military experience{context}: {source}, emphasizing leadership, "
        "operational coordination, accountability, and measurable mission support in civilian terms."
    )
    ats = (
        "Applied leadership, operations management, team coordination, equipment accountability, "
        f"risk management, and process improvement experience to {source.lower()}."
    )
    return ResumeOutput(professional_resume_bullet=professional, ats_optimized_bullet=ats)


def run_backend_resume_agent(data: MissionInput, translator: Translator | None = None) -> ResumeOutput:
    """Use the VetPivot backend translation tool for the professional bullet."""
    active_translator = translator or translate_text
    translated = active_translator(data.military_experience)
    source = data.military_experience.strip().rstrip(".")
    ats = (
        "Applied leadership, operations management, team coordination, equipment accountability, "
        f"risk management, and process improvement experience to {source.lower()}."
    )
    return ResumeOutput(professional_resume_bullet=translated, ats_optimized_bullet=ats)


def run_live_resume_agent(data: MissionInput, generator: GeminiGenerator = generate_json) -> ResumeOutput:
    """Use Gemini to produce structured resume bullets."""
    prompt = json.dumps(
        {
            "military_experience": data.military_experience,
            "mos_branch": data.mos_branch,
            "target_job_description": data.target_job_description,
            "required_json_schema": {
                "professional_resume_bullet": "truthful civilian resume bullet",
                "ats_optimized_bullet": "ATS-aligned resume bullet grounded only in the input",
            },
        },
        indent=2,
    )
    payload = generator(RESUME_LIVE_SYSTEM_INSTRUCTION, prompt)
    return ResumeOutput(
        professional_resume_bullet=_require_text(payload, "professional_resume_bullet"),
        ats_optimized_bullet=_require_text(payload, "ats_optimized_bullet"),
    )


def run_resume_agent(
    data: MissionInput,
    *,
    use_backend: bool = False,
    translator: Translator | None = None,
) -> ResumeOutput:
    """Run the Resume Agent with optional backend-tool fallback."""
    if not use_backend:
        return run_mock_resume_agent(data)
    try:
        return run_backend_resume_agent(data, translator=translator)
    except VetPivotTranslateError:
        return run_mock_resume_agent(data)
