from vetpivot.agents.evaluation_agent import run_evaluation_agent
from vetpivot.schemas import JobFitOutput, MissionInput, ResumeOutput


def test_evaluation_flags_unsupported_credentials():
    data = MissionInput(
        military_experience="Maintained communications equipment for field operations.",
        target_job_description="Role requires equipment maintenance and communication.",
    )
    resume = ResumeOutput(
        professional_resume_bullet="Certified expert in communications systems maintenance.",
        ats_optimized_bullet="Equipment maintenance and communication operations.",
    )
    job_fit = JobFitOutput(fit_label="Partial Match", match_analysis="Partial Match: Some maintenance overlap.")

    result = run_evaluation_agent(data, resume, job_fit)

    assert "certified" in result.unsupported_claims
    assert result.safety_flags


def test_evaluation_flags_unsupported_target_requirements():
    data = MissionInput(
        military_experience="Assisted with equipment inventory checks for a maintenance section.",
        target_job_description="Senior manager requiring 10 years of experience, PMP certification, and a bachelor's degree.",
    )
    resume = ResumeOutput(
        professional_resume_bullet="Assisted with equipment inventory checks.",
        ats_optimized_bullet="Equipment inventory and operations support.",
    )
    job_fit = JobFitOutput(fit_label="Weak Match", match_analysis="Weak Match: Senior requirements are not supported.")

    result = run_evaluation_agent(data, resume, job_fit)

    assert any("target role" in flag.lower() for flag in result.safety_flags)
    assert any("10 years" in claim for claim in result.unsupported_claims)
    assert any("certification" in claim for claim in result.unsupported_claims)
