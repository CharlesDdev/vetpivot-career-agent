import pytest

from vetpivot.agents.career_discovery_agent import run_live_career_discovery_agent
from vetpivot.gemini_client import GeminiUnavailableError
from vetpivot.orchestrator import run_workflow
from vetpivot.schemas import MissionInput, MissionReport
from vetpivot.tools.onet_tool import OnetCareerData, OnetOccupation, OnetUnavailableError


def discovery_input() -> MissionInput:
    return MissionInput(
        military_experience="Taught Convoy Operations to the battery, training 54 soldiers; reduced problems enroute by 80%.",
        mos_branch="88M",
    )


def targeted_input() -> MissionInput:
    return MissionInput(
        military_experience="Taught Convoy Operations to the battery, training 54 soldiers; reduced problems enroute by 80%.",
        mos_branch="88M",
        target_job_description="City bus driver responsible for route safety, passenger communication, and vehicle operations.",
    )


def discovery_generator(system_instruction: str, prompt: str) -> dict[str, object]:
    if "Career Discovery Agent" in system_instruction:
        assert "Taught Convoy Operations" in prompt
        return {
            "suggested_roles": [
                {
                    "title": "City Bus Driver",
                    "explanation": "Transfers route safety, vehicle operations, and passenger-facing communication.",
                    "onet_code": "53-3052.00",
                    "source": "O*NET",
                },
                {
                    "title": "Transportation Dispatcher",
                    "explanation": "Transfers convoy coordination, route planning, and risk monitoring.",
                    "source": "Gemini",
                },
                {
                    "title": "Delivery Driver",
                    "explanation": "Transfers safe vehicle operation, logistics discipline, and on-time movement.",
                    "source": "Gemini",
                },
            ],
            "selected_target_role": (
                "City bus driver responsible for safe route operations, vehicle safety checks, passenger "
                "communication, and route coordination."
            ),
            "career_discovery_notes": "O*NET roles were used with Gemini career reasoning.",
        }
    if "Resume Agent" in system_instruction:
        return {
            "professional_resume_bullet": "Trained 54 personnel in safe route operations and convoy coordination.",
            "ats_optimized_bullet": "Route safety, vehicle operations, driver training, risk reduction, and logistics coordination.",
        }
    if "Job Fit Agent" in system_instruction:
        return {
            "fit_label": "Strong Match",
            "match_analysis": "Strong Match: The experience supports route safety, training, and transportation coordination.",
            "matched_keywords": ["safety", "training", "coordination"],
            "missing_keywords": [],
            "interview_talking_points": [
                "S - Situation: describe the convoy training environment.",
                "T - Task: explain responsibility for training 54 soldiers.",
                "A - Action: describe route safety and coordination steps.",
                "R - Result: connect the 80% reduction to safer transportation operations.",
            ],
        }
    if "Evaluation Agent" in system_instruction:
        return {
            "accuracy_notes": "Output preserves the supplied training size and reduction metric.",
            "safety_flags": ["No obvious unsupported claims or factual drift detected."],
            "unsupported_claims": [],
            "usefulness_notes": "Review exact wording before use.",
        }
    raise AssertionError(f"Unexpected instruction: {system_instruction}")


def onet_success(_: str, __: str) -> OnetCareerData:
    return OnetCareerData(
        occupations=[OnetOccupation(title="Bus Drivers, Transit and Intercity", code="53-3052.00")],
        tasks=["Drive vehicles over specified routes or to specified destinations."],
        skills=["Operation and Control"],
        work_activities=["Operating vehicles, mechanized devices, or equipment."],
    )


def onet_unavailable(_: str, __: str) -> OnetCareerData:
    raise OnetUnavailableError("O*NET test outage")


def test_target_job_supplied_uses_targeted_path():
    result = run_workflow(targeted_input(), mode="mock")

    assert isinstance(result, MissionReport)
    assert result.workflow_mode == "targeted"
    assert result.discovery is None
    assert result.input.target_job_description


def test_target_job_omitted_uses_discovery_path_in_mock_mode():
    result = run_workflow(discovery_input(), mode="mock")

    assert result.workflow_mode == "discovery"
    assert result.discovery is not None
    assert result.discovery.suggested_roles
    assert "City bus driver" in result.discovery.selected_target_role
    assert result.job_fit.fit_label in {"Strong Match", "Partial Match"}


def test_live_discovery_parses_gemini_and_onet_success():
    result = run_live_career_discovery_agent(
        discovery_input(),
        generator=discovery_generator,
        onet_search=onet_success,
    )

    assert result.onet_reference.used is True
    assert result.onet_reference.occupations[0]["code"] == "53-3052.00"
    assert result.suggested_roles[0].title == "City Bus Driver"
    assert "City bus driver" in result.selected_target_role


def test_live_discovery_continues_when_onet_unavailable():
    result = run_live_career_discovery_agent(
        discovery_input(),
        generator=discovery_generator,
        onet_search=onet_unavailable,
    )

    assert result.onet_reference.used is False
    assert result.onet_reference.unavailable_reason == "O*NET test outage"
    assert result.suggested_roles
    assert result.selected_target_role


def test_live_discovery_workflow_returns_optional_fields():
    result = run_workflow(discovery_input(), mode="live", gemini_generator=discovery_generator)

    assert result.mode == "live"
    assert result.workflow_mode == "discovery"
    assert result.discovery is not None
    assert result.discovery.suggested_roles
    assert result.resume.professional_resume_bullet
    assert result.job_fit.match_analysis


def test_auto_discovery_falls_back_to_mock_when_gemini_unavailable():
    def failing_generator(_: str, __: str) -> dict[str, object]:
        raise GeminiUnavailableError("Gemini unavailable")

    result = run_workflow(discovery_input(), mode="auto", gemini_generator=failing_generator)

    assert result.mode == "mock"
    assert result.workflow_mode == "discovery"
    assert result.discovery is not None
    assert result.discovery.suggested_roles


def test_live_discovery_rejects_unusable_gemini_roles():
    def invalid_generator(_: str, __: str) -> dict[str, object]:
        return {
            "suggested_roles": [],
            "selected_target_role": "City Bus Driver",
            "career_discovery_notes": "Invalid response.",
        }

    with pytest.raises(GeminiUnavailableError, match="suggested roles"):
        run_live_career_discovery_agent(discovery_input(), generator=invalid_generator, onet_search=onet_success)
