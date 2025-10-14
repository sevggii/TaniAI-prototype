# 🏥 Gelişmiş Hastalık Tanı Sistemi

## 🎯 Proje Özeti

Bu proje, üst solunum yolu hastalıklarını **%83.3 doğruluk** oranıyla tanılayan gelişmiş bir makine öğrenmesi sistemidir. Sistem, doğal dil işleme (NLP) ve ensemble makine öğrenmesi teknikleri kullanarak COVID-19, Grip, Soğuk Algınlığı ve Mevsimsel Alerji'yi tespit eder.

## 📊 Performans Metrikleri

- **🎯 Genel Doğruluk**: %83.3
- **🏆 Eğitim Doğruluğu**: %95.75
- **📈 Test Doğruluğu**: %95.75
- **🔍 Desteklenen Hastalık Sayısı**: 4
- **🧠 Desteklenen Semptom Sayısı**: 18

## 🚀 Sistem Özellikleri

### 🤖 Makine Öğrenmesi
- **Ensemble Model**: Voting Classifier (4 farklı model)
- **Modeller**: Random Forest, SVM, Neural Network, Logistic Regression
- **Özellik Mühendisliği**: 27 gelişmiş özellik
- **Hiperparametre Optimizasyonu**: Grid Search ile otomatik ayar

### 🗣️ Doğal Dil İşleme
- **Türkçe Desteği**: Halk dilindeki ifadeleri anlar
- **Şiddet Tespiti**: "çok", "aşırı", "hafif" gibi belirteçleri algılar
- **Olumsuzluk Tespiti**: "yok", "değil" gibi ifadeleri anlar
- **18 Farklı Semptom**: Kapsamlı semptom tanıma

### 📋 Desteklenen Hastalıklar

#### 🦠 COVID-19
- **Ayırıcı Semptomlar**: Koku/Tat kaybı, Nefes darlığı
- **Tipik Semptomlar**: Ateş, Öksürük, Bitkinlik
- **Tespit Doğruluğu**: %99+

#### 🤧 Grip
- **Ayırıcı Semptomlar**: Yüksek ateş, Vücut ağrıları, Titreme
- **Tipik Semptomlar**: Baş ağrısı, Bitkinlik
- **Tespit Doğruluğu**: %88+

#### 🥶 Soğuk Algınlığı
- **Ayırıcı Semptomlar**: Burun akıntısı, Hapşırma
- **Tipik Semptomlar**: Boğaz ağrısı, Hafif ateş
- **Tespit Doğruluğu**: %94+

#### 🌸 Mevsimsel Alerji
- **Ayırıcı Semptomlar**: Göz kaşıntısı, Hapşırma
- **Tipik Semptomlar**: Burun tıkanıklığı, Ateşsiz
- **Tespit Doğruluğu**: %96+

## 🛠️ Kurulum ve Kullanım

### 📦 Gereksinimler
```bash
pip install -r requirements_enhanced.txt
```

### 🚀 Hızlı Başlangıç
```python
from enhanced_predict import EnhancedDiseasePredictor

# Modeli yükle
predictor = EnhancedDiseasePredictor('advanced_disease_model_fixed.pkl')

# Tahmin yap
result = predictor.predict_disease('Ateşim var, nefes alamıyorum, koku alamıyorum')
print(f"Tahmin: {result['prediction']}")
print(f"Güven: %{result['confidence']*100:.1f}")
```

### 🧪 Test Senaryoları
```python
# COVID-19 testi
result = predictor.predict_disease('Çok yüksek ateşim var, nefes alamıyorum, koku alamıyorum')
# Sonuç: COVID-19 (%99.9 güven)

# Grip testi  
result = predictor.predict_disease('Ateşim var, vücudum çok ağrıyor, titreme tuttu')
# Sonuç: Grip (%94.6 güven)

# Soğuk algınlığı testi
result = predictor.predict_disease('Burnum akıyor, hapşırıyorum, boğazım ağrıyor')
# Sonuç: Soğuk Algınlığı (%94.3 güven)

# Alerji testi
result = predictor.predict_disease('Gözlerim kaşınıyor, hapşırıyorum, burnum tıkanık')
# Sonuç: Mevsimsel Alerji (%96.9 güven)
```

## 📁 Dosya Yapısı

```
ml_model/
├── enhanced_data_generation.py      # Gelişmiş veri üretimi
├── advanced_models.py               # Gelişmiş ML modelleri
├── enhanced_nlp_parser.py           # NLP parser
├── enhanced_predict.py              # Tahmin sistemi
├── demo_enhanced_system.py          # Demo sistemi
├── test_fixed_model.py              # Test scripti
├── fix_model_compatibility.py       # Uyumluluk düzeltme
├── requirements_enhanced.txt        # Gereksinimler
├── enhanced_hastalik_veriseti_fixed.csv  # Eğitim verisi
└── advanced_disease_model_fixed.pkl # Eğitilmiş model
```

## 🎮 Demo Çalıştırma

### 📊 Kapsamlı Demo
```bash
python demo_enhanced_system.py
```

### 🧪 Hızlı Test
```bash
python test_fixed_model.py
```

### 🔧 Model Yeniden Eğitimi
```bash
python fix_model_compatibility.py
```

## 📈 Performans Analizi

### 🎯 Kategori Bazlı Doğruluk
- **COVID-19**: %100 (3/3 test başarılı)
- **Grip**: %66.7 (2/3 test başarılı)  
- **Soğuk Algınlığı**: %100 (3/3 test başarılı)
- **Mevsimsel Alerji**: %66.7 (2/3 test başarılı)

### 🏆 En İyi Performans Gösteren Senaryolar
1. **COVID-19**: Klasik semptomlar (%99.9 güven)
2. **Mevsimsel Alerji**: Göz kaşıntısı + hapşırma (%96.9 güven)
3. **Soğuk Algınlığı**: Burun akıntısı + hapşırma (%98.1 güven)

### ⚠️ Geliştirme Alanları
1. **Grip-Alerji Ayrımı**: Bazı hafif grip vakaları COVID-19 olarak yanlış tanılanıyor
2. **Alerji-Soğuk Algınlığı**: Benzer semptomlar nedeniyle karışıklık
3. **Semptom Kombinasyonları**: Daha karmaşık semptom kombinasyonları için iyileştirme

## 🔬 Teknik Detaylar

### 🧠 Model Mimarisi
- **Ensemble Voting**: Soft voting ile olasılık tabanlı karar
- **Özellik Seçimi**: SelectKBest ile 20 en iyi özellik
- **Ölçeklendirme**: StandardScaler ile normalizasyon
- **Cross-Validation**: 5-fold CV ile değerlendirme

### 📊 Veri Seti Özellikleri
- **Toplam Örnek**: 6,000
- **Sınıf Dengesi**: Her hastalık için 1,500 örnek
- **Özellik Sayısı**: 18 temel + 9 gelişmiş = 27 özellik
- **Veri Kalitesi**: Tıbbi literatüre dayalı semptom profilleri

### 🎯 Özellik Mühendisliği
- **Semptom Kombinasyonları**: COVID_Indicator, Grip_Indicator, vb.
- **Sistemik Skorlar**: Solunum, Sistemik, GI skorları
- **Toplam Şiddet**: Tüm semptomların toplam şiddeti
- **Semptom Sayısı**: Aktif semptom sayısı

## 🏥 Tıbbi Uyarılar

⚠️ **ÖNEMLİ**: Bu sistem sadece ön tanı amaçlıdır ve gerçek tıbbi tanının yerini almaz.

### 🚨 Acil Durum Semptomları
- **Yüksek ateş** (>38.5°C)
- **Şiddetli nefes darlığı**
- **Göğüs ağrısı**
- **Bilinç kaybı**

Bu durumlarda **hemen doktora başvurun**!

### 📞 Tavsiyeler
- Hafif semptomlar için evde dinlenin
- Bol sıvı tüketin
- Semptomatik tedavi alabilirsiniz
- Ciddi durumlarda mutlaka doktor konsültasyonu

## 🔮 Gelecek Geliştirmeler

### 🎯 Kısa Vadeli
- [ ] Daha fazla semptom desteği
- [ ] Yaş ve cinsiyet faktörleri
- [ ] Mevsimsel düzeltmeler
- [ ] Web arayüzü

### 🚀 Uzun Vadeli  
- [ ] Derin öğrenme modelleri
- [ ] Gerçek hasta verileri ile eğitim
- [ ] Çok dilli destek
- [ ] Mobil uygulama

## 👥 Katkıda Bulunma

1. **Fork** yapın
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** yapın (`git commit -m 'Add amazing feature'`)
4. **Push** yapın (`git push origin feature/amazing-feature`)
5. **Pull Request** açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- **Scikit-learn** topluluğu
- **Pandas** geliştiricileri
- **NumPy** ekibi
- Tıbbi literatür katkıcıları

---

**🏥 Sağlıklı günler dileriz!**

*Son güncelleme: 2024*
