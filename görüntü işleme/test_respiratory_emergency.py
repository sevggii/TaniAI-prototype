"""
Solunum Yolu Acil Vaka Tespit Sistemi - Test ve Karşılaştırma
==============================================================

Bu script respiratory_emergency_detector.py modülünü test eder ve
farklı X-ray görüntülerini karşılaştırır.
"""

import cv2
import numpy as np
from pathlib import Path
import json
import logging
from datetime import datetime
from typing import List, Dict
import matplotlib.pyplot as plt
from respiratory_emergency_detector import RespiratoryEmergencyDetector

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RespiratoryEmergencyTester:
    """Solunum yolu acil vaka testi sınıfı"""
    
    def __init__(self):
        self.detector = RespiratoryEmergencyDetector()
        self.results = []
    
    def test_single_image(self, image_path: str, display: bool = True):
        """Tek görüntü testi"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Görüntü analizi: {image_path}")
        logger.info(f"{'='*60}")
        
        try:
            # Analiz yap
            result = self.detector.analyze_emergency(image_path=image_path)
            
            # Sonuçları yazdır
            self._print_result(result)
            
            # Görselleştir
            if display:
                self._display_result(image_path, result)
            
            self.results.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Test hatası: {e}")
            return None
    
    def test_batch_images(self, image_paths: List[str], save_report: bool = True):
        """Çoklu görüntü testi"""
        logger.info(f"\n{'='*60}")
        logger.info(f"TOPLU ANALİZ - {len(image_paths)} görüntü")
        logger.info(f"{'='*60}\n")
        
        # Batch analiz
        results = self.detector.batch_analyze(image_paths)
        
        # Karşılaştırma
        comparison = self.detector.compare_analyses(results)
        
        # Sonuçları yazdır
        self._print_comparison(comparison)
        
        # Detaylı sonuçlar
        for i, result in enumerate(results, 1):
            logger.info(f"\n--- Görüntü {i}: {result.get('image_path', 'unknown')} ---")
            self._print_result(result)
        
        # Rapor kaydet
        if save_report:
            self._save_report(results, comparison)
        
        self.results = results
        return results, comparison
    
    def compare_with_ground_truth(self, test_data: List[Dict]):
        """
        Ground truth ile karşılaştır
        
        test_data formatı:
        [
            {
                'image_path': 'path/to/image.jpg',
                'ground_truth': {
                    'has_pneumothorax': True,
                    'has_severe_pneumonia': False,
                    'urgency_level': 'critical'
                }
            },
            ...
        ]
        """
        logger.info(f"\n{'='*60}")
        logger.info("GROUND TRUTH KARŞILAŞTIRMASI")
        logger.info(f"{'='*60}\n")
        
        correct_urgency = 0
        total = len(test_data)
        
        detailed_results = []
        
        for data in test_data:
            image_path = data['image_path']
            ground_truth = data['ground_truth']
            
            # Analiz yap
            result = self.detector.analyze_emergency(image_path=image_path)
            
            # Karşılaştır
            predicted_urgency = result['urgency_level']
            actual_urgency = ground_truth.get('urgency_level', 'unknown')
            
            is_correct = predicted_urgency == actual_urgency
            if is_correct:
                correct_urgency += 1
            
            detailed_results.append({
                'image': Path(image_path).name,
                'predicted': predicted_urgency,
                'actual': actual_urgency,
                'correct': is_correct,
                'urgency_score': result['urgency_score']
            })
            
            logger.info(f"📸 {Path(image_path).name}")
            logger.info(f"   Tahmin: {predicted_urgency} | Gerçek: {actual_urgency} | {'✓' if is_correct else '✗'}")
        
        # Doğruluk oranı
        accuracy = (correct_urgency / total * 100) if total > 0 else 0
        
        logger.info(f"\n{'='*60}")
        logger.info(f"SONUÇLAR")
        logger.info(f"{'='*60}")
        logger.info(f"Toplam test: {total}")
        logger.info(f"Doğru tahmin: {correct_urgency}")
        logger.info(f"Doğruluk: {accuracy:.1f}%")
        
        return {
            'accuracy': accuracy,
            'correct': correct_urgency,
            'total': total,
            'detailed_results': detailed_results
        }
    
    def create_synthetic_test_images(self, output_dir: str = "test_images"):
        """Test için sentetik X-ray görüntüleri oluştur"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        logger.info(f"Sentetik test görüntüleri oluşturuluyor: {output_path}")
        
        test_images = []
        
        # 1. Normal akciğer
        normal = self._create_normal_chest_xray()
        normal_path = output_path / "normal_chest.jpg"
        cv2.imwrite(str(normal_path), normal)
        test_images.append({
            'path': str(normal_path),
            'type': 'Normal',
            'expected_urgency': 'low'
        })
        
        # 2. Hafif pnömoni
        mild_pneumonia = self._create_pneumonia_xray(severity='mild')
        mild_path = output_path / "mild_pneumonia.jpg"
        cv2.imwrite(str(mild_path), mild_pneumonia)
        test_images.append({
            'path': str(mild_path),
            'type': 'Hafif Pnömoni',
            'expected_urgency': 'moderate'
        })
        
        # 3. Şiddetli pnömoni
        severe_pneumonia = self._create_pneumonia_xray(severity='severe')
        severe_path = output_path / "severe_pneumonia.jpg"
        cv2.imwrite(str(severe_path), severe_pneumonia)
        test_images.append({
            'path': str(severe_path),
            'type': 'Şiddetli Pnömoni',
            'expected_urgency': 'high'
        })
        
        # 4. Pnömotoraks
        pneumothorax = self._create_pneumothorax_xray()
        pneumothorax_path = output_path / "pneumothorax.jpg"
        cv2.imwrite(str(pneumothorax_path), pneumothorax)
        test_images.append({
            'path': str(pneumothorax_path),
            'type': 'Pnömotoraks',
            'expected_urgency': 'critical'
        })
        
        # 5. Plevral efüzyon
        effusion = self._create_pleural_effusion_xray()
        effusion_path = output_path / "pleural_effusion.jpg"
        cv2.imwrite(str(effusion_path), effusion)
        test_images.append({
            'path': str(effusion_path),
            'type': 'Plevral Efüzyon',
            'expected_urgency': 'moderate'
        })
        
        logger.info(f"✓ {len(test_images)} test görüntüsü oluşturuldu")
        return test_images
    
    def _create_normal_chest_xray(self) -> np.ndarray:
        """Normal göğüs X-ray simülasyonu"""
        img = np.zeros((512, 512), dtype=np.uint8)
        
        # Akciğer bölgeleri (karanlık)
        # Sol akciğer
        cv2.ellipse(img, (170, 256), (80, 150), 0, 0, 360, 40, -1)
        # Sağ akciğer
        cv2.ellipse(img, (342, 256), (80, 150), 0, 0, 360, 40, -1)
        
        # Kalp gölgesi (orta-sağda)
        cv2.ellipse(img, (256, 320), (60, 80), 0, 0, 360, 120, -1)
        
        # Kaburga çizgileri
        for i in range(6):
            y = 120 + i * 40
            cv2.line(img, (100, y), (412, y), 80, 2)
        
        # Gürültü ekle
        noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
        img = cv2.add(img, noise)
        
        return img
    
    def _create_pneumonia_xray(self, severity: str = 'mild') -> np.ndarray:
        """Pnömoni X-ray simülasyonu"""
        img = self._create_normal_chest_xray()
        
        # Opacity (mat alanlar) ekle
        if severity == 'mild':
            # Sağ alt lobda küçük infiltrasyon
            cv2.ellipse(img, (342, 350), (40, 60), 0, 0, 360, 150, -1)
        elif severity == 'severe':
            # Bilateral yaygın infiltrasyon
            cv2.ellipse(img, (170, 280), (70, 120), 0, 0, 360, 180, -1)
            cv2.ellipse(img, (342, 300), (75, 130), 0, 0, 360, 170, -1)
            # Ek opasiteler
            cv2.circle(img, (200, 200), 30, 160, -1)
            cv2.circle(img, (312, 240), 35, 165, -1)
        
        return img
    
    def _create_pneumothorax_xray(self) -> np.ndarray:
        """Pnömotoraks X-ray simülasyonu"""
        img = self._create_normal_chest_xray()
        
        # Sağ akciğerde kollaps - çok karanlık alan (hava)
        # Kollaps çizgisi
        cv2.line(img, (300, 150), (300, 400), 20, 3)
        
        # Dış bölge çok karanlık (serbest hava)
        mask = np.zeros_like(img)
        cv2.rectangle(mask, (300, 100), (450, 450), 255, -1)
        img[mask > 0] = img[mask > 0] * 0.3
        
        # Kollaps olmuş akciğer daha küçük
        cv2.ellipse(img, (250, 256), (40, 100), 0, 0, 360, 60, -1)
        
        return img
    
    def _create_pleural_effusion_xray(self) -> np.ndarray:
        """Plevral efüzyon X-ray simülasyonu"""
        img = self._create_normal_chest_xray()
        
        # Sağ kostofrenk sinüste mat alan (sıvı)
        # Alt kısımda yoğun beyaz alan
        pts = np.array([[280, 380], [400, 380], [400, 450], [280, 450]], np.int32)
        cv2.fillPoly(img, [pts], 200)
        
        # Gradient efekti (sıvı seviyesi)
        for y in range(380, 450):
            intensity = int(200 - (y - 380) * 0.5)
            cv2.line(img, (280, y), (400, y), intensity, 1)
        
        return img
    
    def _print_result(self, result: Dict):
        """Analiz sonucunu yazdır"""
        if 'error' in result:
            logger.error(f"❌ Hata: {result['error']}")
            return
        
        # Aciliyet seviyesi emoji
        level_emoji = {
            'critical': '🚨',
            'high': '⚠️',
            'moderate': '⚡',
            'low': '✓'
        }
        
        urgency_level = result['urgency_level']
        emoji = level_emoji.get(urgency_level, '❓')
        
        logger.info(f"\n{emoji} ACİLİYET SEVİYESİ: {urgency_level.upper()}")
        logger.info(f"📊 Aciliyet Skoru: {result['urgency_score']:.2f}/10")
        logger.info(f"⏱️  Müdahale Gereksinimi: {result['requires_immediate_attention']}")
        
        logger.info(f"\n🔍 ACİL DURUM SKORLARI:")
        for key, value in result['emergency_scores'].items():
            logger.info(f"   • {key}: {value:.2%}")
        
        logger.info(f"\n📋 TESPİT EDİLEN BULGULAR:")
        for finding in result['findings']:
            severity_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MODERATE': '🟡', 'LOW': '🟢'}
            emoji = severity_emoji.get(finding['severity'], '⚪')
            logger.info(f"   {emoji} {finding['name']}")
            logger.info(f"      - Güven: %{finding['confidence']:.1f}")
            logger.info(f"      - Açıklama: {finding['description']}")
            logger.info(f"      - Aksiyon: {finding['action']}")
        
        logger.info(f"\n💡 ÖNERİLER:")
        for rec in result['recommendations']:
            logger.info(f"   • {rec}")
        
        logger.info(f"\n📈 GÖRÜNTÜ ÖZELLİKLERİ:")
        for key, value in result['features'].items():
            logger.info(f"   • {key}: {value:.2f}")
    
    def _print_comparison(self, comparison: Dict):
        """Karşılaştırma sonucunu yazdır"""
        logger.info(f"\n{'='*60}")
        logger.info("KARŞILAŞTIRMA RAPORU")
        logger.info(f"{'='*60}")
        
        logger.info(f"\n📊 GENEL İSTATİSTİKLER:")
        logger.info(f"   Toplam görüntü: {comparison['total_images']}")
        logger.info(f"   Ortalama aciliyet: {comparison['average_urgency']:.2f}/10")
        logger.info(f"   🚨 Kritik vakalar: {comparison['critical_cases']}")
        logger.info(f"   ⚠️  Yüksek öncelik: {comparison['high_priority_cases']}")
        
        logger.info(f"\n📈 ACİLİYET DAĞILIMI:")
        for level, count in comparison['urgency_distribution'].items():
            percentage = (count / comparison['total_images'] * 100) if comparison['total_images'] > 0 else 0
            logger.info(f"   • {level}: {count} ({percentage:.1f}%)")
        
        if 'highest_urgency_case' in comparison:
            highest = comparison['highest_urgency_case']
            logger.info(f"\n🔝 EN ACİL VAKA:")
            logger.info(f"   Görüntü: {Path(highest['image']).name}")
            logger.info(f"   Skor: {highest['score']:.2f}/10")
    
    def _display_result(self, image_path: str, result: Dict):
        """Sonucu görsel olarak göster"""
        try:
            import base64
            
            # Orijinal görüntü
            original = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            
            # Görselleştirme
            if 'visualization_base64' in result:
                vis_data = base64.b64decode(result['visualization_base64'])
                vis_array = np.frombuffer(vis_data, dtype=np.uint8)
                visualization = cv2.imdecode(vis_array, cv2.IMREAD_COLOR)
                
                # Yan yana göster
                plt.figure(figsize=(12, 6))
                
                plt.subplot(1, 2, 1)
                plt.imshow(original, cmap='gray')
                plt.title('Orijinal X-Ray')
                plt.axis('off')
                
                plt.subplot(1, 2, 2)
                plt.imshow(cv2.cvtColor(visualization, cv2.COLOR_BGR2RGB))
                plt.title(f'Analiz - Aciliyet: {result["urgency_score"]:.1f}/10')
                plt.axis('off')
                
                plt.tight_layout()
                plt.show()
        except Exception as e:
            logger.warning(f"Görselleştirme hatası: {e}")
    
    def _save_report(self, results: List[Dict], comparison: Dict):
        """Raporu dosyaya kaydet"""
        report_path = Path("reports")
        report_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = report_path / f"respiratory_emergency_report_{timestamp}.json"
        
        # Visualization base64'leri çıkar (dosya çok büyük olmasın)
        clean_results = []
        for r in results:
            clean_r = r.copy()
            if 'visualization_base64' in clean_r:
                del clean_r['visualization_base64']
            clean_results.append(clean_r)
        
        report = {
            'timestamp': timestamp,
            'comparison': comparison,
            'results': clean_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✓ Rapor kaydedildi: {filename}")


def main():
    """Ana test fonksiyonu"""
    print("=" * 60)
    print("SOLUNUM YOLU ACİL VAKA TESPİT SİSTEMİ - TEST")
    print("=" * 60)
    
    tester = RespiratoryEmergencyTester()
    
    # Menü
    print("\nTest seçenekleri:")
    print("1. Sentetik test görüntüleri oluştur ve test et")
    print("2. Kendi görüntülerini test et")
    print("3. Çıkış")
    
    choice = input("\nSeçim (1-3): ").strip()
    
    if choice == '1':
        # Sentetik görüntüler oluştur
        test_images = tester.create_synthetic_test_images()
        
        # Tüm görüntüleri test et
        image_paths = [img['path'] for img in test_images]
        results, comparison = tester.test_batch_images(image_paths)
        
        print("\n✓ Test tamamlandı!")
        print(f"Rapor: reports/ klasöründe")
        
    elif choice == '2':
        print("\nGörüntü yollarını girin (boş satır ile bitirin):")
        image_paths = []
        while True:
            path = input("Görüntü yolu: ").strip()
            if not path:
                break
            if Path(path).exists():
                image_paths.append(path)
            else:
                print(f"⚠️  Dosya bulunamadı: {path}")
        
        if image_paths:
            results, comparison = tester.test_batch_images(image_paths)
            print("\n✓ Test tamamlandı!")
        else:
            print("⚠️  Hiç görüntü eklenmedi")
    
    else:
        print("Çıkılıyor...")


if __name__ == "__main__":
    main()

