import pytest

from vetpivot.agents.evaluation_agent import run_live_evaluation_agent
from vetpivot.agents.job_fit_agent import run_live_job_fit_agent
from vetpivot.agents.resume_agent import run_live_resume_agent
from vetpivot.gemini_client import GeminiUnavailableError
from vetpivot.orchestrator import run_workflow
from vetpivot.schemas import JobFitOutput, MissionInput, MissionReport, ResumeOutput


def sample_input() -> MissionInput:
    return MissionInput(
        military_experience="Led a team of 12 soldiers maintaining equipment worth $2.3M.",
        mos_branch="Army team leader",
        target_job_description="Operations coordinator responsible for leadership, equipment, safety, and communication.",
    )


def fake_generator(system_instruction: str, prompt: str) -> dict[str, object]:
    if "Resume Agent" in system_instruction:
        return {
            "professional_resume_bullet": "Led a 12-person equipment maintenance team supporting operations.",
            "ats_optimized_bullet": "Leadership, equipment maintenance, safety, and operations coordination.",
        }
    if "Job Fit Agent" in system_instruction:
        return {
            "fit_label": "Strong Match",
            "match_analysis": "Strong Match: The experience aligns with leadership, equipment, safety, and communication.",
            "matched_keywords": ["leadership", "equipment", "safety", "communication"],
            "missing_keywords": [],
            "interview_talking_points": [
                "S - Situation: explain the maintenance environment and team size.",
                "T - Task: describe responsibility for equipment readiness.",
                "A - Action: explain coordination and safety steps taken.",
                "R - Result: connect verified outcomes to the operations role.",
            ],
        }
    if "Evaluation Agent" in system_instruction:
        return {
            "accuracy_notes": "Output preserves the supplied team size and equipment context.",
            "safety_flags": ["No obvious unsupported claims or factual drift detected."],
            "unsupported_claims": [],
            "usefulness_notes": "Review exact metrics before using in a real resume.",
        }
    raise AssertionError(f"Unexpected instruction: {system_instruction}")


def test_live_resume_agent_parses_mocked_gemini_response():
    result = run_live_resume_agent(sample_input(), generator=fake_generator)

    assert result.professional_resume_bullet == "Led a 12-person equipment maintenance team supporting operations."
    assert result.ats_optimized_bullet == "Leadership, equipment maintenance, safety, and operations coordination."


def test_live_resume_agent_strips_unsupported_numeric_claims():
    def generator(_: str, __: str) -> dict[str, object]:
        return {
            "professional_resume_bullet": "Led a 12-person team maintaining $2.3M in equipment.",
            "ats_optimized_bullet": "Maintained $2.3M in equipment and achieved 100% operational readiness.",
        }

    result = run_live_resume_agent(sample_input(), generator=generator)

    assert "12" in result.professional_resume_bullet
    assert "$2.3M" in result.professional_resume_bullet
    assert "$2.3M" in result.ats_optimized_bullet
    assert "100%" not in result.ats_optimized_bullet


def test_live_job_fit_agent_parses_mocked_gemini_response():
    resume = ResumeOutput(
        professional_resume_bullet="Led a 12-person equipment maintenance team supporting operations.",
        ats_optimized_bullet="Leadership, equipment maintenance, safety, and operations coordination.",
    )

    result = run_live_job_fit_agent(sample_input(), resume, generator=fake_generator)

    assert result.fit_label == "Strong Match"
    assert result.missing_keywords == []
    assert any(point.startswith("S - Situation:") for point in result.interview_talking_points)


def test_live_job_fit_agent_sanitizes_unsupported_star_metrics():
    def generator(_: str, __: str) -> dict[str, object]:
        return {
            "fit_label": "Strong Match",
            "match_analysis": "Strong Match: aligned.",
            "matched_keywords": ["maintenance"],
            "missing_keywords": [],
            "interview_talking_points": [
                "Situation: Managed $2.3M in equipment. Task: Ensure 100% operational readiness. Action: Led a 12-person team. Result: Maintained zero downtime and improved turnaround by [X]%.",
            ],
        }

    resume = ResumeOutput(
        professional_resume_bullet="Led a 12-person equipment maintenance team.",
        ats_optimized_bullet="Maintained $2.3M in equipment.",
    )

    result = run_live_job_fit_agent(sample_input(), resume, generator=generator)
    talking_point = result.interview_talking_points[0]

    assert "$2.3M" in talking_point
    assert "12-person" in talking_point
    assert "100%" not in talking_point
    assert "[X]%" not in talking_point
    assert "zero downtime" not in talking_point
    assert "share only verified outcomes" in talking_point


def test_live_job_fit_agent_rejects_invalid_label():
    def invalid_generator(_: str, __: str) -> dict[str, object]:
        return {
            "fit_label": "Great Fit",
            "match_analysis": "Invalid label.",
            "matched_keywords": [],
            "missing_keywords": [],
            "interview_talking_points": ["S - Situation: invalid."],
        }

    resume = ResumeOutput(professional_resume_bullet="Bullet.", ats_optimized_bullet="ATS bullet.")

    with pytest.raises(GeminiUnavailableError, match="invalid fit_label"):
        run_live_job_fit_agent(sample_input(), resume, generator=invalid_generator)


def test_live_evaluation_agent_parses_mocked_gemini_response():
    resume = ResumeOutput(
        professional_resume_bullet="Led a 12-person equipment maintenance team supporting operations.",
        ats_optimized_bullet="Leadership, equipment maintenance, safety, and operations coordination.",
    )
    job_fit = JobFitOutput(
        fit_label="Strong Match",
        match_analysis="Strong Match: Relevant operations experience.",
        matched_keywords=["leadership", "equipment"],
        missing_keywords=[],
        interview_talking_points=["S - Situation: explain the maintenance environment."],
    )

    result = run_live_evaluation_agent(sample_input(), resume, job_fit, generator=fake_generator)

    assert result.accuracy_notes
    assert result.safety_flags
    assert result.unsupported_claims == []


def test_live_workflow_returns_structured_report_with_mocked_gemini():
    result = run_workflow(sample_input(), mode="live", gemini_generator=fake_generator)

    assert isinstance(result, MissionReport)
    assert result.mode == "live"
    assert result.resume.professional_resume_bullet
    assert result.job_fit.fit_label == "Strong Match"
    assert result.evaluation.safety_flags


def test_live_workflow_fails_strictly_when_gemini_unavailable():
    def failing_generator(_: str, __: str) -> dict[str, object]:
        raise GeminiUnavailableError("Gemini unavailable")

    with pytest.raises(GeminiUnavailableError, match="Gemini unavailable"):
        run_workflow(sample_input(), mode="live", gemini_generator=failing_generator)


def test_auto_workflow_falls_back_to_mock_when_gemini_unavailable():
    def failing_generator(_: str, __: str) -> dict[str, object]:
        raise GeminiUnavailableError("Gemini unavailable")

    result = run_workflow(sample_input(), mode="auto", gemini_generator=failing_generator)

    assert isinstance(result, MissionReport)
    assert result.mode == "mock"
    assert result.resume.professional_resume_bullet.startswith("Translated military experience")
