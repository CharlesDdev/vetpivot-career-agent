"""Best-effort Google ADK live runner for Mission 1."""

from __future__ import annotations

import json
import os
import uuid

from vetpivot.schemas import MissionInput


def credentials_available() -> bool:
    return bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))


def run_live_adk(data: MissionInput) -> str:
    """Run the Google ADK root agent and return its final text response."""
    if not credentials_available():
        raise RuntimeError("Live mode requires GOOGLE_API_KEY, GEMINI_API_KEY, or GOOGLE_APPLICATION_CREDENTIALS.")

    try:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
    except Exception as exc:  # pragma: no cover - depends on optional deps
        raise RuntimeError("Google ADK live dependencies are unavailable. Install with: pip install -e .[live]") from exc

    from vetpivot.adk_agents import build_root_agent

    app_name = "vetpivot_career_agent"
    user_id = "mission_1_cli"
    session_id = str(uuid.uuid4())
    session_service = InMemorySessionService()
    session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    runner = Runner(agent=build_root_agent(), app_name=app_name, session_service=session_service)
    prompt = json.dumps(data.__dict__, indent=2)
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    final_text = ""
    for event in runner.run(user_id=user_id, session_id=session_id, new_message=message):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text or ""
    if not final_text:
        raise RuntimeError("Google ADK did not return a final response.")
    return final_text
