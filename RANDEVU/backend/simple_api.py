#!/usr/bin/env python3
"""
Basit TanıAI Backend API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import json
from datetime import datetime

app = FastAPI(title="TanıAI Simple API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    context: str = "medical_assistant"

class TriageRequest(BaseModel):
    text: str

class ClinicRequest(BaseModel):
    symptoms: str

@app.get("/")
async def root():
    return {
        "message": "TanıAI Backend API",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "taniai-backend"
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Basit chat yanıtı"""
    message = request.message.lower()
    
    if "randevu" in message:
        response = "Randevu almak için size yardımcı olabilirim! Hangi bölüm için randevu almak istiyorsunuz?"
    elif "semptom" in message or "ağrı" in message:
        response = "Semptomlarınız hakkında konuşabiliriz. Hangi semptomları yaşıyorsunuz?"
    elif "eczane" in message:
        response = "Yakınızdaki eczaneleri bulmak için eczane bulma özelliğini kullanabilirsiniz."
    elif "merhaba" in message or "selam" in message:
        response = "Merhaba! Ben TanıAI Asistanıyım. Size nasıl yardımcı olabilirim?"
    else:
        response = "Anlıyorum. Size daha iyi yardımcı olabilmem için daha spesifik bir soru sorabilir misiniz?"
    
    return {
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "context": request.context
    }

@app.post("/triage")
async def triage(request: TriageRequest):
    """Basit triyaj"""
    text = request.text.lower()
    
    urgency = "normal"
    recommended_clinic = "Genel Pratisyen"
    analysis = "Genel sağlık kontrolü önerilir."
    recommendations = ["Bol su için", "Dinlenin", "Doktor muayenesi yaptırın"]
    
    if any(word in text for word in ["göğüs", "kalp", "nefes", "acil", "kritik"]):
        urgency = "high"
        recommended_clinic = "Acil Servis"
        analysis = "Acil müdahale gerektirebilecek semptomlar tespit edildi."
        recommendations = ["En kısa sürede acil servise başvurun", "112'yi arayın (gerekirse)"]
    elif any(word in text for word in ["ağrı", "ateş", "bulantı", "öksürük"]):
        urgency = "medium"
        recommended_clinic = "İç Hastalıkları"
        analysis = "Dikkat gerektiren semptomlar tespit edildi."
        recommendations = ["24-48 saat içinde doktora başvurun", "Semptomları takip edin"]
    
    return {
        "urgency": urgency,
        "recommended_clinic": recommended_clinic,
        "analysis": analysis,
        "recommendations": recommendations,
        "confidence": 0.8,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/recommend-clinic")
async def recommend_clinic(request: ClinicRequest):
    """Klinik önerisi"""
    symptoms = request.symptoms.lower()
    
    if any(word in symptoms for word in ["göğüs", "kalp", "nefes"]):
        recommended_clinic = "Kardiyoloji"
        urgency = "high"
        reasoning = "Kalp ve solunum sistemi semptomları için kardiyoloji uygun"
    elif any(word in symptoms for word in ["baş", "nöroloji", "sinir"]):
        recommended_clinic = "Nöroloji"
        urgency = "high"
        reasoning = "Sinir sistemi semptomları için nöroloji uygun"
    elif any(word in symptoms for word in ["kemik", "eklem", "kas"]):
        recommended_clinic = "Ortopedi"
        urgency = "medium"
        reasoning = "Kas-iskelet sistemi semptomları için ortopedi uygun"
    else:
        recommended_clinic = "Genel Pratisyen"
        urgency = "low"
        reasoning = "Genel sağlık kontrolü için uygun"
    
    return {
        "recommended_clinic": recommended_clinic,
        "urgency": urgency,
        "reasoning": reasoning,
        "alternatives": ["İç Hastalıkları", "Aile Hekimi"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/clinics")
async def get_clinics():
    """Klinik listesi"""
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
        },
        {
            "id": "emergency",
            "name": "Acil Servis",
            "description": "Acil müdahale gerektiren durumlar",
            "specialties": ["Acil Tıp"]
        }
    ]
    
    return {
        "clinics": clinics,
        "count": len(clinics),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
