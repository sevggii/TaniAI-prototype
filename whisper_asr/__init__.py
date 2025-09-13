#!/usr/bin/env python3
"""
Whisper ASR Modülü
TanıAI için Speech-to-Text sistemi
"""

import whisper
import tempfile
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class WhisperASR:
    """Whisper tabanlı Speech-to-Text sınıfı"""
    
    def __init__(self, model_name: str = "base"):
        """
        Args:
            model_name: Whisper model boyutu (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Whisper modelini yükler"""
        try:
            logger.info(f"Whisper {self.model_name} modeli yükleniyor...")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper modeli başarıyla yüklendi!")
        except Exception as e:
            logger.error(f"Whisper model yükleme hatası: {e}")
            raise
    
    def transcribe_audio(self, audio_file_path: str, language: str = "tr") -> Dict[str, Any]:
        """
        Ses dosyasını metne çevirir
        
        Args:
            audio_file_path: Ses dosyası yolu
            language: Dil kodu (varsayılan: tr)
            
        Returns:
            Dict: Transkripsiyon sonucu
        """
        try:
            if self.model is None:
                self._load_model()
            
            logger.info(f"Ses dosyası transkripsiyonu başlıyor: {audio_file_path}")
            
            # Whisper ile transkripsiyon
            result = self.model.transcribe(
                audio_file_path, 
                language=language,
                verbose=False
            )
            
            transcript = result["text"].strip()
            
            logger.info(f"Transkripsiyon tamamlandı: {len(transcript)} karakter")
            
            return {
                "success": True,
                "transcript": transcript,
                "language": language,
                "segments": result.get("segments", []),
                "language_probability": result.get("language_probability", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Transkripsiyon hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcript": ""
            }
    
    def transcribe_from_bytes(self, audio_bytes: bytes, language: str = "tr") -> Dict[str, Any]:
        """
        Byte verisinden ses transkripsiyonu yapar
        
        Args:
            audio_bytes: Ses dosyası byte verisi
            language: Dil kodu
            
        Returns:
            Dict: Transkripsiyon sonucu
        """
        temp_file = None
        try:
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            # Transkripsiyon yap
            result = self.transcribe_audio(temp_file_path, language)
            
            return result
            
        except Exception as e:
            logger.error(f"Byte transkripsiyon hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcript": ""
            }
        finally:
            # Geçici dosyayı temizle
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

# Global ASR instance
asr_processor = WhisperASR()

def get_asr_processor() -> WhisperASR:
    """ASR processor instance'ını döndürür"""
    return asr_processor
