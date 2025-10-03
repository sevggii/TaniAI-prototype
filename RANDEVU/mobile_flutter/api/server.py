#!/usr/bin/env python3
"""
FastAPI Server for LLM Clinic Analysis
Flutter uygulamasından gelen şikayetleri analiz eder
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import sys
import os

# API klasörünü Python path'e ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_clinic_analyzer import LLMClinicAnalyzer

# Logging ayarla
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Clinic Analyzer API", version="1.0.0")

# CORS ayarları - Flutter uygulamasından gelen isteklere izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development için tüm origin'lere izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM analyzer'ı başlat
analyzer = None

@app.on_event("startup")
async def startup_event():
    """Uygulama başlatıldığında LLM analyzer'ı initialize et"""
    global analyzer
    try:
        analyzer = LLMClinicAnalyzer()
        logger.info("LLM Clinic Analyzer başlatıldı")
    except Exception as e:
        logger.error(f"LLM Analyzer başlatılamadı: {e}")

class ComplaintRequest(BaseModel):
    complaint: str

class ClinicRecommendation(BaseModel):
    name: str
    reason: str
    confidence: float

class AnalysisResponse(BaseModel):
    primary_clinic: ClinicRecommendation
    secondary_clinics: list[ClinicRecommendation]

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "LLM Clinic Analyzer API çalışıyor", "status": "healthy"}

@app.post("/analyze-complaint", response_model=AnalysisResponse)
async def analyze_complaint(request: ComplaintRequest):
    """
    Hasta şikayetini analiz eder ve klinik önerileri döner
    """
    try:
        if not analyzer:
            raise HTTPException(status_code=500, detail="LLM Analyzer başlatılamadı")
        
        if not request.complaint.strip():
            raise HTTPException(status_code=400, detail="Şikayet boş olamaz")
        
        logger.info(f"Şikayet analiz ediliyor: {request.complaint[:50]}...")
        
        # LLM ile analiz yap
        result = analyzer.analyze_complaint(request.complaint)
        
        if not result:
            raise HTTPException(status_code=500, detail="Analiz başarısız")
        
        # Response formatını düzenle
        response = AnalysisResponse(
            primary_clinic=ClinicRecommendation(
                name=result.get("primary_clinic", {}).get("name", "Bilinmiyor"),
                reason=result.get("primary_clinic", {}).get("reason", "Analiz edilemedi"),
                confidence=result.get("primary_clinic", {}).get("confidence", 0.0)
            ),
            secondary_clinics=[
                ClinicRecommendation(
                    name=clinic.get("name", "Bilinmiyor"),
                    reason=clinic.get("reason", "Analiz edilemedi"),
                    confidence=clinic.get("confidence", 0.0)
                )
                for clinic in result.get("secondary_clinics", [])
            ]
        )
        
        logger.info(f"Analiz tamamlandı: {response.primary_clinic.name}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analiz hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Analiz hatası: {str(e)}")

@app.get("/health")
async def health_check():
    """Detaylı health check"""
    return {
        "status": "healthy",
        "analyzer_ready": analyzer is not None,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
