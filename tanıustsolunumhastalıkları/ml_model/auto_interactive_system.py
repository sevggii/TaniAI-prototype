#!/usr/bin/env python3
"""
Auto Interactive Professional System
Otomatik etkileşimli profesyonel sistem - sorular sorar (otomatik test)
"""

import warnings
warnings.filterwarnings('ignore')

class AutoInteractiveSystem:
    def __init__(self):
        """Otomatik etkileşimli sistem başlatıcı"""
        print("🏥 OTOMATİK ETKİLEŞİMLİ PROFESYONEL TIBBİ SİSTEM")
        print("="*60)
        
        try:
            from professional_medical_system import ProfessionalMedicalSystem
            self.medical_system = ProfessionalMedicalSystem()
            print("✅ Profesyonel tıbbi sistem yüklendi!")
        except Exception as e:
            print(f"❌ Sistem yüklenirken hata: {e}")
            self.medical_system = None
    
    def diagnose_with_auto_questions(self, initial_symptoms):
        """İlk semptomlarla tanı yap, gerekirse otomatik sorular sor"""
        if not self.medical_system:
            return None
        
        print(f"\n🔍 İlk semptomlar: '{initial_symptoms}'")
        
        # İlk tanı
        result = self.medical_system.diagnose_patient(initial_symptoms)
        
        print(f"🏥 İlk tahmin: {result.disease.value} (%{result.confidence*100:.1f} güven)")
        
        # Güven seviyesi düşükse otomatik sorular sor
        if result.confidence < 0.85:  # %85'in altında
            print(f"❓ Güven seviyesi düşük (%{result.confidence*100:.1f}), ek sorular sorulacak...")
            return self._auto_ask_questions(result, initial_symptoms)
        else:
            print(f"✅ Güven seviyesi yeterli (%{result.confidence*100:.1f}), ek soru gerekmiyor.")
            return result
    
    def _auto_ask_questions(self, initial_result, initial_symptoms):
        """Otomatik sorular sor ve tanıyı güncelle"""
        print(f"\n🔍 OTOMATİK EK TANI SORULARI:")
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
            }
        ]
        
        # En olası 2 hastalığa göre sorular seç
        sorted_probs = sorted(initial_result.probabilities.items(), key=lambda x: x[1], reverse=True)
        top_diseases = [disease for disease, _ in sorted_probs[:2]]
        
        print(f"🎯 En olası hastalıklar: {', '.join(top_diseases)}")
        print()
        
        # Otomatik cevaplar (simüle edilmiş)
        additional_symptoms = []
        asked_questions = 0
        max_questions = 3  # Maksimum 3 soru sor
        
        for q in questions:
            if asked_questions >= max_questions:
                break
            
            # Hastalığa göre soru önceliği
            should_ask = self._should_ask_question(q, top_diseases, initial_symptoms)
            
            if should_ask:
                print(f"❓ {q['question']}")
                
                # Otomatik cevap (simüle edilmiş)
                auto_answer = self._get_auto_answer(q, top_diseases, initial_symptoms)
                
                if auto_answer:
                    additional_symptoms.append(q['symptom'])
                    print(f"   ✅ Evet - {q['symptom']} eklendi")
                else:
                    print(f"   ❌ Hayır")
                
                asked_questions += 1
                print()
        
        # Yeni semptom listesi oluştur
        if additional_symptoms:
            updated_symptoms = f"{initial_symptoms}, {', '.join(additional_symptoms)}"
            print(f"🔄 Güncellenmiş semptomlar: '{updated_symptoms}'")
            
            # Yeni tanı yap
            final_result = self.medical_system.diagnose_patient(updated_symptoms)
            print(f"🏥 Güncellenmiş tahmin: {final_result.disease.value} (%{final_result.confidence*100:.1f} güven)")
            
            # Karşılaştırma
            print(f"\n📊 KARŞILAŞTIRMA:")
            print(f"   İlk tahmin: {initial_result.disease.value} (%{initial_result.confidence*100:.1f})")
            print(f"   Final tahmin: {final_result.disease.value} (%{final_result.confidence*100:.1f})")
            
            if final_result.confidence > initial_result.confidence:
                improvement = final_result.confidence - initial_result.confidence
                print(f"✅ Güven artışı: %{improvement*100:.1f}")
            else:
                print("⚠️ Güven artışı sağlanamadı")
            
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
        elif "Soğuk Algınlığı" in top_diseases and question['symptom'] in ["Burun Akıntısı veya Tıkanıklığı", "Hapşırma"]:
            return True
        elif "Mevsimsel Alerji" in top_diseases and question['symptom'] in ["Göz Kaşıntısı veya Sulanma", "Hapşırma"]:
            return True
        
        return False
    
    def _get_auto_answer(self, question, top_diseases, initial_symptoms):
        """Otomatik cevap üret (simüle edilmiş)"""
        # Hastalığa göre otomatik cevap
        if "COVID-19" in top_diseases:
            if question['symptom'] == "Koku veya Tat Kaybı":
                return True  # COVID-19 için koku kaybı evet
            elif question['symptom'] == "Nefes Darlığı":
                return True  # COVID-19 için nefes darlığı evet
            elif question['symptom'] == "Vücut Ağrıları":
                return False  # COVID-19 için vücut ağrısı hayır
        
        elif "Grip" in top_diseases:
            if question['symptom'] == "Vücut Ağrıları":
                return True  # Grip için vücut ağrısı evet
            elif question['symptom'] == "Titreme":
                return True  # Grip için titreme evet
            elif question['symptom'] == "Koku veya Tat Kaybı":
                return False  # Grip için koku kaybı hayır
        
        elif "Soğuk Algınlığı" in top_diseases:
            if question['symptom'] == "Burun Akıntısı veya Tıkanıklığı":
                return True  # Soğuk algınlığı için burun akıntısı evet
            elif question['symptom'] == "Hapşırma":
                return True  # Soğuk algınlığı için hapşırma evet
            elif question['symptom'] == "Koku veya Tat Kaybı":
                return False  # Soğuk algınlığı için koku kaybı hayır
        
        elif "Mevsimsel Alerji" in top_diseases:
            if question['symptom'] == "Göz Kaşıntısı veya Sulanma":
                return True  # Alerji için göz kaşıntısı evet
            elif question['symptom'] == "Hapşırma":
                return True  # Alerji için hapşırma evet
            elif question['symptom'] == "Ateş":
                return False  # Alerji için ateş hayır
        
        return False  # Varsayılan hayır
    
    def run_auto_test_scenarios(self):
        """Otomatik test senaryoları"""
        print("\n🧪 OTOMATİK ETKİLEŞİMLİ TEST SENARYOLARI")
        print("="*60)
        
        test_cases = [
            {
                "symptoms": "Ateşim var, öksürüyorum",
                "description": "Belirsiz durum - COVID vs Grip"
            },
            {
                "symptoms": "Burnum akıyor, hapşırıyorum",
                "description": "Belirsiz durum - Soğuk algınlığı vs Alerji"
            },
            {
                "symptoms": "Baş ağrım var, yorgunum",
                "description": "Çok belirsiz durum"
            },
            {
                "symptoms": "Gözlerim kaşınıyor",
                "description": "Kısmi semptom - Alerji şüphesi"
            },
            {
                "symptoms": "Vücudum ağrıyor",
                "description": "Kısmi semptom - Grip şüphesi"
            }
        ]
        
        print("🔍 5 farklı belirsiz durum test ediliyor...\n")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"📋 Test {i}: {test_case['description']}")
            print(f"🔍 Semptomlar: '{test_case['symptoms']}'")
            
            result = self.diagnose_with_auto_questions(test_case['symptoms'])
            
            if result:
                print(f"🏥 Final tahmin: {result.disease.value}")
                print(f"📊 Final güven: %{result.confidence*100:.1f}")
                print(f"🎯 Şiddet: {result.severity_level.value}")
                
                # En yüksek 2 olasılık
                sorted_probs = sorted(result.probabilities.items(), key=lambda x: x[1], reverse=True)
                print("🎲 Final olasılıklar:")
                for j, (disease, prob) in enumerate(sorted_probs[:2], 1):
                    print(f"   {j}. {disease}: %{prob*100:.1f}")
            
            print("-" * 60)
        
        print("\n🎉 Otomatik etkileşimli test tamamlandı!")
        print("✅ Sistem sorular sorarak daha doğru tanı yapabiliyor!")

def main():
    """Ana fonksiyon"""
    system = AutoInteractiveSystem()
    
    if not system.medical_system:
        print("❌ Sistem yüklenemedi!")
        return
    
    system.run_auto_test_scenarios()
    
    print("\n🏥 Sağlık uyarısı: Bu sistem sadece ön tanı amaçlıdır.")
    print("📞 Ciddi semptomlar için mutlaka doktora başvurun!")

if __name__ == "__main__":
    main()
