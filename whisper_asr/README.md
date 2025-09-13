# Whisper ASR Modülü

Bu klasör TanıAI projesi için Speech-to-Text (ASR) sistemini içerir.

## 📁 Dosya Yapısı

- `__init__.py` - Ana Whisper ASR sınıfı
- `symptom_analyzer.py` - Semptom analizi modülü  
- `api.py` - FastAPI endpoint'leri
- `test.py` - Test scripti
- `README.md` - Bu dosya

## 🚀 Kurulum

```bash
pip install openai-whisper
```

## 🧪 Test

```bash
python whisper_asr/test.py
```

## 📋 API Endpoint'leri

- `POST /whisper/upload-audio` - Ses dosyası yükleme
- `POST /whisper/test-transcription` - Metin testi
- `GET /whisper/status` - Sistem durumu
- `GET /whisper/symptoms` - Desteklenen semptomlar

## 🎯 Özellikler

- ✅ Türkçe ses tanıma
- ✅ Otomatik semptom tespiti
- ✅ Şiddet seviyesi belirleme
- ✅ Çoklu ses formatı desteği
- ✅ FastAPI entegrasyonu

## 📊 Desteklenen Formatlar

- WAV, MP3, M4A, FLAC, OGG
- Maksimum dosya boyutu: 10MB

## 🔧 Kullanım

```python
from whisper_asr import get_asr_processor
from whisper_asr.symptom_analyzer import get_symptom_analyzer

# ASR processor
asr = get_asr_processor()
result = asr.transcribe_audio("ses_dosyasi.wav")

# Semptom analizi
analyzer = get_symptom_analyzer()
symptoms = analyzer.analyze_transcript(result["transcript"])
```
