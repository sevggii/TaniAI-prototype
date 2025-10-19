# 🚀 Railway Deployment Guide - TanıAI

## Hızlı Başlangıç

### 1. Railway Hesabı Oluştur
1. [railway.app](https://railway.app) adresine git
2. GitHub ile giriş yap
3. "New Project" butonuna tıkla

### 2. Projeyi Bağla
1. "Deploy from GitHub repo" seç
2. `TaniAI-prototype` repository'sini seç
3. "Deploy" butonuna tıkla

### 3. Environment Variables Ayarla
Railway dashboard'da "Variables" sekmesine git ve şunları ekle:

```bash
# Database (Railway otomatik PostgreSQL sağlar)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (Railway Redis addon ekle)
REDIS_URL=${{Redis.REDIS_URL}}

# Security
SECRET_KEY=your-super-secret-production-key-32-chars
API_KEY_DEV=prod_key_123

# App Settings
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production
DEBUG=false

# CORS
CORS_ORIGINS=https://your-app.railway.app,https://taniai.com
```

### 4. Addon'ları Ekle
1. "Add Service" → "Database" → "PostgreSQL"
2. "Add Service" → "Database" → "Redis"

### 5. Domain Ayarla
1. "Settings" → "Domains"
2. "Generate Domain" ile ücretsiz domain al
3. Custom domain ekleyebilirsin

## 🎯 Production Optimizasyonları

### Dockerfile Optimizasyonu
- Multi-stage build kullanıldı
- Production dependencies
- Health check eklendi
- Security headers

### Environment Variables
- Production-ready ayarlar
- Secure secret keys
- CORS yapılandırması
- Database connection pooling

### Monitoring
- Health check endpoint: `/health`
- Log aggregation
- Error tracking
- Performance metrics

## 📊 Deployment Sonrası

### Test Et
```bash
# Health check
curl https://your-app.railway.app/health

# API test
curl https://your-app.railway.app/docs
```

### Monitoring
- Railway dashboard'da logs
- Metrics ve performance
- Error tracking
- Uptime monitoring

## 🔧 Troubleshooting

### Common Issues
1. **Port binding**: Railway PORT env var kullan
2. **Database connection**: DATABASE_URL doğru mu?
3. **CORS errors**: CORS_ORIGINS ayarla
4. **Memory issues**: Railway plan upgrade

### Logs
```bash
# Railway CLI ile logs
railway logs

# Specific service logs
railway logs --service your-service
```

## 💰 Maliyet
- **Free Tier**: $5 kredi/ay
- **Hobby Plan**: $5/ay (daha fazla kaynak)
- **Pro Plan**: $20/ay (production ready)

## 🚀 Sonraki Adımlar
1. Custom domain ekle
2. SSL certificate (otomatik)
3. CDN ekle (Cloudflare)
4. Monitoring tools (Sentry)
5. CI/CD pipeline

---
**Railway ile deployment 5 dakikada tamamlanır!** 🎉
