"""Credential-gated live smoke checks for VetPivot."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from vetpivot.api import app
from vetpivot.gemini_client import GeminiUnavailableError, get_gemini_model
from vetpivot.live_adk import run_live_adk
from vetpivot.orchestrator import run_workflow
from vetpivot.schemas import MissionInput, MissionReport

MISSING_CREDENTIALS_EXIT_CODE = 2


def _load_input(path: Path) -> MissionInput:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return MissionInput(
        military_experience=payload.get("military_experience", ""),
        mos_branch=payload.get("mos_branch", ""),
        target_job_description=payload.get("target_job_description", ""),
    )


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _gemini_key_available() -> bool:
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))


def _print_readiness() -> None:
    print("Live readiness:")
    print(f"- google.genai importable: {_module_available('google.genai')}")
    print(f"- google.adk importable: {_module_available('google.adk')}")
    print(f"- GEMINI_API_KEY set: {bool(os.getenv('GEMINI_API_KEY'))}")
    print(f"- GOOGLE_API_KEY set: {bool(os.getenv('GOOGLE_API_KEY'))}")
    print(f"- GOOGLE_APPLICATION_CREDENTIALS set: {bool(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))}")
    print(f"- VETPIVOT_GEMINI_MODEL: {get_gemini_model()}")


def _run_gemini_workflow_smoke(data: MissionInput) -> None:
    report = run_workflow(data, mode="live")
    if not isinstance(report, MissionReport) or report.mode != "live":
        raise RuntimeError("Live Gemini workflow did not return a live MissionReport.")
    if not report.resume.professional_resume_bullet:
        raise RuntimeError("Live Gemini workflow returned an empty resume bullet.")
    print("- Gemini workflow: passed")


def _run_api_smoke(data: MissionInput) -> None:
    client = TestClient(app)
    response = client.post(
        "/api/translate",
        json={"text": data.military_experience, "mode": "live"},
    )
    if response.status_code != 200:
        raise RuntimeError(f"Live API translate returned HTTP {response.status_code}: {response.text}")
    body = response.json()
    if not body.get("translation") or body.get("mode") != "live":
        raise RuntimeError("Live API translate returned an invalid response body.")
    print("- Live API translate: passed")


def _run_adk_smoke(data: MissionInput) -> None:
    response = run_live_adk(data)
    if not response.strip():
        raise RuntimeError("Google ADK returned an empty response.")
    print("- Google ADK runner: passed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run live VetPivot smoke checks when Gemini credentials are configured.")
    parser.add_argument("--input", type=Path, default=Path("examples/strong_match.json"), help="Path to sample Mission input.")
    parser.add_argument("--readiness-only", action="store_true", help="Only print dependency and credential readiness.")
    parser.add_argument("--skip-adk", action="store_true", help="Skip the Google ADK runner smoke check.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    _print_readiness()
    if args.readiness_only:
        return 0

    if not _gemini_key_available():
        print(
            "Missing live credentials: set GEMINI_API_KEY or GOOGLE_API_KEY before running live smoke checks.",
            file=sys.stderr,
        )
        return MISSING_CREDENTIALS_EXIT_CODE

    data = _load_input(args.input)
    try:
        _run_gemini_workflow_smoke(data)
        _run_api_smoke(data)
        if not args.skip_adk:
            _run_adk_smoke(data)
    except Exception as exc:
        print(f"Live smoke failed: {exc}", file=sys.stderr)
        return 1

    print("Live smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
