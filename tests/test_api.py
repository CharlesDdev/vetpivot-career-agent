from fastapi.testclient import TestClient

from vetpivot.gemini_client import GeminiUnavailableError
from vetpivot.api import app
from vetpivot.schemas import EvaluationOutput, JobFitOutput, MissionInput, MissionReport, ResumeOutput


client = TestClient(app)


def valid_payload() -> dict[str, str]:
    return {
        "military_experience": "Led a team of 12 soldiers maintaining communications equipment valued at $2.3M.",
        "mos_branch": "Army communications team leader",
        "target_job_description": "Operations coordinator responsible for team coordination, equipment inventory, safety compliance, and communication.",
    }


def test_career_agent_endpoint_returns_mock_report():
    response = client.post("/api/career-agent", json=valid_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["professional_resume_bullet"]
    assert body["ats_optimized_bullet"]
    assert body["job_fit_assessment"]
    assert isinstance(body["missing_keywords"], list)
    assert body["interview_talking_points"]
    assert body["evaluation_notes"]
    assert body["safety_flags"]
    assert body["mode"] == "mock"


def test_health_endpoint_returns_ok_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_career_agent_endpoint_accepts_explicit_mock_mode():
    payload = valid_payload()
    payload["mode"] = "mock"

    response = client.post("/api/career-agent", json=payload)

    assert response.status_code == 200
    assert response.json()["mode"] == "mock"


def test_career_agent_endpoint_accepts_live_mode(monkeypatch):
    def fake_run_workflow(mission_input, mode):
        assert mode == "live"
        return MissionReport(
            input=mission_input,
            resume=ResumeOutput(
                professional_resume_bullet="Live professional bullet.",
                ats_optimized_bullet="Live ATS bullet.",
            ),
            job_fit=JobFitOutput(
                fit_label="Partial Match",
                match_analysis="Partial Match: Live analysis.",
                matched_keywords=["leadership"],
                missing_keywords=["compliance"],
                interview_talking_points=["S - Situation: live talking point."],
            ),
            evaluation=EvaluationOutput(
                accuracy_notes="Live evaluation notes.",
                safety_flags=["No obvious unsupported claims."],
                unsupported_claims=[],
                usefulness_notes="Live usefulness notes.",
            ),
            mode="live",
        )

    monkeypatch.setattr("vetpivot.api.run_workflow", fake_run_workflow)
    payload = valid_payload()
    payload["mode"] = "live"

    response = client.post("/api/career-agent", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "professional_resume_bullet",
        "ats_optimized_bullet",
        "job_fit_assessment",
        "matched_keywords",
        "missing_keywords",
        "interview_talking_points",
        "evaluation_notes",
        "safety_flags",
        "unsupported_claims",
        "mode",
    }
    assert body["mode"] == "live"


def test_career_agent_endpoint_returns_503_when_live_unavailable(monkeypatch):
    def fake_run_workflow(_: MissionInput, mode: str):
        assert mode == "live"
        raise GeminiUnavailableError("Gemini unavailable")

    monkeypatch.setattr("vetpivot.api.run_workflow", fake_run_workflow)
    payload = valid_payload()
    payload["mode"] = "live"

    response = client.post("/api/career-agent", json=payload)

    assert response.status_code == 503
    assert response.json() == {"detail": "Gemini unavailable"}


def test_career_agent_endpoint_requires_military_experience():
    payload = valid_payload()
    del payload["military_experience"]

    response = client.post("/api/career-agent", json=payload)

    assert response.status_code == 422


def test_career_agent_endpoint_requires_target_job_description():
    payload = valid_payload()
    del payload["target_job_description"]

    response = client.post("/api/career-agent", json=payload)

    assert response.status_code == 422
