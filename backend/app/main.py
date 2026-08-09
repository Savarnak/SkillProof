from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from pathlib import Path
from app.config import settings
from app.schemas.curriculum import Curriculum
from app.schemas.candidate import Candidate

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
    """Mandatory health check endpoint verifying engine status and sample data availability."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    curriculum_file = data_dir / "sample_curriculum.json"
    candidates_file = data_dir / "sample_candidates.json"
    
    curriculum_ok = curriculum_file.exists()
    candidates_ok = candidates_file.exists()
    
    curriculum_count = 0
    candidate_count = 0
    
    if curriculum_ok:
        try:
            with open(curriculum_file, "r", encoding="utf-8") as f:
                cdata = json.load(f)
                curriculum_count = len(cdata.get("modules", []))
        except Exception:
            curriculum_ok = False

    if candidates_ok:
        try:
            with open(candidates_file, "r", encoding="utf-8") as f:
                cand_data = json.load(f)
                candidate_count = len(cand_data)
        except Exception:
            candidates_ok = False

    return {
        "status": "healthy",
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
            "synthetic_candidates_count": candidate_count
        }
    }
