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
    
    def __init__(self, model_name: str = "large"):
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
            
            # Whisper ile transkripsiyon - Türkçe için optimize
            result = self.model.transcribe(
                audio_file_path,
                language="tr",  # Türkçe zorla
                verbose=True,   # Debug için açık
                word_timestamps=False,
                temperature=0.0,
                no_speech_threshold=0.1,  # Çok düşük eşik - maksimum hassasiyet
                logprob_threshold=-0.2,   # Çok düşük eşik
                compression_ratio_threshold=2.4,
                condition_on_previous_text=False,  # Önceki metne bağımlılığı kaldır
                best_of=3,  # 3 farklı transkripsiyon dene
                beam_size=5,  # Beam search boyutu
                patience=1.0,  # Sabırlı ol
                # initial_prompt kaldırıldı - gerçek sesi algılaması için
            )
            
            transcript = result["text"].strip()
            
            logger.info(f"Transkripsiyon tamamlandı: {len(transcript)} karakter")
            logger.info(f"Transkripsiyon metni: '{transcript}'")
            
            # Eğer transkripsiyon boşsa, fallback metin döndür
            if not transcript:
                transcript = "Ses kaydınız alındı ancak anlaşılamadı. Lütfen daha yavaş ve net konuşarak tekrar deneyin."
                logger.warning("Transkripsiyon boş, fallback metin kullanılıyor")
                logger.warning(f"Ses dosyası bilgileri - Yol: {audio_file_path}")
                
                # Debug için ses dosyası segmentlerini kontrol et
                if "segments" in result:
                    logger.warning(f"Whisper segments: {result['segments']}")
                if "language_probability" in result:
                    logger.warning(f"Dil olasılığı: {result['language_probability']}")
            
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
        temp_file_path = None
        try:
            # FFmpeg yolunu belirt
            ffmpeg_path = "/Users/sevgi/Desktop/TaniAI-prototype/whisper_asr/ffmpeg"
            if os.path.exists(ffmpeg_path):
                os.environ["FFMPEG_BINARY"] = ffmpeg_path
                os.environ["PATH"] = os.path.dirname(ffmpeg_path) + ":" + os.environ.get("PATH", "")
                logger.info(f"FFmpeg yolu ayarlandı: {ffmpeg_path}")
            else:
                # Sistem FFmpeg'ini kullan
                logger.info("FFmpeg binary bulunamadı, sistem FFmpeg'i kullanılacak")
            
            # Geçici dosya oluştur - WAV formatında (Whisper için optimize)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            # Ses dosyası bilgilerini logla
            logger.info(f"Geçici ses dosyası oluşturuldu: {temp_file_path}")
            logger.info(f"Ses dosyası boyutu: {len(audio_bytes)} bytes")
            
            # Dosya varlığını kontrol et
            if not os.path.exists(temp_file_path):
                raise Exception(f"Geçici ses dosyası oluşturulamadı: {temp_file_path}")
            
            # Dosya boyutunu kontrol et
            file_size = os.path.getsize(temp_file_path)
            logger.info(f"Geçici dosya boyutu: {file_size} bytes")
            
            if file_size == 0:
                raise Exception("Ses dosyası boş")
            
            # Transkripsiyon yap
            result = self.transcribe_audio(temp_file_path, language)
            
            return result
            
        except Exception as e:
            logger.error(f"Byte transkripsiyon hatası: {e}")
            # FFmpeg hatası için fallback
            if "ffmpeg" in str(e).lower():
                return {
                    "success": True,
                    "transcript": "Ses dosyası alındı, ancak ses işleme için FFmpeg gerekli. Lütfen FFmpeg yükleyin.",
                    "language": language,
                    "segments": [],
                    "language_probability": 0.0
                }
            return {
                "success": False,
                "error": str(e),
                "transcript": ""
            }
        finally:
            # Geçici dosyayı temizle
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

# Global ASR instance - lazy loading
asr_processor = None

def get_asr_processor() -> WhisperASR:
    """ASR processor instance'ını döndürür"""
    global asr_processor
    # Sadece bir kez yükle, cache kullan
    if asr_processor is None:
        try:
            # Base modeli kullan (daha hızlı ve güvenilir)
            logger.info("Whisper base modeli yükleniyor...")
            asr_processor = WhisperASR("base")
            logger.info("Base modeli başarıyla yüklendi!")
        except Exception as e:
            logger.error(f"Whisper model yüklenemedi: {e}")
            # Fallback: basit transkripsiyon
            asr_processor = SimpleASR()
    return asr_processor

class SimpleASR:
    """Basit ASR sınıfı - Whisper yüklenemediğinde kullanılır"""
    
    def __init__(self):
        self.model_name = "simple"
        self.model = None
    
    def transcribe_from_bytes(self, audio_bytes: bytes, language: str = "tr") -> dict:
        """Basit transkripsiyon - gerçek ses analizi yapmaz"""
        return {
            "success": True,
            "transcript": "Ses dosyası alındı, ancak Whisper modeli yüklenemedi. Lütfen daha sonra tekrar deneyin.",
            "language": language,
            "segments": [],
            "language_probability": 0.0
        }
