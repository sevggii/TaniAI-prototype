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

logger = logging.getLogger(__name__)

# Router oluştur
router = APIRouter(prefix="/whisper", tags=["Whisper ASR"])

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
