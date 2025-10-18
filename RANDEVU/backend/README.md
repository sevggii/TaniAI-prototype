# 🏥 TanıAI Klinik Öneri Sistemi - Backend

## 🎯 Proje Tanımı

Bu proje TanıAI sisteminin **"Randevu Yönlendirme / Klinik Öneri"** bileşenidir. Hasta şikayetlerini alır, metni küçük bir LLM (Ollama) modeliyle normalize eder, ancak **nihai klinik kararını LLM değil, kendi eğitimli makine öğrenmesi modeli verir**.

### 🔍 Sistem Nasıl Çalışır?
1. **Hasta şikayeti girer** → "Başım çok ağrıyor, mide bulantım var"
2. **LLM normalizasyon** → Metni temizler ve standartlaştırır
3. **SVM Model analizi** → 41 farklı klinik arasından en uygun olanı seçer
4. **Sonuç döner** → Klinik önerisi + açıklama + alternatifler

## ⚙️ Teknik Kurallar

- **LLM desteği:** Ollama ile küçük modeller (0.5B–2B) kullanılacak
- **LiteLLM entegrasyonu:** LLM çağrıları LiteLLM üzerinden yapılacak (tek gateway)
- **Nihai karar:** LLM'den direkt dönmeyecek. LLM sadece "ön işleme / embedding / aday üretme" için kullanılabilir
- **Nihai klinik tahmini:** `clinic_dataset.jsonl` verisinden eğitilmiş TF-IDF + LinearSVC modeli tarafından verilecek
- **FastAPI:** OpenAI uyumlu orchestrator API oluşturulacak
- **Direkt Randevu:** Sadece MHRS'de direkt randevu alınabilen klinikler desteklenir

## 📁 Klasör Yapısı

```
backend/
├── data/                           # 📊 Veri dosyaları
│   ├── clinic_dataset.jsonl        # 🎯 Birleşik dataset (73,800 veri)
│   ├── MHRS_Klinik_Listesi.txt     # 📋 MHRS'den alınan klinik listesi
│   └── clinics/                    # 📁 Kaynak: 41 klinik dosyası
│       ├── Acil_Servis.jsonl       # 1,800 hasta şikayeti
│       ├── Aile_Hekimliği.jsonl    # 1,800 hasta şikayeti
│       ├── Amatem_(Alkol_ve_Madde_Bağımlılığı).jsonl
│       ├── Anesteziyoloji_ve_Reanimasyon.jsonl
│       ├── Bağımlılık.jsonl
│       ├── Beyin_ve_Sinir_Cerrahisi.jsonl
│       ├── Cerrahi_Onkolojisi.jsonl
│       ├── Çocuk_Cerrahisi.jsonl
│       ├── Çocuk_Diş_Hekimliği.jsonl
│       ├── Çocuk_Sağlığı_ve_Hastalıkları.jsonl
│       ├── Çocuk_ve_Ergen_Ruh_Sağlığı_ve_Hastalıkları.jsonl
│       ├── Deri_ve_Zührevi_Hastalıkları_(Cildiye).jsonl
│       ├── Diş_Hekimliği_(Genel_Diş).jsonl
│       ├── Enfeksiyon_Hastalıkları_ve_Klinik_Mikrobiyoloji.jsonl
│       ├── Fiziksel_Tıp_ve_Rehabilitasyon.jsonl
│       ├── Gastroenteroloji_Cerrahisi.jsonl
│       ├── Geleneksel_Tamamlayıcı_Tıp_Ünitesi.jsonl
│       ├── Genel_Cerrahi.jsonl
│       ├── Göğüs_Cerrahisi.jsonl
│       ├── Göğüs_Hastalıkları.jsonl
│       ├── Göz_Hastalıkları.jsonl
│       ├── İç_Hastalıkları_(Dahiliye).jsonl
│       ├── Kadın_Hastalıkları_ve_Doğum.jsonl
│       ├── Kalp_ve_Damar_Cerrahisi.jsonl
│       ├── Kardiyoloji.jsonl
│       ├── Kulak_Burun_Boğaz_Hastalıkları.jsonl
│       ├── Nöroloji.jsonl
│       ├── Ortopedi_ve_Travmatoloji.jsonl
│       ├── Plastik,_Rekonstrüktif_ve_Estetik_Cerrahi.jsonl
│       ├── Radyasyon_Onkolojisi.jsonl
│       ├── Radyoloji.jsonl
│       ├── Ruh_Sağlığı_ve_Hastalıkları_(Psikiyatri).jsonl
│       ├── Sağlık_Kurulu_(Erişkin).jsonl
│       ├── Sağlık_Kurulu_ÇÖZGER.jsonl
│       ├── Sigara_Bırakma_Danışmanlığı_Birimi.jsonl
│       ├── Sigarayı_Bıraktırma_Kliniği.jsonl
│       ├── Spor_Hekimliği.jsonl
│       ├── Sualtı_Hekimliği_ve_Hiperbarik_Tıp.jsonl
│       ├── Tıbbi_Ekoloji_ve_Hidroklimatoloji.jsonl
│       ├── Tıbbi_Genetik.jsonl
│       └── Üroloji.jsonl
├── models/                         # 🤖 Eğitilmiş modeller
│   └── clinic_router_svm.joblib    # SVM modeli (TF-IDF + LinearSVC)
├── configs/                        # ⚙️ Konfigürasyon dosyaları
│   └── litellm_config.yaml         # Ollama konfigürasyonu
├── src/                            # 💻 Kaynak kodlar
│   ├── orchestrator_api.py         # FastAPI uygulaması (OpenAI uyumlu)
│   ├── classify_core.py            # SVM model yükleme ve tahmin
│   ├── llm_client.py               # LiteLLM entegrasyonu
│   ├── train_clinic_model.py       # Model eğitimi
│   └── build_dataset.py            # Dataset oluşturucu
├── simple_api.py                   # 🚀 Geçici Test API (Flutter bağlantısı için)
├── old/                            # 📦 Eski dosyalar (backup)
│   ├── Deneme.py
│   ├── legacy_klinik_dataset.jsonl
│   └── ... (eski versiyonlar)
├── requirements.txt                # 📋 Python bağımlılıkları
└── README.md                       # 📖 Bu dosya
```

## 🚀 Hızlı Başlangıç

### 1. Bağımlılıkları Yükle
```bash
cd backend
pip install -r requirements.txt
```

### 2. Veri Setini Birleştir
```bash
python src/build_dataset.py
```
**Ne yapar:** 41 ayrı klinik dosyasını (`data/clinics/*.jsonl`) tek bir büyük veri seti haline getirir (`clinic_dataset.jsonl`)
- **Girdi:** 41 klinik dosyası (her biri 1,800 şikayet)
- **Çıktı:** Tek birleşik dosya (73,800 şikayet)
- **Amaç:** Model eğitimi için veriyi hazırlamak

### 3. Model Eğit
```bash
python src/train_clinic_model.py
```
**Ne yapar:** Birleştirilmiş veri setini kullanarak SVM modelini eğitir
- **Girdi:** `clinic_dataset.jsonl` (73,800 şikayet)
- **Çıktı:** `models/clinic_router_svm.joblib` (eğitilmiş model)
- **Süreç:** TF-IDF vektörizasyon + LinearSVC sınıflandırma

### 4. Ollama Başlat (ayrı terminal)
```bash
ollama serve
ollama pull llama3:instruct
```

### 5. LiteLLM Başlat (ayrı terminal)
```bash
litellm --config configs/litellm_config.yaml --port 4000
```

### 6. API Başlat
```bash
uvicorn src.orchestrator_api:app --host 0.0.0.0 --port 8001
```

## 📊 Model Performansı

- **Test Doğruluğu:** 99.65%
- **Weighted F1:** 99.65%
- **Macro F1:** 99.65%
- **Toplam Veri:** 73,800 örnek (41 klinik × 1,800 şikayet)
- **Klinik Sayısı:** 41 (tüm MHRS klinikleri)
- **Model Boyutu:** ~3.6MB (TF-IDF + LinearSVC)
- **Tahmin Süresi:** <100ms (ortalama)

## 🔄 Çalışma Mantığı

1. **Kullanıcı:** Şikayet girer
2. **LLM:** Metni normalize eder (yazım/biçim düzeltme)
3. **SVM Model:** Gerçek makine öğrenmesi ile tahmin yapar
4. **Sonuç:** Klinik + açıklama döner

## 🧠 Model Eğitimi Detayları

### Veri Kaynağı
- **Kaynak:** `data/clinics/*.jsonl` dosyaları (41 MHRS kliniği)
- **Format:** `{"id": "...", "complaint": "...", "clinic": "..."}`
- **Toplam:** 73,800 benzersiz hasta şikayeti (41 klinik × 1,800 şikayet)
- **Klinikler:** 41 MHRS kliniği (alfabetik sırada)
- **Veri Kalitesi:** Her klinik için eşit sayıda şikayet (1,800 adet)
- **Dil:** Türkçe hasta şikayetleri (halk dili)

### Algoritma
- **Vektörizasyon:** TF-IDF (ngram 1-2, max_features=100000)
- **Sınıflandırma:** LinearSVC
- **Veri Bölümü:** Stratified split (80% train, 20% test)

### Önemli Kural
**"LLM (Ollama + LiteLLM) yalnızca normalize/embedding/aday üretimi için kullanılacak; nihai klinik kararı SVM modelinden gelecek."**

## 🔧 API Endpoints

### OpenAI Uyumlu Endpoint
```
POST /v1/chat/completions
```

**Request:**
```json
{
  "model": "clinic-recommender",
  "messages": [
    {
      "role": "user",
      "content": "başım çok ağrıyor"
    }
  ]
}
```

**Response:**
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "clinic-recommender",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "🏥 **Klinik Önerisi**\n\n**Önerilen Klinik:** Nöroloji\n**Açıklama:** Şikayetleriniz analiz edildi ve Nöroloji bölümüne yönlendiriliyorsunuz.\n\n**Alternatif Seçenekler:**\n• Aile Hekimliği\n• İç Hastalıkları (Dahiliye)\n\n**Not:** Bu öneri AI sistemi tarafından oluşturulmuştur. Kesin tanı için mutlaka doktor muayenesi gereklidir."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 50,
    "total_tokens": 55
  }
}
```

### Basit Endpoint
```
POST /recommend-clinic
```

**Request:**
```json
{
  "symptoms": "başım çok ağrıyor"
}
```

**Response:**
```json
{
  "recommended_clinic": "Nöroloji",
  "confidence": 0.95,
  "reasoning": "Şikayetleriniz analiz edildi ve Nöroloji bölümüne yönlendiriliyorsunuz.",
  "alternatives": ["Aile Hekimliği", "İç Hastalıkları (Dahiliye)"],
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🛠️ Geliştirme

### Yeni Klinik Ekleme
1. `data/clinics/` klasörüne yeni `.jsonl` dosyası ekle (1,800 şikayet ile)
2. `python src/build_dataset.py` çalıştır (veri setini yeniden birleştir)
3. `python src/train_clinic_model.py` çalıştır (modeli yeniden eğit)
4. API'yi yeniden başlat

### Model Güncelleme
1. `data/clinics/` klasöründeki verileri güncelle
2. `python src/build_dataset.py` çalıştır (veri setini yeniden birleştir)
3. `python src/train_clinic_model.py` çalıştır (modeli yeniden eğit)
4. API'yi yeniden başlat

## 📋 Desteklenen Klinikler (41 Adet)

### 🏥 Acil ve Temel Klinikler
1. **Acil Servis** - Acil durumlar ve kritik vakalar
2. **Aile Hekimliği** - Genel sağlık hizmetleri ve birinci basamak

### 🧠 Nörolojik ve Ruh Sağlığı
3. **Amatem (Alkol ve Madde Bağımlılığı)** - Bağımlılık tedavisi
4. **Anesteziyoloji ve Reanimasyon** - Anestezi ve yoğun bakım
5. **Bağımlılık** - Madde bağımlılığı tedavisi
6. **Beyin ve Sinir Cerrahisi** - Beyin ve omurilik cerrahisi
7. **Nöroloji** - Sinir sistemi hastalıkları
8. **Ruh Sağlığı ve Hastalıkları (Psikiyatri)** - Ruh sağlığı tedavisi

### 🏥 Cerrahi Branşlar
9. **Cerrahi Onkolojisi** - Kanser cerrahisi
10. **Çocuk Cerrahisi** - Çocuklarda cerrahi müdahaleler
11. **Gastroenteroloji Cerrahisi** - Sindirim sistemi cerrahisi
12. **Genel Cerrahi** - Genel cerrahi müdahaleler
13. **Göğüs Cerrahisi** - Göğüs bölgesi cerrahisi
14. **Kalp ve Damar Cerrahisi** - Kalp ve damar cerrahisi
15. **Kulak Burun Boğaz Hastalıkları** - KBB cerrahisi
16. **Ortopedi ve Travmatoloji** - Kemik ve eklem cerrahisi
17. **Plastik, Rekonstrüktif ve Estetik Cerrahi** - Plastik cerrahi
18. **Üroloji** - Ürogenital sistem cerrahisi

### 👶 Çocuk Sağlığı
19. **Çocuk Diş Hekimliği** - Çocuklarda diş tedavisi
20. **Çocuk Sağlığı ve Hastalıkları** - Çocuk hastalıkları
21. **Çocuk ve Ergen Ruh Sağlığı ve Hastalıkları** - Çocuk psikiyatrisi

### 🔬 İç Hastalıkları ve Uzmanlıklar
22. **Deri ve Zührevi Hastalıkları (Cildiye)** - Cilt hastalıkları
23. **Diş Hekimliği (Genel Diş)** - Genel diş tedavisi
24. **Enfeksiyon Hastalıkları ve Klinik Mikrobiyoloji** - Enfeksiyon hastalıkları
25. **Fiziksel Tıp ve Rehabilitasyon** - Fizik tedavi ve rehabilitasyon
26. **Geleneksel Tamamlayıcı Tıp Ünitesi** - Alternatif tıp
27. **Göğüs Hastalıkları** - Akciğer hastalıkları
28. **Göz Hastalıkları** - Göz hastalıkları
29. **İç Hastalıkları (Dahiliye)** - İç organ hastalıkları
30. **Kadın Hastalıkları ve Doğum** - Kadın sağlığı ve doğum
31. **Kardiyoloji** - Kalp hastalıkları

### 🧬 Özel Uzmanlıklar
32. **Radyasyon Onkolojisi** - Radyoterapi
33. **Radyoloji** - Görüntüleme
34. **Sağlık Kurulu (Erişkin)** - Erişkin sağlık kurulu
35. **Sağlık Kurulu ÇÖZGER** - Çocuk sağlık kurulu
36. **Sigara Bırakma Danışmanlığı Birimi** - Sigara bırakma
37. **Sigara Bıraktırma Kliniği** - Sigara bırakma tedavisi
38. **Spor Hekimliği** - Spor yaralanmaları
39. **Sualtı Hekimliği ve Hiperbarik Tıp** - Dalış tıbbı
40. **Tıbbi Ekoloji ve Hidroklimatoloji** - Çevre tıbbı
41. **Tıbbi Genetik** - Genetik hastalıklar

## 🔍 Test Etme

### Basit Test
```bash
curl -X POST "http://localhost:8001/recommend-clinic" \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "başım çok ağrıyor"}'
```

### OpenAI Format Test
```bash
curl -X POST "http://localhost:8001/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "clinic-recommender",
    "messages": [{"role": "user", "content": "göğsümde sıkışma var"}]
  }'
```

## 📁 Dosya Detayları

### 🚀 **simple_api.py** - Geçici Test API
**Konum:** `RANDEVU/backend/simple_api.py`  
**Amaç:** Flutter uygulamasının backend ile bağlantısını test etmek için oluşturulan basit API

**Özellikler:**
- **FastAPI tabanlı** - Hızlı ve basit
- **CORS desteği** - Flutter'dan erişim için
- **2 Ana Endpoint:**
  - `POST /chat` - Flutter chat mesajları için
  - `POST /recommend-clinic` - Klinik önerisi için
- **Kural tabanlı yanıtlar** - Basit if-else mantığı
- **Geçici çözüm** - Asıl model hazır olana kadar

**Kullanım:**
```bash
cd RANDEVU/backend
python3 simple_api.py
# http://localhost:8000 adresinde çalışır
```

**Test:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "başım ağrıyor"}'
```

### 🧠 **classify_core.py** - Ana ML Modeli
**Konum:** `RANDEVU/backend/src/classify_core.py`  
**Amaç:** Eğitilmiş SVM modelini yükleyip klinik tahminleri yapan ana sınıf

**Özellikler:**
- **ClinicClassifier sınıfı** - Ana sınıflandırıcı
- **Model yükleme** - `clinic_router_svm.joblib` dosyasından
- **TF-IDF vektörizasyon** - Metinleri sayısal vektörlere çevirir
- **SVM tahmini** - 41 klinik arasından seçim yapar
- **Güven skoru** - Tahmin güvenilirliği
- **Hata yönetimi** - Model yüklenemezse güvenli çıkış

**Ana Metodlar:**
- `load_model()` - Modeli diskten yükler
- `predict(text)` - Tek metin için tahmin
- `predict_batch(texts)` - Toplu tahmin
- `get_confidence()` - Güven skoru

**Kullanım:**
```python
from classify_core import ClinicClassifier

classifier = ClinicClassifier()
classifier.load_model()
result = classifier.predict("başım ağrıyor")
# Sonuç: {"clinic": "Nöroloji", "confidence": 0.95}
```

### 🏗️ **orchestrator_api.py** - Ana Production API
**Konum:** `RANDEVU/backend/src/orchestrator_api.py`  
**Amaç:** Tam özellikli, production-ready API (LLM + SVM entegrasyonu)

**Özellikler:**
- **OpenAI uyumlu API** - `/v1/chat/completions` endpoint
- **LLM + SVM entegrasyonu** - Metin normalizasyon + ML tahmini
- **Model yükleme** - Startup'ta otomatik model yükleme
- **Hata yönetimi** - Model yüklenemezse uygulama başlamaz
- **CORS desteği** - Flutter entegrasyonu için

**Endpoints:**
- `POST /v1/chat/completions` - OpenAI format
- `POST /recommend-clinic` - Basit format
- `GET /health` - Sistem durumu

### 🎓 **train_clinic_model.py** - Model Eğitimi
**Konum:** `RANDEVU/backend/src/train_clinic_model.py`  
**Amaç:** 73,800 veri ile SVM modelini eğitir

**Özellikler:**
- **TF-IDF vektörizasyon** - N-gram (1,2), max_features=100,000
- **LinearSVC** - Hızlı ve etkili sınıflandırma
- **Stratified split** - %80 train, %20 test
- **Model kaydetme** - `clinic_router_svm.joblib` formatında
- **Performans raporu** - Accuracy, F1-score, classification report

**Kullanım:**
```bash
cd RANDEVU/backend
python3 src/train_clinic_model.py
```

### 📊 **build_dataset.py** - Veri Hazırlama
**Konum:** `RANDEVU/backend/src/build_dataset.py`  
**Amaç:** 41 klinik dosyasını tek dataset'e birleştirir

**Özellikler:**
- **41 klinik dosyası** - `data/clinics/*.jsonl`
- **Veri birleştirme** - Tek `clinic_dataset.jsonl` dosyası
- **Deduplikasyon** - Tekrarları kaldırır
- **Etiket çıkarımı** - Klinik isimlerini `clinic_labels.txt`'ye kaydeder
- **İstatistik raporu** - Toplam kayıt, klinik sayısı

**Kullanım:**
```bash
cd RANDEVU/backend
python3 src/build_dataset.py
```

### 🔄 **Dosya İlişkileri:**
- **`simple_api.py`** → Flutter için hızlı test (geçici)
- **`classify_core.py`** → Asıl ML modeli (SVM)
- **`orchestrator_api.py`** → Tam özellikli API (LLM + SVM)
- **`train_clinic_model.py`** → Model eğitimi
- **`build_dataset.py`** → Veri hazırlama
- **`llm_client.py`** → LLM entegrasyonu (Ollama)

## 📱 Flutter Entegrasyonu

### 🔗 **Bağlantı Detayları:**
- **Backend URL:** `http://localhost:8000` (PC) / `http://10.0.2.2:8000` (Android Emulator)
- **Flutter Service:** `lib/services/llm_service.dart`
- **API Client:** `lib/features/randevu/data/triage_api_client.dart`
- **UI Page:** `lib/features/randevu/presentation/voice_randevu_page.dart`

### 🚀 **Test Durumu:**
- ✅ **Backend çalışıyor** - `simple_api.py` port 8000'de
- ✅ **Flutter bağlantısı** - CORS ayarları yapıldı
- ✅ **API test edildi** - `curl` ile doğrulandı
- ⚠️ **Model entegrasyonu** - `orchestrator_api.py` henüz çalışmıyor

### 📋 **Sonraki Adımlar:**
1. **Model dosyasını düzelt** - `clinic_router_svm.joblib` yolu
2. **Ollama başlat** - LLM normalizasyon için
3. **LiteLLM başlat** - Port 4000'de
4. **Production API'yi test et** - `orchestrator_api.py`
5. **Flutter'da test et** - Gerçek model ile

## 📝 Önemli Notlar

### 🔧 Teknik Detaylar
- **LLM sadece normalizasyon için kullanılır** - Nihai karar vermez
- **Final karar SVM modelinden gelir** - Makine öğrenmesi tabanlı
- **Tüm klinik çıktıları allowed list içindedir** - Güvenlik kontrolü
- **Model assert ile kontrol edilir** - Hata durumlarında güvenli çıkış
- **41 MHRS kliniği desteklenir** - Tüm randevu alınabilen klinikler

### 📊 Veri Yapısı
- **Her klinik için 1,800 şikayet** - Dengeli veri dağılımı
- **Toplam 73,800 örnek** - Kapsamlı eğitim verisi
- **Türkçe halk dili** - Gerçek hasta ifadeleri
- **JSONL format** - Satır bazlı JSON verisi

### 🚀 Performans
- **<100ms tahmin süresi** - Hızlı yanıt
- **99.65% doğruluk** - Yüksek başarı oranı
- **3.6MB model boyutu** - Hafif ve hızlı
- **OpenAI uyumlu API** - Standart entegrasyon

## 🆘 Sorun Giderme

### Model Yüklenmiyor
```bash
# Model dosyasını kontrol et
ls -la models/clinic_router_svm.joblib

# Yeniden eğit
python src/train_clinic_model.py
```

### LLM Bağlantı Hatası
```bash
# Ollama çalışıyor mu?
ollama list

# LiteLLM çalışıyor mu?
curl http://localhost:4000/v1/models
```

### API Başlamıyor
```bash
# Port kullanımda mı?
lsof -i :8001

# Bağımlılıklar yüklü mü?
pip install -r requirements.txt
```

## 📈 Versiyon Geçmişi

### v2.0 (Güncel)
- ✅ **41 klinik desteği** - Tüm MHRS klinikleri eklendi
- ✅ **73,800 veri noktası** - Kapsamlı eğitim verisi
- ✅ **Alfabetik sıralama** - Düzenli klinik listesi
- ✅ **Detaylı açıklamalar** - Her klinik için açıklama
- ✅ **Güncellenmiş README** - Kapsamlı dokümantasyon

### v1.0 (Önceki)
- 33 klinik desteği
- 59,390 veri noktası
- Temel dokümantasyon

---

**TanıAI Klinik Öneri Sistemi - Backend v2.0** 🏥✨

*Son güncelleme: 2024 - 41 MHRS kliniği ile tam destek*