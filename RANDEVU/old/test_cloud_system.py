#!/usr/bin/env python3
"""
Cloud Ortamı Test Scripti
Google Colab, Kaggle gibi ortamlar için optimize edilmiş
"""

import os
import sys
import json
import requests
import subprocess
import time
from pathlib import Path

def detect_environment():
    """Ortam tespiti"""
    print("🔍 Ortam tespit ediliyor...")
    
    environments = {
        "colab": False,
        "kaggle": False,
        "local": False
    }
    
    # Google Colab kontrolü
    try:
        import google.colab
        environments["colab"] = True
        print("✅ Google Colab ortamı tespit edildi")
    except ImportError:
        pass
    
    # Kaggle kontrolü
    if os.path.exists("/kaggle/input") or "KAGGLE" in os.environ:
        environments["kaggle"] = True
        print("✅ Kaggle ortamı tespit edildi")
    
    # Yerel ortam
    if not environments["colab"] and not environments["kaggle"]:
        environments["local"] = True
        print("✅ Yerel ortam tespit edildi")
    
    return environments

def test_ollama_cloud():
    """Cloud ortamında Ollama testi"""
    print("\n🤖 Ollama Cloud Testi...")
    
    try:
        # Ollama servisini başlat
        print("Ollama servisi başlatılıyor...")
        process = subprocess.Popen(
            ['ollama', 'serve'], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # Servisin başlamasını bekle
        time.sleep(5)
        
        # Ollama API'sini test et
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama çalışıyor, {len(models)} model mevcut")
            
            # Küçük model var mı kontrol et
            small_models = [m["name"] for m in models if "2b" in m["name"] or "1b" in m["name"]]
            if small_models:
                print(f"✅ Küçük modeller: {small_models}")
                return True
            else:
                print("⚠️ Küçük model bulunamadı, indiriliyor...")
                return download_small_model()
        else:
            print(f"❌ Ollama API hatası: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama test hatası: {e}")
        return False

def download_small_model():
    """Küçük model indir"""
    print("📥 Küçük model indiriliyor...")
    
    small_models = ["llama2:2b", "phi:2b", "tinyllama:1.1b"]
    
    for model in small_models:
        try:
            print(f"Model indiriliyor: {model}")
            result = subprocess.run(
                ["ollama", "pull", model], 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"✅ {model} başarıyla indirildi")
                return True
            else:
                print(f"❌ {model} indirme hatası")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {model} indirme timeout")
            continue
        except Exception as e:
            print(f"❌ {model} hatası: {e}")
            continue
    
    print("❌ Hiçbir küçük model indirilemedi")
    return False

def test_whisper_cloud():
    """Cloud ortamında Whisper testi"""
    print("\n🎤 Whisper Cloud Testi...")
    
    try:
        import whisper
        
        # Medium model kullan (cloud için optimize)
        print("Whisper Medium modeli yükleniyor...")
        model = whisper.load_model("medium")
        
        print(f"✅ Whisper Medium modeli yüklendi")
        print(f"Model boyutu: {model.dims}")
        
        return True
        
    except Exception as e:
        print(f"❌ Whisper test hatası: {e}")
        return False

def test_ml_model_cloud():
    """Cloud ortamında ML model testi"""
    print("\n🧠 ML Model Cloud Testi...")
    
    try:
        # Proje yolu ekle
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from ml_clinic.triage_model import get_triage_model
        
        model = get_triage_model()
        result = model.suggest("Baş ağrım var ve mide bulantısı yaşıyorum", top_k=3)
        
        print(f"✅ ML Model çalışıyor")
        print(f"Öneriler: {result.get('suggestions', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML Model test hatası: {e}")
        return False

def test_cloud_llm():
    """Cloud LLM testi"""
    print("\n☁️ Cloud LLM Testi...")
    
    try:
        from cloud_llm_analyzer import CloudLLMAnalyzer, CloudLLMConfig
        
        config = CloudLLMConfig(
            provider="ollama",
            model="llama2:2b",
            base_url="http://localhost:11434"
        )
        
        analyzer = CloudLLMAnalyzer(config)
        
        # Test metni
        test_text = "Baş ağrım var ve mide bulantısı yaşıyorum"
        result = analyzer.analyze_with_cloud_llm(test_text)
        
        print(f"✅ Cloud LLM çalışıyor")
        print(f"Test: {test_text}")
        print(f"Öneri: {result.get('clinic', 'Bilinmeyen')}")
        print(f"Güven: {result.get('confidence', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cloud LLM test hatası: {e}")
        return False

def test_integrated_cloud():
    """Entegre cloud sistemi testi"""
    print("\n🔄 Entegre Cloud Sistem Testi...")
    
    try:
        from ml_clinic.integrated_triage import get_integrated_triage, TriageConfig
        from ml_clinic.llm_clinic_analyzer import LLMConfig
        
        # Config'leri ayarla
        llm_config = LLMConfig(
            provider="ollama",
            model="llama2:2b",
            base_url="http://localhost:11434"
        )
        
        triage_config = TriageConfig(
            use_ml=True,
            use_llm=True,
            ml_weight=0.6,
            llm_weight=0.4
        )
        
        # Entegre sistemi başlat
        integrated_triage = get_integrated_triage(triage_config, llm_config)
        
        # Test senaryoları
        test_cases = [
            "Baş ağrım var ve mide bulantısı yaşıyorum",
            "Çocuğumda ateş ve öksürük var",
            "Göğüs ağrısı ve nefes darlığı çekiyorum",
            "Diş ağrısı dayanılmaz halde"
        ]
        
        print(f"✅ Entegre sistem çalışıyor")
        print(f"\n📝 Test Sonuçları:")
        
        for i, test_text in enumerate(test_cases, 1):
            result = integrated_triage.suggest(test_text, top_k=3)
            print(f"\n{i}. {test_text}")
            print(f"   Öneriler: {result.get('suggestions', [])}")
            print(f"   Yöntemler: {result.get('methods_used', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Entegre sistem test hatası: {e}")
        return False

def test_web_server_cloud():
    """Cloud web sunucusu testi"""
    print("\n🌐 Cloud Web Sunucusu Testi...")
    
    try:
        import subprocess
        import threading
        import time
        
        def start_server():
            try:
                subprocess.run([
                    'python', 'whisper_asr/server.py'
                ], cwd=Path(__file__).parent)
            except Exception as e:
                print(f"Sunucu hatası: {e}")
        
        # Sunucuyu arka planda başlat
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Sunucunun başlamasını bekle
        time.sleep(5)
        
        # API'yi test et
        try:
            response = requests.get("http://localhost:8001/whisper/status", timeout=10)
            if response.status_code == 200:
                print("✅ Web sunucusu çalışıyor")
                print("🌐 Web arayüzü: http://localhost:8001")
                return True
            else:
                print(f"❌ Web sunucusu hatası: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Web sunucusu bağlantı hatası: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Web sunucusu test hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("☁️ TanıAI Cloud Sistem Testi Başlıyor...")
    print("=" * 60)
    
    # Ortam tespiti
    environments = detect_environment()
    
    # Testleri çalıştır
    tests = [
        ("Whisper Model", test_whisper_cloud),
        ("ML Model", test_ml_model_cloud),
        ("Ollama", test_ollama_cloud),
        ("Cloud LLM", test_cloud_llm),
        ("Entegre Sistem", test_integrated_cloud),
        ("Web Sunucusu", test_web_server_cloud),
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
    print("📊 CLOUD TEST SONUÇLARI")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\nToplam: {passed}/{total} test başarılı")
    
    # Ortam bilgisi
    if environments["colab"]:
        print("\n📱 Google Colab ortamında çalışıyor")
    elif environments["kaggle"]:
        print("\n🏆 Kaggle ortamında çalışıyor")
    else:
        print("\n🖥️ Yerel ortamda çalışıyor")
    
    # Sonuç
    if passed == total:
        print("🎉 Tüm testler başarılı! Cloud sistemi kullanıma hazır.")
    elif passed >= total - 1:
        print("⚠️ Çoğu test başarılı. Sistem çalışabilir.")
    else:
        print("❌ Birçok test başarısız. Kurulumu kontrol edin.")
    
    # Öneriler
    print("\n💡 CLOUD ÖNERİLERİ:")
    if not results.get("Ollama", False):
        print("   - Ollama kurulumunu kontrol edin")
        print("   - Küçük model indirin: ollama pull llama2:2b")
    
    if not results.get("Web Sunucusu", False):
        print("   - Web sunucusu portunu kontrol edin")
        print("   - Ngrok ile dışarıdan erişim sağlayın")
    
    if environments["colab"]:
        print("   - Colab'da ngrok kullanarak web erişimi sağlayın")
        print("   - GPU kullanımı için Runtime > Change runtime type > GPU")

if __name__ == "__main__":
    main()
