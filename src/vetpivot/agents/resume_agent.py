"""Resume Agent for translating military experience."""

from __future__ import annotations

from collections.abc import Callable

from vetpivot.schemas import MissionInput, ResumeOutput
from vetpivot.tools.vetpivot_translate_tool import VetPivotTranslateError, translate_text

Translator = Callable[[str], str]


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
