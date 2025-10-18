"""
Model Registry
--------------
Modül karması olmasın diye her eğitilmiş model buraya kayıt düşer.
Her kayıt: id, modality, task, dataset, path, created_at.
"""
from pathlib import Path
import json, time

REG_PATH = Path(__file__).resolve().parents[1] / "model_registry.json"

def register_model(entry: dict):
    entry.setdefault("created_at", int(time.time()))
    data = []
    if REG_PATH.exists():
        data = json.loads(REG_PATH.read_text())
    data.append(entry)
    REG_PATH.write_text(json.dumps(data, indent=2))
    return entry

def latest_by(modality: str, task: str):
    if not REG_PATH.exists(): return None
    data = json.loads(REG_PATH.read_text())
    cand = [e for e in data if e.get("modality")==modality and e.get("task")==task]
    return sorted(cand, key=lambda e: e.get("created_at", 0))[-1] if cand else None
