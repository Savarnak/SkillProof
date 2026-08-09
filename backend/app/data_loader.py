import os
import json
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger("SkillProof.DataLoader")

def get_backend_data_dir() -> Path:
    """
    Resolves the authoritative backend runtime data directory (backend/data/).
    Strictly derived from the backend application package location.
    """
    app_dir = Path(__file__).resolve().parent  # backend/app
    backend_dir = app_dir.parent               # backend
    primary_data_dir = backend_dir / "data"     # backend/data

    if primary_data_dir.exists() and (primary_data_dir / "sample_curriculum.json").exists():
        return primary_data_dir

    # Fallback paths within backend package
    fallback_paths = [
        app_dir / "data",
        Path.cwd() / "data",
        Path.cwd() / "backend" / "data",
    ]
    for p in fallback_paths:
        if p.exists() and (p / "sample_curriculum.json").exists():
            return p

    return primary_data_dir

def load_sample_curriculum() -> Tuple[Optional[Dict[str, Any]], Path, bool]:
    """Loads sample_curriculum.json strictly from backend/data/."""
    data_dir = get_backend_data_dir()
    curr_file = data_dir / "sample_curriculum.json"
    if curr_file.exists():
        try:
            with open(curr_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data, curr_file, True
        except Exception as e:
            logger.error(f"Error loading {curr_file}: {e}")
            return None, curr_file, False
    return None, curr_file, False

def load_sample_candidates() -> Tuple[Optional[list], Path, bool]:
    """Loads sample_candidates.json strictly from backend/data/."""
    data_dir = get_backend_data_dir()
    cand_file = data_dir / "sample_candidates.json"
    if cand_file.exists():
        try:
            with open(cand_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data, cand_file, True
        except Exception as e:
            logger.error(f"Error loading {cand_file}: {e}")
            return None, cand_file, False
    return None, cand_file, False
