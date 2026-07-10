from vetpivot.orchestrator import run_workflow
from vetpivot.schemas import MissionInput, MissionReport
from vetpivot import main as cli_main


def sample_input() -> MissionInput:
    return MissionInput(
        military_experience="Led a team of 12 soldiers maintaining communications equipment.",
        mos_branch="Army communications",
        target_job_description="Operations coordinator with leadership, communication, equipment, safety, and maintenance responsibilities.",
    )


def test_mock_workflow_returns_structured_report():
    result = run_workflow(sample_input(), mode="mock")

    assert isinstance(result, MissionReport)
    assert result.resume.professional_resume_bullet
    assert result.resume.ats_optimized_bullet
    assert result.job_fit.fit_label in {"Strong Match", "Partial Match", "Weak Match"}
    assert result.job_fit.interview_talking_points
    assert result.evaluation.safety_flags


def test_interview_talking_points_use_star_examples():
    result = run_workflow(sample_input(), mode="mock")

    talking_points = "\n".join(result.job_fit.interview_talking_points)
    assert "S - Situation:" in talking_points
    assert "T - Task:" in talking_points
    assert "A - Action:" in talking_points
    assert "R - Result:" in talking_points


def test_auto_falls_back_to_mock_without_live_setup(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)

    result = run_workflow(sample_input(), mode="auto")

    assert isinstance(result, MissionReport)
    assert result.mode == "mock"


def test_cli_live_mode_reports_missing_credentials_without_traceback(monkeypatch, capsys):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.setattr(
        "sys.argv",
        ["vetpivot", "--mode", "live", "--input", "examples/strong_match.json"],
    )

    exit_code = cli_main.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Gemini live mode requires GEMINI_API_KEY or GOOGLE_API_KEY." in captured.err
    assert "Traceback" not in captured.err
