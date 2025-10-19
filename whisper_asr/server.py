#!/usr/bin/env python3
"""
TanıAI Whisper ASR Global Servis
Tüm proje için ortak Speech-to-Text servisi
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os
import sys

# Whisper ASR modüllerini import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from whisper_asr import get_asr_processor

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI uygulaması oluştur
app = FastAPI(
    title="TanıAI Whisper ASR",
    description="Global Speech-to-Text servisi",
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
    return {"message": "TanıAI Whisper ASR Global API", "status": "active"}

@app.post("/whisper/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Ses dosyasını metne çevir (genel kullanım)
    """
    try:
        logger.info(f"Transkripsiyon isteği: {audio_file.filename}")
        
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
        logger.info(f"Transkripsiyon başarılı: {len(transcript)} karakter")
        
        return {
            "success": True,
            "transcript": transcript,
            "language": transcription_result.get("language", "tr"),
            "segments": transcription_result.get("segments", []),
            "language_probability": transcription_result.get("language_probability", 0.0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transkripsiyon hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Ses işleme hatası: {str(e)}")

@app.get("/whisper/status")
async def whisper_status():
    """Whisper ASR sistem durumu"""
    try:
        asr_processor = get_asr_processor()
        
        return {
            "status": "active",
            "model_name": asr_processor.model_name,
            "model_loaded": asr_processor.model is not None,
            "supported_formats": [".wav", ".mp3", ".m4a", ".flac", ".ogg"],
            "max_file_size_mb": 10,
            "supported_languages": ["tr", "en", "auto"]
        }
        
    except Exception as e:
        logger.error(f"Durum kontrolü hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Durum kontrolü hatası: {str(e)}")

if __name__ == "__main__":
    print("🚀 TanıAI Whisper ASR Global Servisi Başlatılıyor...")
    print("📱 Ana sayfa: http://localhost:8001")
    print("🔗 API: http://localhost:8001/whisper/")
    
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8001")),
        log_level=os.getenv("LOG_LEVEL", "info")
    )
