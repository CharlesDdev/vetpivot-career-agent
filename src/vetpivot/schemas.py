"""Dataclasses for the Career Agent workflow."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

FitLabel = Literal["Strong Match", "Partial Match", "Weak Match"]
WorkflowMode = Literal["targeted", "discovery"]


@dataclass(frozen=True)
class MissionInput:
    military_experience: str
    target_job_description: str = ""
    mos_branch: str = ""

    def validate(self) -> None:
        if not self.military_experience.strip():
            raise ValueError("military_experience is required")

    @property
    def workflow_mode(self) -> WorkflowMode:
        if self.target_job_description.strip():
            return "targeted"
        return "discovery"


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
class SuggestedRole:
    title: str
    explanation: str
    onet_code: str = ""
    source: str = ""


@dataclass(frozen=True)
class OnetReference:
    used: bool
    unavailable_reason: str = ""
    occupations: list[dict[str, str]] = field(default_factory=list)
    tasks: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    work_activities: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CareerDiscoveryOutput:
    suggested_roles: list[SuggestedRole] = field(default_factory=list)
    selected_target_role: str = ""
    career_discovery_notes: str = ""
    onet_reference: OnetReference = field(default_factory=lambda: OnetReference(used=False))


@dataclass(frozen=True)
class MissionReport:
    input: MissionInput
    resume: ResumeOutput
    job_fit: JobFitOutput
    evaluation: EvaluationOutput
    mode: str
    workflow_mode: WorkflowMode = "targeted"
    discovery: CareerDiscoveryOutput | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
