import os
import json
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger("SkillProof.DataLoader")

def get_authoritative_data_dir() -> Path:
    """
    Returns the authoritative runtime data directory (backend/data/).
    Resolves strictly based on the backend application package location.
    """
    app_dir = Path(__file__).resolve().parent  # backend/app
    backend_dir = app_dir.parent               # backend
    
    # 1. Primary authoritative location: backend/data
    primary_data_dir = backend_dir / "data"
    if primary_data_dir.exists() and (primary_data_dir / "sample_curriculum.json").exists():
        return primary_data_dir

    # 2. Secondary fallback locations if packaging structure varies
    fallback_paths = [
        app_dir / "data",
        Path.cwd() / "data",
        Path.cwd() / "backend" / "data",
        backend_dir.parent / "data"
    ]
    for path in fallback_paths:
        if path.exists() and (path / "sample_curriculum.json").exists():
            return path

    return primary_data_dir

def load_sample_curriculum() -> Tuple[Optional[Dict[str, Any]], Path, bool]:
    """Loads sample_curriculum.json from the authoritative backend/data/ directory."""
    data_dir = get_authoritative_data_dir()
    curr_file = data_dir / "sample_curriculum.json"
    if curr_file.exists():
        try:
            with open(curr_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data, curr_file, True
        except Exception as e:
            logger.error(f"Failed to parse sample_curriculum.json at {curr_file}: {e}")
            return None, curr_file, False
    return None, curr_file, False

def load_sample_candidates() -> Tuple[Optional[list], Path, bool]:
    """Loads sample_candidates.json from the authoritative backend/data/ directory."""
    data_dir = get_authoritative_data_dir()
    cand_file = data_dir / "sample_candidates.json"
    if cand_file.exists():
        try:
            with open(cand_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data, cand_file, True
        except Exception as e:
            logger.error(f"Failed to parse sample_candidates.json at {cand_file}: {e}")
            return None, cand_file, False
    return None, cand_file, False
