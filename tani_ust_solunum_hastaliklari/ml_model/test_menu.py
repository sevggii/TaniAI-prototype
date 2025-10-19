#!/usr/bin/env python3
"""
Test Menu - Test Menüsü
Farklı test seçenekleri
"""

import warnings
warnings.filterwarnings('ignore')

def test_basic_system():
    """Temel sistem testi"""
    print("🧪 TEMEL SİSTEM TESTİ")
    print("="*50)
    
    try:
        from professional_medical_system import ProfessionalMedicalSystem
        
        medical_system = ProfessionalMedicalSystem()
        
        test_cases = [
            "Ateşim var, öksürüyorum",
            "Gözlerim kaşınıyor, hapşırıyorum",
            "Nefes alamıyorum, koku alamıyorum",
            "Vücudum ağrıyor, titreme var",
            "Burnum akıyor, hapşırıyorum"
        ]
        
        for i, symptoms in enumerate(test_cases, 1):
            print(f"📋 Test {i}: '{symptoms}'")
            result = medical_system.diagnose_patient(symptoms)
            print(f"🏥 Tahmin: {result.disease.value} (%{result.confidence*100:.1f} güven)")
            print(f"🎯 Şiddet: {result.severity_level.value}")
            print("-" * 50)
        
        print("✅ Temel sistem testi tamamlandı!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

def test_edge_cases():
    """Sınır durumları test et"""
    print("🔍 SINIR DURUMLARI TESTİ")
    print("="*50)
    
    try:
        from professional_medical_system import ProfessionalMedicalSystem
        
        medical_system = ProfessionalMedicalSystem()
        
        edge_cases = [
            "Sadece baş ağrım var",
            "Çok yorgunum, halsizim",
            "Ateşim yok ama öksürüyorum",
            "Gözlerim sulanıyor ama hapşırmıyorum",
            "Vücudum ağrıyor ama ateşim yok"
        ]
        
        for i, symptoms in enumerate(edge_cases, 1):
            print(f"📋 Sınır Test {i}: '{symptoms}'")
            result = medical_system.diagnose_patient(symptoms)
            print(f"🏥 Tahmin: {result.disease.value} (%{result.confidence*100:.1f} güven)")
            
            # Olasılık dağılımı
            sorted_probs = sorted(result.probabilities.items(), key=lambda x: x[1], reverse=True)
            print("🎲 Olasılıklar:")
            for j, (disease, prob) in enumerate(sorted_probs[:3], 1):
                print(f"   {j}. {disease}: %{prob*100:.1f}")
            print("-" * 50)
        
        print("✅ Sınır durumları testi tamamlandı!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

def test_confidence_levels():
    """Güven seviyelerini test et"""
    print("📊 GÜVEN SEVİYELERİ TESTİ")
    print("="*50)
    
    try:
        from professional_medical_system import ProfessionalMedicalSystem
        
        medical_system = ProfessionalMedicalSystem()
        
        confidence_tests = [
            {
                "symptoms": "Koku alamıyorum, nefes alamıyorum",
                "expected": "Yüksek güven (COVID-19)"
            },
            {
                "symptoms": "Ateşim var",
                "expected": "Düşük güven (belirsiz)"
            },
            {
                "symptoms": "Gözlerim kaşınıyor, hapşırıyorum, ateşim yok",
                "expected": "Yüksek güven (Alerji)"
            },
            {
                "symptoms": "Vücudum ağrıyor, titreme var, ateşim var",
                "expected": "Yüksek güven (Grip)"
            }
        ]
        
        for i, test in enumerate(confidence_tests, 1):
            print(f"📋 Güven Test {i}: {test['expected']}")
            print(f"🔍 Semptomlar: '{test['symptoms']}'")
            
            result = medical_system.diagnose_patient(test['symptoms'])
            
            print(f"🏥 Tahmin: {result.disease.value}")
            print(f"📊 Güven: %{result.confidence*100:.1f}")
            
            if result.confidence >= 0.9:
                print("✅ Çok yüksek güven")
            elif result.confidence >= 0.7:
                print("👍 Yüksek güven")
            elif result.confidence >= 0.5:
                print("⚠️ Orta güven")
            else:
                print("❌ Düşük güven - ek sorular gerekebilir")
            
            print("-" * 50)
        
        print("✅ Güven seviyeleri testi tamamlandı!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

def test_disease_differentiation():
    """Hastalık ayırımını test et"""
    print("🎯 HASTALIK AYIRIMI TESTİ")
    print("="*50)
    
    try:
        from professional_medical_system import ProfessionalMedicalSystem
        
        medical_system = ProfessionalMedicalSystem()
        
        differentiation_tests = [
            {
                "name": "COVID-19 Ayırıcı Semptomlar",
                "symptoms": "Koku alamıyorum, nefes alamıyorum, ateşim var",
                "expected": "COVID-19"
            },
            {
                "name": "Grip Ayırıcı Semptomlar", 
                "symptoms": "Vücudum çok ağrıyor, titreme var, ateşim var",
                "expected": "Grip"
            },
            {
                "name": "Soğuk Algınlığı Ayırıcı Semptomlar",
                "symptoms": "Burnum akıyor, hapşırıyorum, ateşim yok",
                "expected": "Soğuk Algınlığı"
            },
            {
                "name": "Alerji Ayırıcı Semptomlar",
                "symptoms": "Gözlerim kaşınıyor, hapşırıyorum, ateşim yok",
                "expected": "Mevsimsel Alerji"
            }
        ]
        
        correct_predictions = 0
        
        for i, test in enumerate(differentiation_tests, 1):
            print(f"📋 Ayırım Test {i}: {test['name']}")
            print(f"🔍 Semptomlar: '{test['symptoms']}'")
            print(f"🎯 Beklenen: {test['expected']}")
            
            result = medical_system.diagnose_patient(test['symptoms'])
            
            print(f"🏥 Tahmin: {result.disease.value}")
            print(f"📊 Güven: %{result.confidence*100:.1f}")
            
            if result.disease.value == test['expected']:
                print("✅ DOĞRU TAHMİN!")
                correct_predictions += 1
            else:
                print("❌ YANLIŞ TAHMİN!")
            
            print("-" * 50)
        
        print(f"📊 AYIRIM TEST SONUCU: {correct_predictions}/{len(differentiation_tests)} doğru")
        print(f"📈 Başarı Oranı: %{correct_predictions*100/len(differentiation_tests):.1f}")
        
        if correct_predictions == len(differentiation_tests):
            print("🎉 MÜKEMMEL! Tüm ayırımlar doğru!")
        elif correct_predictions >= 3:
            print("👍 ÇOK İYİ! Çoğu ayırım doğru!")
        else:
            print("⚠️ Geliştirilmesi gerekiyor.")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

def main():
    """Ana menü"""
    print("🏥 PROFESSIONAL MEDICAL SYSTEM - TEST MENÜSÜ")
    print("="*60)
    print("Hangi testi yapmak istiyorsunuz?")
    print()
    print("1. Temel Sistem Testi")
    print("2. Sınır Durumları Testi")
    print("3. Güven Seviyeleri Testi")
    print("4. Hastalık Ayırımı Testi")
    print("5. Tüm Testleri Çalıştır")
    print()
    
    choice = input("Seçiminiz (1-5): ").strip()
    
    if choice == "1":
        test_basic_system()
    elif choice == "2":
        test_edge_cases()
    elif choice == "3":
        test_confidence_levels()
    elif choice == "4":
        test_disease_differentiation()
    elif choice == "5":
        print("🚀 TÜM TESTLER ÇALIŞTIRILIYOR...")
        print("="*60)
        test_basic_system()
        print("\n")
        test_edge_cases()
        print("\n")
        test_confidence_levels()
        print("\n")
        test_disease_differentiation()
        print("\n🎉 TÜM TESTLER TAMAMLANDI!")
    else:
        print("❌ Geçersiz seçim!")
    
    print("\n🏥 Sağlık uyarısı: Bu sistem sadece ön tanı amaçlıdır.")
    print("📞 Ciddi semptomlar için mutlaka doktora başvurun!")

if __name__ == "__main__":
    main()
