"""
İlaç Takibi Aciliyet Sistemi - Test Script
==========================================

Medication Urgency System'i test etmek için kapsamlı test aracı.
"""

import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Test için mock Session (gerçek DB olmadan çalışması için)
class MockSession:
    def query(self, *args, **kwargs):
        return self
    
    def filter(self, *args, **kwargs):
        return self
    
    def count(self):
        return 0
    
    def all(self):
        return []

# Import medication urgency system
try:
    from medication_urgency_system import (
        MedicationUrgencySystem, UrgencyAssessment, UrgencyLevel,
        format_urgency_assessment
    )
except ImportError:
    print("❌ medication_urgency_system.py bulunamadı!")
    sys.exit(1)

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class MedicationUrgencyTester:
    """İlaç aciliyet sistemi test sınıfı"""
    
    def __init__(self):
        # Mock DB session
        self.db = MockSession()
        self.urgency_system = MedicationUrgencySystem(self.db)
    
    def test_critical_medication_missed(self):
        """Test 1: Kritik ilaç kaçırıldı"""
        print("\n" + "="*70)
        print("TEST 1: Kritik İlaç Kaçırıldı (Warfarin)")
        print("="*70)
        
        medication_data = {
            'medication_name': 'WARFARIN',
            'dosage_amount': 5,
            'dosage_unit': 'mg',
            'frequency_type': 'once_daily'
        }
        
        context = {
            'missed_doses': 2,  # 2 doz kaçırılmış
            'active_medications': [],
            'side_effects': [],
            'compliance_rate': 0.6,
            'remaining_doses': 5,
            'frequency_per_day': 1
        }
        
        assessment = self.urgency_system.assess_medication_urgency(
            user_id=1,
            medication_data=medication_data,
            context=context
        )
        
        print(format_urgency_assessment(assessment))
        
        # Beklenen: CRITICAL veya HIGH
        assert assessment.urgency_score >= 6.0, "Kritik ilaç için düşük skor!"
        print("\n✅ Test başarılı - Yüksek aciliyet tespit edildi")
        return assessment
    
    def test_severe_drug_interaction(self):
        """Test 2: Şiddetli ilaç etkileşimi"""
        print("\n" + "="*70)
        print("TEST 2: Şiddetli İlaç Etkileşimi (Warfarin + Aspirin)")
        print("="*70)
        
        medication_data = {
            'medication_name': 'WARFARIN',
            'dosage_amount': 5,
            'dosage_unit': 'mg',
            'frequency_type': 'once_daily'
        }
        
        context = {
            'missed_doses': 0,
            'active_medications': [
                {'medication_name': 'ASPIRIN'}  # Tehlikeli etkileşim!
            ],
            'side_effects': [],
            'compliance_rate': 1.0,
            'remaining_doses': 30,
            'frequency_per_day': 1
        }
        
        assessment = self.urgency_system.assess_medication_urgency(
            user_id=1,
            medication_data=medication_data,
            context=context
        )
        
        print(format_urgency_assessment(assessment))
        
        # Beklenen: CRITICAL veya HIGH
        assert assessment.urgency_score >= 7.0, "Şiddetli etkileşim için düşük skor!"
        assert any(f['type'] == 'severe_interaction' for f in assessment.findings), \
            "Etkileşim bulgusu eksik!"
        print("\n✅ Test başarılı - Şiddetli etkileşim tespit edildi")
        return assessment
    
    def test_critical_side_effect(self):
        """Test 3: Kritik yan etki"""
        print("\n" + "="*70)
        print("TEST 3: Kritik Yan Etki")
        print("="*70)
        
        medication_data = {
            'medication_name': 'METHOTREXATE',
            'dosage_amount': 15,
            'dosage_unit': 'mg',
            'frequency_type': 'weekly'
        }
        
        context = {
            'missed_doses': 0,
            'active_medications': [],
            'side_effects': [
                {
                    'side_effect_name': 'Şiddetli karaciğer enzim yükselmesi',
                    'severity': 'critical'
                }
            ],
            'compliance_rate': 1.0,
            'remaining_doses': 8,
            'frequency_per_day': 1
        }
        
        assessment = self.urgency_system.assess_medication_urgency(
            user_id=1,
            medication_data=medication_data,
            context=context
        )
        
        print(format_urgency_assessment(assessment))
        
        # Beklenen: HIGH veya CRITICAL
        assert assessment.urgency_score >= 6.0, "Kritik yan etki için düşük skor!"
        print("\n✅ Test başarılı - Kritik yan etki tespit edildi")
        return assessment
    
    def test_overdose_risk(self):
        """Test 4: Doz aşımı riski"""
        print("\n" + "="*70)
        print("TEST 4: Doz Aşımı Riski")
        print("="*70)
        
        medication_data = {
            'medication_name': 'ACETAMINOPHEN',
            'dosage_amount': 1000,
            'dosage_unit': 'mg',
            'frequency_type': 'as_needed',
            'max_daily_dose': 4000  # 4g/gün limit
        }
        
        context = {
            'missed_doses': 0,
            'active_medications': [],
            'side_effects': [],
            'compliance_rate': 1.0,
            'daily_doses_taken': 5000,  # 5g alınmış - LİMİT AŞILDI!
            'remaining_doses': 20,
            'frequency_per_day': 4
        }
        
        assessment = self.urgency_system.assess_medication_urgency(
            user_id=1,
            medication_data=medication_data,
            context=context
        )
        
        print(format_urgency_assessment(assessment))
        
        # Beklenen: CRITICAL veya HIGH
        assert assessment.urgency_score >= 7.0, "Doz aşımı için düşük skor!"
        assert any(f['type'] == 'overdose_risk' for f in assessment.findings), \
            "Doz aşımı bulgusu eksik!"
        print("\n✅ Test başarılı - Doz aşımı riski tespit edildi")
        return assessment
    
    def test_refill_urgency(self):
        """Test 5: İlaç bitme aciliyeti"""
        print("\n" + "="*70)
        print("TEST 5: İlaç Bitme Aciliyeti")
        print("="*70)
        
        medication_data = {
            'medication_name': 'INSULIN',
            'dosage_amount': 10,
            'dosage_unit': 'units',
            'frequency_type': 'twice_daily'
        }
        
        context = {
            'missed_doses': 0,
            'active_medications': [],
            'side_effects': [],
            'compliance_rate': 1.0,
            'remaining_doses': 2,  # Sadece 2 doz kaldı!
            'frequency_per_day': 2  # Günde 2 doz = 1 günlük ilaç
        }
        
        assessment = self.urgency_system.assess_medication_urgency(
            user_id=1,
            medication_data=medication_data,
            context=context
        )
        
        print(format_urgency_assessment(assessment))
        
        # Beklenen: MODERATE veya HIGH
        assert assessment.urgency_score >= 5.0, "İlaç bitme için düşük skor!"
        print("\n✅ Test başarılı - İlaç bitme aciliyeti tespit edildi")
        return assessment
    
    def test_normal_medication(self):
        """Test 6: Normal ilaç (düşük aciliyet)"""
        print("\n" + "="*70)
        print("TEST 6: Normal İlaç Kullanımı (Düşük Aciliyet)")
        print("="*70)
        
        medication_data = {
            'medication_name': 'VITAMIN_D',
            'dosage_amount': 1000,
            'dosage_unit': 'IU',
            'frequency_type': 'once_daily'
        }
        
        context = {
            'missed_doses': 0,
            'active_medications': [],
            'side_effects': [],
            'compliance_rate': 1.0,
            'remaining_doses': 60,
            'frequency_per_day': 1
        }
        
        assessment = self.urgency_system.assess_medication_urgency(
            user_id=1,
            medication_data=medication_data,
            context=context
        )
        
        print(format_urgency_assessment(assessment))
        
        # Beklenen: LOW
        assert assessment.urgency_level == UrgencyLevel.LOW, "Normal ilaç için yüksek skor!"
        assert assessment.urgency_score < 4.0, "Düşük aciliyet bekleniyor!"
        print("\n✅ Test başarılı - Düşük aciliyet tespit edildi")
        return assessment
    
    def test_multiple_risk_factors(self):
        """Test 7: Çoklu risk faktörleri"""
        print("\n" + "="*70)
        print("TEST 7: Çoklu Risk Faktörleri (Kötü Senaryo)")
        print("="*70)
        
        medication_data = {
            'medication_name': 'LITHIUM',
            'dosage_amount': 300,
            'dosage_unit': 'mg',
            'frequency_type': 'twice_daily'
        }
        
        context = {
            'missed_doses': 3,  # Çok fazla kaçırılmış
            'active_medications': [
                {'medication_name': 'FUROSEMIDE'}  # Lityum toksisitesi riski
            ],
            'side_effects': [
                {
                    'side_effect_name': 'Titreme',
                    'severity': 'moderate'
                }
            ],
            'compliance_rate': 0.4,  # Çok düşük uyum
            'remaining_doses': 4,  # Az kalmış
            'frequency_per_day': 2,
            'disease_severity': 'severe'  # Ciddi hastalık
        }
        
        assessment = self.urgency_system.assess_medication_urgency(
            user_id=1,
            medication_data=medication_data,
            context=context
        )
        
        print(format_urgency_assessment(assessment))
        
        # Beklenen: CRITICAL
        assert assessment.urgency_score >= 8.0, "Çoklu risk için düşük skor!"
        assert assessment.urgency_level == UrgencyLevel.CRITICAL, "CRITICAL bekleniyor!"
        assert assessment.requires_immediate_attention, "Acil müdahale gerekli!"
        print("\n✅ Test başarılı - Kritik durum tespit edildi")
        return assessment
    
    def test_doctor_notification_creation(self):
        """Test 8: Doktor bildirimi oluşturma"""
        print("\n" + "="*70)
        print("TEST 8: Doktor Bildirimi Oluşturma")
        print("="*70)
        
        # Önce bir aciliyet değerlendirmesi yap
        medication_data = {
            'medication_name': 'WARFARIN',
            'dosage_amount': 5,
            'dosage_unit': 'mg',
            'frequency_type': 'once_daily'
        }
        
        context = {
            'missed_doses': 2,
            'active_medications': [{'medication_name': 'ASPIRIN'}],
            'side_effects': [],
            'compliance_rate': 0.6,
            'remaining_doses': 5,
            'frequency_per_day': 1
        }
        
        assessment = self.urgency_system.assess_medication_urgency(
            user_id=123,
            medication_data=medication_data,
            context=context
        )
        
        # Doktor bildirimi oluştur
        patient_info = {
            'user_id': 123,
            'name': 'Ahmet Yılmaz',
            'age': 65,
            'gender': 'male'
        }
        
        notification = self.urgency_system.create_doctor_notification(
            assessment=assessment,
            patient_info=patient_info,
            medication_data=medication_data
        )
        
        print("\n📞 DOKTOR BİLDİRİMİ:")
        print("="*70)
        print(f"Bildirim Tipi: {notification['notification_type']}")
        print(f"Aciliyet Seviyesi: {notification['urgency_level'].upper()}")
        print(f"Aciliyet Skoru: {notification['urgency_score']:.1f}/10")
        print(f"Acil Müdahale: {'EVET' if notification['requires_immediate_attention'] else 'HAYIR'}")
        print(f"\nHasta: {notification['patient']['name']} ({notification['patient']['age']} yaş)")
        print(f"İlaç: {notification['medication']['name']} - {notification['medication']['dosage']}")
        print(f"Müdahale Süresi: {notification['response_time']}")
        
        print(f"\nRisk Faktörleri:")
        for factor, score in notification['risk_factors'].items():
            if score > 0.3:
                print(f"  • {factor}: {score:.2f}")
        
        print(f"\nBulgular ({len(notification['findings'])}):")
        for finding in notification['findings']:
            print(f"  🔴 {finding['title']}")
            print(f"     {finding['description']}")
        
        # Assertions
        assert notification['notification_type'] == 'medication_urgency_alert'
        assert 'patient' in notification
        assert 'medication' in notification
        assert 'findings' in notification
        
        print("\n✅ Test başarılı - Doktor bildirimi oluşturuldu")
        return notification
    
    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print("\n" + "="*70)
        print("🧪 İLAÇ ACİLİYET SİSTEMİ - KAPSAMLI TEST")
        print("="*70)
        print(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        tests = [
            ("Kritik İlaç Kaçırıldı", self.test_critical_medication_missed),
            ("Şiddetli İlaç Etkileşimi", self.test_severe_drug_interaction),
            ("Kritik Yan Etki", self.test_critical_side_effect),
            ("Doz Aşımı Riski", self.test_overdose_risk),
            ("İlaç Bitme Aciliyeti", self.test_refill_urgency),
            ("Normal İlaç", self.test_normal_medication),
            ("Çoklu Risk Faktörleri", self.test_multiple_risk_factors),
            ("Doktor Bildirimi", self.test_doctor_notification_creation),
        ]
        
        passed = 0
        failed = 0
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                passed += 1
                results.append((test_name, "✅ BAŞARILI", result))
            except AssertionError as e:
                failed += 1
                results.append((test_name, f"❌ BAŞARISIZ: {e}", None))
                logger.error(f"Test başarısız: {test_name} - {e}")
            except Exception as e:
                failed += 1
                results.append((test_name, f"❌ HATA: {e}", None))
                logger.error(f"Test hatası: {test_name} - {e}")
        
        # Özet
        print("\n" + "="*70)
        print("📊 TEST SONUÇLARI ÖZETİ")
        print("="*70)
        print(f"Toplam Test: {len(tests)}")
        print(f"✅ Başarılı: {passed}")
        print(f"❌ Başarısız: {failed}")
        print(f"Başarı Oranı: {(passed/len(tests)*100):.1f}%")
        
        print("\n" + "="*70)
        print("Detaylı Sonuçlar:")
        print("="*70)
        for test_name, status, result in results:
            print(f"{status} - {test_name}")
            if result and hasattr(result, 'urgency_score'):
                print(f"   Skor: {result.urgency_score:.1f}/10 - Seviye: {result.urgency_level.value}")
        
        print("\n" + "="*70)
        print(f"Bitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        return passed == len(tests)


def interactive_test():
    """İnteraktif test modu"""
    print("="*70)
    print("🧪 İLAÇ ACİLİYET SİSTEMİ - İNTERAKTİF TEST")
    print("="*70)
    
    tester = MedicationUrgencyTester()
    
    while True:
        print("\nTest Seçenekleri:")
        print("1. Kritik ilaç kaçırıldı")
        print("2. Şiddetli ilaç etkileşimi")
        print("3. Kritik yan etki")
        print("4. Doz aşımı riski")
        print("5. İlaç bitme aciliyeti")
        print("6. Normal ilaç (düşük aciliyet)")
        print("7. Çoklu risk faktörleri")
        print("8. Doktor bildirimi")
        print("9. Tüm testleri çalıştır")
        print("0. Çıkış")
        
        choice = input("\nSeçim (0-9): ").strip()
        
        if choice == '0':
            print("\n👋 Çıkılıyor...")
            break
        elif choice == '1':
            tester.test_critical_medication_missed()
        elif choice == '2':
            tester.test_severe_drug_interaction()
        elif choice == '3':
            tester.test_critical_side_effect()
        elif choice == '4':
            tester.test_overdose_risk()
        elif choice == '5':
            tester.test_refill_urgency()
        elif choice == '6':
            tester.test_normal_medication()
        elif choice == '7':
            tester.test_multiple_risk_factors()
        elif choice == '8':
            tester.test_doctor_notification_creation()
        elif choice == '9':
            tester.run_all_tests()
        else:
            print("❌ Geçersiz seçim!")


def main():
    """Ana test fonksiyonu"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive':
            interactive_test()
        elif sys.argv[1] == '--all':
            tester = MedicationUrgencyTester()
            success = tester.run_all_tests()
            sys.exit(0 if success else 1)
        else:
            print("Kullanım:")
            print("  python test_medication_urgency.py           # İnteraktif mod")
            print("  python test_medication_urgency.py --all     # Tüm testler")
            print("  python test_medication_urgency.py --interactive  # İnteraktif")
    else:
        # Varsayılan: Tüm testleri çalıştır
        tester = MedicationUrgencyTester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

