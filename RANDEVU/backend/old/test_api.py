#!/usr/bin/env python3
"""
TanıAI Backend API Test Scripti
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Sağlık kontrolü testi"""
    print("🔍 Sağlık kontrolü testi...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API sağlıklı")
            print(f"📊 Yanıt: {response.json()}")
            return True
        else:
            print(f"❌ API sağlıksız: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False

def test_chat():
    """Chat API testi"""
    print("\n💬 Chat API testi...")
    try:
        data = {
            "message": "Merhaba, randevu almak istiyorum",
            "context": "medical_assistant"
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat API çalışıyor")
            print(f"🤖 AI Yanıtı: {result['response']}")
            return True
        else:
            print(f"❌ Chat API hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat API bağlantı hatası: {e}")
        return False

def test_triage():
    """Triyaj API testi"""
    print("\n🏥 Triyaj API testi...")
    try:
        data = {
            "text": "Göğsümde ağrı var, nefes almakta zorlanıyorum"
        }
        
        response = requests.post(f"{BASE_URL}/triage", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Triyaj API çalışıyor")
            print(f"🚨 Aciliyet: {result['urgency']}")
            print(f"🏥 Önerilen Klinik: {result['recommended_clinic']}")
            print(f"📋 Analiz: {result['analysis']}")
            return True
        else:
            print(f"❌ Triyaj API hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Triyaj API bağlantı hatası: {e}")
        return False

def test_clinic_recommendation():
    """Klinik önerisi API testi"""
    print("\n🏥 Klinik önerisi API testi...")
    try:
        data = {
            "symptoms": "Baş ağrısı ve mide bulantısı"
        }
        
        response = requests.post(f"{BASE_URL}/recommend-clinic", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Klinik önerisi API çalışıyor")
            print(f"🏥 Önerilen Klinik: {result['recommended_clinic']}")
            print(f"🚨 Aciliyet: {result['urgency']}")
            print(f"💡 Gerekçe: {result['reasoning']}")
            return True
        else:
            print(f"❌ Klinik önerisi API hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Klinik önerisi API bağlantı hatası: {e}")
        return False

def test_clinics_list():
    """Klinik listesi API testi"""
    print("\n📋 Klinik listesi API testi...")
    try:
        response = requests.get(f"{BASE_URL}/clinics")
        if response.status_code == 200:
            result = response.json()
            print("✅ Klinik listesi API çalışıyor")
            print(f"📊 Toplam klinik sayısı: {result['count']}")
            print("🏥 Mevcut klinikler:")
            for clinic in result['clinics'][:5]:  # İlk 5 kliniği göster
                print(f"  - {clinic['name']}: {clinic['description']}")
            return True
        else:
            print(f"❌ Klinik listesi API hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Klinik listesi API bağlantı hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🧪 TanıAI Backend API Testleri")
    print("="*50)
    
    # Sunucunun başlamasını bekle
    print("⏳ Sunucunun başlaması bekleniyor...")
    time.sleep(3)
    
    tests = [
        ("Sağlık Kontrolü", test_health),
        ("Chat API", test_chat),
        ("Triyaj API", test_triage),
        ("Klinik Önerisi API", test_clinic_recommendation),
        ("Klinik Listesi API", test_clinics_list),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} testi başarısız: {e}")
            results.append((test_name, False))
    
    # Sonuçları özetle
    print("\n" + "="*50)
    print("📊 Test Sonuçları:")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Toplam: {passed}/{len(results)} test başarılı")
    
    if passed == len(results):
        print("🎉 Tüm testler başarılı! API hazır.")
    else:
        print("⚠️ Bazı testler başarısız. Lütfen hataları kontrol edin.")

if __name__ == "__main__":
    main()
