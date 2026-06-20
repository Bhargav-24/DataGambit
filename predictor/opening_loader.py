import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ECO_PATH = BASE_DIR / "eco_names.json"

with open(ECO_PATH, "r", encoding="utf-8") as f:
    ECO_MAP = json.load(f)

CANDIDATE_OPENINGS = [
    {"eco": eco, "opening": name}
    for eco, name in ECO_MAP.items()
]