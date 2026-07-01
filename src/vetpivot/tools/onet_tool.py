"""O*NET Web Services adapter for career discovery."""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass, field
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class OnetUnavailableError(RuntimeError):
    """Raised when O*NET data cannot be retrieved safely."""


@dataclass(frozen=True)
class OnetOccupation:
    title: str
    code: str = ""
    source: str = "O*NET"


@dataclass(frozen=True)
class OnetCareerData:
    occupations: list[OnetOccupation] = field(default_factory=list)
    tasks: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    work_activities: list[str] = field(default_factory=list)


def _api_key() -> str:
    key = os.getenv("ONET_API_KEY") or os.getenv("ONET_KEY")
    if not key or not key.strip():
        raise OnetUnavailableError("O*NET API key is not configured.")
    return key.strip()


def _basic_credentials() -> tuple[str, str]:
    username = os.getenv("ONET_USERNAME") or os.getenv("ONET_USER")
    password = os.getenv("ONET_PASSWORD") or os.getenv("ONET_PASS")
    if not username or not password:
        raise OnetUnavailableError("O*NET credentials are not configured.")
    return username, password


def _auth_headers() -> dict[str, str]:
    try:
        return {"X-API-Key": _api_key()}
    except OnetUnavailableError:
        username, password = _basic_credentials()
        token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {token}"}


def _base_url() -> str:
    return os.getenv("ONET_BASE_URL", "https://api-v2.onetcenter.org").rstrip("/")


def _timeout_seconds() -> float:
    raw_timeout = os.getenv("ONET_TIMEOUT_SECONDS", "8")
    try:
        return float(raw_timeout)
    except ValueError:
        return 8.0


def _get_json(path: str) -> dict[str, Any]:
    request = Request(
        f"{_base_url()}{path}",
        headers={
            "Accept": "application/json",
            "User-Agent": "VetPivot Career Agent",
            **_auth_headers(),
        },
    )
    try:
        with urlopen(request, timeout=_timeout_seconds()) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise OnetUnavailableError(f"O*NET request failed: {exc}") from exc


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    return []


def _text_from_item(item: Any) -> str:
    if isinstance(item, str):
        return item.strip()
    if not isinstance(item, dict):
        return ""
    for key in ("title", "name", "description", "task", "skill", "work_activity"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _normalize_occupations(payload: dict[str, Any], *, source: str) -> list[OnetOccupation]:
    candidates: list[Any] = []
    for key in ("occupation", "career", "result", "match"):
        candidates.extend(_as_list(payload.get(key)))

    occupations: list[OnetOccupation] = []
    seen: set[tuple[str, str]] = set()
    for item in candidates:
        if not isinstance(item, dict):
            continue
        title = item.get("title") or item.get("name") or item.get("occupation_title")
        code = item.get("code") or item.get("onetsoc_code") or item.get("occupation_code")
        if not isinstance(title, str) or not title.strip():
            continue
        normalized = (title.strip(), str(code or "").strip())
        if normalized in seen:
            continue
        seen.add(normalized)
        occupations.append(OnetOccupation(title=normalized[0], code=normalized[1], source=source))
    return occupations


def _profile_items(code: str, profile_type: str) -> list[str]:
    payload = _get_json(f"/online/occupations/{quote(code)}/summary/{profile_type}")
    items: list[Any] = []
    for key in (profile_type, "element", "item", "task", "skill", "work_activity"):
        items.extend(_as_list(payload.get(key)))
    text_items = [_text_from_item(item) for item in items]
    return [item for item in text_items if item][:8]


def search_career_data(military_experience: str, mos_branch: str = "", *, max_results: int = 5) -> OnetCareerData:
    """Search O*NET for likely civilian occupations and lightweight profile data."""
    query_parts = [mos_branch.strip(), military_experience.strip()]
    query = " ".join(part for part in query_parts if part)
    if not query:
        raise OnetUnavailableError("O*NET search query is empty.")

    occupations: list[OnetOccupation] = []
    for path, source in (
        (f"/online/crosswalks/military?keyword={quote(query)}", "O*NET military crosswalk"),
        (f"/online/search?keyword={quote(query)}", "O*NET keyword search"),
    ):
        try:
            payload = _get_json(path)
        except OnetUnavailableError:
            if occupations:
                break
            raise
        occupations.extend(_normalize_occupations(payload, source=source))
        if len(occupations) >= max_results:
            break

    deduped: list[OnetOccupation] = []
    seen: set[tuple[str, str]] = set()
    for occupation in occupations:
        key = (occupation.title, occupation.code)
        if key not in seen:
            seen.add(key)
            deduped.append(occupation)
    deduped = deduped[:max_results]

    tasks: list[str] = []
    skills: list[str] = []
    work_activities: list[str] = []
    if deduped and deduped[0].code:
        try:
            tasks = _profile_items(deduped[0].code, "tasks")
            skills = _profile_items(deduped[0].code, "skills")
            work_activities = _profile_items(deduped[0].code, "work_activities")
        except OnetUnavailableError:
            tasks = []
            skills = []
            work_activities = []

    return OnetCareerData(
        occupations=deduped,
        tasks=tasks,
        skills=skills,
        work_activities=work_activities,
    )
