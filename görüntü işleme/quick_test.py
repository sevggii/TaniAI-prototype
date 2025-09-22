#!/usr/bin/env python3
"""
Hızlı Sistem Testi
==================

Sistemin temel bileşenlerinin çalışıp çalışmadığını test eder.
"""

import sys
import os
from pathlib import Path

# Proje root'unu Python path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_imports():
    """Temel import'ları test et"""
    print("🔍 Temel import'lar test ediliyor...")
    
    try:
        import schemas
        print("✅ schemas.py - OK")
    except Exception as e:
        print(f"❌ schemas.py - HATA: {e}")
        return False
    
    try:
        import models
        print("✅ models.py - OK")
    except Exception as e:
        print(f"❌ models.py - HATA: {e}")
        return False
    
    return True

def test_model_manager():
    """Model Manager'ı test et"""
    print("\n🤖 Model Manager test ediliyor...")
    
    try:
        from models.model_manager import ModelManager
        manager = ModelManager()
        available_models = manager.get_available_models()
        print(f"✅ ModelManager - OK ({len(available_models)} model)")
        return True
    except Exception as e:
        print(f"❌ ModelManager - HATA: {e}")
        return False

def test_schemas():
    """Schemas'ı test et"""
    print("\n📋 Schemas test ediliyor...")
    
    try:
        from schemas import ImageType, BodyRegion, RadiologyAnalysisRequest
        
        # Test data oluştur
        from schemas import ImageMetadata
        metadata = ImageMetadata(
            image_type=ImageType.XRAY,
            body_region=BodyRegion.CHEST,
            patient_age=45,
            patient_gender="male"
        )
        
        request = RadiologyAnalysisRequest(
            image_data="dGVzdA==",  # "test" in base64
            image_metadata=metadata
        )
        
        print("✅ Schemas - OK")
        return True
    except Exception as e:
        print(f"❌ Schemas - HATA: {e}")
        return False

def test_simple_model():
    """Basit model testi"""
    print("\n🧠 Basit model test ediliyor...")
    
    try:
        from models import RadiologyCNN
        
        # Basit model oluştur
        model = RadiologyCNN(num_classes=2, input_channels=1)
        print(f"✅ RadiologyCNN - OK ({sum(p.numel() for p in model.parameters())} parametre)")
        return True
    except Exception as e:
        print(f"❌ RadiologyCNN - HATA: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🧪 Hızlı Sistem Testi Başlatılıyor...\n")
    
    tests = [
        test_basic_imports,
        test_schemas,
        test_model_manager,
        test_simple_model
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Sonuçları:")
    print(f"✅ Başarılı: {passed}/{total}")
    print(f"❌ Başarısız: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Tüm testler başarılı! Sistem çalışıyor.")
        return True
    else:
        print(f"\n⚠️ {total - passed} test başarısız. Sistemde sorunlar var.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
