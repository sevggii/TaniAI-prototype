#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Orchestrator
OpenAI uyumlu API endpoint'i
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import sys
import os
from datetime import datetime

# Kendi modüllerimizi import et
from llm_client import LLMClient
from classify_core import predict_clinic, classifier

# Logging ayarla
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# FastAPI app oluştur
app = FastAPI(
    title="TanıAI Klinik Öneri API",
    description="Hasta şikayetlerini analiz ederek uygun kliniği öneren AI sistemi",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM Client
llm_client = LLMClient()

# Pydantic modelleri
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "clinic-recommender"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.1
    max_tokens: Optional[int] = 200

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict

class ClinicRecommendation(BaseModel):
    recommended_clinic: str
    confidence: float
    reasoning: str
    alternatives: List[str]
    timestamp: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında modeli yükle"""
    logger.info("TanıAI Klinik Öneri API başlatılıyor...")
    
    # Modeli yükle
    if not classifier.load_model():
        logger.error("Model yüklenemedi! Uygulama başlatılamıyor.")
        sys.exit(1)
    
    # LLM bağlantısını test et
    if not llm_client.test_connection():
        logger.warning("LiteLLM bağlantısı kurulamadı! Normalizasyon çalışmayabilir.")
    
    logger.info("API başarıyla başlatıldı!")

@app.get("/")
async def root():
    """Ana endpoint"""
    return {
        "message": "TanıAI Klinik Öneri API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    model_loaded = classifier.model is not None
    llm_connected = llm_client.test_connection()
    
    return {
        "status": "healthy" if model_loaded else "unhealthy",
        "model_loaded": model_loaded,
        "llm_connected": llm_connected,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI uyumlu chat completions endpoint
    """
    try:
        # Son kullanıcı mesajını al
        user_message = None
        for message in reversed(request.messages):
            if message.role == "user":
                user_message = message.content
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Kullanıcı mesajı bulunamadı")
        
        logger.info(f"Gelen şikayet: {user_message}")
        
        # 1. LLM ile metni normalize et
        normalized_text = llm_client.normalize_text(user_message)
        logger.info(f"Normalize edilmiş: {normalized_text}")
        
        # 2. SVM modeli ile klinik tahmini yap
        try:
            clinic = predict_clinic(normalized_text)
        except Exception as e:
            logger.error(f"Klinik tahmin hatası: {e}")
            raise HTTPException(status_code=500, detail=f"Klinik tahmini yapılamadı: {str(e)}")
        
        # 3. Yanıt oluştur
        reasoning = f"Şikayetleriniz analiz edildi ve {clinic} bölümüne yönlendiriliyorsunuz."
        
        # Alternatif klinikler (basit örnek)
        alternatives = ["Aile Hekimliği", "İç Hastalıkları (Dahiliye)"]
        if clinic in alternatives:
            alternatives.remove(clinic)
        
        # OpenAI formatında yanıt
        response_content = f"""🏥 **Klinik Önerisi**

**Önerilen Klinik:** {clinic}
**Açıklama:** {reasoning}

**Alternatif Seçenekler:**
{chr(10).join([f"• {alt}" for alt in alternatives[:3]])}

**Not:** Bu öneri AI sistemi tarafından oluşturulmuştur. Kesin tanı için mutlaka doktor muayenesi gereklidir."""

        # OpenAI formatında response
        response = ChatCompletionResponse(
            id=f"chatcmpl-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            created=int(datetime.now().timestamp()),
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(user_message.split()) + len(response_content.split())
            }
        )
        
        logger.info(f"Yanıt oluşturuldu: {clinic}")
        
        return response
        
    except Exception as e:
        logger.error(f"API hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")

@app.post("/recommend-clinic", response_model=ClinicRecommendation)
async def recommend_clinic(request: dict):
    """
    Basit klinik önerisi endpoint'i
    """
    try:
        symptoms = request.get("symptoms", "")
        if not symptoms:
            raise HTTPException(status_code=400, detail="Şikayet metni gerekli")
        
        # Normalize et
        normalized_text = llm_client.normalize_text(symptoms)
        
        # Tahmin yap
        try:
            clinic = predict_clinic(normalized_text)
        except Exception as e:
            logger.error(f"Klinik tahmin hatası: {e}")
            raise HTTPException(status_code=500, detail=f"Klinik tahmini yapılamadı: {str(e)}")
        
        # Yanıt oluştur
        
        reasoning = f"Şikayetleriniz analiz edildi ve {clinic} bölümüne yönlendiriliyorsunuz."
        
        return ClinicRecommendation(
            recommended_clinic=clinic,
            confidence=0.95,  # Sabit güven değeri
            reasoning=reasoning,
            alternatives=["Aile Hekimliği", "İç Hastalıkları (Dahiliye)"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Recommendation hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clinics")
async def get_available_clinics():
    """Mevcut klinikleri listele"""
    clinics = classifier.get_available_clinics()
    return {
        "clinics": clinics,
        "count": len(clinics)
    }

@app.get("/model-info")
async def get_model_info():
    """Model bilgilerini getir"""
    return classifier.get_model_info()

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(
        app, 
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(os.getenv("PORT", "8001"))
    )
