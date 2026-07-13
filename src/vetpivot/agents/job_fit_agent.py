"""Job Fit Agent for comparing experience to a target role."""

from __future__ import annotations

import json
import re

from vetpivot.agents.live_validation import require_text, require_text_list
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
    "Do not invent metrics, percentages, outcomes, downtime, readiness rates, credentials, or tools. "
    "For STAR Result guidance, tell the user to provide only verified outcomes from their own records if no result was supplied. "
    "Return only valid JSON with keys fit_label, match_analysis, matched_keywords, missing_keywords, "
    "and interview_talking_points. Interview talking points must include STAR guidance."
)

NUMERIC_TOKEN_REGEX = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:%|[kKmMbB])?")
SAFE_RESULT_GUIDANCE = "share only verified outcomes or metrics from your own records; do not add numbers that were not provided."


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


def _strip_unsupported_numbers(text: str, source_text: str) -> str:
    allowed_tokens = {
        token.lower().replace(",", "")
        for token in NUMERIC_TOKEN_REGEX.findall(source_text)
    }

    def replacement(match: re.Match[str]) -> str:
        token = match.group(0)
        normalized = token.lower().replace(",", "")
        return token if normalized in allowed_tokens else ""

    return re.sub(r"\s{2,}", " ", NUMERIC_TOKEN_REGEX.sub(replacement, text)).strip()


def _sanitize_interview_talking_points(points: list[str], source_text: str) -> list[str]:
    sanitized = []
    result_pattern = re.compile(r"(\b(?:R\s*-\s*)?Result:\s*)(.*?)(?=$)", re.IGNORECASE)
    for point in points:
        without_unsupported_numbers = _strip_unsupported_numbers(point, source_text)
        sanitized.append(result_pattern.sub(rf"\1{SAFE_RESULT_GUIDANCE}", without_unsupported_numbers))
    return sanitized


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
    fit_label = require_text(payload, "fit_label", context="job-fit")
    if fit_label not in {"Strong Match", "Partial Match", "Weak Match"}:
        raise GeminiUnavailableError("Gemini job-fit response returned an invalid fit_label.")
    return JobFitOutput(
        fit_label=fit_label,  # type: ignore[arg-type]
        match_analysis=require_text(payload, "match_analysis", context="job-fit"),
        matched_keywords=require_text_list(payload, "matched_keywords", context="job-fit"),
        missing_keywords=require_text_list(payload, "missing_keywords", context="job-fit"),
        interview_talking_points=_sanitize_interview_talking_points(
            require_text_list(payload, "interview_talking_points", context="job-fit"),
            " ".join(
                [
                    data.military_experience,
                    data.mos_branch,
                    resume.professional_resume_bullet,
                    resume.ats_optimized_bullet,
                ]
            ),
        ),
    )
