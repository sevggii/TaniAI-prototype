#!/usr/bin/env python3
"""
Entegre Sistem Test Scripti
Whisper + ML + LLM sistemini test eder
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Proje kök dizinini path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Modülleri import et
try:
    from ml_clinic.integrated_triage import get_integrated_triage, TriageConfig
    from ml_clinic.llm_clinic_analyzer import LLMConfig
    from whisper_asr import get_asr_processor
    print("✅ Tüm modüller başarıyla import edildi")
except ImportError as e:
    print(f"❌ Modül import hatası: {e}")
    sys.exit(1)

# Logging yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ml_model():
    """ML modelini test et"""
    print("\n🔍 ML Model Testi...")
    try:
        from ml_clinic.triage_model import get_triage_model
        ml_model = get_triage_model()
        
        test_text = "Baş ağrım var ve mide bulantısı yaşıyorum"
        result = ml_model.suggest(test_text, top_k=3)
        
        print(f"✅ ML Model çalışıyor")
        print(f"   Test metni: {test_text}")
        print(f"   Öneriler: {result.get('suggestions', [])}")
        return True
    except Exception as e:
        print(f"❌ ML Model hatası: {e}")
        return False

def test_llm_availability():
    """LLM erişilebilirliğini test et"""
    print("\n🔍 LLM Erişilebilirlik Testi...")
    try:
        llm_config = LLMConfig()
        from ml_clinic.llm_clinic_analyzer import get_llm_analyzer
        llm_analyzer = get_llm_analyzer(llm_config)
        
        availability = llm_analyzer.check_llm_availability()
        
        if availability.get("available", False):
            print(f"✅ LLM erişilebilir")
            print(f"   Provider: {availability.get('provider', 'Bilinmeyen')}")
            print(f"   Model: {availability.get('current_model', 'Bilinmeyen')}")
            if "models" in availability:
                print(f"   Mevcut modeller: {availability['models'][:3]}...")
            return True
        else:
            print(f"⚠️ LLM erişilemez: {availability.get('error', 'Bilinmeyen hata')}")
            print("   Ollama kurulu değil veya çalışmıyor olabilir")
            return False
    except Exception as e:
        print(f"❌ LLM test hatası: {e}")
        return False

def test_whisper():
    """Whisper modelini test et"""
    print("\n🔍 Whisper Model Testi...")
    try:
        asr_processor = get_asr_processor()
        
        print(f"✅ Whisper model yüklendi")
        print(f"   Model: {asr_processor.model_name}")
        print(f"   Model yüklü: {asr_processor.model is not None}")
        return True
    except Exception as e:
        print(f"❌ Whisper test hatası: {e}")
        return False

def test_integrated_system():
    """Entegre sistemi test et"""
    print("\n🔍 Entegre Sistem Testi...")
    try:
        # LLM config'i oluştur
        llm_config = LLMConfig(
            provider="ollama",
            model="llama2:7b",  # veya mevcut model
            base_url="http://localhost:11434"
        )
        
        # Triage config'i oluştur
        triage_config = TriageConfig(
            use_ml=True,
            use_llm=True,
            ml_weight=0.6,
            llm_weight=0.4
        )
        
        # Entegre sistemi başlat
        integrated_triage = get_integrated_triage(triage_config, llm_config)
        
        # Sistem durumunu kontrol et
        status = integrated_triage.get_system_status()
        print(f"✅ Entegre sistem başlatıldı")
        print(f"   ML kullanılabilir: {status.get('ml_available', False)}")
        print(f"   LLM kullanılabilir: {status.get('llm_available', False)}")
        print(f"   LLM Provider: {status.get('llm_provider', 'Bilinmeyen')}")
        print(f"   LLM Model: {status.get('llm_model', 'Bilinmeyen')}")
        
        # Test metni ile analiz yap
        test_cases = [
            "Baş ağrım var ve mide bulantısı yaşıyorum",
            "Çocuğumda ateş ve öksürük var",
            "Göğüs ağrısı ve nefes darlığı çekiyorum",
            "Diş ağrısı dayanılmaz halde"
        ]
        
        print(f"\n📝 Test Analizleri:")
        for i, test_text in enumerate(test_cases, 1):
            print(f"\n   Test {i}: {test_text}")
            try:
                result = integrated_triage.suggest(test_text, top_k=3)
                print(f"   ✅ Öneriler: {result.get('suggestions', [])}")
                print(f"   📊 Kullanılan yöntemler: {result.get('methods_used', [])}")
                if 'confidence_scores' in result:
                    print(f"   🎯 Güven skorları: {result['confidence_scores']}")
            except Exception as e:
                print(f"   ❌ Analiz hatası: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Entegre sistem test hatası: {e}")
        return False

def test_clinic_dataset():
    """Klinik dataset'ini test et"""
    print("\n🔍 Klinik Dataset Testi...")
    try:
        dataset_path = project_root / "ml_clinic" / "klinik_dataset.jsonl"
        
        if not dataset_path.exists():
            print(f"❌ Dataset dosyası bulunamadı: {dataset_path}")
            return False
        
        # İlk birkaç satırı oku
        with open(dataset_path, 'r', encoding='utf-8') as f:
            lines = [f.readline().strip() for _ in range(5)]
        
        print(f"✅ Dataset dosyası mevcut")
        print(f"   Dosya boyutu: {dataset_path.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"   İlk örnekler:")
        for i, line in enumerate(lines, 1):
            if line:
                import json
                try:
                    data = json.loads(line)
                    print(f"     {i}. {data.get('complaint', '')[:50]}... -> {data.get('clinic', '')}")
                except:
                    print(f"     {i}. {line[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Dataset test hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚀 TanıAI Entegre Sistem Testi Başlıyor...")
    print("=" * 60)
    
    tests = [
        ("Klinik Dataset", test_clinic_dataset),
        ("ML Model", test_ml_model),
        ("Whisper Model", test_whisper),
        ("LLM Erişilebilirlik", test_llm_availability),
        ("Entegre Sistem", test_integrated_system),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} testi beklenmeyen hata: {e}")
            results[test_name] = False
    
    # Sonuçları özetle
    print("\n" + "=" * 60)
    print("📊 TEST SONUÇLARI")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\nToplam: {passed}/{total} test başarılı")
    
    if passed == total:
        print("🎉 Tüm testler başarılı! Sistem kullanıma hazır.")
    elif passed >= total - 1:
        print("⚠️ Çoğu test başarılı. LLM olmadan da sistem çalışabilir.")
    else:
        print("❌ Birçok test başarısız. Sistem yapılandırmasını kontrol edin.")
    
    # Öneriler
    print("\n💡 ÖNERİLER:")
    if not results.get("LLM Erişilebilirlik", False):
        print("   - Ollama kurulumu yapın: https://ollama.ai/")
        print("   - Model indirin: ollama pull llama2:7b")
        print("   - Ollama servisini başlatın: ollama serve")
    
    if not results.get("ML Model", False):
        print("   - ML model bağımlılıklarını kontrol edin")
        print("   - pip install -r ml_clinic/requirements.txt")
    
    if not results.get("Whisper Model", False):
        print("   - Whisper bağımlılıklarını kontrol edin")
        print("   - pip install openai-whisper torch torchaudio")

if __name__ == "__main__":
    main()
