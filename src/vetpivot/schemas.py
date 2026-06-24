"""Dataclasses for the Mission 1 CLI workflow."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

FitLabel = Literal["Strong Match", "Partial Match", "Weak Match"]


@dataclass(frozen=True)
class MissionInput:
    military_experience: str
    target_job_description: str
    mos_branch: str = ""

    def validate(self) -> None:
        if not self.military_experience.strip():
            raise ValueError("military_experience is required")
        if not self.target_job_description.strip():
            raise ValueError("target_job_description is required")


@dataclass(frozen=True)
class ResumeOutput:
    professional_resume_bullet: str
    ats_optimized_bullet: str


@dataclass(frozen=True)
class JobFitOutput:
    fit_label: FitLabel
    match_analysis: str
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    interview_talking_points: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvaluationOutput:
    accuracy_notes: str
    safety_flags: list[str] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)
    usefulness_notes: str = ""


@dataclass(frozen=True)
class MissionReport:
    input: MissionInput
    resume: ResumeOutput
    job_fit: JobFitOutput
    evaluation: EvaluationOutput
    mode: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
