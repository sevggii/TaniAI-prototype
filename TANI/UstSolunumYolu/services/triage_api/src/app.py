"""
/diagnose – Modality-bilinçli füzyon
• NLP (belirti): TANI/UstSolunumYolu/modules/nlp_symptoms/src/diagnoser.py
• Vision (CXR): TANI/UstSolunumYolu/modules/vision_cxr_covid/models/.../best.keras
• Başka modüller (audio/tabular) geldiğinde 'modality' adına göre eklenir.
"""
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from pathlib import Path
import yaml
import tensorflow as tf
import numpy as np
import json
from PIL import Image
import io

APP=FastAPI()

ROOT=Path(os.getenv("TANI_ROOT", Path(__file__).resolve().parents[4]))
CORE=ROOT/"diagnosis_core"
CFG=yaml.safe_load((CORE/"configs"/"diagnosis.yaml").read_text())
CLASSES=CFG["classes"]; w_sym=CFG["fusion"]["w_symptoms"]; w_vis=CFG["fusion"]["w_vision"]

# NLP modülü
import sys
sys.path.append(str(ROOT))
from UstSolunumYolu.modules.nlp_symptoms.src.diagnoser import score_symptoms

# Vision modülü
VISION_MODEL_PATH = Path(os.getenv("VISION_MODEL_PATH", str(ROOT / "UstSolunumYolu" / "modules" / "vision_cxr_covid" / "models" / "v1_20251019_0107" / "best.keras")))
VISION_LABELS_PATH = Path(os.getenv("VISION_LABELS_PATH", str(ROOT / "UstSolunumYolu" / "modules" / "vision_cxr_covid" / "models" / "v1_20251019_0107" / "labelmap.json")))

# Vision modeli yükle
VIS_MODEL = None
VIS_LABELS = None

def load_vision_model():
    global VIS_MODEL, VIS_LABELS
    try:
        if VISION_MODEL_PATH.exists():
            VIS_MODEL = tf.keras.models.load_model(VISION_MODEL_PATH)
            print(f"✅ Vision model yüklendi: {VISION_MODEL_PATH}")
            
            if VISION_LABELS_PATH.exists():
                VIS_LABELS = json.loads(VISION_LABELS_PATH.read_text())
                print(f"✅ Vision labels yüklendi: {VIS_LABELS}")
            else:
                VIS_LABELS = {"0": "COVID", "1": "Normal"}
                print("⚠️ Label map bulunamadı, varsayılan kullanılıyor")
        else:
            print(f"❌ Vision model bulunamadı: {VISION_MODEL_PATH}")
    except Exception as e:
        print(f"❌ Vision model yükleme hatası: {e}")

# Uygulama başlatıldığında modeli yükle
load_vision_model()

def preprocess_image(image_bytes):
    """Görüntüyü model için hazırla"""
    try:
        # PIL ile görüntüyü aç
        image = Image.open(io.BytesIO(image_bytes))
        
        # RGB'ye çevir
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 224x224 boyutuna getir
        image = image.resize((224, 224))
        
        # NumPy array'e çevir ve normalize et
        img_array = np.array(image) / 255.0
        
        # Batch dimension ekle
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        print(f"❌ Görüntü işleme hatası: {e}")
        return None

def analyze_chest_xray(image_bytes):
    """Chest X-ray görüntüsünü analiz et"""
    if VIS_MODEL is None:
        return {"error": "Vision model yüklenemedi"}
    
    # Görüntüyü hazırla
    processed_image = preprocess_image(image_bytes)
    if processed_image is None:
        return {"error": "Görüntü işlenemedi"}
    
    try:
        # Model ile tahmin yap
        predictions = VIS_MODEL.predict(processed_image, verbose=0)
        
        # Sonuçları işle
        if VIS_LABELS:
            results = {}
            for i, (label_key, label_name) in enumerate(VIS_LABELS.items()):
                if i < len(predictions[0]):
                    results[label_name] = float(predictions[0][i])
            
            # TANI sistemine uygun formata çevir
            vision_probs = {}
            for disease in CLASSES:
                if disease == "COVID-19":
                    vision_probs[disease] = results.get("COVID", 0.0)
                else:
                    # Diğer hastalıklar için vision'dan bilgi yok
                    vision_probs[disease] = 0.0
            
            # Normal sınıfını ekle (vision modeli için)
            vision_probs["Normal"] = results.get("Normal", 0.0)
            
            return vision_probs
        else:
            return {"error": "Label map bulunamadı"}
            
    except Exception as e:
        print(f"❌ Vision analiz hatası: {e}")
        return {"error": f"Analiz hatası: {str(e)}"}

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

@APP.post("/analyze_cxr")
async def analyze_cxr(cxr_image: UploadFile = File(...)):
    """Chest X-ray görüntüsünü analiz et"""
    try:
        # Görüntüyü oku
        image_bytes = await cxr_image.read()
        
        # Vision analizi yap
        vision_results = analyze_chest_xray(image_bytes)
        
        if "error" in vision_results:
            return {"error": vision_results["error"]}
        
        # Sonuçları normalize et
        def _norm(d): 
            s = sum(d.values()) or 1.0
            return {k: (v/s) for k, v in d.items()}
        
        p_vis = _norm(vision_results)
        
        return {
            "modality": "vision",
            "probabilities": p_vis,
            "analysis": {
                "covid_probability": p_vis.get("COVID-19", 0.0),
                "normal_probability": p_vis.get("Normal", 0.0),
                "confidence": max(p_vis.values()) if p_vis else 0.0
            }
        }
        
    except Exception as e:
        return {"error": f"Analiz hatası: {str(e)}"}

@APP.post("/combined_diagnosis")
async def combined_diagnosis(
    symptoms: str = Form(...),
    cxr_image: UploadFile = File(None)
):
    """Kombine tanı (belirti + görüntü)"""
    try:
        # Belirtileri parse et
        import json
        symptoms_dict = json.loads(symptoms)
        
        # NLP olasılıkları
        p_sym = score_symptoms(symptoms_dict)
        
        # Vision olasılıkları
        p_vis = {c: 0.0 for c in CLASSES}
        if cxr_image:
            image_bytes = await cxr_image.read()
            vision_results = analyze_chest_xray(image_bytes)
            if "error" not in vision_results:
                p_vis = vision_results
        
        # normalize & fuse
        def _norm(d): 
            s = sum(d.values()) or 1.0
            return {k: (v/s) for k, v in d.items()}
        
        p_sym = _norm(p_sym)
        p_vis = _norm(p_vis)
        p_fused = _norm({c: w_sym*p_sym.get(c,0.0) + w_vis*p_vis.get(c,0.0) for c in CLASSES})
        
        # En yüksek olasılıklı hastalığı bul
        best_disease = max(p_fused.items(), key=lambda x: x[1])
        
        return {
            "modality": {
                "nlp": p_sym,
                "vision": p_vis
            },
            "prob_fused": p_fused,
            "diagnosis": {
                "disease": best_disease[0],
                "confidence": best_disease[1],
                "has_image": cxr_image is not None
            }
        }
        
    except Exception as e:
        return {"error": f"Kombine tanı hatası: {str(e)}"}

@APP.get("/health")
async def health_check():
    """Sistem durumu kontrolü"""
    return {
        "status": "healthy",
        "vision_model_loaded": VIS_MODEL is not None,
        "nlp_module_loaded": True,
        "classes": CLASSES
    }
