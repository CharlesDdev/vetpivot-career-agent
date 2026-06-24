"""Mission workflow orchestration."""

from __future__ import annotations

from collections.abc import Callable

from vetpivot.agents.evaluation_agent import run_evaluation_agent
from vetpivot.agents.job_fit_agent import run_job_fit_agent
from vetpivot.agents.resume_agent import run_resume_agent
from vetpivot.live_adk import run_live_adk
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


def run_workflow(data: MissionInput, mode: str = "auto") -> MissionReport | str:
    """Run Mission workflow in mock, backend-enabled auto, or live ADK mode."""
    data.validate()
    if mode == "mock":
        return run_mock_workflow(data)
    if mode == "live":
        try:
            return run_local_workflow(data, use_backend=True)
        except RuntimeError:
            return run_mock_workflow(data)
    if mode == "auto":
        return run_local_workflow(data, use_backend=True)
    if mode == "adk":
        return run_live_adk(data)
    raise ValueError("mode must be one of: auto, mock, live")
