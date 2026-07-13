"""Shared validation helpers for live Gemini agent payloads."""

from __future__ import annotations

from vetpivot.gemini_client import GeminiUnavailableError


def require_text(payload: dict[str, object], key: str, *, context: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise GeminiUnavailableError(f"Gemini {context} response missing usable {key}.")
    return value.strip()


def require_text_list(payload: dict[str, object], key: str, *, context: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise GeminiUnavailableError(f"Gemini {context} response missing usable {key}.")
    return [item.strip() for item in value]
