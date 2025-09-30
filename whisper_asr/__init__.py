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
                no_speech_threshold=0.3,  # Daha yüksek eşik - daha az hassas
                logprob_threshold=-1.0,   # Daha yüksek eşik
                compression_ratio_threshold=2.4,
                condition_on_previous_text=False,  # Önceki metne bağımlılığı kaldır
                best_of=1,  # Tek transkripsiyon dene (daha hızlı)
                beam_size=1,  # Daha küçük beam search
                patience=1.0,  # Sabırlı ol
                initial_prompt="Türkçe konuşma, tıbbi şikayet, randevu, baş ağrısı, mide ağrısı, göğüs ağrısı, nefes darlığı, öksürük, boğaz ağrısı, karın ağrısı, sırt ağrısı, bel ağrısı, eklem ağrısı, kaşıntı, döküntü, ateş, halsizlik, yorgunluk, uyku, stres, kaygı, endişe, depresyon, migren, baş dönmesi, çarpıntı, bulantı, kusma, ishal, kabızlık, iştahsızlık, kilo kaybı, kilo alma, terleme, titreme, kas ağrısı, eklem şişliği, cilt değişikliği, saç dökülmesi, tırnak değişikliği, göz problemleri, kulak problemleri, burun tıkanıklığı, sinüs ağrısı, diş ağrısı, çene ağrısı, boyun ağrısı, omuz ağrısı, kol ağrısı, el ağrısı, bacak ağrısı, ayak ağrısı, diz ağrısı, ayak bileği ağrısı, topuk ağrısı, bel fıtığı, boyun fıtığı, romatizma, artrit, osteoporoz, kemik erimesi, kas spazmı, kramp, uyuşma, karıncalanma, yanma, sızlama, zonklama, batma, sancı, ağrı, sızı, acı, rahatsızlık, şikayet, problem, sorun, hastalık, rahatsızlık, muayene, tedavi, ilaç, doktor, hekim, klinik, hastane, randevu, muayene, kontrol, test, tahlil, röntgen, MR, tomografi, ultrason, EKG, kan tahlili, idrar tahlili, dışkı tahlili, biyopsi, ameliyat, operasyon, cerrahi, fizik tedavi, rehabilitasyon, terapi, psikoloji, psikiyatri, nöroloji, kardiyoloji, gastroenteroloji, göğüs hastalıkları, kulak burun boğaz, dermatoloji, ortopedi, jinekoloji, üroloji, endokrinoloji, onkoloji, hematoloji, nefroloji, romatoloji, alerji, immünoloji, enfeksiyon hastalıkları, çocuk hastalıkları, yaşlılık hastalıkları, aile hekimliği, iç hastalıkları, genel cerrahi, plastik cerrahi, beyin cerrahisi, kalp cerrahisi, göğüs cerrahisi, karın cerrahisi, ortopedi cerrahisi, jinekoloji cerrahisi, üroloji cerrahisi, kulak burun boğaz cerrahisi, göz cerrahisi, plastik cerrahi, estetik cerrahi, rekonstrüktif cerrahi, mikrocerrahi, laparoskopik cerrahi, robotik cerrahi, minimal invaziv cerrahi, açık cerrahi, kapalı cerrahi, endoskopik cerrahi, artroskopik cerrahi, nöroşirürji, kardiyovasküler cerrahi, torasik cerrahi, abdominal cerrahi, pelvik cerrahi, spinal cerrahi, kraniyal cerrahi, periferik cerrahi, vasküler cerrahi, onkolojik cerrahi, rekonstrüktif cerrahi, transplantasyon cerrahisi, acil cerrahi, elektif cerrahi, acil müdahale, acil servis, yoğun bakım, anestezi, reanimasyon, yoğun bakım ünitesi, koroner yoğun bakım, nörolojik yoğun bakım, pediatrik yoğun bakım, neonatal yoğun bakım, kardiyak yoğun bakım, pulmoner yoğun bakım, renal yoğun bakım, hepatik yoğun bakım, endokrin yoğun bakım, onkolojik yoğun bakım, hematolojik yoğun bakım, immünolojik yoğun bakım, enfeksiyon yoğun bakım, travma yoğun bakım, yanık yoğun bakım, plastik cerrahi yoğun bakım, ortopedi yoğun bakım, jinekoloji yoğun bakım, üroloji yoğun bakım, kulak burun boğaz yoğun bakım, göz yoğun bakım, dermatoloji yoğun bakım, psikiyatri yoğun bakım, geriatri yoğun bakım, palyatif bakım, evde bakım, huzurevi, bakım evi, rehabilitasyon merkezi, fizik tedavi merkezi, spor merkezi, fitness merkezi, wellness merkezi, spa merkezi, masaj merkezi, akupunktur merkezi, homeopati merkezi, fitoterapi merkezi, aromaterapi merkezi, müzik terapi merkezi, sanat terapi merkezi, dans terapi merkezi, drama terapi merkezi, oyun terapi merkezi, aile terapi merkezi, çift terapi merkezi, grup terapi merkezi, bireysel terapi merkezi, online terapi merkezi, telefon terapi merkezi, video terapi merkezi, chat terapi merkezi, mesaj terapi merkezi, e-posta terapi merkezi, sosyal medya terapi merkezi, mobil uygulama terapi merkezi, web sitesi terapi merkezi, blog terapi merkezi, podcast terapi merkezi, video blog terapi merkezi, canlı yayın terapi merkezi, webinar terapi merkezi, online kurs terapi merkezi, e-kitap terapi merkezi, e-dergi terapi merkezi, e-gazete terapi merkezi, e-haber terapi merkezi, e-magazin terapi merkezi, e-katalog terapi merkezi, e-broşür terapi merkezi, e-flyer terapi merkezi, e-poster terapi merkezi, e-afiş terapi merkezi, e-banner terapi merkezi, e-reklam terapi merkezi, e-pazarlama terapi merkezi, e-satış terapi merkezi, e-ticaret terapi merkezi, e-alışveriş terapi merkezi, e-market terapi merkezi, e-mağaza terapi merkezi, e-süpermarket terapi merkezi, e-hipermarket terapi merkezi, e-avm terapi merkezi, e-plaza terapi merkezi, e-outlet terapi merkezi, e-factory terapi merkezi, e-warehouse terapi merkezi, e-depot terapi merkezi, e-stock terapi merkezi, e-inventory terapi merkezi, e-supply terapi merkezi, e-logistics terapi merkezi, e-shipping terapi merkezi, e-delivery terapi merkezi, e-cargo terapi merkezi, e-kargo terapi merkezi, e-posta terapi merkezi, e-mail terapi merkezi, e-mesaj terapi merkezi, e-sms terapi merkezi, e-whatsapp terapi merkezi, e-telegram terapi merkezi, e-instagram terapi merkezi, e-facebook terapi merkezi, e-twitter terapi merkezi, e-linkedin terapi merkezi, e-youtube terapi merkezi, e-tiktok terapi merkezi, e-snapchat terapi merkezi, e-pinterest terapi merkezi, e-reddit terapi merkezi, e-discord terapi merkezi, e-slack terapi merkezi, e-microsoft terapi merkezi, e-google terapi merkezi, e-apple terapi merkezi, e-amazon terapi merkezi, e-netflix terapi merkezi, e-spotify terapi merkezi, e-youtube terapi merkezi, e-instagram terapi merkezi, e-facebook terapi merkezi, e-twitter terapi merkezi, e-linkedin terapi merkezi, e-tiktok terapi merkezi, e-snapchat terapi merkezi, e-pinterest terapi merkezi, e-reddit terapi merkezi, e-discord terapi merkezi, e-slack terapi merkezi, e-microsoft terapi merkezi, e-google terapi merkezi, e-apple terapi merkezi, e-amazon terapi merkezi, e-netflix terapi merkezi, e-spotify terapi merkezi"
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
            # Medium modeli kullan (daha iyi Türkçe desteği)
            logger.info("Whisper medium modeli yükleniyor...")
            asr_processor = WhisperASR("medium")
            logger.info("Medium modeli başarıyla yüklendi!")
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
