import importlib

from vetpivot.adk_agents import get_adk_model


def test_adk_entrypoint_imports_without_google_adk():
    module = importlib.import_module("vetpivot.agent")

    assert hasattr(module, "root_agent")


def test_adk_model_uses_gemini_model_configuration(monkeypatch):
    monkeypatch.setenv("VETPIVOT_GEMINI_MODEL", "gemini-test-model")

    assert get_adk_model() == "gemini-test-model"
