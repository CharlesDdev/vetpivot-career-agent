from fastapi.testclient import TestClient

from vetpivot.api import app


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


def test_career_agent_endpoint_accepts_explicit_mock_mode():
    payload = valid_payload()
    payload["mode"] = "mock"

    response = client.post("/api/career-agent", json=payload)

    assert response.status_code == 200
    assert response.json()["mode"] == "mock"


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
