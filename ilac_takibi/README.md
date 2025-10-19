# 💊 Profesyonel İlaç Takip Sistemi

Gerçek uygulama için güvenli, kapsamlı ve profesyonel ilaç takip sistemi. Bu sistem hastaların güvenliği için kritik güvenlik kontrolleri, yan etki takibi, ilaç etkileşimleri ve akıllı hatırlatmalar içerir.

## 🚀 Özellikler

### ✅ Temel İlaç Yönetimi
- **İlaç CRUD İşlemleri**: Güvenli ilaç ekleme, güncelleme, silme
- **Dozaj Yönetimi**: Esnek dozaj birimleri ve sıklık ayarları
- **Reçete Takibi**: Doktor, eczane ve reçete bilgileri
- **Durum Yönetimi**: Aktif, duraklatılmış, tamamlanmış, durdurulmuş

### 🔒 Güvenlik ve Validasyon
- **Kritik İlaç Kontrolü**: Yüksek riskli ilaçlar için özel uyarılar
- **Doz Limitleri**: Günlük maksimum/minimum doz kontrolleri
- **İlaç Etkileşimleri**: Otomatik etkileşim tespiti ve uyarıları
- **Aşırı Doz Koruması**: 24 saatlik doz takibi ve uyarıları
- **Son Kullanma Tarihi**: Otomatik son kullanma uyarıları

### 📊 Takip ve Raporlama
- **Kullanım Kayıtları**: Detaylı ilaç kullanım geçmişi
- **Uyum Raporları**: İlaç uyum oranları ve istatistikleri
- **Yan Etki Takibi**: Yan etki kayıtları ve şiddet seviyeleri
- **Atlanan Dozlar**: Atlanan doz takibi ve uyarıları

### 🔔 Akıllı Hatırlatmalar
- **Zamanlanmış Hatırlatmalar**: Özelleştirilebilir hatırlatma saatleri
- **Yenileme Uyarıları**: İlaç bitme öncesi uyarılar
- **Kritik Uyarılar**: Acil durum bildirimleri
- **Çoklu Platform**: Mobil, web ve SMS bildirimleri

## 📁 Dosya Yapısı

```
ilaç takibi/
├── models.py              # Veritabanı modelleri
├── schemas.py             # Pydantic şemaları
├── medication_service.py  # Ana servis katmanı
├── api.py                 # FastAPI endpointleri
├── safety_validations.py  # Güvenlik validasyonları
└── README.md             # Bu dosya
```

## 🛠️ Kurulum

### 1. Gereksinimler
```bash
pip install fastapi sqlalchemy pydantic python-multipart
```

### 2. Veritabanı Kurulumu
```python
from sqlalchemy import create_engine
from ilaç_takibi.models import Base

# Veritabanı bağlantısı
engine = create_engine("sqlite:///medication_tracking.db")
Base.metadata.create_all(bind=engine)
```

### 3. FastAPI Entegrasyonu
```python
from fastapi import FastAPI
from ilaç_takibi.api import router as medication_router

app = FastAPI()
app.include_router(medication_router)
```

## 📚 API Kullanımı

### İlaç Ekleme
```python
import requests

# Yeni ilaç ekleme
medication_data = {
    "medication_name": "Metformin",
    "dosage_amount": 500,
    "dosage_unit": "mg",
    "frequency_type": "twice_daily",
    "reminder_times": ["08:00", "20:00"],
    "start_date": "2024-01-01T00:00:00",
    "prescribing_doctor": "Dr. Ahmet Yılmaz",
    "pharmacy_name": "Merkez Eczanesi",
    "indication": "Tip 2 diyabet",
    "max_daily_dose": 2000,
    "requires_food": True
}

response = requests.post(
    "http://localhost:8000/medications/",
    json=medication_data,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

### İlaç Kullanımı Kaydetme
```python
# İlacı alındı olarak kaydetme
log_data = {
    "medication_id": 1,
    "taken_at": "2024-01-15T08:30:00",
    "dosage_taken": 500,
    "dosage_unit": "mg",
    "was_taken": True,
    "notes": "Kahvaltıdan sonra alındı"
}

response = requests.post(
    "http://localhost:8000/medications/logs",
    json=log_data,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

### Hızlı İlaç Alma
```python
# İlacı şimdi al olarak kaydetme
response = requests.post(
    "http://localhost:8000/medications/1/take",
    params={"dosage_taken": 500, "notes": "Hızlı alım"},
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

### Yan Etki Kaydetme
```python
# Yan etki kaydı
side_effect_data = {
    "medication_id": 1,
    "side_effect_name": "Mide bulantısı",
    "description": "Hafif mide bulantısı",
    "severity": "mild",
    "started_at": "2024-01-15T10:00:00",
    "intensity": 3,
    "requires_medical_attention": False
}

response = requests.post(
    "http://localhost:8000/medications/side-effects",
    json=side_effect_data,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

## 🔒 Güvenlik Özellikleri

### Kritik İlaç Listesi
Sistem aşağıdaki kritik ilaçları otomatik olarak tanır ve özel uyarılar verir:
- Warfarin, Digoxin, Lithium
- Methotrexate, Cyclosporine
- Insulin, Heparin, Clopidogrel

### Doz Limitleri
```python
# Maksimum günlük dozlar (mg)
MAX_DAILY_DOSES = {
    "ACETAMINOPHEN": 4000,
    "IBUPROFEN": 2400,
    "ASPIRIN": 4000,
    "METHOTREXATE": 25,
    "LITHIUM": 2400,
    "DIGOXIN": 0.5
}
```

### İlaç Etkileşimleri
```python
# Yüksek riskli etkileşimler
HIGH_RISK_INTERACTIONS = {
    ("WARFARIN", "ASPIRIN"): "Kanama riski",
    ("DIGOXIN", "FUROSEMIDE"): "Digoksin toksisitesi",
    ("LITHIUM", "FUROSEMIDE"): "Lityum toksisitesi"
}
```

## 📊 Raporlama

### İlaç Özeti
```python
# Kullanıcının ilaç özeti
response = requests.get(
    "http://localhost:8000/medications/summary",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

# Yanıt:
{
    "total_medications": 5,
    "active_medications": 4,
    "medications_due_today": 3,
    "missed_doses_today": 1,
    "upcoming_refills": 2,
    "active_side_effects": 1,
    "critical_interactions": 0
}
```

### Uyum Raporu
```python
# 30 günlük uyum raporu
response = requests.get(
    "http://localhost:8000/medications/1/compliance?days=30",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

# Yanıt:
{
    "medication_id": 1,
    "medication_name": "Metformin",
    "compliance_rate": 85.5,
    "total_doses": 60,
    "taken_doses": 51,
    "missed_doses": 6,
    "delayed_doses": 3,
    "period_start": "2024-01-01T00:00:00",
    "period_end": "2024-01-31T23:59:59"
}
```

## 🚨 Uyarı Sistemi

### Uyarı Türleri
- **Kritik**: Acil tıbbi müdahale gerektiren durumlar
- **Yüksek**: Doktor kontrolü önerilen durumlar
- **Orta**: Dikkat edilmesi gereken durumlar
- **Hafif**: Bilgilendirme amaçlı uyarılar

### Uyarı Örnekleri
```python
# Uyarıları getirme
response = requests.get(
    "http://localhost:8000/medications/alerts",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

# Örnek uyarılar:
[
    {
        "alert_type": "overdose",
        "severity": "critical",
        "title": "Maksimum Günlük Doz Aşıldı",
        "message": "Metformin için günlük maksimum doz aşıldı",
        "requires_action": true
    },
    {
        "alert_type": "interaction",
        "severity": "severe",
        "title": "İlaç Etkileşimi Uyarısı",
        "message": "Warfarin ve Aspirin arasında kanama riski",
        "requires_action": true
    }
]
```

## 🔧 Özelleştirme

### Yeni İlaç Türü Ekleme
```python
# DosageUnit enum'una yeni birim ekleme
class DosageUnit(str, Enum):
    # ... mevcut birimler
    PATCH = "patch"  # Yeni birim
```

### Yeni Etkileşim Ekleme
```python
# safety_validations.py dosyasında
self.high_risk_interactions = {
    # ... mevcut etkileşimler
    ("YENİ_İLAÇ", "MEVCUT_İLAÇ"): "Etkileşim açıklaması"
}
```

## 📱 Mobil Entegrasyon

### Flutter/Dart Örneği
```dart
// İlaç listesi getirme
Future<List<Medication>> getMedications() async {
  final response = await http.get(
    Uri.parse('$baseUrl/medications/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  
  if (response.statusCode == 200) {
    final List<dynamic> data = json.decode(response.body);
    return data.map((json) => Medication.fromJson(json)).toList();
  }
  throw Exception('İlaçlar yüklenemedi');
}

// İlaç alma
Future<void> takeMedication(int medicationId, double dosage) async {
  await http.post(
    Uri.parse('$baseUrl/medications/$medicationId/take'),
    headers: {'Authorization': 'Bearer $token'},
    body: json.encode({
      'dosage_taken': dosage,
      'notes': 'Mobil uygulamadan alındı'
    }),
  );
}
```

## 🧪 Test

### Unit Test Örneği
```python
import pytest
from ilaç_takibi.medication_service import MedicationService
from ilaç_takibi.schemas import MedicationCreate

@pytest.mark.asyncio
async def test_create_medication():
    service = MedicationService(db_session)
    
    medication_data = MedicationCreate(
        medication_name="Test İlaç",
        dosage_amount=100,
        dosage_unit="mg",
        frequency_type="daily",
        reminder_times=["08:00"]
    )
    
    result = await service.create_medication(1, medication_data)
    assert result.medication_name == "Test İlaç"
    assert result.dosage_amount == 100
```

## 🚀 Performans

### Optimizasyon İpuçları
1. **Veritabanı İndeksleri**: Sık kullanılan alanlar için indeks oluşturun
2. **Sayfalama**: Büyük veri setleri için sayfalama kullanın
3. **Önbellekleme**: Redis ile sık kullanılan verileri önbelleğe alın
4. **Background Tasks**: Ağır işlemleri arka planda çalıştırın

### Önerilen İndeksler
```sql
CREATE INDEX idx_medication_user_active ON medications(user_id, is_active);
CREATE INDEX idx_medication_log_user_date ON medication_logs(user_id, taken_at);
CREATE INDEX idx_side_effect_user_medication ON side_effects(user_id, medication_id);
```

## 🔐 Güvenlik

### Veri Koruması
- Tüm API endpointleri JWT token ile korunur
- Hassas veriler şifrelenir
- KVKK/GDPR uyumlu veri işleme
- Audit log tutma

### Güvenlik Kontrolleri
- Rate limiting
- Input validation
- SQL injection koruması
- XSS koruması

## 📞 Destek

### Hata Raporlama
Hata durumunda lütfen şu bilgileri sağlayın:
- Hata mesajı
- API endpoint
- Request payload
- Kullanıcı ID (gizli tutulacak)

### Geliştirici İletişimi
- GitHub Issues
- Email: dev@taniai.com
- Dokümantasyon: docs.taniai.com

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için LICENSE dosyasına bakın.

---

**⚠️ ÖNEMLİ UYARI**: Bu sistem tıbbi tavsiye vermez. Tüm sonuçlar doktor kontrolü ile doğrulanmalıdır. Acil durumlarda derhal tıbbi yardım alın.
