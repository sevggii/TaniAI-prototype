#!/usr/bin/env python3
"""
TanıAI Backend Server Başlatıcı
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_environment():
    """Ortam değişkenlerini ayarla"""
    # Varsayılan değerler
    os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")
    os.environ.setdefault("LITELLM_MODEL", "llama3.2:3b")
    os.environ.setdefault("LLM_TIMEOUT", "30")
    
    # .env dosyası varsa yükle
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env dosyası yüklendi")

def check_ollama():
    """Ollama servisinin çalışıp çalışmadığını kontrol et"""
    try:
        import requests
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama servisi çalışıyor")
            return True
        else:
            print("⚠️ Ollama servisi yanıt vermiyor")
            return False
    except Exception as e:
        print(f"⚠️ Ollama servisi kontrol edilemedi: {e}")
        return False

def install_dependencies():
    """Bağımlılıkları yükle"""
    try:
        print("📦 Bağımlılıklar yükleniyor...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Bağımlılıklar yüklendi")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Bağımlılık yükleme hatası: {e}")
        return False

def start_server():
    """Sunucuyu başlat"""
    try:
        print("🚀 TanıAI Backend sunucusu başlatılıyor...")
        print("📍 URL: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("🔍 Health Check: http://localhost:8000/health")
        print("\n" + "="*50)
        
        # Uvicorn ile sunucuyu başlat
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Sunucu durduruldu")
    except Exception as e:
        print(f"❌ Sunucu başlatma hatası: {e}")

def main():
    """Ana fonksiyon"""
    print("🏥 TanıAI Backend Server")
    print("="*50)
    
    # Ortamı ayarla
    setup_environment()
    
    # Bağımlılıkları kontrol et
    if not install_dependencies():
        print("❌ Bağımlılık yükleme başarısız")
        return
    
    # Ollama kontrolü
    ollama_running = check_ollama()
    if not ollama_running:
        print("⚠️ Ollama çalışmıyor, fallback yanıtlar kullanılacak")
        print("💡 Ollama'yı başlatmak için: ollama serve")
    
    # Sunucuyu başlat
    start_server()

if __name__ == "__main__":
    main()
