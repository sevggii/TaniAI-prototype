# TANI Modüler Tanı Sistemi - Sistem Açıklaması

## 🎯 Sistemin Amacı

TANI, üst solunum yolu hastalıklarını (COVID-19, grip, soğuk algınlığı, mevsimsel alerji) teşhis etmek için **çok modlu** (multi-modal) bir yapay zeka sistemidir. Sistem, farklı veri türlerini birleştirerek daha doğru tanı koyar.

## 🔧 Nasıl Çalışır?

### 1. **Çok Modlu Yaklaşım**
Sistem 4 farklı veri türünü analiz eder:
- **NLP (Doğal Dil)**: Hastanın belirtilerini analiz eder
- **Görüntü**: Göğüs röntgeni (CXR) görüntülerini inceler
- **Ses**: Öksürük seslerini analiz eder (gelecek)
- **Tabular**: Laboratuvar test sonuçlarını değerlendirir (gelecek)

### 2. **Belirti Skorlama (NLP Modülü)**
```
Hasta belirtileri → Ağırlık matrisi → Olasılık dağılımı
```
- 14 farklı belirti (ateş, öksürük, nefes darlığı, vb.)
- Her belirti için 4 hastalık sınıfında ağırlık (0-3 ölçek)
- CDC/WHO kılavuzlarına dayalı ağırlıklar
- Softmax ile olasılık hesaplama

### 3. **Görüntü Analizi (Vision Modülü)**
```
Göğüs röntgeni → EfficientNetV2B0 → COVID/Normal sınıflandırması
```
- Transfer learning ile eğitilmiş model
- Kaggle COVID-19 veri seti kullanılarak eğitildi
- Otomatik veri bölme (train/validation/test)
- Model kayıt defterinde takip

### 4. **Füzyon (Birleştirme)**
```
NLP olasılıkları (%60) + Görüntü olasılıkları (%40) = Final tanı
```
- Ağırlıklı ortalama ile birleştirme
- Yapılandırılabilir ağırlık oranları
- Her modalite için ayrı olasılık dağılımı

## 📊 Sistem Çıktıları

### API Yanıtı Örneği:
```json
{
  "modality": {
    "nlp": {
      "COVID-19": 0.85,
      "GRIP": 0.10,
      "SOGUK_ALGINLIGI": 0.04,
      "MEVSIMSEL_ALERJI": 0.01
    },
    "vision": {
      "COVID-19": 0.90,
      "GRIP": 0.05,
      "SOGUK_ALGINLIGI": 0.03,
      "MEVSIMSEL_ALERJI": 0.02
    }
  },
  "prob_fused": {
    "COVID-19": 0.87,
    "GRIP": 0.08,
    "SOGUK_ALGINLIGI": 0.04,
    "MEVSIMSEL_ALERJI": 0.01
  }
}
```

## 🏗️ Modüler Mimari

### **Avantajları:**
1. **Genişletilebilir**: Yeni modaliteler kolayca eklenebilir
2. **Bakım Kolaylığı**: Her modül bağımsız çalışır
3. **Test Edilebilir**: Modüller ayrı ayrı test edilebilir
4. **Yeniden Kullanılabilir**: Modüller farklı projelerde kullanılabilir

### **Modül Yapısı:**
```
TANI/
├─ diagnosis_core/          # Ortak konfigürasyon ve model kayıt defteri
└─ UstSolunumYolu/
   ├─ modules/              # Her modalite ayrı modül
   │  ├─ nlp_symptoms/      # Belirti analizi
   │  ├─ vision_cxr_covid/  # Göğüs röntgeni analizi
   │  ├─ audio_cough/       # Ses analizi (gelecek)
   │  └─ tabular_labs/      # Laboratuvar analizi (gelecek)
   └─ services/
      └─ triage_api/        # Birleşik API servisi
```

## 🚀 Kullanım Senaryoları

### 1. **Hastane Acil Servisi**
- Hızlı triage (önceliklendirme)
- COVID-19 şüphesi olan hastaları belirleme
- Kaynak optimizasyonu

### 2. **Telemedicine (Uzaktan Tıp)**
- Evde hasta değerlendirmesi
- Görüntü + belirti kombinasyonu
- Uzman doktor yönlendirmesi

### 3. **Toplum Sağlığı**
- Salgın takibi
- Risk değerlendirmesi
- Erken uyarı sistemi

## 📈 Performans ve Doğruluk

### **NLP Modülü:**
- Kural tabanlı (eğitim gerektirmez)
- CDC/WHO kılavuzlarına dayalı
- Hızlı yanıt süresi

### **Vision Modülü:**
- EfficientNetV2B0 (state-of-the-art)
- Transfer learning ile optimize
- Yüksek doğruluk oranı

### **Füzyon:**
- Çok modlu avantajı
- Daha güvenilir tanı
- Belirsizlik azaltma

## 🔮 Gelecek Geliştirmeler

1. **Ses Modülü**: Öksürük analizi ile daha zengin veri
2. **Tabular Modülü**: Laboratuvar sonuçları ile tam tanı
3. **Gerçek Zamanlı**: Canlı veri akışı
4. **Mobil Uygulama**: Hasta tarafında kullanım
5. **Uzman Sistemi**: Doktor onayı ile öğrenme

## 💡 Teknik Detaylar

### **Teknolojiler:**
- **Backend**: FastAPI (Python)
- **ML**: TensorFlow/Keras
- **Görüntü**: EfficientNetV2B0
- **NLP**: Kural tabanlı skorlama
- **Veri**: Kaggle COVID-19 Radiography Database

### **Güvenlik:**
- HIPAA uyumlu veri işleme
- Model kayıt defteri ile takip
- Güvenli API endpoint'leri

Bu sistem, modern tıp teknolojilerini kullanarak daha hızlı, doğru ve erişilebilir tanı hizmeti sunmayı amaçlar.
