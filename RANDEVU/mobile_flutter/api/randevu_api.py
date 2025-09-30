#!/usr/bin/env python3
"""
TanıAI Randevu API
Sesli randevu sistemi için özel API
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os
import sys

# Whisper ASR modülünü import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from whisper_asr import get_asr_processor

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI uygulaması oluştur
app = FastAPI(
    title="TanıAI Randevu API",
    description="Sesli randevu sistemi",
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

@app.get("/")
async def root():
    """Ana sayfa"""
    return {"message": "TanıAI Randevu API", "status": "active"}

@app.post("/whisper/flutter-randevu")
async def flutter_randevu(audio_file: UploadFile = File(...)):
    """
    Flutter'dan gelen ses dosyasını işle ve klinik öner
    """
    try:
        logger.info(f"Flutter randevu isteği: {audio_file.filename}")
        
        # Dosya validasyonu
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="Dosya adı bulunamadı")
        
        # Dosya boyutu kontrolü (10MB limit)
        content = await audio_file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="Dosya boyutu çok büyük (Max: 10MB)")
        
        logger.info(f"Ses dosyası yüklendi: {audio_file.filename} ({len(content)} bytes)")
        
        # ASR processor'ı al
        asr_processor = get_asr_processor()
        
        # Transkripsiyon yap
        transcription_result = asr_processor.transcribe_from_bytes(content)
        
        if not transcription_result["success"]:
            raise HTTPException(
                status_code=500, 
                detail=f"Transkripsiyon hatası: {transcription_result['error']}"
            )
        
        transcript = transcription_result["transcript"]
        
        if not transcript.strip():
            return {
                "success": False,
                "error": "Ses dosyasından metin çıkarılamadı",
                "transcript": ""
            }
        
        logger.info(f"Transkripsiyon başarılı: {len(transcript)} karakter")
        
        # Klinik önerileri
        suggestions = _get_clinic_suggestions(transcript)
        
        return {
            "success": True,
            "transcript": transcript,
            "suggestions": suggestions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Flutter randevu hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Ses işleme hatası: {str(e)}")

def _get_clinic_suggestions(transcript: str):
    """Gelişmiş klinik önerileri döndürür"""
    transcript_lower = transcript.lower()
    
    # Detaylı anahtar kelime analizi
    symptoms = {
        'neurological': ['baş', 'kafa', 'migren', 'başağrısı', 'baş ağrısı', 'başım', 'kafam', 'baş dönmesi', 'dönüyor'],
        'cardiac': ['göğüs', 'kalp', 'nefes', 'çarpıntı', 'kalbim', 'göğsüm', 'nefes darlığı', 'çarpıntım'],
        'gastrointestinal': ['karın', 'mide', 'bulantı', 'kusma', 'karın ağrısı', 'mide ağrısı', 'bulantım', 'kusuyorum'],
        'respiratory': ['öksürük', 'boğaz', 'burun', 'nefes', 'solunum', 'öksürüyorum', 'boğazım'],
        'dermatological': ['cilt', 'deri', 'kaşıntı', 'döküntü', 'kızarıklık', 'cildim', 'kaşınıyor'],
        'musculoskeletal': ['eklem', 'kas', 'sırt', 'bel', 'boyun', 'ağrı', 'sırtım', 'belim', 'boynum'],
        'psychological': ['stres', 'kaygı', 'endişe', 'depresyon', 'uyku', 'stresli', 'kaygılı']
    }
    
    # Semptom skorları
    scores = {}
    for category, keywords in symptoms.items():
        score = sum(1 for keyword in keywords if keyword in transcript_lower)
        if score > 0:
            scores[category] = score
    
    # En yüksek skorlu kategoriyi bul
    if scores:
        primary_category = max(scores, key=scores.get)
        
        if primary_category == 'neurological':
            return [
                {
                    "clinic": "Nöroloji",
                    "reason": "Baş ağrısı ve nörolojik şikayetler için",
                    "confidence": 0.85
                },
                {
                    "clinic": "Aile Hekimliği", 
                    "reason": "Genel değerlendirme için",
                    "confidence": 0.7
                }
            ]
        elif primary_category == 'cardiac':
            return [
                {
                    "clinic": "Kardiyoloji",
                    "reason": "Kalp ve göğüs şikayetleri için",
                    "confidence": 0.85
                },
                {
                    "clinic": "Göğüs Hastalıkları",
                    "reason": "Nefes darlığı değerlendirmesi için",
                    "confidence": 0.75
                }
            ]
        elif primary_category == 'gastrointestinal':
            return [
                {
                    "clinic": "Gastroenteroloji",
                    "reason": "Mide ve karın şikayetleri için",
                    "confidence": 0.85
                },
                {
                    "clinic": "Genel Cerrahi",
                    "reason": "Karın ağrısı değerlendirmesi için",
                    "confidence": 0.7
                }
            ]
        elif primary_category == 'respiratory':
            return [
                {
                    "clinic": "Göğüs Hastalıkları",
                    "reason": "Solunum yolu şikayetleri için",
                    "confidence": 0.85
                },
                {
                    "clinic": "Kulak Burun Boğaz",
                    "reason": "Boğaz ve burun şikayetleri için",
                    "confidence": 0.75
                }
            ]
        elif primary_category == 'dermatological':
            return [
                {
                    "clinic": "Dermatoloji",
                    "reason": "Cilt ve deri şikayetleri için",
                    "confidence": 0.85
                },
                {
                    "clinic": "Aile Hekimliği",
                    "reason": "Genel değerlendirme için",
                    "confidence": 0.7
                }
            ]
        elif primary_category == 'musculoskeletal':
            return [
                {
                    "clinic": "Ortopedi",
                    "reason": "Kas ve eklem şikayetleri için",
                    "confidence": 0.85
                },
                {
                    "clinic": "Fizik Tedavi",
                    "reason": "Kas ve eklem rehabilitasyonu için",
                    "confidence": 0.75
                }
            ]
        elif primary_category == 'psychological':
            return [
                {
                    "clinic": "Psikiyatri",
                    "reason": "Ruh sağlığı değerlendirmesi için",
                    "confidence": 0.85
                },
                {
                    "clinic": "Aile Hekimliği",
                    "reason": "Genel değerlendirme için",
                    "confidence": 0.7
                }
            ]
    
    # Varsayılan öneriler
    return [
        {
            "clinic": "Aile Hekimliği",
            "reason": "Genel değerlendirme için",
            "confidence": 0.7
        },
        {
            "clinic": "İç Hastalıkları",
            "reason": "Genel muayene için",
            "confidence": 0.6
        }
    ]

if __name__ == "__main__":
    print("🚀 TanıAI Randevu API Başlatılıyor...")
    print("📱 Ana sayfa: http://localhost:8002")
    print("🔗 API: http://localhost:8002/whisper/")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
