import json
import socket

import pytest

from vetpivot.tools import onet_tool
from vetpivot.tools.onet_tool import OnetUnavailableError, search_career_data


class FakeResponse:
    def __init__(self, payload: dict[str, object]):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_onet_search_requires_credentials(monkeypatch):
    monkeypatch.delenv("ONET_API_KEY", raising=False)
    monkeypatch.delenv("ONET_KEY", raising=False)
    monkeypatch.delenv("ONET_USERNAME", raising=False)
    monkeypatch.delenv("ONET_USER", raising=False)
    monkeypatch.delenv("ONET_PASSWORD", raising=False)
    monkeypatch.delenv("ONET_PASS", raising=False)

    with pytest.raises(OnetUnavailableError, match="credentials|API key"):
        search_career_data("convoy operations", "88M")


def test_onet_search_prefers_api_key_and_parses_occupations_and_profile(monkeypatch):
    monkeypatch.setenv("ONET_API_KEY", "test-api-key")
    monkeypatch.setenv("ONET_USERNAME", "legacy-user")
    monkeypatch.setenv("ONET_PASSWORD", "legacy-pass")

    def fake_urlopen(request, timeout):
        url = request.full_url
        assert timeout == 8.0
        assert request.headers["X-api-key"] == "test-api-key"
        assert "Authorization" not in request.headers
        if "/online/crosswalks/military" in url:
            return FakeResponse(
                {
                    "occupation": [
                        {
                            "title": "Bus Drivers, Transit and Intercity",
                            "code": "53-3052.00",
                        }
                    ]
                }
            )
        if "/online/search" in url:
            return FakeResponse({"occupation": []})
        if url.endswith("/summary/tasks"):
            return FakeResponse({"task": [{"description": "Drive vehicles over specified routes."}]})
        if url.endswith("/summary/skills"):
            return FakeResponse({"skill": [{"name": "Operation and Control"}]})
        if url.endswith("/summary/work_activities"):
            return FakeResponse({"work_activity": [{"name": "Operating vehicles or equipment"}]})
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(onet_tool, "urlopen", fake_urlopen)

    result = search_career_data("convoy operations", "88M")

    assert result.occupations[0].title == "Bus Drivers, Transit and Intercity"
    assert result.occupations[0].code == "53-3052.00"
    assert result.tasks == ["Drive vehicles over specified routes."]
    assert result.skills == ["Operation and Control"]
    assert result.work_activities == ["Operating vehicles or equipment"]


def test_onet_search_supports_legacy_basic_auth(monkeypatch):
    monkeypatch.delenv("ONET_API_KEY", raising=False)
    monkeypatch.delenv("ONET_KEY", raising=False)
    monkeypatch.setenv("ONET_USERNAME", "user")
    monkeypatch.setenv("ONET_PASSWORD", "pass")

    def fake_urlopen(request, timeout):
        assert timeout == 8.0
        assert request.headers["Authorization"] == "Basic dXNlcjpwYXNz"
        return FakeResponse({"occupation": []})

    monkeypatch.setattr(onet_tool, "urlopen", fake_urlopen)

    result = search_career_data("convoy operations", "88M")

    assert result.occupations == []


def test_onet_search_converts_socket_timeout_to_unavailable(monkeypatch):
    monkeypatch.setenv("ONET_API_KEY", "test-api-key")

    def fake_urlopen(request, timeout):
        raise socket.timeout("timed out")

    monkeypatch.setattr(onet_tool, "urlopen", fake_urlopen)

    with pytest.raises(OnetUnavailableError, match="timed out"):
        search_career_data("convoy operations", "88M")
