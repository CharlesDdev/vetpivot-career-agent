import importlib


def test_adk_entrypoint_imports_without_google_adk():
    module = importlib.import_module("vetpivot.agent")

    assert hasattr(module, "root_agent")
