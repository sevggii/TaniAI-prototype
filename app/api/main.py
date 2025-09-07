from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from typing import Dict, List, Optional, Any
import uvicorn
import logging
import time
from datetime import datetime
import hashlib
import secrets

from ..models.nutrient_diagnosis_system import NutrientDiagnosisSystem
# from .voice import router as voice_router  # Geçici olarak devre dışı

# FastAPI uygulaması oluştur
app = FastAPI(
    title="TanıAI - Vitamin Eksikliği Teşhis Sistemi",
    description="Hastaların semptomlarını analiz ederek vitamin eksikliklerini tespit eden AI sistemi",
    version="1.0.0"
)

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Güvenlik middleware'leri
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate limiting için basit bir cache
request_cache = {}
MAX_REQUESTS_PER_MINUTE = 60

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Basit rate limiting middleware"""
    client_ip = request.client.host
    current_time = time.time()
    
    # 1 dakika önceki istekleri temizle
    if client_ip in request_cache:
        request_cache[client_ip] = [
            req_time for req_time in request_cache[client_ip] 
            if current_time - req_time < 60
        ]
    else:
        request_cache[client_ip] = []
    
    # Rate limit kontrolü
    if len(request_cache[client_ip]) >= MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Çok fazla istek. Lütfen 1 dakika bekleyin.")
    
    # İsteği kaydet
    request_cache[client_ip].append(current_time)
    
    # İsteği işle
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response

# Static dosyaları serve et
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Sesli erişim router'ını ekle (geçici olarak devre dışı)
# app.include_router(voice_router, prefix="/api/voice", tags=["voice"])

# Nutrient teşhis sistemi (Vitamin + Mineral)
nutrient_system = NutrientDiagnosisSystem()

# Pydantic modelleri
class DiagnosisRequest(BaseModel):
    patient_name: str
    age: int
    gender: str
    symptoms: Dict[str, int]
    
    @validator('patient_name')
    def validate_patient_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Hasta adı en az 2 karakter olmalıdır')
        if len(v) > 100:
            raise ValueError('Hasta adı 100 karakterden uzun olamaz')
        # Güvenlik: Sadece harf, boşluk ve Türkçe karakterlere izin ver
        import re
        if not re.match(r'^[a-zA-ZçğıöşüÇĞIİÖŞÜ\s]+$', v):
            raise ValueError('Hasta adı sadece harf ve boşluk içerebilir')
        return v.strip()
    
    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 120:
            raise ValueError('Yaş 0-120 arasında olmalıdır')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        allowed_genders = ['Erkek', 'Kadın', 'erkek', 'kadın', 'E', 'K']
        if v not in allowed_genders:
            raise ValueError('Cinsiyet Erkek veya Kadın olmalıdır')
        return v.title()
    
    @validator('symptoms')
    def validate_symptoms(cls, v):
        if not v:
            raise ValueError('En az bir semptom belirtilmelidir')
        if len(v) > 50:
            raise ValueError('En fazla 50 semptom belirtilebilir')
        
        # Semptom değerlerini kontrol et
        for symptom, severity in v.items():
            if not isinstance(severity, int):
                raise ValueError(f'Semptom şiddeti sayı olmalıdır: {symptom}')
            if severity < 0 or severity > 3:
                raise ValueError(f'Semptom şiddeti 0-3 arasında olmalıdır: {symptom}')
        
        return v

class DiagnosisResponse(BaseModel):
    summary: Dict[str, Any]
    nutrient_results: Dict[str, Any]
    priority_nutrients: List[str]
    overall_risk_level: str
    immediate_actions: List[str]
    tests_recommended: List[str]
    dietary_recommendations: List[str]
    mvp_deficient: List[str]
    extended_deficient: List[str]

class HealthResponse(BaseModel):
    status: str
    message: str
    models_loaded: int
    total_symptoms: int

# Ana sayfa
@app.get("/")
async def read_root():
    """Ana sayfa - HTML arayüzünü serve eder"""
    from fastapi.responses import FileResponse
    return FileResponse("app/static/index.html")

# API endpoints
@app.get("/api")
async def api_info():
    """API bilgileri"""
    return {
        "name": "TanıAI API",
        "version": "1.0.0",
        "description": "Vitamin eksikliği teşhis sistemi",
        "endpoints": {
            "health": "/api/health",
            "symptoms": "/api/symptoms",
            "diagnose": "/api/diagnose",
            "train": "/api/train"
        }
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Sistem sağlık durumu"""
    return HealthResponse(
        status="healthy",
        message="TanıAI sistemi çalışıyor",
        models_loaded=len(nutrient_system.models),
        total_symptoms=len(nutrient_system.all_symptoms)
    )

@app.get("/api/symptoms")
async def get_symptoms():
    """Tüm semptomları listeler"""
    return {
        "symptoms": nutrient_system.get_all_symptoms(),
        "total_count": len(nutrient_system.all_symptoms)
    }

@app.post("/api/diagnose", response_model=DiagnosisResponse)
async def diagnose_nutrient_deficiency(request: DiagnosisRequest):
    """Vitamin ve mineral eksikliği teşhisi yapar"""
    try:
        logger.info(f"Teşhis isteği alındı - Hasta: {request.patient_name}, Yaş: {request.age}")
        
        # Semptom sayısını kontrol et
        if len(request.symptoms) < 1:
            raise HTTPException(status_code=400, detail="En az bir semptom belirtilmelidir")
        
        # Tüm nutrientler için teşhis yap
        results = nutrient_system.diagnose_all_nutrients(request.symptoms)
        
        if not results:
            raise HTTPException(status_code=500, detail="Teşhis sonuçları alınamadı")
        
        # Özet raporu oluştur
        summary = nutrient_system.get_summary_report(results)
        
        # Öncelikli nutrientleri belirle
        priority_nutrients = nutrient_system.get_priority_nutrients(results)
        
        # Genel önerileri al
        overall_recommendations = nutrient_system.get_overall_recommendations(results)
        
        # Güvenlik uyarısı ekle
        summary['disclaimer'] = "Bu teşhis yapay zeka destekli bir ön değerlendirmedir. Kesin tanı için doktor kontrolü gereklidir."
        
        logger.info(f"Teşhis tamamlandı - Risk seviyesi: {summary['overall_risk_level']}")
        
        return DiagnosisResponse(
            summary=summary,
            nutrient_results=results,
            priority_nutrients=priority_nutrients,
            overall_risk_level=summary['overall_risk_level'],
            immediate_actions=overall_recommendations['immediate_actions'],
            tests_recommended=overall_recommendations['tests_recommended'],
            dietary_recommendations=overall_recommendations['dietary_recommendations'],
            mvp_deficient=summary['mvp_deficient'],
            extended_deficient=summary['extended_deficient']
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validasyon hatası: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Geçersiz veri: {str(e)}")
    except Exception as e:
        logger.error(f"Teşhis hatası: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Teşhis sırasında beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.")

@app.post("/api/train")
async def train_models():
    """Tüm modelleri yeniden eğitir"""
    try:
        nutrient_system.train_all_models()
        return {
            "status": "success",
            "message": "Tüm modeller başarıyla eğitildi",
            "models_trained": len(nutrient_system.all_nutrients)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model eğitimi sırasında hata oluştu: {str(e)}")

@app.get("/api/nutrient/{nutrient_name}")
async def get_nutrient_info(nutrient_name: str):
    """Belirli bir nutrient hakkında bilgi döndürür"""
    nutrient_info = nutrient_system.get_nutrient_info(nutrient_name)
    if not nutrient_info:
        raise HTTPException(status_code=404, detail="Nutrient bulunamadı")
    return nutrient_info

@app.get("/api/demo-scenarios")
async def get_demo_scenarios():
    """Demo senaryolarını döndürür"""
    return {
        "scenarios": nutrient_system.get_demo_scenarios()
    }

@app.get("/api/reference-ranges")
async def get_reference_ranges():
    """Tüm nutrientlerin referans aralıklarını döndürür"""
    try:
        reference_ranges = {}
        for nutrient in nutrient_system.all_nutrients:
            info = nutrient_system.get_nutrient_info(nutrient)
            if 'reference_ranges' in info:
                reference_ranges[nutrient] = {
                    'name': info['name'],
                    'type': info['type'],
                    'reference_ranges': info['reference_ranges']
                }
        return {"reference_ranges": reference_ranges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Referans aralıkları alınamadı: {str(e)}")

@app.get("/api/reference-ranges/{nutrient_name}")
async def get_nutrient_reference_ranges(nutrient_name: str):
    """Belirli bir nutrientin referans aralıklarını döndürür"""
    try:
        info = nutrient_system.get_nutrient_info(nutrient_name)
        if not info:
            raise HTTPException(status_code=404, detail=f"{nutrient_name} nutrient bulunamadı")
        
        if 'reference_ranges' not in info:
            raise HTTPException(status_code=404, detail=f"{nutrient_name} için referans aralığı bulunamadı")
        
        return {
            "nutrient": nutrient_name,
            "name": info['name'],
            "type": info['type'],
            "reference_ranges": info['reference_ranges']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Referans aralığı alınamadı: {str(e)}")

@app.get("/api/model-performance")
async def get_model_performance():
    """Tüm modellerin performans metriklerini döndürür"""
    try:
        performance_data = {}
        
        for nutrient, model in nutrient_system.models.items():
            if hasattr(model, 'model_performance') and model.model_performance:
                performance_data[nutrient] = {
                    'accuracy': model.model_performance['accuracy'],
                    'auc_score': model.model_performance['auc_score'],
                    'cv_mean': model.model_performance['cv_mean'],
                    'cv_std': model.model_performance['cv_std'],
                    'confusion_matrix': model.model_performance['confusion_matrix']
                }
            else:
                performance_data[nutrient] = {
                    'status': 'Model henüz eğitilmedi veya performans verisi yok'
                }
        
        return {
            "model_performance": performance_data,
            "total_models": len(nutrient_system.models),
            "trained_models": len([m for m in performance_data.values() if 'accuracy' in m])
        }
    except Exception as e:
        logger.error(f"Model performans verisi alınamadı: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model performans verisi alınamadı: {str(e)}")

@app.get("/api/health-detailed")
async def detailed_health_check():
    """Detaylı sistem sağlık durumu"""
    try:
        system_info = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "models": {
                "total": len(nutrient_system.all_nutrients),
                "loaded": len(nutrient_system.models),
                "mvp": len(nutrient_system.mvp_nutrients),
                "extended": len(nutrient_system.extended_nutrients),
                "diagnosis_modules": len(nutrient_system.diagnosis_modules)
            },
            "symptoms": {
                "total": len(nutrient_system.all_symptoms),
                "sample": list(nutrient_system.all_symptoms)[:10]
            },
            "performance": {
                "memory_usage": "N/A",  # Gerçek uygulamada psutil kullanılabilir
                "uptime": "N/A"
            }
        }
        
        return system_info
    except Exception as e:
        logger.error(f"Detaylı sağlık kontrolü hatası: {str(e)}")
        raise HTTPException(status_code=500, detail="Sistem sağlık durumu alınamadı")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)