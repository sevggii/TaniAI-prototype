"""
/diagnose – Modality-bilinçli füzyon
• NLP (belirti): TANI/UstSolunumYolu/modules/nlp_symptoms/src/diagnoser.py
• Vision (CXR): TANI/UstSolunumYolu/modules/vision_cxr_covid/models/.../best.keras
• Başka modüller (audio/tabular) geldiğinde 'modality' adına göre eklenir.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import yaml

APP=FastAPI()

ROOT=Path(__file__).resolve().parents[4]
CORE=ROOT/"diagnosis_core"
CFG=yaml.safe_load((CORE/"configs"/"diagnosis.yaml").read_text())
CLASSES=CFG["classes"]; w_sym=CFG["fusion"]["w_symptoms"]; w_vis=CFG["fusion"]["w_vision"]

# NLP modülü
import sys
sys.path.append(str(ROOT))
from UstSolunumYolu.modules.nlp_symptoms.src.diagnoser import score_symptoms

# Vision modülü (şimdilik devre dışı)
VIS_MODEL=None
VIS_LABELS=None

class SymptomInput(BaseModel):
    ates: bool = False
    titreme: bool = False
    kuru_oksuruk: bool = False
    balgamli_oksuruk: bool = False
    bogaz_agrisi: bool = False
    burun_akintisi: bool = False
    burun_tikanikligi: bool = False
    hapşirma: bool = False
    kas_agrisi: bool = False
    yorgunluk: bool = False
    nefes_darligi: bool = False
    koku_kaybi: bool = False
    goz_kasintisi: bool = False
    goz_sulanmasi: bool = False

@APP.post("/diagnose")
async def diagnose(request: dict):
    # Belirtileri al
    symptoms = request.get("symptoms", {})
    
    # NLP olasılıkları
    p_sym = score_symptoms(symptoms)
    
    # Vision olasılıkları (şimdilik sadece NLP)
    p_vis = {c: 0.0 for c in CLASSES}
    
    # normalize & fuse
    def _norm(d): 
        s = sum(d.values()) or 1.0
        return {k: (v/s) for k, v in d.items()}
    
    p_sym = _norm(p_sym)
    p_vis = _norm(p_vis)
    p_fused = _norm({c: w_sym*p_sym.get(c,0.0) + w_vis*p_vis.get(c,0.0) for c in CLASSES})
    
    return {
        "modality": {
            "nlp": p_sym,
            "vision": p_vis
        },
        "prob_fused": p_fused
    }
