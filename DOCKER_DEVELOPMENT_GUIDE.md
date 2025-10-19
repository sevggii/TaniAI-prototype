# 🐳 TanıAI Docker Geliştirme Rehberi

Bu rehber, TanıAI projesinin Docker ile nasıl çalıştırılacağını ve geliştirmeye devam edileceğini açıklar.

## 📋 Proje Yapısı

TanıAI projesi şu modüllerden oluşur:


- **Görüntü İşleme** (`görüntü işleme/`) - Radyolojik görüntü analizi
- **Tanı Sistemi** (`Tanı-hastalıklar/`) - Vitamin eksikliği teşhisi
- **Randevu Sistemi** (`RANDEVU/`) - Klinik randevu yönetimi
- **İlaç Takibi** (`ilaç takibi/`) - İlaç takip ve uyarı sistemi
- **TANI** (`TANI/`) - Üst solunum yolu hastalıkları teşhisi
- **Whisper ASR** (`whisper_asr/`) - Ses tanıma servisi
- **Güvenlik** (`güvenlik/`) - Güvenlik ve monitoring

## 🚀 Hızlı Başlangıç

### 1. Environment Dosyasını Hazırla

```bash
# .env dosyasını oluştur
cp env.example .env

# .env dosyasını düzenle (gerekirse)
nano .env
```

### 2. Production Modunda Çalıştır

```bash
# Tüm servisleri başlat
docker-compose up -d

# Logları takip et
docker-compose logs -f

# Belirli bir servisi takip et
docker-compose logs -f image-analysis
```

### 3. Development Modunda Çalıştır

```bash
# Development modunda başlat (hot reload ile)
docker-compose -f docker-compose.dev.yml up -d

# Logları takip et
docker-compose -f docker-compose.dev.yml logs -f
```

## 🔧 Geliştirme İş Akışı

### Yeni Özellik Ekleme

1. **Kodu Düzenle**: Herhangi bir modülde değişiklik yap
2. **Hot Reload**: Development modunda çalışıyorsan değişiklikler otomatik yansır
3. **Test Et**: API endpointlerini test et
4. **Commit**: Değişiklikleri commit et

### Yeni Modül Ekleme

1. **Dockerfile Oluştur**: Yeni modül için `Dockerfile` oluştur
2. **docker-compose.yml Güncelle**: Yeni servisi ekle
3. **Environment Variables**: Gerekli env var'ları ekle
4. **Test Et**: Yeni modülü test et

### Yeni Bağımlılık Ekleme

1. **requirements.txt Güncelle**: İlgili modülün requirements.txt dosyasını güncelle
2. **Container'ı Yeniden Build Et**:
   ```bash
   docker-compose build [servis-adı]
   docker-compose up -d [servis-adı]
   ```

## 📊 Servis Portları

| Servis | Port | Açıklama |
|--------|------|----------|
| PostgreSQL | 5432 | Veritabanı |
| Redis | 6379 | Cache ve Session |
| Görüntü İşleme | 8001 | Radyolojik analiz API |
| Tanı Sistemi | 8002 | Vitamin teşhisi API |
| İlaç Takibi | 8003 | İlaç takip API |
| Randevu Sistemi | 8004 | Randevu yönetimi API |
| Whisper ASR | 8005 | Ses tanıma API |
| TANI Triage | 8006 | Üst solunum yolu teşhisi API |

## 🔍 Debugging ve Monitoring

### Container Logları

```bash
# Tüm servislerin logları
docker-compose logs

# Belirli bir servisin logları
docker-compose logs image-analysis

# Canlı log takibi
docker-compose logs -f --tail=100 image-analysis
```

### Container İçine Girme

```bash
# Container içine bash ile gir
docker-compose exec image-analysis bash

# Container içine python ile gir
docker-compose exec image-analysis python
```

### Servis Durumu

```bash
# Tüm servislerin durumu
docker-compose ps

# Belirli servisin durumu
docker-compose ps image-analysis
```

## 🛠️ Yaygın Komutlar

### Servisleri Yönetme

```bash
# Servisleri başlat
docker-compose up -d

# Servisleri durdur
docker-compose down

# Servisleri yeniden başlat
docker-compose restart

# Belirli servisi yeniden başlat
docker-compose restart image-analysis
```

### Veritabanı İşlemleri

```bash
# PostgreSQL'e bağlan
docker-compose exec postgres psql -U taniai_user -d taniai_db

# Veritabanını yedekle
docker-compose exec postgres pg_dump -U taniai_user taniai_db > backup.sql

# Veritabanını geri yükle
docker-compose exec -T postgres psql -U taniai_user -d taniai_db < backup.sql
```

### Volume Yönetimi

```bash
# Volume'ları listele
docker volume ls

# Volume'ı temizle
docker volume rm taniai-prototype_postgres_data
```

## 🧪 Testing

### API Testleri

```bash
# Health check
curl http://localhost:8001/health

# Görüntü analizi testi
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_type": "chest_xray", "image_data": "base64_data"}'

# Tanı sistemi testi
curl -X POST http://localhost:8002/diagnosis/analyze \
  -H "Content-Type: application/json" \
  -d '{"symptoms": [{"name": "yorgunluk", "severity": 3}]}'
```

### Unit Testleri

```bash
# Container içinde test çalıştır
docker-compose exec image-analysis python -m pytest tests/

# Belirli test dosyası
docker-compose exec image-analysis python -m pytest tests/test_api.py
```

## 🚨 Sorun Giderme

### Servis Başlamıyor

1. **Logları kontrol et**:
   ```bash
   docker-compose logs [servis-adı]
   ```

2. **Port çakışması kontrol et**:
   ```bash
   netstat -tulpn | grep :8001
   ```

3. **Container'ı yeniden build et**:
   ```bash
   docker-compose build --no-cache [servis-adı]
   ```

### Veritabanı Bağlantı Sorunu

1. **PostgreSQL durumunu kontrol et**:
   ```bash
   docker-compose exec postgres pg_isready -U taniai_user
   ```

2. **Environment variables kontrol et**:
   ```bash
   docker-compose exec image-analysis env | grep DATABASE
   ```

### Memory Sorunları

1. **Container memory kullanımını kontrol et**:
   ```bash
   docker stats
   ```

2. **Memory limit artır** (docker-compose.yml'de):
   ```yaml
   services:
     image-analysis:
       deploy:
         resources:
           limits:
             memory: 2G
   ```

## 📝 Environment Variables

Tüm environment variables `env.example` dosyasında tanımlanmıştır. Önemli olanlar:

- `DATABASE_URL`: PostgreSQL bağlantı URL'i
- `REDIS_URL`: Redis bağlantı URL'i
- `SECRET_KEY`: JWT için secret key
- `API_KEY_*`: API anahtarları
- `HOST`, `PORT`: Servis host ve port ayarları
- `MODELS_DIR`, `DATA_DIR`: Model ve veri dizinleri

## 🔄 CI/CD Pipeline

### GitHub Actions Örneği

```yaml
name: Docker Build and Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build and test
      run: |
        docker-compose -f docker-compose.dev.yml up -d
        docker-compose -f docker-compose.dev.yml exec image-analysis python -m pytest
        docker-compose -f docker-compose.dev.yml down
```

## 📚 Ek Kaynaklar

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)

## 🤝 Katkıda Bulunma

1. Fork yap
2. Feature branch oluştur (`git checkout -b feature/amazing-feature`)
3. Değişiklikleri commit et (`git commit -m 'Add amazing feature'`)
4. Branch'i push et (`git push origin feature/amazing-feature`)
5. Pull Request oluştur

## 📞 Destek

Sorunlar için:
- GitHub Issues kullan
- Docker loglarını paylaş
- Environment bilgilerini ekle
