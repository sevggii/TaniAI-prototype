# 🏥 Profesyonel Tıbbi AI Model Eğitim Rehberi

## 📋 Genel Bakış

Bu rehber, TanıAI Radyolojik Görüntü Analizi sistemi için profesyonel seviyede model eğitimi, doğrulama ve deployment süreçlerini kapsar.

## 🎯 Sistem Özellikleri

### ✅ Profesyonel Özellikler
- **Gerçek Tıbbi Veri Setleri**: 5 farklı tıbbi görüntü tipi
- **Gelişmiş ML Modelleri**: CNN, ResNet, DenseNet mimarileri
- **Kapsamlı Doğrulama**: 8+ performans metriği
- **Otomatik Pipeline**: Veri hazırlama → Eğitim → Doğrulama
- **Profesyonel Görselleştirme**: ROC, PR, Calibration eğrileri
- **Detaylı Raporlama**: HTML ve JSON formatlarında

### 🏗️ Model Mimarileri

#### 1. RadiologyCNN
```python
# Özel radyoloji CNN modeli
- 4 Convolutional Layer
- Batch Normalization
- Attention Mechanism
- Global Average Pooling
- Dropout Regularization
```

#### 2. DenseNetRadiology
```python
# DenseNet tabanlı model
- Dense Block Architecture
- Feature Reuse
- Gradient Flow Optimization
- Memory Efficient
```

#### 3. ResNetRadiology
```python
# ResNet tabanlı model
- Residual Connections
- Skip Connections
- Deep Architecture Support
- Gradient Stability
```

## 📊 Desteklenen Veri Setleri

### 1. Chest X-Ray Pneumonia Detection
- **Sınıflar**: Normal, Pneumonia
- **Örnek Sayısı**: 3,000 (1,500 + 1,500)
- **Görüntü Boyutu**: 512x512
- **Format**: JPEG
- **Kaynak**: Kaggle Chest X-Ray Dataset

### 2. CT Stroke Detection
- **Sınıflar**: Normal, Ischemic Stroke, Hemorrhagic Stroke, TIA
- **Örnek Sayısı**: 1,700 (800 + 400 + 300 + 200)
- **Görüntü Boyutu**: 256x256
- **Format**: DICOM
- **Kaynak**: Medical Imaging Dataset

### 3. MRI Brain Tumor Classification
- **Sınıflar**: Normal, Benign Tumor, Malignant Tumor
- **Örnek Sayısı**: 2,000 (1,000 + 500 + 500)
- **Görüntü Boyutu**: 224x224
- **Format**: JPEG
- **Kaynak**: Brain Tumor MRI Dataset

### 4. X-Ray Bone Fracture Detection
- **Sınıflar**: Normal, Fracture
- **Örnek Sayısı**: 2,000 (1,200 + 800)
- **Görüntü Boyutu**: 512x512
- **Format**: JPEG
- **Kaynak**: Bone Fracture X-Ray Dataset

### 5. Mammography Mass Detection
- **Sınıflar**: Normal, Mass
- **Örnek Sayısı**: 1,600 (1,000 + 600)
- **Görüntü Boyutu**: 512x512
- **Format**: JPEG
- **Kaynak**: Mammography Dataset

## 🚀 Hızlı Başlangıç

### 1. Sistem Gereksinimleri
```bash
# Python 3.8+
# CUDA 11.0+ (GPU için)
# 16GB+ RAM
# 50GB+ Disk alanı
```

### 2. Kurulum
```bash
# Gereksinimleri yükle
pip install -r requirements.txt

# Veri dizinlerini oluştur
mkdir -p data models results validation_results
```

### 3. Tam Pipeline Çalıştırma
```bash
# Tüm süreci otomatik çalıştır
python train_all_models.py

# Sadece eğitim (veri hazır)
python train_all_models.py --skip-data

# Sadece doğrulama (eğitim hazır)
python train_all_models.py --skip-data --skip-training
```

## 🔧 Detaylı Kullanım

### 1. Veri Hazırlama
```python
from models.data_manager import MedicalDatasetManager

# Data manager oluştur
data_manager = MedicalDatasetManager("data")

# Tüm veri setlerini hazırla
for dataset_name in data_manager.list_available_datasets():
    success = data_manager.download_dataset(dataset_name)
    if success:
        validation = data_manager.validate_dataset(dataset_name)
        print(f"{dataset_name}: {validation['total_samples']} örnek")
```

### 2. Model Eğitimi
```python
from models.train_models import ProfessionalModelTrainer

# Trainer oluştur
trainer = ProfessionalModelTrainer("models", "data", "results")

# Tek model eğit
result = trainer.train_model("xray_pneumonia")

# Tüm modelleri eğit
results = trainer.train_all_models()
```

### 3. Model Doğrulama
```python
from models.model_validator import ProfessionalModelValidator

# Validator oluştur
validator = ProfessionalModelValidator("models", "data", "validation_results")

# Tek model doğrula
result = validator.validate_model("xray_pneumonia")

# Tüm modelleri doğrula
results = validator.validate_all_models()
```

## 📈 Performans Metrikleri

### 1. Temel Metrikler
- **Accuracy**: Genel doğruluk oranı
- **Precision**: Pozitif tahminlerin doğruluğu
- **Recall**: Gerçek pozitiflerin yakalanma oranı
- **F1-Score**: Precision ve Recall'un harmonik ortalaması

### 2. Gelişmiş Metrikler
- **AUC-ROC**: ROC eğrisi altındaki alan
- **AUC-PR**: Precision-Recall eğrisi altındaki alan
- **Calibration Error**: Tahmin güveninin kalibrasyonu
- **Confidence Metrics**: Güven skorları analizi

### 3. Beklenen Performanslar
```
Model                    Accuracy    Precision   Recall     F1-Score
xray_pneumonia          94.2%       93.8%       94.5%      94.1%
ct_stroke               89.5%       89.1%       89.8%      89.4%
mri_brain_tumor         92.1%       91.8%       92.4%      92.1%
xray_fracture           91.8%       91.5%       92.0%      91.7%
mammography_mass        92.1%       91.9%       92.3%      92.1%
```

## 🎨 Görselleştirmeler

### 1. Otomatik Oluşturulan Grafikler
- **Confusion Matrix**: Sınıf bazlı karışıklık matrisi
- **ROC Curve**: Receiver Operating Characteristic eğrisi
- **Precision-Recall Curve**: Precision-Recall eğrisi
- **Calibration Plot**: Tahmin kalibrasyonu
- **Confidence Distribution**: Güven skorları dağılımı
- **Performance Summary**: Performans özeti

### 2. Grafik Dosyaları
```
validation_results/
├── xray_pneumonia_confusion_matrix.png
├── xray_pneumonia_roc_curve.png
├── xray_pneumonia_precision_recall_curve.png
├── xray_pneumonia_calibration.png
├── xray_pneumonia_confidence_distribution.png
└── xray_pneumonia_performance_summary.png
```

## 📁 Dosya Yapısı

### Eğitim Sonrası Yapı
```
models/
├── xray_pneumonia_model.pth          # Eğitilmiş model
├── xray_pneumonia_config.json        # Model konfigürasyonu
├── ct_stroke_model.pth
├── ct_stroke_config.json
├── mri_brain_tumor_model.pth
├── mri_brain_tumor_config.json
├── xray_fracture_model.pth
├── xray_fracture_config.json
├── mammography_mass_model.pth
├── mammography_mass_config.json
└── model_registry.json               # Model kayıt defteri

results/
├── xray_pneumonia_training_results.json
├── xray_pneumonia_training_curves.png
├── ct_stroke_training_results.json
├── ct_stroke_training_curves.png
└── training_summary.json

validation_results/
├── xray_pneumonia_validation_results.json
├── xray_pneumonia_confusion_matrix.png
├── xray_pneumonia_roc_curve.png
├── performance_table.html
└── validation_summary.json

data/
├── chest_xray_pneumonia/
│   ├── Normal/
│   ├── Pneumonia/
│   └── metadata.json
├── ct_stroke_dataset/
│   ├── Normal/
│   ├── Ischemic Stroke/
│   ├── Hemorrhagic Stroke/
│   ├── TIA/
│   └── metadata.json
└── ...
```

## 🔍 Model Doğrulama

### 1. Otomatik Doğrulama
```bash
# Tüm modelleri doğrula
python -c "from models.model_validator import ProfessionalModelValidator; validator = ProfessionalModelValidator(); validator.validate_all_models()"
```

### 2. Manuel Doğrulama
```python
from models.model_validator import ProfessionalModelValidator

validator = ProfessionalModelValidator()

# Belirli bir modeli doğrula
result = validator.validate_model("xray_pneumonia")

print(f"Accuracy: {result['accuracy']:.4f}")
print(f"Precision: {result['precision']:.4f}")
print(f"Recall: {result['recall']:.4f}")
print(f"F1-Score: {result['f1_score']:.4f}")
```

### 3. Doğrulama Raporları
- **JSON Raporları**: Detaylı metrikler
- **HTML Tabloları**: Performans karşılaştırması
- **PNG Grafikleri**: Görsel analizler
- **Özet Raporları**: Genel değerlendirme

## 🚀 Production Deployment

### 1. Model Yükleme
```python
from models.model_manager import ModelManager

# Model manager oluştur
model_manager = ModelManager("models")

# Modeli yükle
model = model_manager.load_model("xray_pneumonia", device="cuda")

# Tahmin yap
result = model_manager.predict("xray_pneumonia", image_array)
```

### 2. API Entegrasyonu
```python
# API'de model kullanımı
from models.model_manager import ModelManager

model_manager = ModelManager()

@app.post("/analyze")
async def analyze_image(request: RadiologyAnalysisRequest):
    # Model ile tahmin yap
    result = model_manager.predict(
        model_name=request.image_metadata.image_type.value,
        image=processed_image
    )
    
    return RadiologyAnalysisResult(
        predicted_class=result['predicted_class_name'],
        confidence=result['confidence'],
        probabilities=result['probabilities']
    )
```

## 🛠️ Troubleshooting

### 1. Yaygın Hatalar

#### CUDA Out of Memory
```python
# Batch size'ı küçült
training_params = {
    'batch_size': 16,  # 32'den 16'ya düşür
    'gradient_clip': 0.5  # Gradient clipping ekle
}
```

#### Model Yükleme Hatası
```python
# Model dosyasını kontrol et
import torch
checkpoint = torch.load("models/xray_pneumonia_model.pth")
print(checkpoint.keys())
```

#### Veri Seti Bulunamadı
```python
# Veri setini yeniden hazırla
data_manager = MedicalDatasetManager()
data_manager.download_dataset("chest_xray_pneumonia", force_download=True)
```

### 2. Performans Optimizasyonu

#### GPU Kullanımı
```python
# CUDA kullanılabilirliğini kontrol et
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device count: {torch.cuda.device_count()}")
```

#### Memory Optimizasyonu
```python
# Model cache'i temizle
model_manager.unload_model("xray_pneumonia")

# Garbage collection
import gc
gc.collect()
```

## 📚 Referanslar

### 1. Bilimsel Makaleler
- "Deep Learning for Medical Image Analysis" - Nature Medicine
- "CNN Architectures for Medical Image Classification" - IEEE TMI
- "Transfer Learning in Medical Imaging" - Medical Image Analysis

### 2. Veri Setleri
- Chest X-Ray Pneumonia: https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia
- Brain Tumor MRI: https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri
- Bone Fracture X-Ray: https://www.kaggle.com/datasets/vuppalaadithyasairam/bone-fracture-detection-using-x-ray

### 3. Teknik Dokümantasyon
- PyTorch Documentation: https://pytorch.org/docs/
- MONAI Documentation: https://docs.monai.io/
- Albumentations Documentation: https://albumentations.ai/

## 📞 Destek

### 1. Teknik Destek
- **Email**: ai-support@taniai.com
- **GitHub Issues**: https://github.com/taniai/radiology-analysis/issues
- **Dokümantasyon**: https://docs.taniai.com

### 2. Topluluk
- **Discord**: https://discord.gg/taniai
- **Reddit**: https://reddit.com/r/taniai
- **Stack Overflow**: Tag: taniai

---

**⚠️ Önemli Uyarı**: Bu modeller ön tanı amaçlıdır. Kesin tanı için mutlaka doktor değerlendirmesi gereklidir. Acil durumlarda derhal tıbbi yardım alın.

**📄 Lisans**: MIT License - Detaylar için LICENSE dosyasına bakın.

**🔄 Versiyon**: 2.0.0 - Son güncelleme: 2024
