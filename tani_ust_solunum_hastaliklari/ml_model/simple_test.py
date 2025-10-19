#!/usr/bin/env python3
"""
Simple Test - Professional Medical System
Hata vermeden basit test
"""

import warnings
warnings.filterwarnings('ignore')

def simple_test():
    print("🏥 PROFESSIONAL MEDICAL SYSTEM - SIMPLE TEST")
    print("="*60)
    
    try:
        from professional_medical_system import ProfessionalMedicalSystem
        
        print("🔧 Sistem yükleniyor...")
        medical_system = ProfessionalMedicalSystem()
        
        if medical_system.ultra_precise_predictor.model_data is None:
            print("❌ Model yüklenemedi!")
            return
        
        print("✅ Sistem hazır!")
        print()
        
        # Test senaryoları
        test_cases = [
            {
                "symptoms": "Ateşim var, öksürüyorum",
                "expected": "COVID-19"
            },
            {
                "symptoms": "Gözlerim kaşınıyor, hapşırıyorum",
                "expected": "Mevsimsel Alerji"
            },
            {
                "symptoms": "Nefes alamıyorum, koku alamıyorum",
                "expected": "COVID-19"
            },
            {
                "symptoms": "Vücudum ağrıyor, titreme var",
                "expected": "Grip"
            },
            {
                "symptoms": "Burnum akıyor, hapşırıyorum",
                "expected": "Soğuk Algınlığı"
            }
        ]
        
        print("🧪 5 test senaryosu çalıştırılıyor...\n")
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"📋 Test {i}: '{test_case['symptoms']}'")
            print(f"🎯 Beklenen: {test_case['expected']}")
            
            try:
                result = medical_system.diagnose_patient(test_case['symptoms'])
                
                print(f"🏥 Tahmin: {result.disease.value}")
                print(f"📊 Güven: %{result.confidence*100:.1f}")
                print(f"🎯 Şiddet: {result.severity_level.value}")
                
                # Doğru tahmin kontrolü
                if result.disease.value == test_case['expected']:
                    print("✅ DOĞRU TAHMİN!")
                    success_count += 1
                else:
                    print("❌ YANLIŞ TAHMİN!")
                
                # En yüksek 2 olasılık
                sorted_probs = sorted(result.probabilities.items(), key=lambda x: x[1], reverse=True)
                print("🎲 En yüksek 2 olasılık:")
                for j, (disease, prob) in enumerate(sorted_probs[:2], 1):
                    print(f"   {j}. {disease}: %{prob*100:.1f}")
                
                print("-" * 60)
                
            except Exception as e:
                print(f"❌ Test {i} sırasında hata: {e}")
                print("-" * 60)
        
        # Sonuç
        print(f"\n📊 TEST SONUÇLARI:")
        print(f"✅ Başarılı: {success_count}/5")
        print(f"📈 Başarı Oranı: %{success_count*100/5:.1f}")
        
        if success_count == 5:
            print("🎉 MÜKEMMEL! Tüm testler başarılı!")
        elif success_count >= 4:
            print("👍 ÇOK İYİ! Neredeyse tüm testler başarılı!")
        elif success_count >= 3:
            print("👌 İYİ! Çoğu test başarılı!")
        else:
            print("⚠️ Geliştirilmesi gerekiyor.")
        
        print("\n🏥 Sağlık uyarısı: Bu sistem sadece ön tanı amaçlıdır.")
        print("📞 Ciddi semptomlar için mutlaka doktora başvurun!")
        
    except Exception as e:
        print(f"❌ Sistem yüklenirken hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
