#!/bin/bash

echo "🚀 Clinic LLM Server Başlatılıyor..."

# Port 8000'i temizle
echo "🧹 Port 8000 temizleniyor..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# 2 saniye bekle
sleep 2

# Server'ı başlat
echo "🤖 Server başlatılıyor..."
cd /Users/sevgi/TaniAI-prototype/RANDEVU
python3 clinic_llm_server.py &

echo "✅ Server başlatıldı!"
echo "🌐 URL: http://localhost:8000"
echo "📊 Dataset: 8000 hasta, 40 klinik"
echo "🦙 Model: TinyLLaMA"

# Server'ın başlamasını bekle
sleep 3

# Test et
echo "🧪 Test ediliyor..."
curl -s http://localhost:8000/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Server başarıyla çalışıyor!"
else
    echo "❌ Server başlatılamadı!"
fi
