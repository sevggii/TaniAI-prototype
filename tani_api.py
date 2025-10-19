"""
TANI Tanı Sistemi API
====================

Sadece TANI tanı sistemi için minimal API
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List
from datetime import datetime
import sys
from pathlib import Path
import os

# TANI sistem import'ları
tani_root = Path(__file__).parent / "TANI"
sys.path.append(str(tani_root))
from UstSolunumYolu.modules.nlp_symptoms.src.diagnoser import score_symptoms

# FastAPI uygulaması
app = FastAPI(
    title="TANI Tanı Sistemi API",
    description="Üst solunum yolu hastalıkları tanı sistemi",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Güvenlik
security = HTTPBearer()

# Basit API anahtarı sistemi
VALID_API_KEYS = {
    "dev_key_123": {"role": "developer", "rate_limit": 1000},
    "test_key_456": {"role": "test", "rate_limit": 100}
}

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """API anahtarı doğrulama"""
    api_key = credentials.credentials
    
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Geçersiz API anahtarı"
        )
    
    return api_key

class TaniSymptomRequest(BaseModel):
    """TANI semptom analiz isteği"""
    symptoms: Dict[str, bool] = Field(..., description="Semptomlar (ates, kuru_oksuruk, vb.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": {
                    "ates": True,
                    "kuru_oksuruk": True,
                    "nefes_darligi": True,
                    "koku_kaybi": True,
                    "burun_akintisi": False,
                    "hapşirma": False
                }
            }
        }

class TaniDiagnosisResponse(BaseModel):
    """TANI tanı yanıtı"""
    modality: Dict[str, Dict[str, float]] = Field(..., description="Modalite sonuçları")
    prob_fused: Dict[str, float] = Field(..., description="Birleştirilmiş olasılıklar")
    diagnosis: str = Field(..., description="En yüksek olasılıklı tanı")
    confidence: float = Field(..., description="Güven skoru")
    recommendations: List[str] = Field(..., description="Öneriler")
    timestamp: str = Field(..., description="Analiz zamanı")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Ana endpoint"""
    return {
        "message": "TANI Tanı Sistemi API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Sistem sağlık kontrolü"""
    return {
        "status": "healthy",
        "service": "tani",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/tani/diagnose", 
          response_model=TaniDiagnosisResponse,
          tags=["TANI Diagnosis"])
async def tani_diagnose(
    request: TaniSymptomRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    🩺 TANI Semptom Analizi
    
    Üst solunum yolu hastalıklarını semptomlara göre analiz eder:
    - COVID-19
    - GRIP (Grip)
    - SOGUK_ALGINLIGI (Soğuk Algınlığı)
    - MEVSIMSEL_ALERJI (Mevsimsel Alerji)
    """
    try:
        # Semptom analizi yap
        nlp_probs = score_symptoms(request.symptoms)
        
        # Vision modülü şimdilik devre dışı (sadece NLP)
        vision_probs = {c: 0.0 for c in ["COVID-19", "GRIP", "SOGUK_ALGINLIGI", "MEVSIMSEL_ALERJI"]}
        
        # Normalize et
        def normalize_probs(probs):
            total = sum(probs.values()) or 1.0
            return {k: v/total for k, v in probs.items()}
        
        nlp_probs = normalize_probs(nlp_probs)
        vision_probs = normalize_probs(vision_probs)
        
        # Füzyon (NLP %60, Vision %40)
        w_nlp, w_vision = 0.6, 0.4
        fused_probs = {
            disease: w_nlp * nlp_probs.get(disease, 0.0) + w_vision * vision_probs.get(disease, 0.0)
            for disease in ["COVID-19", "GRIP", "SOGUK_ALGINLIGI", "MEVSIMSEL_ALERJI"]
        }
        fused_probs = normalize_probs(fused_probs)
        
        # En yüksek olasılıklı tanıyı bul
        best_diagnosis = max(fused_probs.items(), key=lambda x: x[1])
        diagnosis_name = best_diagnosis[0]
        confidence = best_diagnosis[1]
        
        # Öneriler oluştur
        recommendations = []
        if diagnosis_name == "COVID-19":
            recommendations = [
                "COVID-19 şüphesi var. Derhal test yaptırın.",
                "Kendinizi izole edin ve diğer insanlarla teması sınırlayın.",
                "Ateş ve nefes darlığı varsa acil servise başvurun.",
                "Bol sıvı tüketin ve dinlenin."
            ]
        elif diagnosis_name == "GRIP":
            recommendations = [
                "Grip belirtileri tespit edildi. Doktora başvurun.",
                "Bol sıvı tüketin ve yatak istirahati yapın.",
                "Ateş düşürücü ilaçlar kullanabilirsiniz.",
                "Diğer insanlarla teması sınırlayın."
            ]
        elif diagnosis_name == "SOGUK_ALGINLIGI":
            recommendations = [
                "Soğuk algınlığı belirtileri tespit edildi.",
                "Bol sıvı tüketin ve dinlenin.",
                "Burun tıkanıklığı için tuzlu su ile gargara yapın.",
                "Semptomlar 7-10 gün içinde düzelmelidir."
            ]
        elif diagnosis_name == "MEVSIMSEL_ALERJI":
            recommendations = [
                "Mevsimsel alerji belirtileri tespit edildi.",
                "Antihistaminik ilaçlar kullanabilirsiniz.",
                "Alerjenlerden kaçının (polen, toz vb.).",
                "Gözlerinizi yıkayın ve burun temizliği yapın."
            ]
        
        return TaniDiagnosisResponse(
            modality={
                "nlp": nlp_probs,
                "vision": vision_probs
            },
            prob_fused=fused_probs,
            diagnosis=diagnosis_name,
            confidence=confidence,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TANI tanı hatası: {str(e)}")

@app.get("/tani/symptoms", tags=["TANI Diagnosis"])
async def get_available_symptoms():
    """
    📋 Mevcut Semptomlar
    
    TANI sisteminde kullanılabilen tüm semptomları listeler.
    """
    symptoms = {
        "ates": {"turkish": "Ateş", "english": "Fever", "type": "boolean"},
        "titreme": {"turkish": "Titreme", "english": "Chills", "type": "boolean"},
        "kuru_oksuruk": {"turkish": "Kuru Öksürük", "english": "Dry Cough", "type": "boolean"},
        "balgamli_oksuruk": {"turkish": "Balgamlı Öksürük", "english": "Productive Cough", "type": "boolean"},
        "bogaz_agrisi": {"turkish": "Boğaz Ağrısı", "english": "Sore Throat", "type": "boolean"},
        "burun_akintisi": {"turkish": "Burun Akıntısı", "english": "Runny Nose", "type": "boolean"},
        "burun_tikanikligi": {"turkish": "Burun Tıkanıklığı", "english": "Nasal Congestion", "type": "boolean"},
        "hapşirma": {"turkish": "Hapşırma", "english": "Sneezing", "type": "boolean"},
        "kas_agrisi": {"turkish": "Kas Ağrısı", "english": "Muscle Ache", "type": "boolean"},
        "yorgunluk": {"turkish": "Yorgunluk", "english": "Fatigue", "type": "boolean"},
        "nefes_darligi": {"turkish": "Nefes Darlığı", "english": "Shortness of Breath", "type": "boolean"},
        "koku_kaybi": {"turkish": "Koku Kaybı", "english": "Loss of Smell", "type": "boolean"},
        "goz_kasintisi": {"turkish": "Göz Kaşıntısı", "english": "Itchy Eyes", "type": "boolean"},
        "goz_sulanmasi": {"turkish": "Göz Sulanması", "english": "Watery Eyes", "type": "boolean"}
    }
    
    return {
        "symptoms": symptoms,
        "total_symptoms": len(symptoms),
        "diseases": ["COVID-19", "GRIP", "SOGUK_ALGINLIGI", "MEVSIMSEL_ALERJI"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/tani/health", tags=["TANI Diagnosis"])
async def tani_health_check():
    """
    ✓ TANI Sistem Sağlık Kontrolü
    
    TANI tanı sisteminin durumunu kontrol eder.
    """
    try:
        # NLP modülünü test et
        test_symptoms = {"ates": True, "kuru_oksuruk": True}
        test_result = score_symptoms(test_symptoms)
        
        return {
            "status": "healthy",
            "nlp_module": "loaded",
            "vision_module": "not_available",
            "test_result": test_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "tani_api:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
