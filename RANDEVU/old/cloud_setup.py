#!/usr/bin/env python3
"""
Cloud Ortamı için TanıAI Kurulum Scripti
Google Colab, Kaggle, AWS, Azure gibi ortamlar için optimize edilmiş
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

def install_requirements():
    """Gerekli paketleri kur"""
    print("📦 Gerekli paketler kuruluyor...")
    
    requirements = [
        "openai-whisper",
        "torch",
        "torchaudio", 
        "scikit-learn",
        "pandas",
        "numpy",
        "fastapi",
        "uvicorn",
        "python-multipart",
        "requests",
        "aiohttp"
    ]
    
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✅ {req} kuruldu")
        except subprocess.CalledProcessError as e:
            print(f"❌ {req} kurulum hatası: {e}")

def setup_cloud_llm():
    """Cloud-friendly LLM kurulumu"""
    print("\n🤖 Cloud LLM kurulumu...")
    
    # OpenAI API key kontrolü
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OpenAI API key bulundu")
        return "openai"
    
    # Hugging Face kontrolü
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    if hf_token:
        print("✅ Hugging Face token bulundu")
        return "huggingface"
    
    # Google Colab kontrolü
    try:
        import google.colab
        print("✅ Google Colab ortamı tespit edildi")
        return "colab"
    except ImportError:
        pass
    
    print("⚠️ Cloud LLM servisi bulunamadı, sadece ML modeli kullanılacak")
    return "ml_only"

def download_whisper_model():
    """Whisper modelini indir"""
    print("\n🎤 Whisper modeli indiriliyor...")
    
    try:
        import whisper
        # Cloud ortamında daha küçük model kullan
        model_size = "medium"  # large yerine medium (daha az RAM)
        print(f"Model boyutu: {model_size}")
        
        model = whisper.load_model(model_size)
        print(f"✅ Whisper {model_size} modeli yüklendi")
        return True
    except Exception as e:
        print(f"❌ Whisper model hatası: {e}")
        return False

def test_ml_model():
    """ML modelini test et"""
    print("\n🧠 ML modeli test ediliyor...")
    
    try:
        from ml_clinic.triage_model import get_triage_model
        model = get_triage_model()
        
        test_text = "Baş ağrım var ve mide bulantısı yaşıyorum"
        result = model.suggest(test_text, top_k=3)
        
        print(f"✅ ML Model çalışıyor")
        print(f"   Test: {test_text}")
        print(f"   Öneriler: {result.get('suggestions', [])}")
        return True
    except Exception as e:
        print(f"❌ ML Model hatası: {e}")
        return False

def create_cloud_config():
    """Cloud ortamı için yapılandırma oluştur"""
    print("\n⚙️ Cloud yapılandırması oluşturuluyor...")
    
    config = {
        "environment": "cloud",
        "whisper_model": "medium",
        "llm_provider": "openai",  # veya huggingface
        "llm_model": "gpt-3.5-turbo",
        "use_ml": True,
        "use_llm": True,
        "ml_weight": 0.7,
        "llm_weight": 0.3
    }
    
    # Çevre değişkenlerini ayarla
    os.environ["LLM_PROVIDER"] = config["llm_provider"]
    os.environ["LLM_MODEL"] = config["llm_model"]
    os.environ["USE_ML"] = "true"
    os.environ["USE_LLM"] = "true"
    
    with open("cloud_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Cloud yapılandırması oluşturuldu")
    return config

def start_cloud_server():
    """Cloud sunucusunu başlat"""
    print("\n🚀 Cloud sunucusu başlatılıyor...")
    
    try:
        from whisper_asr.server import app
        import uvicorn
        
        print("Sunucu başlatılıyor...")
        print("🌐 Web arayüzü: http://localhost:8001")
        print("📡 API: http://localhost:8001/whisper/")
        
        uvicorn.run(app, host="0.0.0.0", port=8001)
        
    except Exception as e:
        print(f"❌ Sunucu başlatma hatası: {e}")

def main():
    """Ana kurulum fonksiyonu"""
    print("☁️ TanıAI Cloud Kurulumu Başlıyor...")
    print("=" * 50)
    
    # 1. Gerekli paketleri kur
    install_requirements()
    
    # 2. Cloud LLM kurulumu
    llm_type = setup_cloud_llm()
    
    # 3. Whisper modelini indir
    whisper_ok = download_whisper_model()
    
    # 4. ML modelini test et
    ml_ok = test_ml_model()
    
    # 5. Cloud yapılandırması
    config = create_cloud_config()
    
    # 6. Sonuçları göster
    print("\n" + "=" * 50)
    print("📊 KURULUM SONUÇLARI")
    print("=" * 50)
    
    print(f"Whisper Model: {'✅' if whisper_ok else '❌'}")
    print(f"ML Model: {'✅' if ml_ok else '❌'}")
    print(f"LLM Provider: {llm_type}")
    print(f"Environment: Cloud")
    
    if whisper_ok and ml_ok:
        print("\n🎉 Kurulum başarılı! Sunucu başlatılıyor...")
        start_cloud_server()
    else:
        print("\n❌ Kurulum tamamlanamadı. Hataları kontrol edin.")

if __name__ == "__main__":
    main()
