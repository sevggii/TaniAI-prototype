#!/usr/bin/env python3
"""
Ultra Hassas Sistem Testi - 4 Hastalığı Mükemmel Ayırt Etme
"""

import warnings
warnings.filterwarnings('ignore')

def test_ultra_precise_system():
    """Ultra hassas sistemi test eder"""
    print("🎯 ULTRA HASSAS HASTALIK TANİ SİSTEMİ - TEST")
    print("="*60)
    
    try:
        from ultra_precise_predict import UltraPreciseDiseasePredictor
        
        # Ultra hassas modeli yükle
        predictor = UltraPreciseDiseasePredictor("ultra_precise_disease_model.pkl")
        
        if predictor.model_data is None:
            print("❌ Ultra hassas model yüklenemedi.")
            return False
        
        print("✅ Ultra hassas sistem yüklendi!")
        print(f"📊 Model türü: {type(predictor.model_data['model'])}")
        
        # Ultra hassas test senaryoları - hastalıklar arası farkları test eder
        ultra_test_cases = [
            # COVID-19 - Ayırıcı semptomlar
            {
                "input": "Çok yüksek ateşim var, nefes alamıyorum, koku alamıyorum, öksürüyorum",
                "expected": "COVID-19",
                "description": "COVID-19 ayırıcı semptomları (koku kaybı + nefes darlığı)"
            },
            {
                "input": "Ateşim var, koku ve tat kaybım var, nefes darlığım çok",
                "expected": "COVID-19",
                "description": "COVID-19 core semptomları"
            },
            {
                "input": "Öksürüyorum, nefes alamıyorum, koku alamıyorum, göğsümde ağrı var",
                "expected": "COVID-19",
                "description": "COVID-19 solunum komplikasyonları"
            },
            
            # Grip - Ayırıcı semptomlar
            {
                "input": "Ateşim var, vücudum çok ağrıyor, titreme tuttu, çok yorgunum",
                "expected": "Grip",
                "description": "Grip ayırıcı semptomları (vücut ağrısı + titreme)"
            },
            {
                "input": "Yüksek ateş, baş ağrısı, vücut ağrıları, titreme var",
                "expected": "Grip",
                "description": "Grip sistemik semptomları"
            },
            {
                "input": "Ateşim çok yüksek, her yerim ağrıyor, titreme var, bitkinim",
                "expected": "Grip",
                "description": "Şiddetli grip semptomları"
            },
            
            # Soğuk Algınlığı - Ayırıcı semptomlar
            {
                "input": "Burnum akıyor, hapşırıyorum, boğazım ağrıyor ama ateşim yok",
                "expected": "Soğuk Algınlığı",
                "description": "Soğuk algınlığı ayırıcı semptomları (burun akıntısı + hapşırma)"
            },
            {
                "input": "Burun tıkanıklığı, hafif öksürük, boğaz ağrısı, ateş yok",
                "expected": "Soğuk Algınlığı",
                "description": "Hafif soğuk algınlığı"
            },
            {
                "input": "Hapşırıyorum, burnum akıyor, hafif baş ağrısı, ateş yok",
                "expected": "Soğuk Algınlığı",
                "description": "Üst solunum yolu enfeksiyonu"
            },
            
            # Mevsimsel Alerji - Ayırıcı semptomlar
            {
                "input": "Gözlerim kaşınıyor, hapşırıyorum, burnum tıkanık ama ateşim yok",
                "expected": "Mevsimsel Alerji",
                "description": "Alerji ayırıcı semptomları (göz kaşıntısı + hapşırma)"
            },
            {
                "input": "Gözlerim sulanıyor, sürekli hapşırıyorum, burnum akıyor, ateş yok",
                "expected": "Mevsimsel Alerji",
                "description": "Şiddetli alerji semptomları"
            },
            {
                "input": "Göz kaşıntısı, hapşırma, burun tıkanıklığı, ateş yok, vücut ağrısı yok",
                "expected": "Mevsimsel Alerji",
                "description": "Klasik alerji belirtileri"
            },
            
            # Karışık/Borderline vakalar
            {
                "input": "Ateşim var, öksürüyorum ama koku kaybım yok",
                "expected": "Grip",
                "description": "COVID-19 vs Grip ayrımı"
            },
            {
                "input": "Burnum akıyor, hapşırıyorum ama göz kaşıntım yok",
                "expected": "Soğuk Algınlığı",
                "description": "Soğuk algınlığı vs Alerji ayrımı"
            },
            {
                "input": "Gözlerim kaşınıyor, hapşırıyorum ama ateşim yok, vücut ağrım yok",
                "expected": "Mevsimsel Alerji",
                "description": "Alerji vs diğer hastalıklar ayrımı"
            }
        ]
        
        print(f"🧪 {len(ultra_test_cases)} ultra hassas test senaryosu çalıştırılıyor...\n")
        
        correct_predictions = 0
        total_predictions = len(ultra_test_cases)
        
        # Kategori bazlı sonuçlar
        category_results = {
            "COVID-19": {"correct": 0, "total": 0},
            "Grip": {"correct": 0, "total": 0},
            "Soğuk Algınlığı": {"correct": 0, "total": 0},
            "Mevsimsel Alerji": {"correct": 0, "total": 0}
        }
        
        for i, test_case in enumerate(ultra_test_cases, 1):
            print(f"📋 Test {i}: {test_case['description']}")
            print(f"🔍 Giriş: '{test_case['input']}'")
            print(f"🎯 Beklenen: {test_case['expected']}")
            
            result = predictor.predict_disease(test_case['input'])
            
            if result.get('error'):
                print(f"❌ Hata: {result['error']}")
            else:
                prediction = result['prediction']
                confidence = result['confidence']
                max_prob = result['max_probability']
                
                print(f"🏥 Tahmin: {prediction}")
                print(f"📊 Güven: %{confidence*100:.1f}")
                print(f"🎲 Maksimum Olasılık: %{max_prob*100:.1f}")
                
                # Tespit edilen semptomları göster
                if result['detected_symptoms']:
                    detected = [f"{s}: {v:.1f}" for s, v in result['detected_symptoms'].items() if v > 0.1]
                    if detected:
                        print(f"🔍 Tespit edilen: {', '.join(detected)}")
                
                # Sonuç değerlendirmesi
                if prediction == test_case['expected']:
                    print("✅ DOĞRU TAHMİN!")
                    correct_predictions += 1
                    category_results[prediction]["correct"] += 1
                else:
                    print("❌ YANLIŞ TAHMİN!")
                    print(f"   Beklenen: {test_case['expected']}")
                    print(f"   Tahmin: {prediction}")
                
                category_results[test_case['expected']]["total"] += 1
                
                # En yüksek 3 olasılık
                sorted_probs = sorted(result['probabilities'].items(), key=lambda x: x[1], reverse=True)
                print("🎯 En yüksek 3 olasılık:")
                for j, (disease, prob) in enumerate(sorted_probs[:3], 1):
                    bar = "█" * int(prob * 15)
                    print(f"   {j}. {disease}: %{prob*100:5.1f} {bar}")
            
            print("-" * 60)
        
        # Sonuçları özetle
        accuracy = correct_predictions / total_predictions
        print(f"\n📊 ULTRA HASSAS TEST SONUÇLARI:")
        print("="*60)
        print(f"🎯 Toplam test: {total_predictions}")
        print(f"✅ Doğru tahmin: {correct_predictions}")
        print(f"❌ Yanlış tahmin: {total_predictions - correct_predictions}")
        print(f"📈 Genel doğruluk: %{accuracy*100:.1f}")
        
        if accuracy >= 0.95:
            print("🎉 MÜKEMMEL! Ultra hassas sistem %95+ doğruluk gösteriyor!")
            print("🏆 4 hastalık mükemmel şekilde ayırt ediliyor!")
        elif accuracy >= 0.90:
            print("✅ ÇOK İYİ! Ultra hassas sistem %90+ doğruluk gösteriyor!")
            print("👍 Hastalıklar çok iyi ayırt ediliyor!")
        elif accuracy >= 0.85:
            print("✅ İYİ! Ultra hassas sistem %85+ doğruluk gösteriyor!")
            print("👍 Sistem iyi çalışıyor!")
        else:
            print("⚠️ Sistem geliştirilebilir!")
        
        # Kategori bazlı performans
        print(f"\n📋 KATEGORİ BAZLI PERFORMANS:")
        for disease, stats in category_results.items():
            if stats["total"] > 0:
                disease_accuracy = stats["correct"] / stats["total"]
                print(f"   {disease}: {stats['correct']}/{stats['total']} (%{disease_accuracy*100:.1f})")
        
        return accuracy >= 0.90
        
    except Exception as e:
        print(f"❌ Test sırasında hata: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_ultra_precision():
    """Ultra hassasiyet gösterimi"""
    print("\n" + "="*60)
    print("🎯 ULTRA HASSASİYET GÖSTERİMİ")
    print("="*60)
    
    try:
        from ultra_precise_predict import UltraPreciseDiseasePredictor
        
        predictor = UltraPreciseDiseasePredictor("ultra_precise_disease_model.pkl")
        
        if predictor.model_data is None:
            print("❌ Ultra hassas model yüklenemedi.")
            return
        
        # Benzer semptomlarla farklı hastalıkları test et
        similar_symptoms = [
            {
                "input": "Ateşim var, öksürüyorum",
                "description": "Genel semptomlar - hangi hastalık?"
            },
            {
                "input": "Burnum akıyor, hapşırıyorum",
                "description": "Burun semptomları - soğuk algınlığı mı alerji mi?"
            },
            {
                "input": "Vücudum ağrıyor, ateşim var",
                "description": "Sistemik semptomlar - grip mi COVID mi?"
            }
        ]
        
        print("🔍 Benzer semptomlarla ultra hassas ayrım testi:")
        
        for i, test in enumerate(similar_symptoms, 1):
            print(f"\n📋 Test {i}: {test['description']}")
            print(f"🔍 Giriş: '{test['input']}'")
            
            result = predictor.predict_disease(test['input'])
            
            if not result.get('error'):
                prediction = result['prediction']
                confidence = result['confidence']
                
                print(f"🏥 Tahmin: {prediction}")
                print(f"📊 Güven: %{confidence*100:.1f}")
                
                # Tüm olasılıkları göster
                sorted_probs = sorted(result['probabilities'].items(), key=lambda x: x[1], reverse=True)
                print("🎯 Tüm olasılıklar:")
                for j, (disease, prob) in enumerate(sorted_probs, 1):
                    bar = "█" * int(prob * 20)
                    print(f"   {j}. {disease}: %{prob*100:5.1f} {bar}")
    
    except Exception as e:
        print(f"❌ Gösterim sırasında hata: {e}")

def main():
    """Ana fonksiyon"""
    print("🎯 ULTRA HASSAS HASTALIK TANİ SİSTEMİ")
    print("🏆 Hedef: 4 Hastalığı Mükemmel Ayırt Etme")
    
    # Ultra hassas test
    success = test_ultra_precise_system()
    
    # Hassasiyet gösterimi
    demonstrate_ultra_precision()
    
    print("\n" + "="*60)
    print("🎉 ULTRA HASSAS TEST TAMAMLANDI!")
    print("="*60)
    
    if success:
        print("✅ Ultra hassas sistem başarıyla çalışıyor!")
        print("🏆 4 hastalık mükemmel şekilde ayırt ediliyor!")
        print("🎯 Hedef %90+ başarıyla ulaşıldı!")
    else:
        print("⚠️ Sistem çalışıyor ancak ultra hassasiyet geliştirilebilir.")
    
    print("\n🏥 Sağlık uyarısı: Bu sistem sadece ön tanı amaçlıdır.")
    print("📞 Ciddi semptomlar için mutlaka doktora başvurun!")

if __name__ == "__main__":
    main()
