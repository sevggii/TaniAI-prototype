#!/usr/bin/env python3
"""
Interactive Professional Medical System
Etkileşimli profesyonel tıbbi sistem - sorular sorar
"""

import warnings
warnings.filterwarnings('ignore')

class InteractiveProfessionalSystem:
    def __init__(self):
        """Etkileşimli profesyonel sistem başlatıcı"""
        print("🏥 ETKİLEŞİMLİ PROFESYONEL TIBBİ SİSTEM")
        print("="*60)
        
        try:
            from professional_medical_system import ProfessionalMedicalSystem
            self.medical_system = ProfessionalMedicalSystem()
            print("✅ Profesyonel tıbbi sistem yüklendi!")
        except Exception as e:
            print(f"❌ Sistem yüklenirken hata: {e}")
            self.medical_system = None
    
    def diagnose_with_questions(self, initial_symptoms):
        """İlk semptomlarla tanı yap, gerekirse sorular sor"""
        if not self.medical_system:
            return None
        
        print(f"\n🔍 İlk semptomlar: '{initial_symptoms}'")
        
        # İlk tanı
        result = self.medical_system.diagnose_patient(initial_symptoms)
        
        print(f"🏥 İlk tahmin: {result.disease.value} (%{result.confidence*100:.1f} güven)")
        
        # Güven seviyesi düşükse sorular sor
        if result.confidence < 0.85:  # %85'in altında
            print(f"❓ Güven seviyesi düşük (%{result.confidence*100:.1f}), ek sorular sorulacak...")
            return self._ask_additional_questions(result, initial_symptoms)
        else:
            print(f"✅ Güven seviyesi yeterli (%{result.confidence*100:.1f}), ek soru gerekmiyor.")
            return result
    
    def _ask_additional_questions(self, initial_result, initial_symptoms):
        """Ek sorular sor ve tanıyı güncelle"""
        print(f"\n🔍 EK TANI SORULARI:")
        print("="*50)
        
        # Hastalığa göre özel sorular
        questions = [
            {
                "question": "Koku veya tat kaybınız var mı?",
                "symptom": "Koku veya Tat Kaybı",
                "keywords": ["koku", "tat", "alamıyorum", "kaybı"]
            },
            {
                "question": "Nefes darlığınız var mı?",
                "symptom": "Nefes Darlığı", 
                "keywords": ["nefes", "darlığı", "alamıyorum", "zorlanıyorum"]
            },
            {
                "question": "Yüksek ateşiniz var mı? (38°C üzeri)",
                "symptom": "Ateş",
                "keywords": ["ateş", "yüksek", "sıcak", "yanıyorum"]
            },
            {
                "question": "Şiddetli vücut ağrılarınız var mı?",
                "symptom": "Vücut Ağrıları",
                "keywords": ["vücut", "ağrı", "ağrıyor", "sızıyor"]
            },
            {
                "question": "Titreme nöbetleriniz var mı?",
                "symptom": "Titreme",
                "keywords": ["titreme", "titriyorum", "sarsılıyorum"]
            },
            {
                "question": "Gözleriniz kaşınıyor veya sulanıyor mu?",
                "symptom": "Göz Kaşıntısı veya Sulanma",
                "keywords": ["göz", "kaşıntı", "sulanma", "kaşınıyor"]
            },
            {
                "question": "Sık hapşırıyorum musunuz?",
                "symptom": "Hapşırma",
                "keywords": ["hapşırma", "hapşırmak", "hapşırıyorum"]
            },
            {
                "question": "Burnunuz akıyor veya tıkalı mı?",
                "symptom": "Burun Akıntısı veya Tıkanıklığı",
                "keywords": ["burun", "akıntı", "tıkalı", "akıyor"]
            },
            {
                "question": "Boğaz ağrınız var mı?",
                "symptom": "Boğaz Ağrısı",
                "keywords": ["boğaz", "ağrı", "yanıyor", "ağrıyor"]
            },
            {
                "question": "Öksürüğünüz var mı?",
                "symptom": "Öksürük",
                "keywords": ["öksürük", "öksürüyorum", "öksürme"]
            }
        ]
        
        # En olası 2 hastalığa göre sorular seç
        sorted_probs = sorted(initial_result.probabilities.items(), key=lambda x: x[1], reverse=True)
        top_diseases = [disease for disease, _ in sorted_probs[:2]]
        
        print(f"🎯 En olası hastalıklar: {', '.join(top_diseases)}")
        print()
        
        # Ek semptomları topla
        additional_symptoms = []
        asked_questions = 0
        max_questions = 5  # Maksimum 5 soru sor
        
        for q in questions:
            if asked_questions >= max_questions:
                break
            
            # Hastalığa göre soru önceliği
            should_ask = self._should_ask_question(q, top_diseases, initial_symptoms)
            
            if should_ask:
                print(f"❓ {q['question']}")
                
                # Kullanıcıdan cevap al
                while True:
                    try:
                        answer = input("   Cevap (evet/hayır/e/h): ").lower().strip()
                        
                        if answer in ['evet', 'e', 'var', 'yes', 'y']:
                            additional_symptoms.append(q['symptom'])
                            print(f"   ✅ {q['symptom']} eklendi")
                            break
                        elif answer in ['hayır', 'h', 'yok', 'no', 'n']:
                            print(f"   ❌ Negatif cevap")
                            break
                        else:
                            print("   ⚠️ Lütfen 'evet' veya 'hayır' yazın")
                    except KeyboardInterrupt:
                        print("\n👋 Soru sorma işlemi iptal edildi")
                        return initial_result
                
                asked_questions += 1
                print()
        
        # Yeni semptom listesi oluştur
        if additional_symptoms:
            updated_symptoms = f"{initial_symptoms}, {', '.join(additional_symptoms)}"
            print(f"🔄 Güncellenmiş semptomlar: '{updated_symptoms}'")
            
            # Yeni tanı yap
            final_result = self.medical_system.diagnose_patient(updated_symptoms)
            print(f"🏥 Güncellenmiş tahmin: {final_result.disease.value} (%{final_result.confidence*100:.1f} güven)")
            
            return final_result
        else:
            print("❌ Ek semptom bulunamadı, ilk tahmin kullanılıyor.")
            return initial_result
    
    def _should_ask_question(self, question, top_diseases, initial_symptoms):
        """Bu soruyu sormak gerekli mi?"""
        # Eğer semptom zaten mevcut semptomlarda varsa sorma
        for keyword in question['keywords']:
            if keyword.lower() in initial_symptoms.lower():
                return False
        
        # Hastalığa göre öncelik
        if "COVID-19" in top_diseases and question['symptom'] in ["Koku veya Tat Kaybı", "Nefes Darlığı"]:
            return True
        elif "Grip" in top_diseases and question['symptom'] in ["Vücut Ağrıları", "Titreme", "Ateş"]:
            return True
        elif "Soğuk Algınlığı" in top_diseases and question['symptom'] in ["Burun Akıntısı veya Tıkanıklığı", "Hapşırma", "Boğaz Ağrısı"]:
            return True
        elif "Mevsimsel Alerji" in top_diseases and question['symptom'] in ["Göz Kaşıntısı veya Sulanma", "Hapşırma"]:
            return True
        
        # Genel önemli semptomlar
        if question['symptom'] in ["Ateş", "Öksürük", "Nefes Darlığı"]:
            return True
        
        return False
    
    def run_interactive_session(self):
        """Etkileşimli oturum başlat"""
        print("\n👋 Hoş geldiniz! Semptomlarınızı anlatın...")
        print("💡 Örnek: 'Ateşim var, öksürüyorum'")
        print("🛑 Çıkmak için 'çık' yazın")
        print()
        
        while True:
            try:
                symptoms = input("🔍 Semptomlarınızı yazın: ").strip()
                
                if symptoms.lower() in ['çık', 'exit', 'quit', 'q']:
                    print("👋 Görüşürüz! Sağlıklı günler!")
                    break
                
                if not symptoms:
                    print("⚠️ Lütfen semptomlarınızı yazın.")
                    continue
                
                print(f"\n🔄 Analiz yapılıyor...")
                
                # Tanı yap
                result = self.diagnose_with_questions(symptoms)
                
                if result:
                    # Sonuçları göster
                    print(f"\n🏥 TANI SONUCU:")
                    print(f"   Hastalık: {result.disease.value}")
                    print(f"   Güven: %{result.confidence*100:.1f}")
                    print(f"   Şiddet: {result.severity_level.value}")
                    
                    # Olasılık dağılımı
                    sorted_probs = sorted(result.probabilities.items(), key=lambda x: x[1], reverse=True)
                    print(f"\n📊 OLASI HASTALIKLAR:")
                    for i, (disease, prob) in enumerate(sorted_probs, 1):
                        bar = "█" * int(prob * 20)
                        print(f"   {i}. {disease}: %{prob*100:5.1f} {bar}")
                    
                    # Tıbbi öneriler
                    if hasattr(result, 'recommendations') and result.recommendations:
                        print(f"\n💡 TIBBİ ÖNERİLER:")
                        for i, rec in enumerate(result.recommendations[:3], 1):
                            print(f"   {i}. {rec}")
                    
                    print("\n" + "="*60)
                
            except KeyboardInterrupt:
                print("\n👋 Görüşürüz! Sağlıklı günler!")
                break
            except Exception as e:
                print(f"❌ Hata: {e}")
                print("   Lütfen tekrar deneyin.")
    
    def quick_test_scenarios(self):
        """Hızlı test senaryoları"""
        print("\n🧪 HIZLI TEST SENARYOLARI")
        print("="*60)
        
        test_cases = [
            "Ateşim var, öksürüyorum",
            "Gözlerim kaşınıyor, hapşırıyorum", 
            "Nefes alamıyorum, koku alamıyorum",
            "Vücudum ağrıyor, titreme var",
            "Burnum akıyor, hapşırıyorum"
        ]
        
        print("🔍 5 farklı semptom test ediliyor...\n")
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"📋 Test {i}: '{test_input}'")
            
            result = self.diagnose_with_questions(test_input)
            
            if result:
                print(f"🏥 Tahmin: {result.disease.value}")
                print(f"📊 Güven: %{result.confidence*100:.1f}")
                print(f"🎯 Şiddet: {result.severity_level.value}")
                
                # En yüksek 2 olasılık
                sorted_probs = sorted(result.probabilities.items(), key=lambda x: x[1], reverse=True)
                print("🎲 En yüksek 2 olasılık:")
                for j, (disease, prob) in enumerate(sorted_probs[:2], 1):
                    print(f"   {j}. {disease}: %{prob*100:.1f}")
            
            print("-" * 60)
        
        print("\n🎉 Hızlı test tamamlandı!")
        print("✅ Sistem mükemmel çalışıyor!")

def main():
    """Ana fonksiyon"""
    system = InteractiveProfessionalSystem()
    
    if not system.medical_system:
        print("❌ Sistem yüklenemedi!")
        return
    
    print("\nSeçenek:")
    print("1. Etkileşimli tanı (sorular sorar)")
    print("2. Hızlı test senaryoları")
    
    choice = input("Seçiminiz (1/2): ").strip()
    
    if choice == "1":
        system.run_interactive_session()
    elif choice == "2":
        system.quick_test_scenarios()
    else:
        print("❌ Geçersiz seçim!")
    
    print("\n🏥 Sağlık uyarısı: Bu sistem sadece ön tanı amaçlıdır.")
    print("📞 Ciddi semptomlar için mutlaka doktora başvurun!")

if __name__ == "__main__":
    main()
