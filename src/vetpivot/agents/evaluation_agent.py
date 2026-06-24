"""Evaluation Agent for safety and quality review."""

from __future__ import annotations

import re

from vetpivot.schemas import EvaluationOutput, JobFitOutput, MissionInput, ResumeOutput

RISKY_TERMS = ["certified", "expert", "guaranteed", "clearance", "degree"]
CERTIFICATION_TERMS = ["certified", "certification", "license", "licensed", "clearance"]
DEGREE_TERMS = ["degree", "bachelor", "master", "phd", "doctorate"]
JOB_TITLE_PATTERNS = [
    r"\b(team leader)\b",
    r"\b(project manager)\b",
    r"\b(operations manager)\b",
    r"\b(operations coordinator)\b",
    r"\b(supervisor)\b",
]


def _money_facts(text: str) -> list[str]:
    return re.findall(r"\$\s?\d+(?:\.\d+)?\s?(?:[kKmMbB]|million|billion)?", text)


def _team_size_facts(text: str) -> list[str]:
    return re.findall(r"\b(?:team of|led|supervised|managed)\s+(\d+)\b", text, flags=re.IGNORECASE)


def _years_facts(text: str) -> list[str]:
    return re.findall(r"\b\d+\+?\s+years?\b", text, flags=re.IGNORECASE)


def _term_facts(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if term in lower]


def _job_title_facts(text: str) -> list[str]:
    facts: list[str] = []
    for pattern in JOB_TITLE_PATTERNS:
        facts.extend(match.lower() for match in re.findall(pattern, text, flags=re.IGNORECASE))
    return facts


def _missing_source_facts(source: str, generated: str) -> list[str]:
    missing: list[str] = []
    generated_lower = generated.lower()
    generated_compact = generated_lower.replace(" ", "")
    for fact in _money_facts(source):
        if fact.lower().replace(" ", "") not in generated_compact:
            missing.append(f"dollar amount changed or omitted: {fact}")
    for size in _team_size_facts(source):
        if size not in generated:
            missing.append(f"team size changed or omitted: {size}")
    for years in _years_facts(source):
        if years.lower() not in generated_lower:
            missing.append(f"years of experience changed or omitted: {years}")
    for title in _job_title_facts(source):
        if title not in generated_lower:
            missing.append(f"job title changed or omitted: {title}")
    return missing


def _unsupported_generated_facts(source: str, generated: str) -> list[str]:
    source_lower = source.lower()
    unsupported = [term for term in RISKY_TERMS if term in generated and term not in source_lower]
    unsupported.extend(term for term in _term_facts(generated, CERTIFICATION_TERMS) if term not in source_lower)
    unsupported.extend(term for term in _term_facts(generated, DEGREE_TERMS) if term not in source_lower)
    unsupported.extend(years for years in _years_facts(generated) if years.lower() not in source_lower)
    return sorted(set(unsupported))


def _unsupported_target_requirements(source: str, target: str) -> list[str]:
    source_lower = source.lower()
    target_lower = target.lower()
    unsupported: list[str] = []
    unsupported.extend(
        f"target requires {years} not supported by source"
        for years in _years_facts(target)
        if years.lower() not in source_lower
    )
    unsupported.extend(
        f"target mentions {term} not supported by source"
        for term in _term_facts(target_lower, CERTIFICATION_TERMS + DEGREE_TERMS)
        if term not in source_lower
    )
    return sorted(set(unsupported))


def run_evaluation_agent(data: MissionInput, resume: ResumeOutput, job_fit: JobFitOutput) -> EvaluationOutput:
    generated_text = " ".join(
        [
            resume.professional_resume_bullet,
            resume.ats_optimized_bullet,
            job_fit.match_analysis,
            " ".join(job_fit.interview_talking_points),
        ]
    )
    generated = generated_text.lower()
    source_text = " ".join([data.military_experience, data.mos_branch])
    source = source_text.lower()

    unsupported = _unsupported_generated_facts(source, generated)
    unsupported_target_requirements = _unsupported_target_requirements(source_text, data.target_job_description)
    factual_drift = _missing_source_facts(source_text, generated_text)
    safety_flags: list[str] = []
    if unsupported:
        safety_flags.append("Generated output may contain unsupported credential, degree, title, or experience language.")
    if unsupported_target_requirements:
        safety_flags.append("Target role includes high-risk requirements not supported by the original experience.")
    if factual_drift:
        safety_flags.append("Factual drift risk: generated output may have changed or omitted important facts from the original input.")
    if job_fit.fit_label == "Strong Match" and len(job_fit.matched_keywords) < 5:
        safety_flags.append("Fit label may be overstated for the number of supported matches.")
    if not safety_flags:
        safety_flags.append("No obvious unsupported claims or factual drift detected in the deterministic review.")

    notes = "Output is grounded in the supplied experience and uses conservative civilian framing."
    if factual_drift:
        notes = "Factual preservation risk detected: " + "; ".join(factual_drift) + "."

    return EvaluationOutput(
        accuracy_notes=notes,
        safety_flags=safety_flags,
        unsupported_claims=unsupported + unsupported_target_requirements + factual_drift,
        usefulness_notes="Review the bullet for exact metrics before using it in a real resume.",
    )
