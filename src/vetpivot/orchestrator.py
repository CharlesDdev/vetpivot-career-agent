"""Mission workflow orchestration."""

from __future__ import annotations

from collections.abc import Callable

from vetpivot.agents.evaluation_agent import run_evaluation_agent, run_live_evaluation_agent
from vetpivot.agents.job_fit_agent import run_job_fit_agent, run_live_job_fit_agent
from vetpivot.agents.resume_agent import run_live_resume_agent, run_resume_agent
from vetpivot.gemini_client import GeminiGenerator, GeminiUnavailableError, generate_json
from vetpivot.schemas import MissionInput, MissionReport

Translator = Callable[[str], str]


def run_local_workflow(data: MissionInput, *, use_backend: bool = False, translator: Translator | None = None) -> MissionReport:
    data.validate()
    resume_kwargs = {"use_backend": use_backend}
    if translator is not None:
        resume_kwargs["translator"] = translator
    resume = run_resume_agent(data, **resume_kwargs)
    job_fit = run_job_fit_agent(data, resume)
    evaluation = run_evaluation_agent(data, resume, job_fit)
    mode = "backend" if use_backend and not resume.professional_resume_bullet.startswith("Translated military experience") else "mock"
    return MissionReport(input=data, resume=resume, job_fit=job_fit, evaluation=evaluation, mode=mode)


def run_mock_workflow(data: MissionInput) -> MissionReport:
    return run_local_workflow(data, use_backend=False)


def run_gemini_workflow(data: MissionInput, generator: GeminiGenerator = generate_json) -> MissionReport:
    """Run the live Gemini-powered agent workflow."""
    data.validate()
    resume = run_live_resume_agent(data, generator=generator)
    job_fit = run_live_job_fit_agent(data, resume, generator=generator)
    evaluation = run_live_evaluation_agent(data, resume, job_fit, generator=generator)
    return MissionReport(input=data, resume=resume, job_fit=job_fit, evaluation=evaluation, mode="live")


def run_workflow(data: MissionInput, mode: str = "auto", gemini_generator: GeminiGenerator | None = None) -> MissionReport:
    """Run Mission workflow in mock, strict live Gemini, or auto fallback mode."""
    data.validate()
    generator = gemini_generator or generate_json
    if mode == "mock":
        return run_mock_workflow(data)
    if mode == "live":
        return run_gemini_workflow(data, generator=generator)
    if mode == "auto":
        try:
            return run_gemini_workflow(data, generator=generator)
        except GeminiUnavailableError:
            return run_mock_workflow(data)
    raise ValueError("mode must be one of: auto, mock, live")
