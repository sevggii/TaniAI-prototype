"""
NLP/Belirti Skorlama
• configs/diagnosis.yaml'daki 0–3 ölçekli tablo (CDC/WHO ve klinik kaynaklardan
  sayısallaştırılmış) kullanılarak softmax olasılıkları üretir.
• Bu modül eğitim gerektirmez; veri geldiğinde ML ile güncellenebilir.
"""
from pathlib import Path
import yaml, math

CFG = yaml.safe_load((Path(__file__).resolve().parents[4] / "diagnosis_core" / "configs" / "diagnosis.yaml").read_text())
CLASSES = CFG["classes"]; W = CFG["symptom_weights"]

def _softmax(z):
    m=max(z); ex=[math.exp(v-m) for v in z]; s=sum(ex) or 1.0; return [v/s for v in ex]

def score_symptoms(symptoms: dict):
    z=[0.0]*len(CLASSES)
    for name, present in symptoms.items():
        if present and name in W:
            for i,v in enumerate(W[name]): z[i]+=float(v)
    probs=_softmax(z)
    return {c: float(p) for c,p in zip(CLASSES, probs)}
