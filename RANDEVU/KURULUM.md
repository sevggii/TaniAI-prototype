# 🏥 TanıAI Randevu Sistemi Kurulum Rehberi

## 🎯 Sistem Özellikleri

- **Whisper ASR**: Global ses-metin çeviri servisi
- **Flutter Uygulaması**: Mobil randevu sistemi
- **Randevu API**: Klinik öneri sistemi
- **Modern UI**: Kullanıcı dostu arayüz

## 📋 Gereksinimler

### Sistem Gereksinimleri
- Python 3.8+
- Flutter SDK
- 4GB+ RAM
- FFmpeg (ses işleme için)

### Python Bağımlılıkları
```bash
pip install -r requirements.txt
```

## 🚀 Kurulum Adımları

### 1. Whisper ASR Global Servisini Başlatın
```bash
cd whisper_asr
python3 server.py
```
Servis http://localhost:8001 adresinde çalışacak.

### 2. Randevu API'sini Başlatın
```bash
cd RANDEVU/mobile_flutter/api
python3 randevu_api.py
```
API http://localhost:8002 adresinde çalışacak.

### 3. Flutter Uygulamasını Çalıştırın
```bash
cd RANDEVU/mobile_flutter
flutter run
```

## 🔧 Servis Durumu Kontrolü

### Whisper ASR Durumu
```bash
curl http://localhost:8001/whisper/status
```

### Randevu API Durumu
```bash
curl http://localhost:8002/
```

## 📱 Kullanım

1. Flutter uygulamasını açın
2. "Sesli Randevu" seçeneğini seçin
3. Mikrofon butonuna basın ve konuşun
4. Sistem otomatik olarak uygun kliniği önerecek

## 🛠️ Sorun Giderme

### Whisper Model Yüklenemiyor
- FFmpeg'in kurulu olduğundan emin olun
- Yeterli RAM olduğunu kontrol edin

### API Bağlantı Hatası
- Her iki servisin de çalıştığını kontrol edin
- Port çakışması olup olmadığını kontrol edin

### Flutter Uygulaması Çalışmıyor
- Flutter SDK'nın güncel olduğunu kontrol edin
- `flutter doctor` komutunu çalıştırın
