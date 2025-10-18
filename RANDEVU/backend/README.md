# 🏥 TanıAI Backend - Klinik Öneri Sistemi

## 📋 Genel Bakış
Bu backend, hasta şikayetlerini analiz ederek uygun kliniği öneren bir AI sistemi içerir. 20,500 gerçek hasta verisiyle eğitilmiş Ollama modeli kullanır.

## 📁 Dosya Yapısı

### 🤖 **Model Eğitimi ve Yönetimi**
- **`clinic_model_trainer.py`** - Ana model eğitim scripti
  - `clinics/` klasöründeki verileri okur
  - Modelfile oluşturur
  - Ollama modelini eğitir
  - **Kullanım:** `python3 clinic_model_trainer.py`

- **`clinic_recommender_service.py`** - Eğitilmiş model servisi
  - Ollama API'si ile iletişim
  - Klinik önerisi yapar
  - JSON formatında sonuç döner

### 🧪 **Test ve Geliştirme**
- **`test_clinic_model.py`** - Model test arayüzü
  - Konsol tabanlı test sistemi
  - Tek/çoklu şikayet testi
  - Gerçek zamanlı analiz
  - **Kullanım:** `python3 test_clinic_model.py`

- **`test_api.py`** - API endpoint testleri
  - FastAPI testleri
  - HTTP istek testleri

### 🌐 **API Servisleri**
- **`main.py`** - Ana FastAPI uygulaması
  - REST API endpoints
  - CORS desteği
  - Klinik önerisi API'si
  - **Kullanım:** `python3 main.py`

- **`simple_api.py`** - Basit API servisi
  - Minimal API implementasyonu
  - Hızlı test için

- **`start_server.py`** - Sunucu başlatma scripti
  - Uvicorn ile sunucu başlatır
  - **Kullanım:** `python3 start_server.py`

### 🔧 **LLM Entegrasyonu**
- **`llm_service.py`** - LLM servis yönetimi
  - Çoklu LLM provider desteği
  - OpenAI, Google, Ollama entegrasyonu
  - Fallback mekanizması

### 📊 **Veri Dosyaları**
- **`clinic_training.jsonl`** - Eğitim verisi (20,500 örnek)
- **`ClinicModelfile`** - Ollama model tanımı
- **`requirements.txt`** - Python bağımlılıkları

### 🗂️ **Klasörler**
- **`clinics/`** - Klinik verileri (41 JSONL dosyası)
  - Her klinik için ayrı dosya
  - Gerçek hasta şikayetleri
  - Model eğitimi için veri kaynağı

- **`old_models/`** - Eski model implementasyonları
  - `clinic_service.py` - Eski klinik servisi
  - `triage_service.py` - Eski triyaj servisi

## 🚀 Hızlı Başlangıç

### 1. **Bağımlılıkları Yükle**
```bash
pip3 install -r requirements.txt
```

### 2. **Modeli Eğit (İlk Kez)**
```bash
python3 clinic_model_trainer.py
ollama create clinic-recommender -f ClinicModelfile
```

### 3. **Modeli Test Et**
```bash
python3 test_clinic_model.py
```

### 4. **API'yi Başlat**
```bash
python3 main.py
# veya
python3 start_server.py
```

## 🔄 Model Eğitimi Süreci

### **Veri Akışı:**
```
clinics/*.jsonl → clinic_model_trainer.py → ClinicModelfile → Ollama Model
```

### **Eğitim Adımları:**
1. **Veri Yükleme:** 41 klinikten 500'er örnek (20,500 toplam)
2. **Prompt Oluşturma:** Sistem + örnekler + kurallar
3. **Modelfile:** Ollama için model tanımı
4. **Model Yükleme:** `ollama create` komutu

### **Model Özellikleri:**
- **Base Model:** Llama 3.2 3B
- **Eğitim Yöntemi:** Few-shot learning
- **Veri Kaynağı:** Gerçek hasta şikayetleri
- **Çıktı Formatı:** JSON (`{"clinic": "...", "confidence": 0.95, "reasoning": "..."}`)

## 🧪 Test Senaryoları

### **Tek Şikayet:**
```
1. Şikayet: Başım ağrıyor
Başka semptom var mı? (e/h): h
→ Nöroloji önerisi
```

### **Çoklu Semptom:**
```
1. Şikayet: Düştüm bileğimi incittim
Başka semptom var mı? (e/h): e
Ek semptomlar: Bileğim çok ağrıyor ve morardı
→ Acil Servis önerisi
```

## 🔧 API Endpoints

### **Klinik Önerisi:**
```http
POST /recommend-clinic
Content-Type: application/json

{
  "symptoms": "Başım ağrıyor"
}
```

### **Yanıt:**
```json
{
  "recommended_clinic": "Nöroloji",
  "urgency": "normal",
  "reasoning": "Baş ağrısı semptomları nöroloji bölümüne uygun",
  "alternatives": ["Aile Hekimliği"],
  "timestamp": "2024-01-01T12:00:00"
}
```

## 📈 Performans

### **Model Metrikleri:**
- **Eğitim Verisi:** 20,500 örnek
- **Klinik Sayısı:** 41
- **Ortalama Güven:** 0.85-0.95
- **Yanıt Süresi:** <2 saniye

### **Desteklenen Klinikler:**
Acil Servis, Aile Hekimliği, Nöroloji, Kardiyoloji, Göz Hastalıkları, Ortopedi ve Travmatoloji, Genel Cerrahi, ve 34 diğer klinik.

## 🛠️ Geliştirme

### **Model Güncelleme:**
1. `clinics/` klasörüne yeni veri ekle
2. `python3 clinic_model_trainer.py` çalıştır
3. `ollama create clinic-recommender -f ClinicModelfile` ile güncelle

### **Yeni Klinik Ekleme:**
1. `clinics/Yeni_Klinik.jsonl` dosyası oluştur
2. JSON formatında hasta verileri ekle: `{"complaint": "...", "clinic": "Yeni Klinik"}`
3. Modeli yeniden eğit

## 🚨 Sorun Giderme

### **Model Bulunamıyor:**
```bash
ollama list | grep clinic
ollama create clinic-recommender -f ClinicModelfile
```

### **API Çalışmıyor:**
```bash
python3 -c "import requests; print(requests.get('http://localhost:11434/api/tags').json())"
```

### **Veri Hatası:**
```bash
python3 -c "import json; print(len([json.loads(line) for line in open('../clinics/Aile_Hekimliği.jsonl')]))"
```

## 📞 İletişim
Sorularınız için: [GitHub Issues](https://github.com/sevggii)


