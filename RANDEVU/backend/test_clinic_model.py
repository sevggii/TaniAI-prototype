#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Klinik Model Testi
Eğitilmiş modeli konsolda test eder
"""

import requests
import json
import logging

# Logging ayarla
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ClinicModelTester:
    """Klinik model test sınıfı"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "clinic-recommender"
        
    def test_single_complaint(self, complaint: str) -> dict:
        """Tek şikayet test et"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"Hasta Şikayeti: {complaint}",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                
                # JSON parse etmeye çalış
                try:
                    # JSON kısmını bul
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    
                    if start != -1 and end != -1:
                        json_str = response_text[start:end]
                        clinic_data = json.loads(json_str)
                        
                        return {
                            "success": True,
                            "complaint": complaint,
                            "recommended_clinic": clinic_data.get("clinic", "Bilinmiyor"),
                            "confidence": clinic_data.get("confidence", 0.0),
                            "reasoning": clinic_data.get("reasoning", "Açıklama yok"),
                            "raw_response": response_text
                        }
                    else:
                        return {
                            "success": False,
                            "complaint": complaint,
                            "error": "JSON formatı bulunamadı",
                            "raw_response": response_text
                        }
                        
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "complaint": complaint,
                        "error": f"JSON parse hatası: {e}",
                        "raw_response": response_text
                    }
            else:
                return {
                    "success": False,
                    "complaint": complaint,
                    "error": f"API hatası: {response.status_code}",
                    "raw_response": ""
                }
                
        except Exception as e:
            return {
                "success": False,
                "complaint": complaint,
                "error": f"Test hatası: {e}",
                "raw_response": ""
            }
    

def main():
    """Ana fonksiyon - Otomatik niyet anlama"""
    print("\n" + "=" * 60)
    print("🏥 KLİNİK MODEL TEST SİSTEMİ")
    print("=" * 60)
    
    tester = ClinicModelTester()
    complaint_number = 1
    
    while True:
        try:
            # Şikayeti al
            first_complaint = input(f"\n{complaint_number}. Şikayet: ").strip()
            
            # Çıkış komutları
            if first_complaint.lower() in ['çıkış', 'exit', 'q', 'quit']:
                print("\n👋 Program sonlandırılıyor...")
                break
            
            # Boş giriş - program sonlandır
            if not first_complaint:
                print("\n👋 Program sonlandırılıyor...")
                break
            
            # Başka semptom var mı sor (aynı doktor ziyaretine ekleme)
            more_symptoms = input("Başka semptom var mı? (e/h): ").strip().lower()
            
            if more_symptoms in ['h', 'hayır', 'n', 'no', '']:
                # Tek semptom - hemen analiz et
                result = tester.test_single_complaint(first_complaint)
                
                print("\n" + "=" * 50)
                print("📋 ANALİZ SONUCU")
                print("=" * 50)
                if result["success"]:
                    print(f"✅ Önerilen Klinik: {result['recommended_clinic']}")
                    print(f"✅ Güven: {result['confidence']}")
                    print(f"✅ Açıklama: {result['reasoning']}")
                else:
                    print(f"❌ Hata: {result['error']}")
                print("=" * 50)
                complaint_number += 1
            else:
                # Aynı doktor ziyaretine ek semptomlar ekle
                additional_symptoms = input("Ek semptomlar: ").strip()
                
                if additional_symptoms:
                    full_complaint = f"{first_complaint}, {additional_symptoms}"
                else:
                    full_complaint = first_complaint
                
                # Birleştirilmiş şikayeti analiz et
                result = tester.test_single_complaint(full_complaint)
                
                print("\n" + "=" * 50)
                print("📋 ANALİZ SONUCU")
                print("=" * 50)
                if result["success"]:
                    print(f"✅ Önerilen Klinik: {result['recommended_clinic']}")
                    print(f"✅ Güven: {result['confidence']}")
                    print(f"✅ Açıklama: {result['reasoning']}")
                else:
                    print(f"❌ Hata: {result['error']}")
                print("=" * 50)
                complaint_number += 1
                
        except KeyboardInterrupt:
            print("\n\n👋 Program kullanıcı tarafından sonlandırıldı.")
            break
        except EOFError:
            print("\n\n👋 Program sonlandırıldı.")
            break


if __name__ == "__main__":
    main()


'''
============================================================
🏥 KLİNİK MODEL TEST SİSTEMİ
============================================================

1. Şikayet: başım ağrıyor
Başka semptom var mı? (e/h): h

==================================================
📋 ANALİZ SONUCU
==================================================
✅ Önerilen Klinik: Nöroloji
✅ Güven: 0.95
✅ Açıklama: Baş ağrısı semptomu nöroloji bölümüne uygun
==================================================

2. Şikayet: düştüm kolum ağrıyor
Başka semptom var mı? (e/h): h

==================================================
📋 ANALİZ SONUCU
==================================================
✅ Önerilen Klinik: Acil Servis
✅ Güven: 0.98
✅ Açıklama: Kırık ve acil müdahale gerektiren durum
==================================================

3. Şikayet: kalbim ağrıyor
Başka semptom var mı? (e/h): h

==================================================
📋 ANALİZ SONUCU
==================================================
✅ Önerilen Klinik: Kardiyoloji
✅ Güven: 0.95
✅ Açıklama: Kalp ağrısı, kalp krizi riski var, immediate müdahale gerektirir
==================================================
'''

'''
============================================================
🏥 KLİNİK MODEL TEST SİSTEMİ
============================================================

1. Şikayet: başım çok ağrıyor
Başka semptom var mı? (e/h): h

==================================================
📋 ANALİZ SONUCU
==================================================
✅ Önerilen Klinik: Nöroloji
✅ Güven: 0.96
✅ Açıklama: Baş ağrısı ve migren semptomları nöroloji bölümüne uygun
==================================================

2. Şikayet: midem çok bulanıyor
Başka semptom var mı? (e/h): h

==================================================
📋 ANALİZ SONUCU
==================================================
✅ Önerilen Klinik: Gastroenteroloji Cerrahisi
✅ Güven: 0.93
✅ Açıklama: Midem bulantısı gastroenteroloji bölümüne uygun
==================================================

3. Şikayet: yüksekten düştüm bileğim ağrıyor
Başka semptom var mı? (e/h): e
Ek semptomlar: çok kanamam var

==================================================
📋 ANALİZ SONUCU
==================================================
✅ Önerilen Klinik: Acil Servis
✅ Güven: 0.99
✅ Açıklama: Yükten düşme ve bileyim kanaması acil müdahale gerektirir
==================================================
'''