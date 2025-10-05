#!/usr/bin/env python3
"""
Whisper ASR (Automatic Speech Recognition) Entegrasyonu
Sesli asistan için Whisper Large modeli desteği
"""

import os
import logging
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

logger = logging.getLogger(__name__)

class WhisperASR:
    """Whisper ASR sınıfı"""
    
    def __init__(self, model_size: str = "large"):
        self.model_size = model_size
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Whisper modelini yükle"""
        if not WHISPER_AVAILABLE:
            logger.error("Whisper kütüphanesi yüklü değil. pip install openai-whisper")
            return
        
        try:
            logger.info(f"Whisper {self.model_size} modeli yükleniyor...")
            self.model = whisper.load_model(self.model_size)
            logger.info(f"Whisper {self.model_size} modeli başarıyla yüklendi")
        except Exception as e:
            logger.error(f"Whisper modeli yüklenemedi: {e}")
            self.model = None
    
    def transcribe_audio_file(self, audio_path: str) -> Dict[str, Any]:
        """Ses dosyasını metne çevir"""
        if not self.model:
            return {
                "success": False,
                "error": "Whisper modeli yüklü değil",
                "transcript": ""
            }
        
        try:
            if not os.path.exists(audio_path):
                return {
                    "success": False,
                    "error": f"Ses dosyası bulunamadı: {audio_path}",
                    "transcript": ""
                }
            
            logger.info(f"Ses dosyası transkripsiyonu başlıyor: {audio_path}")
            result = self.model.transcribe(audio_path, language="tr")
            
            transcript = result["text"].strip()
            confidence = result.get("segments", [{}])[0].get("avg_logprob", 0) if result.get("segments") else 0
            
            logger.info(f"Transkripsiyon tamamlandı: {len(transcript)} karakter")
            
            return {
                "success": True,
                "transcript": transcript,
                "confidence": confidence,
                "language": result.get("language", "tr"),
                "segments": result.get("segments", [])
            }
            
        except Exception as e:
            logger.error(f"Transkripsiyon hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcript": ""
            }
    
    def transcribe_from_bytes(self, audio_bytes: bytes, file_extension: str = "wav") -> Dict[str, Any]:
        """Byte verisinden ses dosyasını metne çevir"""
        if not self.model:
            return {
                "success": False,
                "error": "Whisper modeli yüklü değil",
                "transcript": ""
            }
        
        try:
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            try:
                # Transkripsiyon yap
                result = self.transcribe_audio_file(temp_path)
                return result
            finally:
                # Geçici dosyayı sil
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Byte transkripsiyon hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcript": ""
            }
    
    def is_available(self) -> bool:
        """Whisper kullanılabilir mi?"""
        return WHISPER_AVAILABLE and self.model is not None

# Global instance
_whisper_instance: Optional[WhisperASR] = None

def get_whisper_asr(model_size: str = "large") -> WhisperASR:
    """Whisper ASR instance'ını al"""
    global _whisper_instance
    
    if _whisper_instance is None:
        _whisper_instance = WhisperASR(model_size)
    
    return _whisper_instance

def transcribe_audio_file(audio_path: str, model_size: str = "large") -> Dict[str, Any]:
    """Ses dosyasını metne çevir"""
    asr = get_whisper_asr(model_size)
    return asr.transcribe_audio_file(audio_path)

def transcribe_from_bytes(audio_bytes: bytes, file_extension: str = "wav", model_size: str = "large") -> Dict[str, Any]:
    """Byte verisinden ses dosyasını metne çevir"""
    asr = get_whisper_asr(model_size)
    return asr.transcribe_from_bytes(audio_bytes, file_extension)

if __name__ == "__main__":
    # Test
    asr = get_whisper_asr("large")
    
    if asr.is_available():
        print("✅ Whisper ASR hazır!")
        print(f"Model: {asr.model_size}")
    else:
        print("❌ Whisper ASR kullanılamıyor")
        print("Kurulum: pip install openai-whisper")
