#!/usr/bin/env python3
"""
TanıAI Whisper ASR Bağımsız Sunucu
Sesli semptom girişi için ayrı FastAPI uygulaması
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import logging
import os

# Whisper ASR modüllerini import et
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from whisper_asr import get_asr_processor
from whisper_asr.symptom_analyzer import get_symptom_analyzer
try:
    from ml_clinic.triage_model import get_triage_model
    from ml_clinic.integrated_triage import get_integrated_triage
except Exception:
    # Modül yolu düzeltmesi (bağımsız çalıştırma)
    import sys as _sys
    _sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ml_clinic.triage_model import get_triage_model
    from ml_clinic.integrated_triage import get_integrated_triage

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI uygulaması oluştur
app = FastAPI(
    title="TanıAI Whisper ASR",
    description="Sesli semptom girişi ve analizi sistemi",
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

# Static dosyaları serve et
app.mount("/static", StaticFiles(directory="whisper_asr"), name="static")

@app.get("/")
async def root():
    """Ana sayfa"""
    return FileResponse("whisper_asr/index.html")

@app.post("/whisper/upload-audio")
async def upload_audio_file(audio_file: UploadFile = File(...)):
    """
    Ses dosyası yükleme ve işleme endpoint'i
    """
    try:
        # Dosya validasyonu
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="Dosya adı bulunamadı")
        
        # Dosya boyutu kontrolü (10MB limit)
        content = await audio_file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="Dosya boyutu çok büyük (Max: 10MB)")
        
        # Desteklenen formatlar
        allowed_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.webm']
        file_extension = os.path.splitext(audio_file.filename.lower())[1]
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Desteklenmeyen dosya formatı. Desteklenen: {', '.join(allowed_extensions)}"
            )
        
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
                "transcript": "",
                "file_name": audio_file.filename,
                "file_size": len(content)
            }
        
        # Semptom analizi yap
        symptom_analyzer = get_symptom_analyzer()
        analysis_result = symptom_analyzer.analyze_transcript(transcript)
        
        logger.info(f"Transkripsiyon başarılı: {len(transcript)} karakter, {analysis_result['symptom_count']} semptom")
        
        return {
            "success": True,
            "transcript": transcript,
            "detected_symptoms": analysis_result["detected_symptoms"],
            "symptom_count": analysis_result["symptom_count"],
            "file_name": audio_file.filename,
            "file_size": len(content),
            "language": transcription_result.get("language", "tr"),
            "confidence": transcription_result.get("language_probability", 0.0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ses dosyası işleme hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Ses işleme hatası: {str(e)}")

@app.post("/whisper/clinic-from-audio")
async def clinic_from_audio(audio_file: UploadFile = File(...)):
    """Ses dosyasından transkript çıkarıp ML triage ile klinik önerir"""
    content = await audio_file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Dosya boyutu çok büyük (Max: 10MB)")
    asr_processor = get_asr_processor()
    res = asr_processor.transcribe_from_bytes(content)
    if not res.get("success"):
        raise HTTPException(status_code=500, detail=f"Transkripsiyon hatası: {res.get('error')}")
    transcript = res.get("transcript", "").strip()
    if not transcript:
        return {"success": False, "error": "Boş transkript"}
    triage = get_triage_model()
    tri = triage.suggest(transcript, top_k=3)
    return {"success": True, "transcript": transcript, "triage": tri}

@app.post("/whisper/clinic-from-text")
async def clinic_from_text(text: str = File(...)):
    """Verilen metinden ML triage ile klinik önerir"""
    t = (text or "").strip()
    if not t:
        raise HTTPException(status_code=400, detail="Metin boş olamaz")
    triage = get_triage_model()
    tri = triage.suggest(t, top_k=3)
    return {"success": True, "input_text": t, "triage": tri}

@app.post("/whisper/clinic-from-audio-llm")
async def clinic_from_audio_llm(audio_file: UploadFile = File(...)):
    """Ses dosyasından transkript çıkarıp entegre ML+LLM triage ile klinik önerir"""
    try:
        content = await audio_file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Dosya boyutu çok büyük (Max: 10MB)")

        asr_processor = get_asr_processor()
        transcription_result = asr_processor.transcribe_from_bytes(content)
        if not transcription_result.get("success"):
            raise HTTPException(status_code=500, detail=f"Transkripsiyon hatası: {transcription_result.get('error')}")

        transcript = transcription_result.get("transcript", "").strip()
        if not transcript:
            return {"success": False, "error": "Boş transkript"}

        # Entegre triage sistemi kullan
        integrated_triage = get_integrated_triage()
        result = integrated_triage.suggest(transcript, top_k=3)

        return {
            "success": True,
            "transcript": transcript,
            "triage": result,
            "system_status": integrated_triage.get_system_status()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Entegre klinik öneri (audio) hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Entegre klinik öneri hatası: {str(e)}")

@app.post("/whisper/clinic-from-text-llm")
async def clinic_from_text_llm(text: str = File(...)):
    """Verilen metinden entegre ML+LLM triage ile klinik önerir"""
    try:
        t = (text or "").strip()
        if not t:
            raise HTTPException(status_code=400, detail="Metin boş olamaz")
        
        # Entegre triage sistemi kullan
        integrated_triage = get_integrated_triage()
        result = integrated_triage.suggest(t, top_k=3)
        
        return {
            "success": True, 
            "triage": result, 
            "input_text": t,
            "system_status": integrated_triage.get_system_status()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Entegre klinik öneri (text) hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Entegre klinik öneri hatası: {str(e)}")

@app.get("/whisper/system-status")
async def get_system_status():
    """Entegre sistem durumunu döndürür"""
    try:
        integrated_triage = get_integrated_triage()
        status = integrated_triage.get_system_status()
        
        # ASR durumu da ekle
        asr_processor = get_asr_processor()
        status["asr"] = {
            "model_name": asr_processor.model_name,
            "model_loaded": asr_processor.model is not None
        }
        
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        logger.error(f"Sistem durumu hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Sistem durumu hatası: {str(e)}")

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
            "supported_languages": ["tr", "en", "auto"],
            "features": [
                "Ses dosyası transkripsiyonu",
                "Türkçe semptom analizi",
                "Otomatik semptom tespiti",
                "Şiddet seviyesi belirleme"
            ]
        }
        
    except Exception as e:
        logger.error(f"Durum kontrolü hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Durum kontrolü hatası: {str(e)}")

@app.get("/whisper/symptoms")
async def get_supported_symptoms():
    """Desteklenen semptomları döndürür"""
    try:
        symptom_analyzer = get_symptom_analyzer()
        
        symptoms = list(symptom_analyzer.symptom_keywords.keys())
        
        return {
            "success": True,
            "symptoms": symptoms,
            "total_count": len(symptoms),
            "categories": {
                "fiziksel": [s for s in symptoms if any(x in s for x in ['agrisi', 'ates', 'bulanti', 'sari'])],
                "psikolojik": [s for s in symptoms if any(x in s for x in ['depresyon', 'konsantrasyon', 'uyku'])],
                "hormonal": [s for s in symptoms if any(x in s for x in ['adet', 'meme', 'sac', 'kilo'])]
            }
        }
        
    except Exception as e:
        logger.error(f"Semptom listesi hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Semptom listesi hatası: {str(e)}")

if __name__ == "__main__":
    print("🚀 TanıAI Whisper ASR Sunucusu Başlatılıyor...")
    print("📱 Ana sayfa: http://localhost:8001")
    print("🔗 API: http://localhost:8001/whisper/")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    )
