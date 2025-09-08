#!/usr/bin/env python3
"""
Tanı hastalık sistemi test scripti
Baş dönmesi, halsizlik ve sürekli uyuma isteği semptomlarıyla test
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Proje dizinini Python path'e ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services import VitaminDiagnosisService, RiskAssessmentService, NutritionRecommendationService
from app.schemas import SymptomInput, UserProfileCreate, DiagnosisRequest

async def test_diagnosis_system():
    """Tanı sistemi test fonksiyonu"""
    
    print("🔍 Tanı Hastalık Sistemi Test Başlatılıyor...")
    print("=" * 60)
    
    # Test semptomları - kullanıcının belirttiği semptomlar
    symptoms = [
        SymptomInput(
            symptom_name="bas_donmesi",
            severity=3,  # Şiddetli
            duration_days=7
        ),
        SymptomInput(
            symptom_name="halsizlik", 
            severity=3,  # Şiddetli
            duration_days=10
        ),
        SymptomInput(
            symptom_name="yorgunluk",
            severity=3,  # Şiddetli
            duration_days=14
        ),
        SymptomInput(
            symptom_name="uyku_hali",
            severity=2,  # Orta
            duration_days=5
        )
    ]
    
    # Test kullanıcı profili
    user_profile = UserProfileCreate(
        diet_type="omnivore",
        activity_level="moderate",
        medical_conditions=[],
        medications=[],
        allergies=[],
        smoking_status="never",
        alcohol_consumption="none"
    )
    
    # Kullanıcı bilgileri (ayrı olarak)
    user_age = 30
    user_gender = "male"
    
    # Teşhis isteği
    diagnosis_request = DiagnosisRequest(
        symptoms=symptoms,
        user_profile=user_profile,
        additional_notes="Baş dönmesi, halsizlik ve sürekli uyuma isteği var. 2 haftadır devam ediyor."
    )
    
    print("📋 Test Semptomları:")
    for symptom in symptoms:
        print(f"   • {symptom.symptom_name}: Şiddet {symptom.severity} ({symptom.duration_days} gün)")
    
    print(f"\n👤 Kullanıcı Profili:")
    print(f"   • Yaş: {user_age}")
    print(f"   • Cinsiyet: {user_gender}")
    print(f"   • Diyet: {user_profile.diet_type}")
    print(f"   • Aktivite: {user_profile.activity_level}")
    
    print("\n" + "=" * 60)
    print("🔬 ANALİZ BAŞLIYOR...")
    print("=" * 60)
    
    try:
        # Servisleri başlat
        diagnosis_service = VitaminDiagnosisService()
        risk_service = RiskAssessmentService()
        nutrition_service = NutritionRecommendationService()
        
        print("✅ Servisler başlatıldı")
        
        # Semptom analizi yap
        print("\n🔍 Semptom analizi yapılıyor...")
        diagnosis_result = await diagnosis_service.analyze_symptoms(
            symptoms=symptoms,
            user_profile=user_profile
        )
        
        print("✅ Semptom analizi tamamlandı")
        
        # Sonuçları göster
        print("\n" + "=" * 60)
        print("📊 TEŞHİS SONUÇLARI")
        print("=" * 60)
        
        if 'primary_diagnosis' in diagnosis_result:
            primary = diagnosis_result['primary_diagnosis']
            print(f"🎯 Ana Teşhis: {primary.get('nutrient', 'Bilinmiyor')}")
            print(f"📈 Eksiklik Olasılığı: %{primary.get('deficiency_probability', 0) * 100:.1f}")
            print(f"⚠️ Risk Seviyesi: {primary.get('risk_level', 'Bilinmiyor')}")
            print(f"🎯 Güven: %{primary.get('confidence', 0) * 100:.1f}")
            
            if 'recommendations' in primary:
                rec = primary['recommendations']
                if 'immediate_actions' in rec:
                    print(f"\n🚨 Acil Eylemler:")
                    for action in rec['immediate_actions']:
                        print(f"   • {action}")
                
                if 'dietary_recommendations' in rec:
                    print(f"\n🍎 Beslenme Önerileri:")
                    for rec_item in rec['dietary_recommendations']:
                        print(f"   • {rec_item}")
                
                if 'supplement_recommendations' in rec:
                    print(f"\n💊 Takviye Önerileri:")
                    for rec_item in rec['supplement_recommendations']:
                        print(f"   • {rec_item}")
                
                if 'tests_recommended' in rec:
                    print(f"\n🧪 Önerilen Testler:")
                    for test in rec['tests_recommended']:
                        print(f"   • {test}")
        
        # Tüm sonuçları göster
        if 'all_results' in diagnosis_result:
            print(f"\n📋 Tüm Nutrient Analizleri:")
            for nutrient, result in diagnosis_result['all_results'].items():
                if isinstance(result, dict) and 'deficiency_probability' in result:
                    prob = result.get('deficiency_probability', 0)
                    risk = result.get('risk_level', 'Bilinmiyor')
                    print(f"   • {nutrient}: %{prob * 100:.1f} ({risk})")
        
        # Risk değerlendirmesi
        print("\n" + "=" * 60)
        print("⚠️ RİSK DEĞERLENDİRMESİ")
        print("=" * 60)
        
        risk_assessment = await risk_service.assess_risk(
            diagnosis_result=diagnosis_result,
            user_profile=user_profile
        )
        
        print(f"🎯 Genel Risk Seviyesi: {risk_assessment.overall_risk_level}")
        print(f"📊 Risk Skoru: {risk_assessment.risk_score:.1f}/100")
        
        print(f"\n📈 Risk Faktörleri:")
        for factor, score in risk_assessment.risk_factors.items():
            print(f"   • {factor}: {score:.1f}")
        
        if risk_assessment.recommendations:
            print(f"\n💡 Risk Azaltma Önerileri:")
            for rec in risk_assessment.recommendations:
                print(f"   • {rec}")
        
        if risk_assessment.urgent_actions:
            print(f"\n🚨 Acil Eylemler:")
            for action in risk_assessment.urgent_actions:
                print(f"   • {action}")
        
        # Beslenme önerileri
        print("\n" + "=" * 60)
        print("🍎 BESLENME ÖNERİLERİ")
        print("=" * 60)
        
        nutrition_recommendations = await nutrition_service.get_recommendations(
            diagnosis_result=diagnosis_result,
            user_profile=user_profile
        )
        
        if nutrition_recommendations.dietary_recommendations:
            print("🥗 Diyet Önerileri:")
            for rec in nutrition_recommendations.dietary_recommendations:
                print(f"   • {rec}")
        
        if nutrition_recommendations.supplement_recommendations:
            print("\n💊 Takviye Önerileri:")
            for rec in nutrition_recommendations.supplement_recommendations:
                print(f"   • {rec}")
        
        if nutrition_recommendations.foods_to_include:
            print("\n✅ Tüketilmesi Gereken Besinler:")
            for food in nutrition_recommendations.foods_to_include:
                print(f"   • {food}")
        
        if nutrition_recommendations.foods_to_avoid:
            print("\n❌ Kaçınılması Gereken Besinler:")
            for food in nutrition_recommendations.foods_to_avoid:
                print(f"   • {food}")
        
        # Klinik uyarılar
        if 'clinical_warnings' in diagnosis_result:
            print("\n" + "=" * 60)
            print("⚠️ KLİNİK UYARILAR")
            print("=" * 60)
            for warning in diagnosis_result['clinical_warnings']:
                print(f"   {warning}")
        
        print("\n" + "=" * 60)
        print("✅ TEST TAMAMLANDI")
        print("=" * 60)
        
        # JSON çıktısı
        print("\n📄 Detaylı JSON Çıktısı:")
        print(json.dumps(diagnosis_result, indent=2, ensure_ascii=False, default=str))
        
    except Exception as e:
        print(f"❌ Test hatası: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_diagnosis_system())
