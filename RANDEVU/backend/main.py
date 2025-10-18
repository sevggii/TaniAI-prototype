#!/usr/bin/env python3
"""
TanıAI Backend API
LLM entegrasyonu ve klinik triyaj servisi
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import json
import logging
from datetime import datetime

# LLM servislerini import et
try:
    from llm_service import LLMService
    from clinic_recommender_service import ClinicRecommenderService  # Yeni eğitilmiş model
except ImportError:
    # Fallback için basit servisler
    class LLMService:
        @staticmethod
        def get_chat_response(message: str) -> str:
            return "Merhaba! Ben TanıAI Asistanıyım. Size nasıl yardımcı olabilirim?"
    
    class ClinicRecommenderService:
        @staticmethod
        def recommend_clinic(complaint: str) -> Dict[str, Any]:
            return {
                "success": True,
                "recommended_clinic": "Aile Hekimliği",
                "confidence": 0.8,
                "reasoning": "Fallback önerisi",
                "urgency": "normal",
                "alternatives": ["İç Hastalıkları"]
            }

# FastAPI uygulaması
app = FastAPI(
    title="TanıAI Backend API",
    description="LLM entegrasyonu ve klinik triyaj servisi",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domainler kullanın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request modelleri
class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = "medical_assistant"

class TriageRequest(BaseModel):
    text: str

class ClinicRecommendationRequest(BaseModel):
    symptoms: str

# Response modelleri
class ChatResponse(BaseModel):
    response: str
    timestamp: str
    context: str

class TriageResponse(BaseModel):
    urgency: str
    recommended_clinic: str
    analysis: str
    recommendations: List[str]
    confidence: float
    timestamp: str

class ClinicRecommendationResponse(BaseModel):
    recommended_clinic: str
    urgency: str
    reasoning: str
    alternatives: List[str]
    timestamp: str

# Servisleri başlat
llm_service = LLMService()
clinic_recommender = ClinicRecommenderService()  # Eğitilmiş model

@app.get("/")
async def root():
    """API durumu"""
    return {
        "message": "TanıAI Backend API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "llm": "available",
            "triage": "available",
            "clinic": "available"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat yanıtı al"""
    try:
        response = llm_service.get_chat_response(request.message)
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat(),
            context=request.context
        )
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat servisi hatası")

@app.post("/triage", response_model=TriageResponse)
async def triage(request: TriageRequest):
    """Semptom triyajı"""
    try:
        result = triage_service.analyze_symptoms(request.text)
        
        return TriageResponse(
            urgency=result.get("urgency", "normal"),
            recommended_clinic=result.get("recommended_clinic", "Genel Pratisyen"),
            analysis=result.get("analysis", "Genel sağlık kontrolü önerilir."),
            recommendations=result.get("recommendations", ["Bol su için", "Dinlenin"]),
            confidence=result.get("confidence", 0.7),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logging.error(f"Triage error: {e}")
        raise HTTPException(status_code=500, detail="Triyaj servisi hatası")

@app.post("/recommend-clinic", response_model=ClinicRecommendationResponse)
async def recommend_clinic(request: ClinicRecommendationRequest):
    """Klinik önerisi al - EĞİTİLMİŞ MODEL"""
    try:
        # Eğitilmiş modeli kullan
        result = clinic_recommender.recommend_clinic(request.symptoms)
        
        if result.get("success", False):
            return ClinicRecommendationResponse(
                recommended_clinic=result.get("recommended_clinic", "Aile Hekimliği"),
                urgency=result.get("urgency", "normal"),
                reasoning=result.get("reasoning", "Eğitilmiş model önerisi"),
                alternatives=result.get("alternatives", ["İç Hastalıkları", "Aile Hekimi"]),
                timestamp=datetime.now().isoformat()
            )
        else:
            # Fallback
            return ClinicRecommendationResponse(
                recommended_clinic="Aile Hekimliği",
                urgency="normal",
                reasoning="Fallback önerisi",
                alternatives=["İç Hastalıkları"],
                timestamp=datetime.now().isoformat()
            )
    except Exception as e:
        logging.error(f"Clinic recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Klinik önerisi servisi hatası")

@app.get("/clinics")
async def get_clinics():
    """Mevcut klinikleri listele"""
    try:
        # Klinik verilerini yükle
        clinics_file = "clinics/clinics.json"
        if os.path.exists(clinics_file):
            with open(clinics_file, 'r', encoding='utf-8') as f:
                clinics = json.load(f)
        else:
            # Varsayılan klinikler
            clinics = [
                {
                    "id": "general",
                    "name": "Genel Pratisyen",
                    "description": "Genel sağlık kontrolü ve rutin muayeneler",
                    "specialties": ["Genel Tıp", "Aile Hekimliği"]
                },
                {
                    "id": "cardiology",
                    "name": "Kardiyoloji",
                    "description": "Kalp ve damar hastalıkları",
                    "specialties": ["Kardiyoloji", "Kalp Cerrahisi"]
                },
                {
                    "id": "neurology",
                    "name": "Nöroloji",
                    "description": "Sinir sistemi hastalıkları",
                    "specialties": ["Nöroloji", "Beyin Cerrahisi"]
                }
            ]
        
        return {
            "clinics": clinics,
            "count": len(clinics),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Get clinics error: {e}")
        raise HTTPException(status_code=500, detail="Klinik listesi alınamadı")

if __name__ == "__main__":
    import uvicorn
    
    # Logging ayarla
    logging.basicConfig(level=logging.INFO)
    
    # Sunucuyu başlat
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
