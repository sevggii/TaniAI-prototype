# TanıAI Entegre Sistem Kurulum Rehberi

Bu rehber, Whisper + ML + LLM entegre sistemini kurmak ve kullanmak için gerekli adımları içerir.

## 🎯 Sistem Özellikleri

- **Whisper Large Model**: Ses dosyalarını Türkçe metne çevirir
- **ML Triage Model**: Scikit-learn tabanlı klinik öneri sistemi
- **LLM Entegrasyonu**: Ollama ile LLM tabanlı akıllı analiz
- **Hibrit Sistem**: ML + LLM sonuçlarını birleştirerek daha doğru öneriler

## 📋 Gereksinimler

### Sistem Gereksinimleri
- Python 3.8+
- 8GB+ RAM (LLM için)
- GPU önerilir (Whisper için)

### Python Bağımlılıkları
```bash
pip install -r ml_clinic/requirements.txt
```

## 🚀 Kurulum Adımları

### 🖥️ Yerel Kurulum (Windows/Linux/macOS)

#### 1. Python Bağımlılıklarını Kurun
```bash
cd RANDEVU
pip install -r ml_clinic/requirements.txt
```

#### 2. Ollama Kurulumu (LLM için)
```bash
# Ollama'yı indirin ve kurun: https://ollama.ai/download

# Küçük model indirin (2B parametre)
ollama pull llama2:2b
# veya daha büyük model
ollama pull llama2:7b
```

#### 3. Ollama Servisini Başlatın
```bash
ollama serve
```

#### 4. Sistem Testini Çalıştırın
```bash
cd RANDEVU
python test_integrated_system.py
```

### ☁️ Cloud Kurulum (Google Colab/Kaggle)

#### 1. Google Colab'da Çalıştır
- `TanıAI_Cloud_Setup.ipynb` dosyasını Colab'a yükleyin
- Tüm hücreleri sırayla çalıştırın
- Otomatik kurulum yapılacak

#### 2. Kaggle'da Çalıştır
```python
# Kaggle notebook'unda
!curl -fsSL https://ollama.ai/install.sh | sh
!ollama pull llama2:2b
!ollama serve &
```

#### 3. Cloud Özellikleri
- **Whisper Medium Model**: Cloud için optimize edilmiş
- **Llama2:2b Model**: 2B parametre, hızlı ve verimli
- **Otomatik Kurulum**: Tek tıkla kurulum
- **Web Erişimi**: Ngrok ile dışarıdan erişim

## 🔧 Yapılandırma

### Çevre Değişkenleri (Opsiyonel)

```bash
# .env dosyası oluşturun
LLM_PROVIDER=ollama
LLM_MODEL=llama2:7b
LLM_BASE_URL=http://localhost:11434
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.1
LLM_TIMEOUT=30

USE_ML=true
USE_LLM=true
ML_WEIGHT=0.6
LLM_WEIGHT=0.4
```

## 🎮 Kullanım

### 1. Sunucuyu Başlatın

```bash
cd RANDEVU/whisper_asr
python server.py
```

Sunucu `http://localhost:8001` adresinde çalışacak.

### 2. API Endpoint'leri

#### Sistem Durumu
```bash
curl http://localhost:8001/whisper/system-status
```

#### Metin ile Klinik Önerisi (ML)
```bash
curl -X POST "http://localhost:8001/whisper/clinic-from-text" \
  -F "text=Baş ağrım var ve mide bulantısı yaşıyorum"
```

#### Metin ile Klinik Önerisi (ML + LLM)
```bash
curl -X POST "http://localhost:8001/whisper/clinic-from-text-llm" \
  -F "text=Baş ağrım var ve mide bulantısı yaşıyorum"
```

#### Ses Dosyası ile Klinik Önerisi (ML + LLM)
```bash
curl -X POST "http://localhost:8001/whisper/clinic-from-audio-llm" \
  -F "audio_file=@test_audio.wav"
```

### 3. Web Arayüzü

Tarayıcıda `http://localhost:8001` adresine gidin.

## 📊 Test Senaryoları

### Örnek Test Metinleri

```python
test_cases = [
    "Baş ağrım var ve mide bulantısı yaşıyorum",
    "Çocuğumda ateş ve öksürük var", 
    "Göğüs ağrısı ve nefes darlığı çekiyorum",
    "Diş ağrısı dayanılmaz halde",
    "Depresyondayım ve uyuyamıyorum",
    "Karın ağrısı ve ishal var"
]
```

### Beklenen Sonuçlar

- **Baş ağrısı + mide bulantısı** → Nöroloji veya İç Hastalıkları
- **Çocuk + ateş** → Çocuk Sağlığı ve Hastalıkları
- **Göğüs ağrısı** → Kardiyoloji
- **Diş ağrısı** → Diş Hekimliği
- **Depresyon** → Ruh Sağlığı ve Hastalıkları
- **Karın ağrısı** → İç Hastalıkları (Dahiliye)

## 🔍 Sorun Giderme

### LLM Bağlantı Sorunları

```bash
# Ollama durumunu kontrol edin
curl http://localhost:11434/api/tags

# Ollama'yı yeniden başlatın
ollama serve
```

### Whisper Model Sorunları

```bash
# Whisper modelini yeniden indirin
pip uninstall openai-whisper
pip install openai-whisper
```

### ML Model Sorunları

```bash
# Bağımlılıkları yeniden kurun
pip install -r ml_clinic/requirements.txt
```

## 📈 Performans Optimizasyonu

### GPU Kullanımı (Whisper için)

```python
# CUDA kullanımı için
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

### Model Boyutu Seçimi

- **Whisper**: `large` (en iyi), `medium` (orta), `small` (hızlı)
- **LLM**: `llama2:7b` (en iyi), `llama2:2b` (hızlı)

### Bellek Optimizasyonu

```python
# Küçük modeller için
LLM_MODEL=llama2:2b
WHISPER_MODEL=small
```

## 🚨 Acil Durum Tespiti

Sistem aşağıdaki durumları acil olarak tespit eder:

- **Kalp krizi belirtileri**: Göğüs ağrısı + soğuk terleme
- **İnme belirtileri**: Ani yüz kayması + konuşma bozukluğu
- **Şiddetli travma**: Bilinç kaybı + kanama
- **Gebelik acil**: Hamilelik + şiddetli ağrı

Bu durumlarda sistem "ACIL" yanıtı verir ve 112 aranmasını önerir.

## 📝 Log Dosyaları

```bash
# Log dosyalarını kontrol edin
tail -f logs/system.log
```

## 🔄 Güncelleme

```bash
# Sistemi güncelleyin
git pull
pip install -r ml_clinic/requirements.txt
python test_integrated_system.py
```

## 📞 Destek

Sorunlar için:
1. `test_integrated_system.py` çalıştırın
2. Log dosyalarını kontrol edin
3. Sistem gereksinimlerini doğrulayın

## 🎯 Gelecek Geliştirmeler

- [ ] Daha fazla LLM modeli desteği
- [ ] Web arayüzü iyileştirmeleri
- [ ] Gerçek zamanlı ses analizi
- [ ] Çoklu dil desteği
- [ ] Mobil uygulama
