# 🚀 Hızlı Başlangıç - Solunum Yolu Acil Vaka Sistemi

## ⚡ 3 Adımda Başla

### 1️⃣ Demo Çalıştır

```bash
cd "C:\Users\Denem\Music\case\TaniAI-prototype\görüntü işleme"
python quick_respiratory_test.py --demo
```

**Ne Yapar?**
- 5 farklı sentetik test görüntüsü oluşturur
- Her birini analiz eder ve aciliyet skoru verir
- Detaylı rapor oluşturur

### 2️⃣ Kendi X-ray Görüntünü Test Et

```bash
python quick_respiratory_test.py --image "chest_xray.jpg"
```

**Çıktı Örneği:**
```
🚨 ACİLİYET: CRITICAL
📊 Skor: 8.5/10
🔍 Bulgular:
   • Pnömotoraks Şüphesi (%85)
     → ACİL toraks cerrahisi konsültasyonu gerekli
💡 Öneriler:
   Müdahale süresi: 15 dakika
   🚨 ACİL DURUM - Hemen doktora bildir
```

### 3️⃣ API Başlat ve Entegre Et

```bash
python api.py
```

API: `http://localhost:8000/docs`

**Python'dan Kullan:**
```python
import requests
import base64

with open("xray.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

response = requests.post(
    "http://localhost:8000/respiratory/emergency",
    json={"image_data": img_b64},
    headers={"Authorization": "Bearer dev_key_123"}
)

result = response.json()
print(f"Aciliyet: {result['urgency_level']} - {result['urgency_score']}/10")
```

---

## 📁 Oluşturulan Dosyalar

```
görüntü işleme/
├── respiratory_emergency_detector.py    # Ana tespit modülü
├── test_respiratory_emergency.py        # Test ve karşılaştırma
├── quick_respiratory_test.py           # Hızlı test aracı
├── api.py                              # API (endpoint eklendi)
├── RESPIRATORY_EMERGENCY_README.md     # Detaylı dokümantasyon
└── HIZLI_BASLANGIC.md                 # Bu dosya
```

---

## 🎯 Sistem Özellikleri

### ✅ Tespit Edilen Acil Durumlar
- ⛔ **Pnömotoraks** - Akciğer kollapsı
- 🫁 **Şiddetli Pnömoni** - Yaygın enfeksiyon
- 💧 **Pulmoner Ödem** - Akciğerde sıvı birikimi
- 💦 **Plevral Efüzyon** - Plevral boşlukta sıvı

### 🔬 Teknoloji
- **OpenCV** - Görüntü işleme
- **ML Model** - Pnömoni tespiti
- **Otomatik Skorlama** - 1-10 aciliyet skoru
- **REST API** - Kolay entegrasyon

### ⏱️ Aciliyet Seviyeleri
| Skor | Seviye | Müdahale Süresi |
|------|--------|-----------------|
| 8-10 | 🚨 CRITICAL | 15 dakika |
| 6-8  | ⚠️ HIGH | 30 dakika |
| 4-6  | ⚡ MODERATE | 2 saat |
| 1-4  | ✓ LOW | 24 saat |

---

## 💡 Kullanım Senaryoları

### Senaryo 1: Acil Servis Triyajı
```python
from respiratory_emergency_detector import RespiratoryEmergencyDetector

detector = RespiratoryEmergencyDetector()
result = detector.analyze_emergency(image_path="hasta_xray.jpg")

if result['urgency_score'] >= 8:
    print("🚨 ACİL! Hemen doktora bildir")
    # Doktora SMS/bildirim gönder
```

### Senaryo 2: Toplu Görüntü Analizi
```python
# Gün içindeki tüm röntgenleri analiz et
daily_xrays = ["xray1.jpg", "xray2.jpg", "xray3.jpg"]
results = detector.batch_analyze(daily_xrays)
comparison = detector.compare_analyses(results)

print(f"Kritik vakalar: {comparison['critical_cases']}")
```

### Senaryo 3: Karşılaştırmalı Test
```python
from test_respiratory_emergency import RespiratoryEmergencyTester

tester = RespiratoryEmergencyTester()

# Aynı veri seti üzerinde test
test_images = tester.create_synthetic_test_images()
results, comparison = tester.test_batch_images([img['path'] for img in test_images])

# Doğruluk analizi
for img, res in zip(test_images, results):
    print(f"{img['type']}: Beklenen={img['expected_urgency']}, "
          f"Tespit={res['urgency_level']}")
```

---

## 🧪 Test Çıktısı Örneği

```
======================================================================
SOLUNUM YOLU ACİL VAKA TESPİT SİSTEMİ - HIZLI TEST
======================================================================

📸 Sentetik test görüntüleri oluşturuluyor...
✓ 5 test görüntüsü hazırlandı

======================================================================
TEST 1/5: Normal
Beklenen aciliyet: low
======================================================================

✓ ACİLİYET SEVİYESİ: LOW
📊 Aciliyet Skoru: 2.3/10
⏱️  Müdahale Gereksinimi: False

🎯 Tahmin: LOW - ✓ DOĞRU

======================================================================
TEST 2/5: Pnömotoraks
Beklenen aciliyet: critical
======================================================================

🚨 ACİLİYET SEVİYESİ: CRITICAL
📊 Aciliyet Skoru: 8.7/10
⏱️  Müdahale Gereksinimi: True

🔍 TESPİT EDİLEN BULGULAR:
   🔴 Pnömotoraks Şüphesi
      - Güven: %87.0
      - Açıklama: Akciğer kollapsı göstergeleri tespit edildi
      - Aksiyon: ACİL toraks cerrahisi konsültasyonu gerekli

🎯 Tahmin: CRITICAL - ✓ DOĞRU

======================================================================
📊 TOPLU KARŞILAŞTIRMA RAPORU
======================================================================

📊 GENEL İSTATİSTİKLER:
   Toplam görüntü: 5
   Ortalama aciliyet: 5.2/10
   🚨 Kritik vakalar: 1
   ⚠️  Yüksek öncelik: 1

✅ TEST TAMAMLANDI!
======================================================================

📁 Oluşturulan dosyalar:
   • Test görüntüleri: test_images/
   • Detaylı rapor: reports/
```

---

## 🆘 Yardım

**Daha fazla bilgi:**
```bash
python quick_respiratory_test.py --help
```

**Detaylı dokümantasyon:**
- `RESPIRATORY_EMERGENCY_README.md`

**API dokümantasyonu:**
- `http://localhost:8000/docs` (API çalıştıktan sonra)

---

## ⚠️ Önemli Notlar

1. **Tıbbi Sorumluluk**: Bu sistem ön tanı amaçlıdır, kesin tanı için doktor değerlendirmesi gereklidir.

2. **Model Eğitimi**: Mevcut pnömoni modeli varsa kullanılır, yoksa sadece OpenCV analizi yapılır.

3. **Veri Setleri**: Gerçek verilerle test etmek için kendi X-ray görüntülerinizi kullanın.

4. **Performans**: İlk analiz biraz uzun sürebilir (model yükleme), sonrakiler daha hızlıdır.

---

**Başarılar! 🎉**

Sorularınız için: info@taniai.com

