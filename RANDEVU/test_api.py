#!/usr/bin/env python3
"""
API Test Scripti - Flutter entegrasyonu için
"""

import requests
import json
import os

def test_api():
    """API'yi test et"""
    
    # API URL'i
    api_url = "http://localhost:8000/whisper/flutter-randevu"
    
    # Test ses dosyası (varsa)
    test_audio = "test_audio.wav"
    
    if not os.path.exists(test_audio):
        print("❌ Test ses dosyası bulunamadı!")
        print("📝 Önce bir ses dosyası kaydet: test_audio.wav")
        return
    
    try:
        # Ses dosyasını gönder
        with open(test_audio, 'rb') as f:
            files = {'audio_file': f}
            response = requests.post(api_url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Başarılı!")
            print(f"📝 Transkript: {result['transcript']}")
            print("🏥 Öneriler:")
            
            for suggestion in result['suggestions']:
                if suggestion.get('urgent'):
                    print(f"   🚨 ACİL: {suggestion['clinic']}")
                    print(f"      {suggestion.get('message', '')}")
                else:
                    print(f"   📋 {suggestion['clinic']} - Güven: {suggestion['confidence']:.2f}")
                    print(f"      Sebep: {suggestion['reason']}")
        else:
            print(f"❌ API Hatası: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ API'ye bağlanılamadı!")
        print("🔧 Önce API'yi başlat: cd whisper_asr && python server.py")
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    test_api()
