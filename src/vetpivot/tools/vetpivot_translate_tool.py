"""VetPivot backend translation tool."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFAULT_TRANSLATE_URL = "https://vetpivot-backend-796137818435.us-central1.run.app/api/translate"
DEFAULT_TIMEOUT_SECONDS = 8.0


class VetPivotTranslateError(RuntimeError):
    """Raised when the VetPivot backend tool cannot return a usable translation."""


def get_translate_url() -> str:
    return os.getenv("VETPIVOT_TRANSLATE_URL", DEFAULT_TRANSLATE_URL).strip()


def get_translate_timeout() -> float:
    raw_timeout = os.getenv("VETPIVOT_TRANSLATE_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
    try:
        timeout = float(raw_timeout)
    except ValueError as exc:
        raise VetPivotTranslateError("VETPIVOT_TRANSLATE_TIMEOUT_SECONDS must be a number") from exc
    if timeout <= 0:
        raise VetPivotTranslateError("VETPIVOT_TRANSLATE_TIMEOUT_SECONDS must be greater than zero")
    return timeout


def translate_text(text: str, url: str | None = None, timeout: float | None = None) -> str:
    """Translate military language with the VetPivot backend."""
    payload = json.dumps({"text": text}).encode("utf-8")
    request = urllib.request.Request(
        url or get_translate_url(),
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout or get_translate_timeout()) as response:
            status = response.status
            body = response.read().decode("utf-8")
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        raise VetPivotTranslateError(f"VetPivot backend request failed: {exc}") from exc

    if status < 200 or status >= 300:
        raise VetPivotTranslateError(f"VetPivot backend returned HTTP {status}")

    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise VetPivotTranslateError("VetPivot backend returned invalid JSON") from exc

    translation = data.get("translation")
    if not isinstance(translation, str) or not translation.strip():
        raise VetPivotTranslateError("VetPivot backend response did not include a usable translation")
    return translation.strip()


def vetpivot_translate(text: str) -> dict[str, str]:
    """ADK function tool for translating military experience.

    ADK function tools work best when they return structured data rather than
    raising operational errors into the model loop. The deterministic CLI path
    still uses `translate_text` directly so fallback behavior remains explicit.
    """
    try:
        return {"status": "success", "translation": translate_text(text)}
    except VetPivotTranslateError as exc:
        return {"status": "error", "error_message": str(exc)}
