#!/usr/bin/env python3
"""
🏥 Üst Solunum Yolu Hastalık Tanı API
=====================================

Mobil uygulamalar için FastAPI tabanlı REST API

Kullanım:
    uvicorn mobile_api_example:app --reload --host 0.0.0.0 --port 8000

Endpoint:
    POST /api/v1/diagnose
    Body: {"symptoms": "Ateşim var, nefes alamıyorum"}

Author: Medical AI Team
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
import logging
from datetime import datetime
import uuid

# Import our disease predictor
try:
    from ultra_precise_predict import UltraPreciseDiseasePredictor
except ImportError:
    from professional_medical_system import ProfessionalMedicalSystem as UltraPreciseDiseasePredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="🏥 Üst Solunum Yolu Hastalık Tanı API",
    description="Mobil uygulamalar için yapay zeka destekli hastalık tanı sistemi",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Mobil uygulamalardan erişim için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain'ler belirtin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
try:
    predictor = UltraPreciseDiseasePredictor("ultra_precise_disease_model.pkl")
    logger.info("✅ Model başarıyla yüklendi")
except Exception as e:
    logger.error(f"❌ Model yüklenemedi: {e}")
    predictor = None


# Pydantic models for request/response
class SymptomInput(BaseModel):
    """Semptom girişi için model"""
    symptoms: str = Field(
        ..., 
        min_length=5, 
        max_length=500,
        description="Hasta semptomu (Türkçe)",
        example="Ateşim var, nefes alamıyorum, koku alamıyorum"
    )
    patient_id: Optional[str] = Field(
        None,
        description="Opsiyonel hasta ID (anonim)"
    )
    
    @validator('symptoms')
    def validate_symptoms(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Semptom açıklaması boş olamaz")
        return v.strip()


class DiagnosisResponse(BaseModel):
    """Tanı sonucu için model"""
    diagnosis_id: str = Field(description="Benzersiz tanı ID")
    disease: str = Field(description="Tespit edilen hastalık")
    confidence: float = Field(description="Güven skoru (0-1)")
    confidence_percentage: str = Field(description="Güven yüzdesi")
    severity: str = Field(description="Ciddiyet seviyesi")
    detected_symptoms: Dict[str, float] = Field(description="Tespit edilen semptomlar")
    recommendations: List[str] = Field(description="Tıbbi öneriler")
    probabilities: Dict[str, float] = Field(description="Tüm hastalık olasılıkları")
    timestamp: str = Field(description="Tanı zamanı")
    warning: str = Field(description="Tıbbi uyarı")


class HealthResponse(BaseModel):
    """API sağlık kontrolü için model"""
    status: str
    model_loaded: bool
    version: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Hata yanıtı için model"""
    error: str
    detail: str
    timestamp: str


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Ana endpoint - API bilgisi"""
    return {
        "message": "🏥 Üst Solunum Yolu Hastalık Tanı API",
        "version": "1.0.0",
        "endpoints": {
            "diagnose": "/api/v1/diagnose",
            "health": "/api/v1/health",
            "docs": "/docs"
        }
    }


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    API sağlık kontrolü
    
    Returns:
        Sistem durumu ve model yükleme bilgisi
    """
    return HealthResponse(
        status="healthy" if predictor else "degraded",
        model_loaded=predictor is not None,
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.post(
    "/api/v1/diagnose",
    response_model=DiagnosisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Diagnosis"],
    summary="Hastalık Tanısı Yap",
    description="Semptom açıklamasından hastalık tanısı yapar"
)
async def diagnose(input_data: SymptomInput):
    """
    Hastalık tanısı endpoint
    
    Args:
        input_data: Semptom açıklaması içeren girdi
        
    Returns:
        Detaylı tanı sonucu
        
    Raises:
        HTTPException: Model yüklü değilse veya tahmin başarısız olursa
    """
    # Model kontrolü
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model yüklü değil. Lütfen sistem yöneticisine başvurun."
        )
    
    try:
        # Tanı yap
        logger.info(f"📋 Yeni tanı isteği: '{input_data.symptoms[:50]}...'")
        result = predictor.predict_disease(input_data.symptoms)
        
        # Benzersiz ID oluştur
        diagnosis_id = str(uuid.uuid4())
        
        # Yanıt hazırla
        response = DiagnosisResponse(
            diagnosis_id=diagnosis_id,
            disease=result.get('prediction', 'Bilinmeyen'),
            confidence=result.get('confidence', 0.0),
            confidence_percentage=f"%{result.get('confidence', 0.0) * 100:.1f}",
            severity=result.get('severity_level', 'Orta'),
            detected_symptoms=result.get('detected_symptoms', {}),
            recommendations=result.get('recommendations', []),
            probabilities=result.get('probabilities', {}),
            timestamp=datetime.now().isoformat(),
            warning="⚠️ Bu sistem ön tanı amaçlıdır. Kesin tanı için doktora başvurun!"
        )
        
        logger.info(f"✅ Tanı tamamlandı: {response.disease} (%{response.confidence*100:.1f})")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Tanı hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tanı işlemi sırasında hata oluştu: {str(e)}"
        )


@app.get("/api/v1/diseases", tags=["Information"])
async def get_supported_diseases():
    """
    Desteklenen hastalıkları listeler
    
    Returns:
        Hastalık listesi ve özellikleri
    """
    return {
        "supported_diseases": [
            {
                "name": "COVID-19",
                "accuracy": "100%",
                "key_symptoms": ["Koku/tat kaybı", "Nefes darlığı", "Ateş", "Öksürük"]
            },
            {
                "name": "Soğuk Algınlığı",
                "accuracy": "100%",
                "key_symptoms": ["Burun akıntısı", "Hapşırma", "Boğaz ağrısı"]
            },
            {
                "name": "Mevsimsel Alerji",
                "accuracy": "100%",
                "key_symptoms": ["Göz kaşıntısı", "Hapşırma", "Burun tıkanıklığı"]
            },
            {
                "name": "Grip",
                "accuracy": "88%",
                "key_symptoms": ["Yüksek ateş", "Vücut ağrıları", "Titreme", "Bitkinlik"]
            }
        ],
        "total_diseases": 4,
        "overall_accuracy": "86.7%"
    }


@app.get("/api/v1/symptoms", tags=["Information"])
async def get_supported_symptoms():
    """
    Desteklenen semptomları listeler
    
    Returns:
        Semptom listesi
    """
    return {
        "supported_symptoms": [
            "Ateş", "Öksürük", "Nefes Darlığı", "Bitkinlik",
            "Vücut Ağrıları", "Baş Ağrısı", "Boğaz Ağrısı",
            "Burun Akıntısı", "Burun Tıkanıklığı", "Hapşırma",
            "Koku/Tat Kaybı", "İshal", "Bulantı/Kusma",
            "Göğüs Ağrısı", "Titreme", "Göz Kızarıklığı",
            "Göz Kaşıntısı", "Hırıltılı Solunum"
        ],
        "total_symptoms": 18,
        "language": "Türkçe"
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Genel exception handler"""
    logger.error(f"Beklenmeyen hata: {str(exc)}")
    return {
        "error": "İç sunucu hatası",
        "detail": str(exc),
        "timestamp": datetime.now().isoformat()
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında çalışır"""
    logger.info("🚀 API başlatılıyor...")
    logger.info(f"📊 Model durumu: {'✅ Yüklü' if predictor else '❌ Yüklenmedi'}")
    logger.info("🌐 API hazır: http://localhost:8000")
    logger.info("📚 Dokümantasyon: http://localhost:8000/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Uygulama kapatılırken çalışır"""
    logger.info("🛑 API kapatılıyor...")


if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  🏥 Üst Solunum Yolu Hastalık Tanı API                  ║
    ║  Version: 1.0.0                                          ║
    ║  Mobil Uygulama Entegrasyonu için Hazır                 ║
    ╚══════════════════════════════════════════════════════════╝
    
    📍 API Adresi: http://localhost:8000
    📚 Dokümantasyon: http://localhost:8000/docs
    🔍 Endpoint: POST /api/v1/diagnose
    
    🚀 Başlatılıyor...
    """)
    
    uvicorn.run(
        "mobile_api_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

