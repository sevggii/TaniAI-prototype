#!/usr/bin/env python3
"""
Basit Test API - Flutter için
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="TanıAI Test API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "TanıAI Test API", "status": "active"}

@app.post("/recommend-clinic")
async def recommend_clinic(data: dict):
    """Basit klinik önerisi"""
    symptoms = data.get("symptoms", "")
    
    # Basit kural tabanlı öneriler
    if "baş" in symptoms.lower() or "kafa" in symptoms.lower():
        return {
            "recommended_clinic": "Nöroloji",
            "confidence": 0.95,
            "reasoning": "Baş ağrısı şikayetleri için Nöroloji bölümüne yönlendiriliyorsunuz.",
            "alternatives": ["Aile Hekimliği", "İç Hastalıkları (Dahiliye)"],
            "timestamp": "2024-01-01T12:00:00"
        }
    elif "kalp" in symptoms.lower() or "göğüs" in symptoms.lower():
        return {
            "recommended_clinic": "Kardiyoloji",
            "confidence": 0.95,
            "reasoning": "Kalp ve göğüs şikayetleri için Kardiyoloji bölümüne yönlendiriliyorsunuz.",
            "alternatives": ["Göğüs Hastalıkları", "Aile Hekimliği"],
            "timestamp": "2024-01-01T12:00:00"
        }
    elif "karın" in symptoms.lower() or "mide" in symptoms.lower():
        return {
            "recommended_clinic": "Gastroenteroloji",
            "confidence": 0.90,
            "reasoning": "Mide ve karın şikayetleri için Gastroenteroloji bölümüne yönlendiriliyorsunuz.",
            "alternatives": ["Genel Cerrahi", "Aile Hekimliği"],
            "timestamp": "2024-01-01T12:00:00"
        }
    else:
        return {
            "recommended_clinic": "Aile Hekimliği",
            "confidence": 0.70,
            "reasoning": "Genel değerlendirme için Aile Hekimliği bölümüne yönlendiriliyorsunuz.",
            "alternatives": ["İç Hastalıkları (Dahiliye)"],
            "timestamp": "2024-01-01T12:00:00"
        }

@app.post("/chat")
async def chat(data: dict):
    """Chat endpoint - Flutter için"""
    message = data.get("message", "")
    
    # Basit kural tabanlı yanıtlar
    if "baş" in message.lower() or "kafa" in message.lower():
        return {
            "response": "Baş ağrınız için **Nöroloji** bölümüne randevu almanızı öneriyorum. Baş ağrısı ciddi olabilir, mutlaka doktora görünün."
        }
    elif "kalp" in message.lower() or "göğüs" in message.lower():
        return {
            "response": "Kalp ve göğüs şikayetleriniz için **Kardiyoloji** bölümüne randevu almanızı öneriyorum. Bu tür şikayetler acil olabilir."
        }
    elif "karın" in message.lower() or "mide" in message.lower():
        return {
            "response": "Mide ve karın şikayetleriniz için **Gastroenteroloji** bölümüne randevu almanızı öneriyorum."
        }
    elif "randevu" in message.lower():
        return {
            "response": "Hangi şikayetleriniz var? Size uygun kliniği önerebilirim. Örneğin: 'Başım ağrıyor', 'Kalp çarpıntım var' gibi."
        }
    else:
        return {
            "response": "Şikayetlerinizi daha detaylı anlatabilir misiniz? Size uygun kliniği önerebilirim."
        }

@app.post("/triage")
async def triage(data: dict):
    """Triyaj endpoint"""
    text = data.get("text", "")
    
    # Basit triyaj
    if "baş" in text.lower():
        return {
            "clinic": "Nöroloji",
            "candidates": [
                {"clinic": "Nöroloji", "reason": "Baş ağrısı", "confidence": 0.95},
                {"clinic": "Aile Hekimliği", "reason": "Genel değerlendirme", "confidence": 0.70}
            ],
            "redFlag": False,
            "explanations": ["Baş ağrısı şikayetleri analiz edildi"],
            "canonicalized": True
        }
    else:
        return {
            "clinic": "Aile Hekimliği",
            "candidates": [
                {"clinic": "Aile Hekimliği", "reason": "Genel değerlendirme", "confidence": 0.80}
            ],
            "redFlag": False,
            "explanations": ["Genel şikayetler için Aile Hekimliği"],
            "canonicalized": True
        }

if __name__ == "__main__":
    print("🚀 Basit Test API başlatılıyor...")
    print("📱 Flutter bağlantısı: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
