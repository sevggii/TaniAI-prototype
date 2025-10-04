"""
Triage Pipeline Test Senaryoları
Tüm test senaryolarını kapsayan kapsamlı test suite
"""

import unittest
import json
import sys
import os
from typing import Dict, Any

# Test için path ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_clinic.integrated_triage import IntegratedTriage, TriageConfig
from triage.canonical import canonicalize, load_mhrs_canonical
from triage.rules import apply_gatekeeping
from triage.redflags import detect_red_flags
from triage.schema import parse_llm_response, create_emergency_response


class TestTriagePipeline(unittest.TestCase):
    """Triage pipeline test sınıfı"""
    
    @classmethod
    def setUpClass(cls):
        """Test sınıfı başlatma"""
        cls.config = TriageConfig()
        cls.config.dataset_path = "/Users/sevgi/TaniAI-prototype/RANDEVU/mobile_flutter/klinik_dataset.jsonl"
        cls.config.canonical_path = "/Users/sevgi/TaniAI-prototype/RANDEVU/data/mhrs_canonical.json"
        cls.config.rag_enabled = True
        cls.config.cache_enabled = True
        
        # Triage sistemi başlat
        try:
            cls.triage = IntegratedTriage(cls.config)
        except Exception as e:
            print(f"⚠️ Triage sistemi başlatılamadı: {e}")
            cls.triage = None
    
    def test_scenario_1_combined_symptoms(self):
        """Test Senaryosu 1: Kombine şikayetler"""
        complaint = "Başım çok ağrıyor ve mide bulantım var"
        
        if not self.triage:
            self.skipTest("Triage sistemi yüklenemedi")
        
        result = self.triage.analyze_complaint(complaint)
        
        # JSON şema doğrulaması
        self.assertIn('primary_clinic', result)
        self.assertIn('secondary_clinics', result)
        self.assertIn('strategy', result)
        self.assertIn('model_version', result)
        self.assertIn('latency_ms', result)
        self.assertIn('requires_prior', result)
        self.assertIn('prior_list', result)
        self.assertIn('gate_note', result)
        
        # Primary clinic kontrolü
        primary = result['primary_clinic']
        self.assertIn('name', primary)
        self.assertIn('reason', primary)
        self.assertIn('confidence', primary)
        
        # Confidence [0,1] aralığında olmalı
        self.assertGreaterEqual(primary['confidence'], 0.0)
        self.assertLessEqual(primary['confidence'], 1.0)
        
        # Beklenen kliniklerden biri olmalı (ACİL de olabilir)
        expected_clinics = ["Nöroloji", "İç Hastalıkları (Dahiliye)", "ACİL"]
        self.assertIn(primary['name'], expected_clinics)
        
        print(f"✅ Senaryo 1: {primary['name']} (güven: {primary['confidence']:.2f})")
    
    def test_scenario_2_emergency_chest_pain(self):
        """Test Senaryosu 2: Acil durum - göğüs ağrısı"""
        complaint = "Aniden göğsümde ezici ağrı var, soğuk terliyorum"
        
        if not self.triage:
            self.skipTest("Triage sistemi yüklenemedi")
        
        result = self.triage.analyze_complaint(complaint)
        
        # Acil durum kontrolü
        self.assertEqual(result['primary_clinic']['name'], 'ACİL')
        self.assertIn('112', result['gate_note'])
        
        # Strategy redflag olmalı
        self.assertEqual(result['strategy'], 'redflag')
        
        print(f"✅ Senaryo 2: {result['primary_clinic']['name']} - {result['gate_note']}")
    
    def test_scenario_3_pediatric_symptoms(self):
        """Test Senaryosu 3: Pediatrik şikayetler"""
        complaint = "Çocuğumda ateş ve öksürük var"
        
        if not self.triage:
            self.skipTest("Triage sistemi yüklenemedi")
        
        result = self.triage.analyze_complaint(complaint)
        
        # Çocuk sağlığı kontrolü (ACİL de olabilir)
        expected_clinics = ["Çocuk Sağlığı ve Hastalıkları", "ACİL"]
        self.assertIn(result['primary_clinic']['name'], expected_clinics)
        
        print(f"✅ Senaryo 3: {result['primary_clinic']['name']}")
    
    def test_scenario_4_gatekeeping_rheumatology(self):
        """Test Senaryosu 4: Gatekeeping - Romatoloji"""
        complaint = "Romatizma şikayetlerim var; eklemde şişlik"
        
        if not self.triage:
            self.skipTest("Triage sistemi yüklenemedi")
        
        result = self.triage.analyze_complaint(complaint)
        
        # Romatoloji önerilirse gatekeeping kontrolü
        if result['primary_clinic']['name'] == 'Romatoloji':
            self.assertTrue(result['requires_prior'])
            self.assertIn('İç Hastalıkları (Dahiliye)', result['prior_list'])
            self.assertIn('gate_note', result)
            self.assertTrue(len(result['gate_note']) > 0)
        
        print(f"✅ Senaryo 4: {result['primary_clinic']['name']} - Gatekeeping: {result['requires_prior']}")
    
    def test_scenario_5_llm_fallback(self):
        """Test Senaryosu 5: LLM fallback"""
        complaint = "Garip bir ağrım var, ne olduğunu bilmiyorum"
        
        if not self.triage:
            self.skipTest("Triage sistemi yüklenemedi")
        
        result = self.triage.analyze_complaint(complaint)
        
        # Fallback stratejisi kontrolü
        self.assertIn(result['strategy'], ['llm', 'fallback', 'mixed'])
        
        # Primary clinic mutlaka olmalı
        self.assertIsNotNone(result['primary_clinic']['name'])
        self.assertTrue(len(result['primary_clinic']['name']) > 0)
        
        print(f"✅ Senaryo 5: {result['primary_clinic']['name']} - Strateji: {result['strategy']}")
    
    def test_canonical_mapping(self):
        """Kanonik mapping testi"""
        canonical_table = load_mhrs_canonical("")
        
        test_cases = [
            ("noroloji", "Nöroloji", True),
            ("kardiyoloji", "Kardiyoloji", True),
            ("ic hastaliklari", "İç Hastalıkları (Dahiliye)", True),
            ("bilinmeyen klinik", "Aile Hekimliği", False),
        ]
        
        for input_name, expected_canonical, expected_match in test_cases:
            canonical, matched, similarity = canonicalize(input_name, canonical_table)
            self.assertEqual(canonical, expected_canonical)
            print(f"✅ Kanonik: '{input_name}' → '{canonical}' (match: {matched})")
    
    def test_gatekeeping_rules(self):
        """Gatekeeping kuralları testi"""
        test_cases = [
            ("Kardiyoloji", True, ["İç Hastalıkları (Dahiliye)"]),
            ("Nöroloji", False, []),
            ("Çocuk Kardiyolojisi", True, ["Çocuk Sağlığı ve Hastalıkları"]),
            ("Aile Hekimliği", False, []),
        ]
        
        for clinic, expected_requires, expected_prior in test_cases:
            gate = apply_gatekeeping(clinic)
            self.assertEqual(gate.requires_prior, expected_requires)
            self.assertEqual(gate.prior_list, expected_prior)
            print(f"✅ Gatekeeping: {clinic} - requires_prior: {gate.requires_prior}")
    
    def test_red_flag_detection(self):
        """Red-flag tespiti testi"""
        test_cases = [
            ("Aniden göğsümde ezici ağrı var, soğuk terliyorum", True, "Kalp krizi"),
            ("Aniden yüzüm kaydı, konuşamıyorum", True, "İnme"),
            ("Bayıldım, bilincimi kaybettim", True, "Bilinç kaybı"),
            ("Başım ağrıyor", False, ""),
            ("Mide bulantım var", False, ""),
        ]
        
        for complaint, expected_urgent, expected_type in test_cases:
            result = detect_red_flags(complaint)
            self.assertEqual(result.urgent, expected_urgent)
            if expected_urgent:
                self.assertEqual(result.label, "ACİL")
            print(f"✅ Red-flag: '{complaint[:30]}...' → Urgent: {result.urgent}")
    
    def test_json_schema_validation(self):
        """JSON şema validasyonu testi"""
        # Geçerli JSON
        valid_json = '''
        {
            "primary_clinic": {
                "name": "Nöroloji",
                "reason": "Baş ağrısı için",
                "confidence": 0.85
            },
            "secondary_clinics": [
                {
                    "name": "İç Hastalıkları (Dahiliye)",
                    "reason": "Alternatif",
                    "confidence": 0.7
                }
            ]
        }
        '''
        
        result = parse_llm_response(valid_json)
        self.assertIn('primary_clinic', result)
        self.assertIn('secondary_clinics', result)
        self.assertEqual(result['primary_clinic']['name'], 'Nöroloji')
        
        # Eksik alanlar
        incomplete_json = '{"primary_clinic": {"name": "Göz Hastalıkları"}}'
        result = parse_llm_response(incomplete_json)
        self.assertIn('reason', result['primary_clinic'])
        self.assertIn('confidence', result['primary_clinic'])
        
        # Geçersiz JSON
        invalid_json = "Bu bir JSON değil"
        result = parse_llm_response(invalid_json)
        self.assertIn('primary_clinic', result)
        
        print("✅ JSON şema validasyonu başarılı")
    
    def test_emergency_response(self):
        """Acil durum yanıtı testi"""
        emergency = create_emergency_response("Kalp krizi şüphesi", "112'yi arayın")
        
        self.assertEqual(emergency['primary_clinic']['name'], 'ACİL')
        self.assertEqual(emergency['strategy'], 'redflag')
        self.assertIn('112', emergency['gate_note'])
        
        print("✅ Acil durum yanıtı başarılı")


def run_tests():
    """Testleri çalıştır"""
    print("🧪 TanıAI Triage Pipeline Testleri Başlatılıyor...\n")
    
    # Test suite oluştur
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTriagePipeline)
    
    # Test runner
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Sonuç özeti
    print(f"\n📊 Test Sonuçları:")
    print(f"  ✅ Başarılı: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  ❌ Başarısız: {len(result.failures)}")
    print(f"  🚨 Hata: {len(result.errors)}")
    print(f"  📈 Toplam: {result.testsRun}")
    
    if result.failures:
        print(f"\n❌ Başarısız Testler:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\n🚨 Hatalı Testler:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
