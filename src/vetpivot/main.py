"""CLI entrypoint for VetPivot Career Agent Mission 1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from vetpivot.gemini_client import GeminiUnavailableError
from vetpivot.orchestrator import run_workflow
from vetpivot.schemas import MissionInput, MissionReport


def _load_input(path: Path) -> MissionInput:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return MissionInput(
        military_experience=payload.get("military_experience", ""),
        mos_branch=payload.get("mos_branch", ""),
        target_job_description=payload.get("target_job_description", ""),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the VetPivot Mission 1 CLI demo.")
    parser.add_argument("--input", type=Path, default=Path("examples/mission_1_sample.json"), help="Path to Mission 1 JSON input.")
    parser.add_argument("--mode", choices=["auto", "mock", "live"], default="auto", help="Run deterministic mock, live Google ADK, or auto fallback.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = run_workflow(_load_input(args.input), mode=args.mode)
    except GeminiUnavailableError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if isinstance(result, MissionReport):
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
