"""Job Fit Agent for comparing experience to a target role."""

from __future__ import annotations

from vetpivot.schemas import JobFitOutput, MissionInput, ResumeOutput

KEYWORD_BANK = [
    "leadership",
    "operations",
    "management",
    "coordination",
    "communication",
    "logistics",
    "maintenance",
    "training",
    "safety",
    "compliance",
    "risk",
    "inventory",
    "equipment",
    "process improvement",
    "team",
    "project",
]


def _job_keywords(job_description: str) -> list[str]:
    text = job_description.lower()
    return [keyword for keyword in KEYWORD_BANK if keyword in text]


def run_job_fit_agent(data: MissionInput, resume: ResumeOutput) -> JobFitOutput:
    """Return a simple label-based fit analysis without numeric scoring."""
    combined_experience = " ".join(
        [
            data.military_experience,
            data.mos_branch,
            resume.professional_resume_bullet,
            resume.ats_optimized_bullet,
        ]
    ).lower()
    job_keywords = _job_keywords(data.target_job_description)
    matched = [keyword for keyword in job_keywords if keyword in combined_experience]
    missing = [keyword for keyword in job_keywords if keyword not in matched]

    if len(matched) >= 5:
        label = "Strong Match"
    elif len(matched) >= 2:
        label = "Partial Match"
    else:
        label = "Weak Match"

    if matched:
        matched_text = ", ".join(matched)
        match_text = f"{label}: The experience aligns with {matched_text}."
    else:
        match_text = f"{label}: The target role includes requirements that are not clearly supported."

    talking_points = [
        "Describe the mission, team size, and operating environment in civilian terms.",
        "Explain how the work connects to the target role requirements without overstating qualifications.",
        "Prepare a concrete example showing leadership, accountability, or risk management from the provided experience.",
    ]
    if missing:
        missing_text = ", ".join(missing)
        talking_points.append(f"Be ready to address gaps around: {missing_text}.")

    return JobFitOutput(
        fit_label=label,
        match_analysis=match_text,
        matched_keywords=matched,
        missing_keywords=missing,
        interview_talking_points=talking_points,
    )
