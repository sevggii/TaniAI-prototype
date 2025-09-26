#!/usr/bin/env python3
"""
Whisper ASR API Endpoints
TanıAI ana sayfası için ses dosyası işleme API'leri
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
import tempfile
import os

from .whisper_asr import get_asr_processor
from .symptom_analyzer import get_symptom_analyzer
# Yeni triage sistemi import et
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# test_system.py'den BetterTriageSystem'i import et
from test_system import BetterTriageSystem

logger = logging.getLogger(__name__)

# Router oluştur
router = APIRouter(prefix="/whisper", tags=["Whisper ASR"])

# Triage sistemi instance
triage_system = BetterTriageSystem()

@router.post("/flutter-randevu")
async def flutter_randevu(audio_file: UploadFile = File(...)):
    """
    Flutter'dan gelen ses dosyasını işle ve klinik öner
    """
    try:
        logger.info(f"Flutter randevu isteği: {audio_file.filename}")
        
        # Ses dosyasını geçici olarak kaydet
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Whisper ile transkripsiyon yap
            asr_processor = get_asr_processor()
            transcript = asr_processor.transcribe(temp_file_path)
            
            logger.info(f"Transkript: {transcript}")
            
            # Triage sistemi ile klinik öner
            suggestions = triage_system.suggest(transcript, top_k=3)
            
            # Sonuçları formatla
            result = {
                "success": True,
                "transcript": transcript,
                "suggestions": suggestions,
                "timestamp": os.path.getmtime(temp_file_path)
            }
            
            return JSONResponse(content=result)
            
        finally:
            # Geçici dosyayı sil
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Flutter randevu hatası: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "Ses işleme hatası"
            }
        )

@router.post("/upload-audio")
async def upload_audio_file(audio_file: UploadFile = File(...)):
    """
    Ses dosyası yükleme ve işleme endpoint'i
    
    Args:
        audio_file: Yüklenen ses dosyası
        
    Returns:
        JSONResponse: İşleme sonucu
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
        allowed_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
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
            return JSONResponse(content={
                "success": False,
                "error": "Ses dosyasından metin çıkarılamadı",
                "transcript": "",
                "file_name": audio_file.filename,
                "file_size": len(content)
            })
        
        # Semptom analizi yap
        symptom_analyzer = get_symptom_analyzer()
        analysis_result = symptom_analyzer.analyze_transcript(transcript)
        
        logger.info(f"Transkripsiyon başarılı: {len(transcript)} karakter, {analysis_result['symptom_count']} semptom")
        
        return JSONResponse(content={
            "success": True,
            "transcript": transcript,
            "detected_symptoms": analysis_result["detected_symptoms"],
            "symptom_count": analysis_result["symptom_count"],
            "file_name": audio_file.filename,
            "file_size": len(content),
            "language": transcription_result.get("language", "tr"),
            "confidence": transcription_result.get("language_probability", 0.0)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ses dosyası işleme hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Ses işleme hatası: {str(e)}")

@router.post("/test-transcription")
async def test_transcription(text: str = Form(...)):
    """
    Transkripsiyon testi - metin girişi ile
    
    Args:
        text: Test metni
        
    Returns:
        JSONResponse: Test sonucu
    """
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Test metni boş olamaz")
        
        # Semptom analizi yap
        symptom_analyzer = get_symptom_analyzer()
        analysis_result = symptom_analyzer.analyze_transcript(text)
        
        return JSONResponse(content={
            "success": True,
            "input_text": text,
            "detected_symptoms": analysis_result["detected_symptoms"],
            "symptom_count": analysis_result["symptom_count"],
            "analysis_success": analysis_result["analysis_success"]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test transkripsiyon hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Test hatası: {str(e)}")

@router.post("/clinic-from-audio")
async def clinic_from_audio(audio_file: UploadFile = File(...)):
    """Ses dosyasından transkript çıkarıp ML triage ile klinik önerir"""
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
            return JSONResponse(content={"success": False, "error": "Boş transkript"})

        triage = get_triage_model()
        result = triage.suggest(transcript, top_k=3)

        return JSONResponse(content={
            "success": True,
            "transcript": transcript,
            "triage": result
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Klinik öneri (audio) hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Klinik öneri hatası: {str(e)}")

@router.post("/clinic-from-text")
async def clinic_from_text(text: str = Form(...)):
    """Verilen metinden ML triage ile klinik önerir"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Metin boş olamaz")
        triage = get_triage_model()
        result = triage.suggest(text, top_k=3)
        return JSONResponse(content={"success": True, "triage": result, "input_text": text})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Klinik öneri (text) hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Klinik öneri hatası: {str(e)}")

@router.post("/clinic-from-audio-llm")
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
            return JSONResponse(content={"success": False, "error": "Boş transkript"})

        # Entegre triage sistemi kullan
        integrated_triage = get_integrated_triage()
        result = integrated_triage.suggest(transcript, top_k=3)

        return JSONResponse(content={
            "success": True,
            "transcript": transcript,
            "triage": result,
            "system_status": integrated_triage.get_system_status()
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Entegre klinik öneri (audio) hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Entegre klinik öneri hatası: {str(e)}")

@router.post("/clinic-from-text-llm")
async def clinic_from_text_llm(text: str = Form(...)):
    """Verilen metinden entegre ML+LLM triage ile klinik önerir"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Metin boş olamaz")
        
        # Entegre triage sistemi kullan
        integrated_triage = get_integrated_triage()
        result = integrated_triage.suggest(text, top_k=3)
        
        return JSONResponse(content={
            "success": True, 
            "triage": result, 
            "input_text": text,
            "system_status": integrated_triage.get_system_status()
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Entegre klinik öneri (text) hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Entegre klinik öneri hatası: {str(e)}")

@router.get("/system-status")
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
        
        return JSONResponse(content={
            "success": True,
            "status": status
        })
    except Exception as e:
        logger.error(f"Sistem durumu hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Sistem durumu hatası: {str(e)}")

@router.get("/status")
async def whisper_status():
    """
    Whisper ASR sistem durumu
    
    Returns:
        JSONResponse: Sistem durumu
    """
    try:
        asr_processor = get_asr_processor()
        
        return JSONResponse(content={
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
        })
        
    except Exception as e:
        logger.error(f"Durum kontrolü hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Durum kontrolü hatası: {str(e)}")

@router.get("/symptoms")
async def get_supported_symptoms():
    """
    Desteklenen semptomları döndürür
    
    Returns:
        JSONResponse: Semptom listesi
    """
    try:
        symptom_analyzer = get_symptom_analyzer()
        
        symptoms = list(symptom_analyzer.symptom_keywords.keys())
        
        return JSONResponse(content={
            "success": True,
            "symptoms": symptoms,
            "total_count": len(symptoms),
            "categories": {
                "fiziksel": [s for s in symptoms if any(x in s for x in ['agrisi', 'ates', 'bulanti', 'sari'])],
                "psikolojik": [s for s in symptoms if any(x in s for x in ['depresyon', 'konsantrasyon', 'uyku'])],
                "hormonal": [s for s in symptoms if any(x in s for x in ['adet', 'meme', 'sac', 'kilo'])]
            }
        })
        
    except Exception as e:
        logger.error(f"Semptom listesi hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Semptom listesi hatası: {str(e)}")
