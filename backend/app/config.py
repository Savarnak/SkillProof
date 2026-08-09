from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillProof — Adaptive AI Technical Interviewer"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # LLM Settings
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    
    # Interview Deterministic Constraints
    MIN_REQUIRED_QUESTIONS: int = 8
    MIN_REQUIRED_CURRICULUM_DAYS: int = 4

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
