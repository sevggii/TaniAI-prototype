#!/usr/bin/env python3
"""
Whisper ASR Test Script
TanıAI Speech-to-Text sistemi testi
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from whisper_asr import get_asr_processor
from whisper_asr.symptom_analyzer import get_symptom_analyzer

def test_whisper_installation():
    """Whisper kurulumunu test eder"""
    print("🔍 Whisper kurulumu test ediliyor...")
    
    try:
        # Model yükleme testi
        print("📥 Base modeli yükleniyor...")
        asr_processor = get_asr_processor()
        print("✅ Whisper modeli başarıyla yüklendi!")
        
        # Model bilgileri
        print(f"📊 Model: {asr_processor.model_name}")
        print(f"🎯 Model yüklü: {asr_processor.model is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ Whisper kurulum hatası: {e}")
        return False

def test_symptom_analysis():
    """Semptom analizi testi"""
    print("\n🩺 Semptom analizi testi...")
    
    try:
        symptom_analyzer = get_symptom_analyzer()
        
        # Test metni (Türkçe)
        test_text = "Merhaba, ben çok yorgunum ve başım ağrıyor. Ayrıca mide bulantım var."
        print(f"📝 Test metni: {test_text}")
        
        # Analiz yap
        result = symptom_analyzer.analyze_transcript(test_text)
        
        print(f"✅ Analiz başarılı!")
        print(f"📊 Tespit edilen semptomlar: {result['symptom_count']} adet")
        
        if result['detected_symptoms']:
            print("🔍 Bulunan semptomlar:")
            for symptom, severity in result['detected_symptoms'].items():
                severity_text = {1: "Hafif", 2: "Orta", 3: "Şiddetli"}[severity]
                print(f"   - {symptom}: {severity_text} ({severity})")
        
        return True
        
    except Exception as e:
        print(f"❌ Semptom analizi test hatası: {e}")
        return False

def test_api_endpoints():
    """API endpoint'leri test eder"""
    print("\n🌐 API endpoint'leri test ediliyor...")
    
    try:
        from whisper_asr.api import router
        
        print("✅ API router başarıyla yüklendi!")
        print(f"📋 Endpoint'ler:")
        
        for route in router.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                print(f"   - {methods}: {route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚀 TanıAI Whisper ASR Test Başlıyor...\n")
    
    # Kurulum testi
    if not test_whisper_installation():
        print("❌ Kurulum başarısız!")
        return
    
    # Semptom analizi testi
    if not test_symptom_analysis():
        print("❌ Semptom analizi testi başarısız!")
        return
    
    # API testi
    if not test_api_endpoints():
        print("❌ API testi başarısız!")
        return
    
    print("\n🎉 Tüm testler başarılı!")
    print("📋 Kullanım:")
    print("   1. Ses dosyası yüklemek için: POST /whisper/upload-audio")
    print("   2. Metin testi için: POST /whisper/test-transcription")
    print("   3. Durum kontrolü için: GET /whisper/status")
    print("   4. Semptom listesi için: GET /whisper/symptoms")

if __name__ == "__main__":
    main()
