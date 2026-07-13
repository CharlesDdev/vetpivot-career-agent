import json

from vetpivot.agents.evaluation_agent import run_evaluation_agent
from vetpivot.agents.resume_agent import run_resume_agent
from vetpivot.gemini_client import GeminiUnavailableError
from vetpivot.orchestrator import run_local_workflow, run_workflow
from vetpivot.schemas import JobFitOutput, MissionInput, ResumeOutput
from vetpivot.tools import vetpivot_translate_tool
from vetpivot.tools.vetpivot_translate_tool import VetPivotTranslateError, translate_text, vetpivot_translate


class FakeResponse:
    status = 200

    def __init__(self, payload: dict[str, object]):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def sample_input() -> MissionInput:
    return MissionInput(
        military_experience="Led a team of 12 soldiers maintaining equipment worth $2.3M.",
        mos_branch="Army team leader",
        target_job_description="Operations role requiring leadership, equipment, safety, and communication.",
    )


def test_mock_mode_does_not_call_backend():
    def failing_translator(_: str) -> str:
        raise AssertionError("backend should not be called in mock mode")

    result = run_local_workflow(sample_input(), use_backend=False, translator=failing_translator)

    assert result.mode == "mock"
    assert result.resume.professional_resume_bullet.startswith("Translated military experience")


def test_backend_success_uses_translation():
    result = run_local_workflow(sample_input(), use_backend=True, translator=lambda _: "Managed a 12-person equipment team supporting operations.")

    assert result.mode == "backend"
    assert result.resume.professional_resume_bullet == "Managed a 12-person equipment team supporting operations."


def test_backend_failure_falls_back_to_mock():
    def failing_translator(_: str) -> str:
        raise VetPivotTranslateError("backend unavailable")

    result = run_local_workflow(sample_input(), use_backend=True, translator=failing_translator)

    assert result.mode == "mock"
    assert result.resume.professional_resume_bullet.startswith("Translated military experience")


def test_invalid_backend_response_falls_back_to_mock(monkeypatch):
    def fake_urlopen(request, timeout):
        return FakeResponse({"unexpected": "missing translation"})

    monkeypatch.setattr(vetpivot_translate_tool.urllib.request, "urlopen", fake_urlopen)

    result = run_resume_agent(sample_input(), use_backend=True, translator=translate_text)

    assert result.professional_resume_bullet.startswith("Translated military experience")


def test_adk_translation_tool_returns_structured_success(monkeypatch):
    monkeypatch.setattr("vetpivot.tools.vetpivot_translate_tool.translate_text", lambda _: "Civilian translation.")

    result = vetpivot_translate("military text")

    assert result == {"status": "success", "translation": "Civilian translation."}


def test_adk_translation_tool_uses_runtime_type_annotations():
    assert vetpivot_translate.__annotations__["text"] is str


def test_adk_translation_tool_returns_structured_error(monkeypatch):
    def failing_translate(_: str) -> str:
        raise VetPivotTranslateError("backend unavailable")

    monkeypatch.setattr("vetpivot.tools.vetpivot_translate_tool.translate_text", failing_translate)

    result = vetpivot_translate("military text")

    assert result["status"] == "error"
    assert "backend unavailable" in result["error_message"]


def test_auto_mode_gemini_failure_falls_back_to_mock():
    def failing_gemini(_: str, __: str) -> dict[str, object]:
        raise GeminiUnavailableError("Gemini unavailable")

    result = run_workflow(sample_input(), mode="auto", gemini_generator=failing_gemini)

    assert result.mode == "mock"


def test_evaluation_flags_factual_drift_for_important_facts():
    data = sample_input()
    resume = ResumeOutput(
        professional_resume_bullet="Led a team responsible for maintaining equipment valued at .3M.",
        ats_optimized_bullet="Equipment maintenance and operations support.",
    )
    job_fit = JobFitOutput(fit_label="Partial Match", match_analysis="Partial Match: Some equipment overlap.")

    result = run_evaluation_agent(data, resume, job_fit)

    assert any("factual" in flag.lower() for flag in result.safety_flags)
    assert any("$2.3M" in claim for claim in result.unsupported_claims)
