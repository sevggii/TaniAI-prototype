#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TanıAI Backend - Hızlı Başlangıç Scripti
Tüm sistemi kontrol eder ve gerekli adımları gösterir
"""

import subprocess
import requests
import json
import os
import sys

def check_ollama():
    """Ollama servisini kontrol et"""
    print("🔍 Ollama servisi kontrol ediliyor...")
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("✅ Ollama çalışıyor")
            return True
        else:
            print("❌ Ollama yanıt vermiyor")
            return False
    except:
        print("❌ Ollama çalışmıyor. Başlatın: ollama serve")
        return False

def check_model():
    """clinic-recommender modelini kontrol et"""
    print("🔍 Model kontrol ediliyor...")
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        models = response.json().get('models', [])
        
        clinic_models = [m for m in models if 'clinic' in m.get('name', '').lower()]
        
        if clinic_models:
            print(f"✅ {len(clinic_models)} klinik modeli bulundu:")
            for model in clinic_models:
                print(f"   - {model['name']}")
            return True
        else:
            print("❌ clinic-recommender modeli bulunamadı")
            return False
    except:
        print("❌ Model kontrol edilemedi")
        return False

def test_model():
    """Modeli test et"""
    print("🧪 Model test ediliyor...")
    try:
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': 'clinic-recommender',
            'prompt': 'Hasta Şikayeti: Başım ağrıyor',
            'stream': False
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Model çalışıyor")
            print(f"   Yanıt: {result.get('response', '')[:100]}...")
            return True
        else:
            print("❌ Model yanıt vermiyor")
            return False
    except Exception as e:
        print(f"❌ Model test hatası: {e}")
        return False

def check_dependencies():
    """Python bağımlılıklarını kontrol et"""
    print("🔍 Python bağımlılıkları kontrol ediliyor...")
    try:
        import fastapi
        import uvicorn
        import requests
        print("✅ Temel bağımlılıklar yüklü")
        return True
    except ImportError as e:
        print(f"❌ Eksik bağımlılık: {e}")
        print("   Çözüm: pip3 install -r requirements.txt")
        return False

def check_data():
    """Veri dosyalarını kontrol et"""
    print("🔍 Veri dosyaları kontrol ediliyor...")
    
    clinics_dir = "../clinics"
    if not os.path.exists(clinics_dir):
        print(f"❌ {clinics_dir} klasörü bulunamadı")
        return False
    
    jsonl_files = [f for f in os.listdir(clinics_dir) if f.endswith('.jsonl')]
    
    if jsonl_files:
        print(f"✅ {len(jsonl_files)} klinik veri dosyası bulundu")
        return True
    else:
        print("❌ Klinik veri dosyası bulunamadı")
        return False

def show_quick_commands():
    """Hızlı komutları göster"""
    print("\n" + "="*60)
    print("🚀 HIZLI KOMUTLAR")
    print("="*60)
    print("1. Modeli test et:")
    print("   python3 test_clinic_model.py")
    print()
    print("2. API'yi başlat:")
    print("   python3 main.py")
    print()
    print("3. Modeli yeniden eğit:")
    print("   python3 clinic_model_trainer.py")
    print("   ollama create clinic-recommender -f ClinicModelfile")
    print()
    print("4. Ollama'yı başlat:")
    print("   ollama serve")
    print()
    print("5. Mevcut modelleri listele:")
    print("   ollama list")

def main():
    """Ana fonksiyon"""
    print("🏥 TanıAI Backend - Sistem Kontrolü")
    print("="*50)
    
    # Kontroller
    checks = [
        ("Ollama Servisi", check_ollama),
        ("Python Bağımlılıkları", check_dependencies),
        ("Veri Dosyaları", check_data),
        ("Klinik Modeli", check_model),
        ("Model Testi", test_model)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        result = check_func()
        results.append((name, result))
    
    # Özet
    print("\n" + "="*50)
    print("📊 SİSTEM DURUMU")
    print("="*50)
    
    passed = 0
    for name, result in results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\nToplam: {passed}/{len(results)} başarılı")
    
    if passed == len(results):
        print("\n🎉 Sistem tamamen hazır!")
        show_quick_commands()
    else:
        print("\n⚠️  Bazı sorunlar var. Yukarıdaki hataları düzeltin.")
        print("\n🔧 SORUN GİDERME:")
        print("1. Ollama çalışmıyorsa: ollama serve")
        print("2. Model yoksa: python3 clinic_model_trainer.py")
        print("3. Bağımlılık yoksa: pip3 install -r requirements.txt")

if __name__ == "__main__":
    main()
