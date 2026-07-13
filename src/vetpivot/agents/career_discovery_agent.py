"""Career Discovery Agent for users without a target civilian job."""

from __future__ import annotations

import json
from collections.abc import Callable

from vetpivot.agents.live_validation import require_text
from vetpivot.gemini_client import GeminiGenerator, GeminiUnavailableError, generate_json
from vetpivot.schemas import CareerDiscoveryOutput, MissionInput, OnetReference, SuggestedRole
from vetpivot.tools.onet_tool import OnetCareerData, OnetUnavailableError, search_career_data

OnetSearch = Callable[[str, str], OnetCareerData]

DISCOVERY_LIVE_SYSTEM_INSTRUCTION = (
    "You are the VetPivot Career Discovery Agent. Suggest realistic civilian career directions from military "
    "experience and MOS/branch. Use O*NET data when supplied, but do not invent credentials, licenses, degrees, "
    "or qualifications. Frame suggestions as possible directions, not guaranteed matches. Return only valid JSON "
    "with keys suggested_roles, selected_target_role, and career_discovery_notes."
)


def _onet_reference_from_data(data: OnetCareerData, *, unavailable_reason: str = "") -> OnetReference:
    return OnetReference(
        used=bool(data.occupations) and not unavailable_reason,
        unavailable_reason=unavailable_reason,
        occupations=[
            {"title": occupation.title, "code": occupation.code, "source": occupation.source}
            for occupation in data.occupations
        ],
        tasks=data.tasks,
        skills=data.skills,
        work_activities=data.work_activities,
    )


def run_mock_career_discovery_agent(data: MissionInput) -> CareerDiscoveryOutput:
    """Return deterministic discovery suggestions for tests and offline judging."""
    text = f"{data.military_experience} {data.mos_branch}".lower()
    if "88m" in text or "convoy" in text or "route" in text or "driver" in text:
        roles = [
            SuggestedRole(
                title="City Bus Driver",
                explanation=(
                    "Connects convoy operations, route safety, vehicle movement discipline, and passenger-facing "
                    "communication to a civilian transportation role."
                ),
                source="deterministic mock",
            ),
            SuggestedRole(
                title="Delivery Driver",
                explanation="Uses route planning, safe vehicle operation, logistics discipline, and on-time movement experience.",
                source="deterministic mock",
            ),
            SuggestedRole(
                title="Transportation Dispatcher",
                explanation="Builds on convoy coordination, communication, risk monitoring, and movement control.",
                source="deterministic mock",
            ),
        ]
        selected = (
            "City bus driver responsible for safe route operations, passenger communication, vehicle safety checks, "
            "route coordination, training, logistics discipline, and risk management."
        )
    else:
        roles = [
            SuggestedRole(
                title="Operations Coordinator",
                explanation="Uses team coordination, process discipline, communication, and measurable mission support.",
                source="deterministic mock",
            ),
            SuggestedRole(
                title="Logistics Coordinator",
                explanation="Builds on equipment accountability, scheduling, operational follow-through, and risk management.",
                source="deterministic mock",
            ),
            SuggestedRole(
                title="Training Coordinator",
                explanation="Applies experience explaining procedures, supporting teams, and improving task execution.",
                source="deterministic mock",
            ),
        ]
        selected = (
            "Operations coordinator responsible for team coordination, communication, safety, equipment accountability, "
            "training, logistics, and process improvement."
        )

    return CareerDiscoveryOutput(
        suggested_roles=roles,
        selected_target_role=selected,
        career_discovery_notes="Deterministic mock discovery used because no target job was supplied.",
        onet_reference=OnetReference(used=False, unavailable_reason="Mock mode does not call O*NET."),
    )


def _parse_roles(payload: dict[str, object]) -> list[SuggestedRole]:
    value = payload.get("suggested_roles")
    if not isinstance(value, list):
        raise GeminiUnavailableError("Gemini discovery response missing usable suggested_roles.")

    roles: list[SuggestedRole] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        explanation = item.get("explanation")
        if not isinstance(title, str) or not title.strip():
            continue
        if not isinstance(explanation, str) or not explanation.strip():
            continue
        onet_code = item.get("onet_code")
        source = item.get("source")
        roles.append(
            SuggestedRole(
                title=title.strip(),
                explanation=explanation.strip(),
                onet_code=onet_code.strip() if isinstance(onet_code, str) else "",
                source=source.strip() if isinstance(source, str) else "",
            )
        )

    if not roles:
        raise GeminiUnavailableError("Gemini discovery response did not include any usable suggested roles.")
    return roles[:5]


def _target_from_discovery(discovery: CareerDiscoveryOutput) -> str:
    selected = discovery.selected_target_role.strip()
    if selected:
        return selected
    if discovery.suggested_roles:
        role = discovery.suggested_roles[0]
        return f"{role.title}: {role.explanation}"
    return ""


def run_live_career_discovery_agent(
    data: MissionInput,
    *,
    generator: GeminiGenerator = generate_json,
    onet_search: OnetSearch = search_career_data,
) -> CareerDiscoveryOutput:
    """Use Gemini plus optional O*NET data to suggest civilian career directions."""
    onet_data = OnetCareerData()
    unavailable_reason = ""
    try:
        onet_data = onet_search(data.military_experience, data.mos_branch)
    except OnetUnavailableError as exc:
        unavailable_reason = str(exc)

    onet_reference = _onet_reference_from_data(onet_data, unavailable_reason=unavailable_reason)
    prompt = json.dumps(
        {
            "military_experience": data.military_experience,
            "mos_branch": data.mos_branch,
            "onet": {
                "available": onet_reference.used,
                "unavailable_reason": unavailable_reason,
                "occupations": onet_reference.occupations,
                "tasks": onet_reference.tasks,
                "skills": onet_reference.skills,
                "work_activities": onet_reference.work_activities,
            },
            "required_json_schema": {
                "suggested_roles": [
                    {
                        "title": "civilian occupation title",
                        "explanation": "short grounded explanation of transferable fit",
                        "onet_code": "optional O*NET code when used",
                        "source": "O*NET or Gemini",
                    }
                ],
                "selected_target_role": "best role or role profile to use for resume/job-fit agents",
                "career_discovery_notes": "brief note explaining whether O*NET was used",
            },
        },
        indent=2,
    )
    payload = generator(DISCOVERY_LIVE_SYSTEM_INSTRUCTION, prompt)
    discovery = CareerDiscoveryOutput(
        suggested_roles=_parse_roles(payload),
        selected_target_role=require_text(payload, "selected_target_role", context="discovery"),
        career_discovery_notes=require_text(payload, "career_discovery_notes", context="discovery"),
        onet_reference=onet_reference,
    )
    return discovery


def discovery_target_description(discovery: CareerDiscoveryOutput) -> str:
    """Build the target-job context consumed by existing resume and job-fit agents."""
    selected = _target_from_discovery(discovery)
    role_lines = [f"{role.title}: {role.explanation}" for role in discovery.suggested_roles]
    onet_lines = []
    if discovery.onet_reference.tasks:
        onet_lines.append("O*NET tasks: " + "; ".join(discovery.onet_reference.tasks[:5]))
    if discovery.onet_reference.skills:
        onet_lines.append("O*NET skills: " + "; ".join(discovery.onet_reference.skills[:5]))
    if discovery.onet_reference.work_activities:
        onet_lines.append("O*NET work activities: " + "; ".join(discovery.onet_reference.work_activities[:5]))
    lines: list[str] = []
    seen: set[str] = set()
    for line in [selected, *role_lines, *onet_lines]:
        normalized = line.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            lines.append(normalized)
    return "\n".join(lines)
