#!/usr/bin/env python3
"""
TanıAI Sesli Erişim Modülü
Twilio entegrasyonu ile sesli semptom girişi
"""

from fastapi import APIRouter, Request, Form
from twilio.twiml import VoiceResponse
from twilio.rest import Client
import os
from typing import Dict, Any
import json

router = APIRouter()

# Twilio konfigürasyonu
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'your_account_sid')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'your_auth_token')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+1234567890')

# Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class VoiceSymptomProcessor:
    """Sesli semptom işleme sınıfı"""
    
    def __init__(self):
        self.symptom_keywords = {
            'yorgunluk': ['yorgun', 'yorgunum', 'halsiz', 'halsizim', 'bitkin', 'bitkinim'],
            'bulanti': ['bulantı', 'bulantım', 'kusacak', 'mide bulanıyor'],
            'ates': ['ateş', 'ateşim', 'fever', 'sıcaklık'],
            'bas_agrisi': ['baş ağrısı', 'başım ağrıyor', 'kafam ağrıyor'],
            'karin_agrisi': ['karın ağrısı', 'karınım ağrıyor', 'mide ağrısı'],
            'sari': ['sarılık', 'sarı', 'sarı renk', 'cilt sararması'],
            'adet_gecikmesi': ['adet gecikmesi', 'regl gecikmesi', 'adet olmadım'],
            'meme_hassasiyeti': ['meme ağrısı', 'göğüs ağrısı', 'meme hassasiyeti'],
            'sac_dokulmesi': ['saç dökülmesi', 'saçlarım dökülüyor', 'kellik'],
            'kilo_degisimi': ['kilo aldım', 'kilo verdim', 'kilo değişimi']
        }
    
    def process_voice_input(self, transcript: str) -> Dict[str, int]:
        """Sesli girişi semptomlara çevirir"""
        symptoms = {}
        transcript_lower = transcript.lower()
        
        for symptom, keywords in self.symptom_keywords.items():
            severity = 0
            for keyword in keywords:
                if keyword in transcript_lower:
                    # Şiddet belirleme
                    if any(word in transcript_lower for word in ['çok', 'çok fazla', 'aşırı']):
                        severity = 3
                    elif any(word in transcript_lower for word in ['orta', 'biraz']):
                        severity = 2
                    else:
                        severity = 1
                    break
            
            if severity > 0:
                symptoms[symptom] = severity
        
        return symptoms

voice_processor = VoiceSymptomProcessor()

@router.post("/voice/webhook")
async def voice_webhook(request: Request):
    """Twilio sesli arama webhook'u"""
    form_data = await request.form()
    
    # Twilio'dan gelen veriler
    call_sid = form_data.get('CallSid')
    from_number = form_data.get('From')
    to_number = form_data.get('To')
    
    # Sesli yanıt oluştur
    response = VoiceResponse()
    
    # Hoş geldin mesajı
    response.say(
        "Merhaba! TanıAI sesli asistanına hoş geldiniz. "
        "Lütfen yaşadığınız semptomları anlatın. "
        "Örneğin: 'Çok yorgunum, başım ağrıyor ve mide bulantım var' diyebilirsiniz.",
        language='tr-TR'
    )
    
    # Kullanıcıdan semptom dinle
    response.record(
        max_length=30,
        timeout=10,
        action='/api/voice/process-symptoms',
        method='POST'
    )
    
    return str(response)

@router.post("/voice/process-symptoms")
async def process_symptoms(request: Request):
    """Kaydedilen sesi işler ve teşhis yapar"""
    form_data = await request.form()
    recording_url = form_data.get('RecordingUrl')
    call_sid = form_data.get('CallSid')
    
    # Burada gerçek uygulamada Twilio'dan ses dosyasını indirip
    # speech-to-text servisi ile metne çevirmeniz gerekir
    # Şimdilik demo için sabit metin kullanıyoruz
    
    # Demo semptom metni
    demo_transcript = "Çok yorgunum, başım ağrıyor ve mide bulantım var"
    
    # Semptomları işle
    symptoms = voice_processor.process_voice_input(demo_transcript)
    
    # Teşhis yap (API'ye istek gönder)
    diagnosis_result = await make_diagnosis_request(symptoms)
    
    # Sonucu sesli olarak söyle
    response = VoiceResponse()
    
    if diagnosis_result:
        # Teşhis sonucunu sesli olarak oku
        result_text = format_diagnosis_for_voice(diagnosis_result)
        response.say(result_text, language='tr-TR')
    else:
        response.say(
            "Üzgünüm, semptomlarınızı analiz ederken bir hata oluştu. "
            "Lütfen daha sonra tekrar deneyin.",
            language='tr-TR'
        )
    
    # Arama sonlandır
    response.hangup()
    
    return str(response)

async def make_diagnosis_request(symptoms: Dict[str, int]) -> Dict[str, Any]:
    """Teşhis API'sine istek gönderir"""
    try:
        import requests
        
        patient_data = {
            "patient_name": "Sesli Hasta",
            "age": 35,
            "gender": "Belirtilmedi",
            "symptoms": symptoms
        }
        
        # Local API'ye istek gönder
        api_response = requests.post(
            "http://localhost:8000/api/diagnose",
            headers={"Content-Type": "application/json"},
            json=patient_data,
            timeout=10
        )
        
        if api_response.status_code == 200:
            return api_response.json()
        else:
            return None
            
    except Exception as e:
        print(f"Sesli teşhis hatası: {e}")
        return None

def format_diagnosis_for_voice(diagnosis: Dict[str, Any]) -> str:
    """Teşhis sonucunu sesli okuma için formatlar"""
    result_text = "Teşhis sonuçlarınız: "
    
    # Risk seviyesi
    risk_level = diagnosis.get('overall_risk_level', 'Düşük')
    result_text += f"Genel risk seviyeniz {risk_level}. "
    
    # Eksik nutrientler
    priority_nutrients = diagnosis.get('priority_nutrients', [])
    if priority_nutrients:
        result_text += f"Tespit edilen sorunlar: {', '.join(priority_nutrients[:3])}. "
    else:
        result_text += "Belirgin bir sorun tespit edilmedi. "
    
    # Öneriler
    result_text += "Doktor kontrolü önerilir. "
    
    return result_text

@router.get("/voice/status")
async def voice_status():
    """Sesli erişim durumu"""
    return {
        "status": "active",
        "twilio_configured": bool(TWILIO_ACCOUNT_SID != 'your_account_sid'),
        "phone_number": TWILIO_PHONE_NUMBER,
        "features": [
            "Sesli semptom girişi",
            "Otomatik teşhis",
            "Sesli sonuç okuma"
        ]
    }

@router.post("/voice/test")
async def test_voice_processing(text: str = Form(...)):
    """Sesli işleme test endpoint'i"""
    symptoms = voice_processor.process_voice_input(text)
    
    return {
        "input_text": text,
        "detected_symptoms": symptoms,
        "symptom_count": len(symptoms)
    }
