"""FastAPI bridge for the VetPivot Career Agent workflow."""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from vetpivot.gemini_client import GeminiUnavailableError
from vetpivot.orchestrator import run_workflow
from vetpivot.schemas import MissionInput, MissionReport

ApiMode = Literal["mock", "live", "auto"]


class CareerAgentRequest(BaseModel):
    military_experience: str = Field(..., min_length=1)
    target_job_description: str = Field(..., min_length=1)
    mos_branch: str = ""
    mode: ApiMode = "mock"


class CareerAgentResponse(BaseModel):
    professional_resume_bullet: str
    ats_optimized_bullet: str
    job_fit_assessment: str
    matched_keywords: list[str]
    missing_keywords: list[str]
    interview_talking_points: list[str]
    evaluation_notes: str
    safety_flags: list[str]
    unsupported_claims: list[str]
    mode: str


app = FastAPI(
    title="VetPivot Career Agent API",
    description="API bridge for the VetPivot Career Agent CLI/orchestrator workflow.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://vet-resume-builder.web.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "VetPivot Career Agent API",
        "docs": "/docs",
        "career_agent_endpoint": "POST /api/career-agent",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/career-agent", response_model=CareerAgentResponse)
def career_agent(request: CareerAgentRequest) -> CareerAgentResponse:
    mission_input = MissionInput(
        military_experience=request.military_experience,
        mos_branch=request.mos_branch,
        target_job_description=request.target_job_description,
    )
    try:
        report = run_workflow(mission_input, mode=request.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeminiUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not isinstance(report, MissionReport):
        raise HTTPException(status_code=500, detail="Career agent did not return a structured report")

    return CareerAgentResponse(
        professional_resume_bullet=report.resume.professional_resume_bullet,
        ats_optimized_bullet=report.resume.ats_optimized_bullet,
        job_fit_assessment=report.job_fit.match_analysis,
        matched_keywords=report.job_fit.matched_keywords,
        missing_keywords=report.job_fit.missing_keywords,
        interview_talking_points=report.job_fit.interview_talking_points,
        evaluation_notes=report.evaluation.accuracy_notes,
        safety_flags=report.evaluation.safety_flags,
        unsupported_claims=report.evaluation.unsupported_claims,
        mode=report.mode,
    )
