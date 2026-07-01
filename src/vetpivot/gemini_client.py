"""Gemini client helpers for live VetPivot agent behavior."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any

DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"


class GeminiUnavailableError(RuntimeError):
    """Raised when Gemini live mode cannot return a usable structured result."""


def get_gemini_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    api_key = api_key.strip()
    if not api_key:
        raise GeminiUnavailableError("Gemini live mode requires GEMINI_API_KEY or GOOGLE_API_KEY.")
    return api_key


def get_gemini_model() -> str:
    return os.getenv("VETPIVOT_GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object from Gemini text, allowing simple fenced blocks."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise GeminiUnavailableError("Gemini returned invalid JSON.") from exc
    if not isinstance(parsed, dict):
        raise GeminiUnavailableError("Gemini response must be a JSON object.")
    return parsed


class GeminiClient:
    """Small wrapper around the Google GenAI SDK Interactions API."""

    def __init__(self, *, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or get_gemini_api_key()
        self.model = model or get_gemini_model()

    def generate_text(self, *, system_instruction: str, prompt: str) -> str:
        try:
            from google import genai
        except Exception as exc:  # pragma: no cover - depends on optional live dependency
            raise GeminiUnavailableError("google-genai is not installed. Install live dependencies with: pip install -e .[live]") from exc

        try:
            client = genai.Client(api_key=self.api_key)
            interaction = client.interactions.create(
                model=self.model,
                system_instruction=system_instruction,
                input=prompt,
                generation_config={"temperature": 0.2},
            )
        except Exception as exc:  # pragma: no cover - network/API dependent
            raise GeminiUnavailableError(f"Gemini request failed: {exc}") from exc

        output_text = getattr(interaction, "output_text", "")
        if not isinstance(output_text, str) or not output_text.strip():
            raise GeminiUnavailableError("Gemini returned an empty response.")
        return output_text.strip()

    def generate_json(self, *, system_instruction: str, prompt: str) -> dict[str, Any]:
        return parse_json_object(self.generate_text(system_instruction=system_instruction, prompt=prompt))


GeminiGenerator = Callable[[str, str], dict[str, Any]]


def generate_json(system_instruction: str, prompt: str) -> dict[str, Any]:
    return GeminiClient().generate_json(system_instruction=system_instruction, prompt=prompt)
