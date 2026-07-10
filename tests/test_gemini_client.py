import pytest

from vetpivot.gemini_client import GeminiClient, GeminiUnavailableError, get_gemini_api_key, get_gemini_model, parse_json_object


def test_parse_json_object_accepts_plain_json():
    result = parse_json_object('{"professional_resume_bullet": "Managed operations."}')

    assert result == {"professional_resume_bullet": "Managed operations."}


def test_parse_json_object_accepts_fenced_json():
    result = parse_json_object('```json\n{"fit_label": "Partial Match"}\n```')

    assert result == {"fit_label": "Partial Match"}


def test_parse_json_object_rejects_invalid_json():
    with pytest.raises(GeminiUnavailableError, match="invalid JSON"):
        parse_json_object("not json")


def test_get_gemini_api_key_prefers_gemini_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")

    assert get_gemini_api_key() == "gemini-key"


def test_get_gemini_api_key_falls_back_to_google_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")

    assert get_gemini_api_key() == "google-key"


def test_get_gemini_api_key_requires_credentials(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    with pytest.raises(GeminiUnavailableError, match="requires GEMINI_API_KEY or GOOGLE_API_KEY"):
        get_gemini_api_key()


def test_get_gemini_model_uses_env_override(monkeypatch):
    monkeypatch.setenv("VETPIVOT_GEMINI_MODEL", "gemini-test-model")

    assert get_gemini_model() == "gemini-test-model"


def test_gemini_client_generate_json_uses_text_output(monkeypatch):
    class FakeResponse:
        text = '{"safety_flags": ["No obvious issue."]}'

    class FakeModels:
        def generate_content(self, **kwargs):
            assert kwargs["model"] == "gemini-test-model"
            assert kwargs["contents"] == "prompt"
            assert kwargs["config"].system_instruction == "system"
            assert kwargs["config"].temperature == 0.2
            return FakeResponse()

    class FakeGenAIClient:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.models = FakeModels()

    class FakeGenerateContentConfig:
        def __init__(self, *, systemInstruction, temperature):
            self.system_instruction = systemInstruction
            self.temperature = temperature

    class FakeGenAI:
        Client = FakeGenAIClient

    class FakeTypes:
        GenerateContentConfig = FakeGenerateContentConfig

    import sys
    import types

    google_module = types.ModuleType("google")
    google_module.genai = FakeGenAI
    google_genai_module = types.ModuleType("google.genai")
    google_genai_module.types = FakeTypes
    monkeypatch.setitem(sys.modules, "google", google_module)
    monkeypatch.setitem(sys.modules, "google.genai", google_genai_module)

    result = GeminiClient(api_key="test-key", model="gemini-test-model").generate_json(
        system_instruction="system",
        prompt="prompt",
    )

    assert result == {"safety_flags": ["No obvious issue."]}
