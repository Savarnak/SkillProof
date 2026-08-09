from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from pathlib import Path
from app.config import settings
from app.schemas.curriculum import Curriculum
from app.schemas.candidate import Candidate
from app.api.routes import router as interview_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Adaptive AI Technical Interviewer Engine — Know it. Show it. Prove it."
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(interview_router)


@app.get("/")
def read_root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "running",
        "tagline": "Know it. Show it. Prove it.",
        "documentation": "/docs"
    }

@app.get("/api/health")
def health_check():
    """Mandatory health check endpoint verifying engine status and backend/data sample data availability."""
    from app.data_loader import load_sample_curriculum, load_sample_candidates
    
    cdata, curr_file, curriculum_ok = load_sample_curriculum()
    curriculum_count = len(cdata.get("modules", [])) if (curriculum_ok and cdata) else 0

    cands, cand_file, candidates_ok = load_sample_candidates()
    candidate_count = len(cands) if (candidates_ok and cands) else 0

    return {
        "status": "healthy" if curriculum_ok else "degraded",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "deterministic_rules": {
            "min_required_questions": settings.MIN_REQUIRED_QUESTIONS,
            "min_required_curriculum_days": settings.MIN_REQUIRED_CURRICULUM_DAYS
        },
        "sample_data": {
            "curriculum_loaded": curriculum_ok,
            "modules_count": curriculum_count,
            "candidates_loaded": candidates_ok,
            "synthetic_candidates_count": candidate_count,
            "data_path": str(curr_file)
        }
    }
