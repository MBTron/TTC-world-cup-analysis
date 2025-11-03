from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

def get_project_root() -> Path:
    """Returns the project root directory."""
    return Path(__file__).resolve().parent.parent

def get_data_directories(create: bool = False) -> dict:
    """
    Returns paths to data directories. 

    Args:
        create: If True, create directories if they don't exist
    """

    root = get_project_root()
    dirs = {
        'data': root / "data",
        'raw': root / "data" / "raw",
        'gtfs': root / "data" / "gtfs"
    }
    
    if create:
        for dir_path in dirs.values():
            dir_path.mkdir(parents = True, exist_ok=True)

    return dirs
