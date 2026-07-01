"""Job Fit Agent for comparing experience to a target role."""

from __future__ import annotations

import json

from vetpivot.gemini_client import GeminiGenerator, GeminiUnavailableError, generate_json
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

JOB_FIT_LIVE_SYSTEM_INSTRUCTION = (
    "You are the VetPivot Job Fit Agent. Compare the supplied experience and resume bullets to the target job. "
    "Use only these fit labels: Strong Match, Partial Match, Weak Match. Do not use numeric scoring. "
    "Return only valid JSON with keys fit_label, match_analysis, matched_keywords, missing_keywords, "
    "and interview_talking_points. Interview talking points must include STAR guidance."
)


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
        "S - Situation: explain the mission, team size, and operating environment in civilian terms.",
        "T - Task: describe your responsibility for the work without overstating qualifications.",
        "A - Action: explain the leadership, coordination, safety, or maintenance steps you personally took.",
        "R - Result: connect the verified outcome or metric to the target role requirements.",
    ]
    if missing:
        missing_text = ", ".join(missing)
        talking_points.append(f"Gap prep: address missing target keywords with honest examples around {missing_text}.")

    return JobFitOutput(
        fit_label=label,
        match_analysis=match_text,
        matched_keywords=matched,
        missing_keywords=missing,
        interview_talking_points=talking_points,
    )


def _require_text(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise GeminiUnavailableError(f"Gemini job-fit response missing usable {key}.")
    return value.strip()


def _require_text_list(payload: dict[str, object], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise GeminiUnavailableError(f"Gemini job-fit response missing usable {key}.")
    return [item.strip() for item in value]


def run_live_job_fit_agent(data: MissionInput, resume: ResumeOutput, generator: GeminiGenerator = generate_json) -> JobFitOutput:
    """Use Gemini to produce structured job-fit analysis."""
    prompt = json.dumps(
        {
            "military_experience": data.military_experience,
            "mos_branch": data.mos_branch,
            "target_job_description": data.target_job_description,
            "resume": {
                "professional_resume_bullet": resume.professional_resume_bullet,
                "ats_optimized_bullet": resume.ats_optimized_bullet,
            },
            "allowed_fit_labels": ["Strong Match", "Partial Match", "Weak Match"],
            "required_json_schema": {
                "fit_label": "one allowed label",
                "match_analysis": "brief grounded explanation",
                "matched_keywords": ["keyword supported by the source"],
                "missing_keywords": ["target keyword not clearly supported"],
                "interview_talking_points": ["STAR-format talking point grounded in the input"],
            },
        },
        indent=2,
    )
    payload = generator(JOB_FIT_LIVE_SYSTEM_INSTRUCTION, prompt)
    fit_label = _require_text(payload, "fit_label")
    if fit_label not in {"Strong Match", "Partial Match", "Weak Match"}:
        raise GeminiUnavailableError("Gemini job-fit response returned an invalid fit_label.")
    return JobFitOutput(
        fit_label=fit_label,  # type: ignore[arg-type]
        match_analysis=_require_text(payload, "match_analysis"),
        matched_keywords=_require_text_list(payload, "matched_keywords"),
        missing_keywords=_require_text_list(payload, "missing_keywords"),
        interview_talking_points=_require_text_list(payload, "interview_talking_points"),
    )
