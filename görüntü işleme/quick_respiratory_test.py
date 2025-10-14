"""
Hızlı Solunum Yolu Acil Vaka Testi
===================================

Bu script, solunum yolu acil vaka tespit sistemini
hızlıca test etmek için kullanılır.

Kullanım:
    python quick_respiratory_test.py
"""

from respiratory_emergency_detector import RespiratoryEmergencyDetector
from test_respiratory_emergency import RespiratoryEmergencyTester
import logging
from pathlib import Path

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)


def quick_demo():
    """Hızlı demo"""
    print("=" * 70)
    print("🏥 SOLUNUM YOLU ACİL VAKA TESPİT SİSTEMİ - HIZLI TEST")
    print("=" * 70)
    
    # Tester oluştur
    tester = RespiratoryEmergencyTester()
    
    print("\n📸 Sentetik test görüntüleri oluşturuluyor...")
    test_images = tester.create_synthetic_test_images()
    
    print(f"✓ {len(test_images)} test görüntüsü hazırlandı\n")
    
    # Her görüntüyü tek tek test et
    for i, img_data in enumerate(test_images, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}/{len(test_images)}: {img_data['type']}")
        print(f"Beklenen aciliyet: {img_data['expected_urgency']}")
        print(f"{'='*70}")
        
        result = tester.test_single_image(img_data['path'], display=False)
        
        # Karşılaştırma
        expected = img_data['expected_urgency']
        actual = result['urgency_level']
        match = "✓ DOĞRU" if expected == actual else f"✗ YANLIŞ (beklenen: {expected})"
        
        print(f"\n🎯 Tahmin: {actual.upper()} - {match}")
    
    # Toplu karşılaştırma
    print(f"\n{'='*70}")
    print("📊 TOPLU KARŞILAŞTIRMA RAPORU")
    print(f"{'='*70}")
    
    image_paths = [img['path'] for img in test_images]
    results, comparison = tester.test_batch_images(image_paths, save_report=True)
    
    print("\n" + "="*70)
    print("✅ TEST TAMAMLANDI!")
    print("="*70)
    print("\n📁 Oluşturulan dosyalar:")
    print(f"   • Test görüntüleri: test_images/")
    print(f"   • Detaylı rapor: reports/")
    print("\n💡 Kendi X-ray görüntülerinizi test etmek için:")
    print("   python test_respiratory_emergency.py")


def test_with_custom_image(image_path: str):
    """Özel görüntü ile test"""
    print("=" * 70)
    print(f"🏥 Görüntü Analizi: {Path(image_path).name}")
    print("=" * 70)
    
    detector = RespiratoryEmergencyDetector()
    
    try:
        result = detector.analyze_emergency(image_path=image_path)
        
        # Sonuçları göster
        print(f"\n{'🚨' if result['urgency_score'] >= 6 else '✓'} ACİLİYET: {result['urgency_level'].upper()}")
        print(f"📊 Skor: {result['urgency_score']:.1f}/10")
        
        print(f"\n🔍 Bulgular:")
        for finding in result['findings']:
            print(f"   • {finding['name']} (%{finding['confidence']:.0f})")
            print(f"     → {finding['action']}")
        
        print(f"\n💡 Öneriler:")
        for rec in result['recommendations']:
            print(f"   {rec}")
        
        return result
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def compare_multiple_images(image_paths: list):
    """Birden fazla görüntüyü karşılaştır"""
    print("=" * 70)
    print(f"🏥 ÇOKLU GÖRÜNTÜ KARŞILAŞTIRMASI - {len(image_paths)} görüntü")
    print("=" * 70)
    
    detector = RespiratoryEmergencyDetector()
    results = detector.batch_analyze(image_paths)
    comparison = detector.compare_analyses(results)
    
    # Özet tablo
    print(f"\n{'Görüntü':<30} {'Aciliyet':<12} {'Skor':<8} {'Durum'}")
    print("-" * 70)
    
    for result in results:
        name = Path(result.get('image_path', 'unknown')).name[:28]
        urgency = result.get('urgency_level', 'unknown')
        score = result.get('urgency_score', 0)
        
        # Durum emoji
        if urgency == 'critical':
            status = '🚨 ACİL'
        elif urgency == 'high':
            status = '⚠️  Yüksek'
        elif urgency == 'moderate':
            status = '⚡ Orta'
        else:
            status = '✓ Düşük'
        
        print(f"{name:<30} {urgency:<12} {score:>5.1f}/10  {status}")
    
    print("\n" + "=" * 70)
    print("📊 ÖZET İSTATİSTİKLER")
    print("=" * 70)
    print(f"Ortalama aciliyet: {comparison['average_urgency']:.2f}/10")
    print(f"🚨 Kritik vakalar: {comparison['critical_cases']}")
    print(f"⚠️  Yüksek öncelik: {comparison['high_priority_cases']}")
    
    return results, comparison


def interactive_mode():
    """İnteraktif mod"""
    print("=" * 70)
    print("🏥 SOLUNUM YOLU ACİL VAKA TESPİT SİSTEMİ")
    print("=" * 70)
    
    while True:
        print("\n📋 Menü:")
        print("1. 🚀 Hızlı demo (sentetik görüntüler)")
        print("2. 📸 Tek görüntü analizi")
        print("3. 📊 Çoklu görüntü karşılaştırması")
        print("4. ❌ Çıkış")
        
        choice = input("\nSeçim (1-4): ").strip()
        
        if choice == '1':
            quick_demo()
            break
            
        elif choice == '2':
            image_path = input("\nGörüntü yolu: ").strip()
            if Path(image_path).exists():
                test_with_custom_image(image_path)
            else:
                print(f"❌ Dosya bulunamadı: {image_path}")
                
        elif choice == '3':
            print("\nGörüntü yollarını girin (her satırda bir tane, boş satır ile bitirin):")
            image_paths = []
            while True:
                path = input("  → ").strip()
                if not path:
                    break
                if Path(path).exists():
                    image_paths.append(path)
                else:
                    print(f"    ⚠️  Atlandı (bulunamadı): {path}")
            
            if image_paths:
                compare_multiple_images(image_paths)
            else:
                print("⚠️  Hiç geçerli görüntü girilmedi")
                
        elif choice == '4':
            print("\n👋 Çıkılıyor...")
            break
            
        else:
            print("❌ Geçersiz seçim")


if __name__ == "__main__":
    import sys
    
    # Komut satırı argümanları
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            # Hızlı demo
            quick_demo()
        elif sys.argv[1] == '--image' and len(sys.argv) > 2:
            # Tek görüntü
            test_with_custom_image(sys.argv[2])
        elif sys.argv[1] == '--batch' and len(sys.argv) > 2:
            # Çoklu görüntü
            image_paths = sys.argv[2:]
            compare_multiple_images(image_paths)
        else:
            print("Kullanım:")
            print("  python quick_respiratory_test.py --demo")
            print("  python quick_respiratory_test.py --image path/to/xray.jpg")
            print("  python quick_respiratory_test.py --batch image1.jpg image2.jpg ...")
    else:
        # İnteraktif mod
        interactive_mode()

