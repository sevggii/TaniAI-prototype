# 🚨 Solunum Yolu Acil Vaka Tespit Sistemi

## 📋 İçindekiler

- [Genel Bakış](#genel-bakış)
- [Hızlı Başlangıç](#hızlı-başlangıç)
- [Kullanım](#kullanım)
- [API Entegrasyonu](#api-entegrasyonu)
- [Özellikler](#özellikler)
- [Test ve Karşılaştırma](#test-ve-karşılaştırma)

---

## 🎯 Genel Bakış

Bu sistem, göğüs röntgeni (X-ray) görüntülerinden **solunum yolu acil vakalarını** otomatik olarak tespit eder ve doktora aciliyet skoruyla birlikte bildirir.

### Tespit Edilen Acil Durumlar

| Acil Durum | Aciliyet Seviyesi | Müdahale Süresi |
|------------|-------------------|-----------------|
| **Pnömotoraks** | 🚨 CRITICAL | 15 dakika |
| **Şiddetli Pnömoni** | ⚠️ HIGH | 30 dakika |
| **Pulmoner Ödem** | ⚠️ HIGH | 30 dakika |
| **Plevral Efüzyon** | ⚡ MODERATE | 2 saat |

### Teknolojiler

- **OpenCV**: Görüntü işleme ve özellik çıkarımı
- **Machine Learning**: Pnömoni tespit modeli
- **FastAPI**: REST API servisi
- **NumPy/PIL**: Görüntü manipülasyonu

---

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler

```bash
cd "C:\Users\Denem\Music\case\TaniAI-prototype\görüntü işleme"
pip install -r requirements.txt
```

### 2. Hızlı Demo (Sentetik Görüntülerle)

```bash
python quick_respiratory_test.py --demo
```

Bu komut:
✓ 5 sentetik test görüntüsü oluşturur (normal, hafif pnömoni, şiddetli pnömoni, pnömotoraks, efüzyon)  
✓ Her birini analiz eder  
✓ Sonuçları ekrana yazdırır  
✓ Detaylı rapor oluşturur (`reports/` klasöründe)

### 3. Kendi Görüntünüzü Test Edin

```bash
python quick_respiratory_test.py --image "yol/chest_xray.jpg"
```

---

## 💻 Kullanım

### Kod İçinden Kullanım

```python
from respiratory_emergency_detector import RespiratoryEmergencyDetector

# Detector oluştur
detector = RespiratoryEmergencyDetector()

# Tek görüntü analizi
result = detector.analyze_emergency(image_path="chest_xray.jpg")

# Sonuçları kontrol et
print(f"Aciliyet Skoru: {result['urgency_score']:.1f}/10")
print(f"Aciliyet Seviyesi: {result['urgency_level']}")
print(f"Acil Müdahale Gerekli: {result['requires_immediate_attention']}")

# Bulgular
for finding in result['findings']:
    print(f"- {finding['name']}: %{finding['confidence']:.0f}")
    print(f"  Aksiyon: {finding['action']}")

# Öneriler
for rec in result['recommendations']:
    print(f"• {rec}")
```

### Çoklu Görüntü Analizi ve Karşılaştırma

```python
# Birden fazla görüntü
image_paths = [
    "hasta1_xray.jpg",
    "hasta2_xray.jpg",
    "hasta3_xray.jpg"
]

# Batch analiz
results = detector.batch_analyze(image_paths)

# Karşılaştırma
comparison = detector.compare_analyses(results)

print(f"Toplam: {comparison['total_images']}")
print(f"Kritik vakalar: {comparison['critical_cases']}")
print(f"Ortalama aciliyet: {comparison['average_urgency']:.1f}/10")
```

### Base64 Encoded Görüntü ile

```python
import base64

# Görüntüyü base64'e çevir
with open("chest_xray.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

# Analiz
result = detector.analyze_emergency(image_base64=image_b64)
```

---

## 🌐 API Entegrasyonu

### API Başlatma

```bash
cd "C:\Users\Denem\Music\case\TaniAI-prototype\görüntü işleme"
python api.py
```

API şurada çalışacak: `http://localhost:8000`

Dokümantasyon: `http://localhost:8000/docs`

### API Endpoint'leri

#### 1. Tek Görüntü Analizi

**POST** `/respiratory/emergency`

```python
import requests
import base64

# Görüntüyü hazırla
with open("chest_xray.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# İstek
response = requests.post(
    "http://localhost:8000/respiratory/emergency",
    json={
        "image_data": image_data,
        "patient_age": 45,
        "patient_gender": "male",
        "symptoms": ["dyspnea", "chest_pain"]
    },
    headers={"Authorization": "Bearer dev_key_123"}
)

result = response.json()
print(f"Aciliyet: {result['urgency_level']}")
print(f"Skor: {result['urgency_score']}/10")
```

#### 2. Toplu Analiz

**POST** `/respiratory/emergency/batch`

```python
# Birden fazla görüntü
images_b64 = [image1_b64, image2_b64, image3_b64]

response = requests.post(
    "http://localhost:8000/respiratory/emergency/batch",
    json={"images": images_b64},
    headers={"Authorization": "Bearer dev_key_123"}
)

result = response.json()
print(f"Kritik vakalar: {result['comparison']['critical_cases']}")
```

#### 3. Sistem Durumu

**GET** `/respiratory/emergency/health`

```python
response = requests.get("http://localhost:8000/respiratory/emergency/health")
status = response.json()
print(f"Durum: {status['status']}")
print(f"Model yüklü: {status['model_loaded']}")
```

#### 4. İstatistikler

**GET** `/respiratory/emergency/stats`

```python
response = requests.get(
    "http://localhost:8000/respiratory/emergency/stats",
    headers={"Authorization": "Bearer dev_key_123"}
)
stats = response.json()
```

---

## ✨ Özellikler

### 1. Aciliyet Skorlama (1-10)

Sistem, birden fazla faktörü değerlendirerek 1-10 arası aciliyet skoru hesaplar:

- **Pnömotoraks riski** (ağırlık: 4.0)
- **Şiddetli pnömoni** (ağırlık: 2.5)
- **Pulmoner ödem** (ağırlık: 3.0)
- **Plevral efüzyon** (ağırlık: 2.0)

### 2. OpenCV ile Görüntü Analizi

#### Akciğer Bölgesi Tespiti
- Otomatik akciğer segmentasyonu
- Sağ ve sol akciğer ayrımı

#### Opacity (Mat Alan) Analizi
- Pnömoni göstergesi
- Yüzde hesaplama

#### Pnömotoraks Göstergeleri
- Kollaps çizgisi tespiti (Canny edge detection)
- Serbest hava alanları
- Akciğer asimetrisi

#### Plevral Efüzyon Tespiti
- Alt akciğer bölgesi yoğunluk analizi
- Gradient hesaplama

#### Texture Analizi
- Gabor filtreleri
- Pulmoner ödem tespiti

### 3. Görselleştirme

Sistem, analiz sonuçlarını görsel olarak işaretler:

- Mat alanları (opacity) kırmızı renkle vurgular
- Bulgular için renk kodlu metin ekler
- Base64 olarak döndürür

### 4. Detaylı Raporlama

Her analiz şunları içerir:

```json
{
  "urgency_score": 7.5,
  "urgency_level": "high",
  "requires_immediate_attention": true,
  "emergency_scores": {
    "pneumothorax": 0.85,
    "severe_pneumonia": 0.45,
    "pulmonary_edema": 0.30,
    "pleural_effusion": 0.20
  },
  "findings": [
    {
      "name": "Pnömotoraks Şüphesi",
      "severity": "CRITICAL",
      "confidence": 85.0,
      "description": "Akciğer kollapsı göstergeleri tespit edildi",
      "action": "ACİL toraks cerrahisi konsültasyonu gerekli"
    }
  ],
  "recommendations": [
    "Müdahale süresi: 15 dakika",
    "🚨 ACİL DURUM - Hemen doktora bildir",
    "Hasta vital bulgularını monitörize et"
  ],
  "features": {
    "opacity_percentage": 35.5,
    "lung_asymmetry": 0.42,
    "density_mean": 125.3,
    "texture_variance": 18.7
  }
}
```

---

## 🧪 Test ve Karşılaştırma

### İnteraktif Test Aracı

```bash
python test_respiratory_emergency.py
```

Menü seçenekleri:
1. Sentetik test görüntüleri oluştur ve test et
2. Kendi görüntülerini test et
3. Çıkış

### Toplu Test ve Karşılaştırma

```python
from test_respiratory_emergency import RespiratoryEmergencyTester

tester = RespiratoryEmergencyTester()

# Test görüntüleri oluştur
test_images = tester.create_synthetic_test_images()

# Tümünü test et
image_paths = [img['path'] for img in test_images]
results, comparison = tester.test_batch_images(image_paths)

# Sonuçlar otomatik kaydedilir: reports/respiratory_emergency_report_*.json
```

### Ground Truth ile Karşılaştırma

Kendi veri setinizle doğruluk testi:

```python
test_data = [
    {
        'image_path': 'pneumothorax_case1.jpg',
        'ground_truth': {
            'urgency_level': 'critical'
        }
    },
    {
        'image_path': 'normal_case1.jpg',
        'ground_truth': {
            'urgency_level': 'low'
        }
    }
]

accuracy_report = tester.compare_with_ground_truth(test_data)
print(f"Doğruluk: {accuracy_report['accuracy']:.1f}%")
```

### Sentetik Test Görüntüleri

Sistem otomatik olarak şu test görüntülerini oluşturabilir:

1. **Normal Akciğer** (beklenen: low)
2. **Hafif Pnömoni** (beklenen: moderate)
3. **Şiddetli Pnömoni** (beklenen: high)
4. **Pnömotoraks** (beklenen: critical)
5. **Plevral Efüzyon** (beklenen: moderate)

---

## 📊 Performans ve Optimizasyon

### İşlem Süreleri

- Tek görüntü analizi: ~2-5 saniye
- Toplu analiz (10 görüntü): ~15-30 saniye

### Eşik Değerler (Özelleştirilebilir)

```python
detector.emergency_thresholds = {
    'pneumothorax_score': 0.7,
    'severe_pneumonia_score': 0.75,
    'pulmonary_edema_score': 0.65,
    'pleural_effusion_score': 0.6,
    'opacity_percentage': 40.0,
    'asymmetry_score': 0.5,
}
```

---

## 🔧 Sorun Giderme

### Model bulunamadı hatası

```bash
# Model dosyasını kontrol edin
ls models/pneumonia_trained_model.pkl
```

Yoksa, sistem sadece OpenCV analizi kullanır (yine de çalışır).

### Görüntü kalitesi uyarısı

Minimum gereksinimler:
- Çözünürlük: 256x256 piksel
- Format: JPG, PNG, DICOM
- Grayscale X-ray görüntüsü

### API bağlantı hatası

```bash
# API'nin çalıştığını kontrol edin
curl http://localhost:8000/respiratory/emergency/health
```

---

## 📝 Kullanım Senaryoları

### 1. Acil Servis Triyajı

```python
# Hasta geldiğinde hemen X-ray analizi
result = detector.analyze_emergency(image_path="hasta_xray.jpg")

if result['urgency_level'] == 'critical':
    # Acil ekibi uyar
    notify_emergency_team(result)
elif result['urgency_level'] == 'high':
    # Doktoru hızlıca bilgilendir
    notify_doctor(result, priority='high')
```

### 2. Radyoloji Önceliklendirme

```python
# Gün içinde çekilen tüm röntgenleri analiz et
daily_xrays = get_daily_xrays()
results = detector.batch_analyze(daily_xrays)

# Acil vakaları en üste çıkar
critical_cases = [r for r in results if r['urgency_level'] == 'critical']
high_priority = [r for r in results if r['urgency_level'] == 'high']

# Radyologa öncelik sırasına göre sun
prioritized_list = critical_cases + high_priority + ...
```

### 3. İkinci Görüş Sistemi

```python
# Radyolog yorumuna ek olarak AI analizi
ai_result = detector.analyze_emergency(image_path=xray_path)
radiologist_report = get_radiologist_report(xray_id)

# Karşılaştır
if ai_result['urgency_level'] == 'critical' and 
   radiologist_report['urgency'] != 'critical':
    # Uyarı: AI kritik bulgu tespit etti, çift kontrol öner
    suggest_second_review()
```

---

## 🎓 Önemli Notlar

### ⚠️ Tıbbi Sorumluluk Reddi

Bu sistem **ön tanı amaçlıdır** ve doktor değerlendirmesinin yerini tutmaz:

- ✓ Radyologlara yardımcı araç olarak kullanılabilir
- ✓ Acil vakaların hızlı tespitini destekler
- ✗ Kesin tanı için kullanılmamalıdır
- ✗ Tek başına tedavi kararı vermek için yeterli değildir

**Acil durumlarda derhal tıbbi yardım alın!**

### 🔬 Geliştirme Notları

Sistemi geliştirmek için:

1. **Gerçek veri seti kullanın**: TCIA, NIH Chest X-ray gibi
2. **Modeli eğitin**: `models/pneumonia_trained_model.pkl` dosyasını güncelleyin
3. **Eşik değerleri kalibre edin**: Hastane verinize göre ayarlayın
4. **Validation yapın**: Ground truth ile karşılaştırın

---

## 📞 Destek

Sorularınız için:
- GitHub Issues
- E-posta: info@taniai.com
- Dokümantasyon: `docs/`

---

## 📄 Lisans

MIT License - Detaylar için `LICENSE.md` dosyasına bakın.

---

**Son Güncelleme**: 2024  
**Versiyon**: 1.0.0

