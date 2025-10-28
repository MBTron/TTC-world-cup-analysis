from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

print("PROJECT_ROOT =", PROJECT_ROOT)

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
GTFS_DIR = DATA_DIR / "gtfs"

for d in [DATA_DIR, RAW_DIR, GTFS_DIR]:
    # Use parents=True, exist_ok=True to create the full path if needed
    # and not error if the directory already exists.
    d.mkdir(parents=True, exist_ok=True)
