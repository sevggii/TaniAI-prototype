# Turkish Medical Anamnesis Clinic Prediction System

Bu proje, Türkçe anamnez metinlerini analiz ederek hastaların hangi kliniğe yönlendirilmesi gerektiğini tahmin eden bir makine öğrenmesi sistemidir.

## Proje Özeti

Sistem, MHRS (Merkezi Hekim Randevu Sistemi) klinik listesindeki 66 farklı kliniği destekler ve Türkçe anamnez metinlerini analiz ederek en uygun kliniği önerir.

## Model Performansı

- **Accuracy (Doğruluk)**: 89.17%
- **Macro F1 Score**: 89.11%
- **Micro F1 Score**: 89.17%

## Dosya Yapısı

```
RANDEVU/
├── data/
│   ├── train.csv              # Eğitim verisi (1200 örnek)
│   ├── test.csv               # Test verisi (1200 örnek)
│   └── clinics.json           # Klinik listesi
├── models/
│   ├── clinic_classifier.pkl  # Eğitilmiş model
│   ├── tfidf_vectorizer.pkl   # TF-IDF vektörizer
│   └── clinic_names.json      # Klinik isimleri
├── results/
│   ├── evaluation_results.json # Değerlendirme sonuçları
│   └── confusion_matrix.png    # Karışıklık matrisi
├── data_generation.py         # Sentetik veri üretimi
├── train_model.py            # Model eğitimi
├── inference.py              # Tahmin sistemi
└── README.md                 # Bu dosya
```

## Kurulum ve Kullanım

### Gereksinimler

```bash
pip install pandas numpy scikit-learn matplotlib seaborn joblib
```

### 1. Veri Üretimi

Sentetik Türkçe anamnez verilerini üretmek için:

```bash
cd RANDEVU
python data_generation.py
```

Bu komut şunları oluşturur:
- `data/train.csv`: 1200 eğitim örneği
- `data/test.csv`: 1200 test örneği
- `data/clinics.json`: Klinik listesi

### 2. Model Eğitimi

Modeli eğitmek için:

```bash
python train_model.py
```

Bu komut şunları oluşturur:
- `models/clinic_classifier.pkl`: Eğitilmiş Logistic Regression modeli
- `models/tfidf_vectorizer.pkl`: TF-IDF vektörizer
- `models/clinic_names.json`: Klinik isimleri
- `results/evaluation_results.json`: Detaylı değerlendirme sonuçları
- `results/confusion_matrix.png`: Karışıklık matrisi görselleştirmesi

### 3. Tahmin Sistemi

#### Etkileşimli Mod

```bash
python inference.py
```

Bu mod sürekli olarak anamnez metni girmenizi bekler ve tahminleri gösterir.

#### Tek Metin Tahmini

```bash
python inference.py "Hasta son 3 gündür şiddetli baş ağrısı şikayeti ile başvurdu"
```

#### Toplu İşlem

```bash
python inference.py input.txt output.txt
```

`input.txt` dosyasındaki her satır bir anamnez metni olmalıdır.

## Örnek Kullanım

```python
from inference import ClinicPredictor

# Tahmin sistemini başlat
predictor = ClinicPredictor()

# Tek tahmin
anamnesis = "Hasta son 3 gündür şiddetli baş ağrısı ve mide bulantısı şikayeti ile başvurdu"
prediction = predictor.predict_single(anamnesis)
print(f"Tahmin: {prediction}")

# En iyi 3 tahmin
predictions = predictor.predict_clinic(anamnesis, top_k=3)
for clinic, confidence in predictions:
    print(f"{clinic}: {confidence:.2%} güven")
```

## Desteklenen Klinikler

Sistem 66 farklı kliniği destekler, örnekler:

- Aile Hekimliği
- Algoloji
- Beyin ve Sinir Cerrahisi
- Çocuk Sağlığı ve Hastalıkları
- Deri ve Zührevi Hastalıkları (Cildiye)
- Diş Hekimliği (Genel Diş)
- Endokrinoloji ve Metabolizma Hastalıkları
- Gastroenteroloji
- Göz Hastalıkları
- Kardiyoloji
- Nöroloji
- Ortopedi ve Travmatoloji
- Ruh Sağlığı ve Hastalıkları (Psikiyatri)
- Üroloji
- Ve daha fazlası...

## Teknik Detaylar

### Veri Ön İşleme

- Türkçe karakter normalizasyonu (ı→i, ğ→g, ü→u, ş→s, ö→o, ç→c)
- Noktalama işaretlerinin kaldırılması
- Türkçe stopword'lerin filtrelenmesi
- Küçük harfe çevirme
- Minimum kelime uzunluğu filtresi (2 karakter)

### Model Mimarisi

- **Algoritma**: Logistic Regression
- **Vektörizasyon**: TF-IDF (Term Frequency-Inverse Document Frequency)
- **Özellik Sayısı**: 5000 (unigram + bigram)
- **Minimum Doküman Frekansı**: 2
- **Maksimum Doküman Frekansı**: %95

### Veri Seti Özellikleri

- **Toplam Örnek**: 2400 (1200 eğitim + 1200 test)
- **Klinik Sayısı**: 66
- **Dil**: Türkçe
- **Veri Tipi**: Sentetik (gerçekçi Türkçe anamnez metinleri)

## Örnek Anamnez Metinleri

```
"Hasta son 3 gündür şiddetli baş ağrısı ve mide bulantısı şikayeti ile başvurdu. Ağrı dayanılmaz düzeyde."

"Çocuk hasta ateş ve öksürük şikayeti ile geldi. Gece uykuyu bölüyor."

"Hasta göz ağrısı ve görme bozukluğu şikayeti ile başvurdu. Son günlerde artış gösteriyor."

"Kalp çarpıntısı ve nefes darlığı şikayeti var. Günlük aktiviteleri etkiliyor."
```

## Sınırlamalar

1. **Dil Desteği**: Sadece Türkçe metinleri destekler
2. **Veri Kalitesi**: Sentetik veri ile eğitilmiştir, gerçek veri ile test edilmelidir
3. **Klinik Sayısı**: Sadece MHRS listesindeki 66 kliniği destekler
4. **Metin Uzunluğu**: Çok kısa veya çok uzun metinler için performans düşebilir

## Gelecek Geliştirmeler

- [ ] Gerçek hastane verisi ile yeniden eğitim
- [ ] Daha gelişmiş NLP teknikleri (BERT, Word2Vec)
- [ ] Çok dilli destek
- [ ] Web arayüzü geliştirme
- [ ] API servisi oluşturma
- [ ] Model performansını artırma

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## İletişim

Sorularınız için lütfen proje sahibi ile iletişime geçin.
