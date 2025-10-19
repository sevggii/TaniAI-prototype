"""
Solunum Yolu Acil Vaka Tespit Sistemi
=====================================

Bu modül X-ray görüntülerinden solunum yolu acil vakalarını tespit eder:
- Pnömotoraks (Acil!)
- Şiddetli Pnömoni
- Pulmoner Ödem
- Plevral Efüzyon
- Masif Atelektazi

OpenCV ile görüntü analizi + Makine öğrenmesi modeli kombinasyonu
"""

import cv2
import numpy as np
import pickle
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json

# PIL for image handling
from PIL import Image
import base64
import io

logger = logging.getLogger(__name__)


class RespiratoryEmergencyDetector:
    """Solunum yolu acil vaka tespit sınıfı"""
    
    def __init__(self, model_path: str = None):
        """
        Args:
            model_path: Pnömoni modeli yolu
        """
        self.model_path = model_path or "models/pneumonia_trained_model.pkl"
        self.model = None
        self.load_model()
        
        # Acil durum eşik değerleri
        self.emergency_thresholds = {
            'pneumothorax_score': 0.7,      # Pnömotoraks riski
            'severe_pneumonia_score': 0.75,  # Şiddetli pnömoni
            'pulmonary_edema_score': 0.65,   # Pulmoner ödem
            'pleural_effusion_score': 0.6,   # Plevral efüzyon
            'opacity_percentage': 40.0,      # Akciğer opasite %
            'asymmetry_score': 0.5,          # Akciğer asimetrisi
        }
        
        # Aciliyet seviyeleri
        self.urgency_levels = {
            'critical': {'min': 8, 'color': (0, 0, 255), 'response_time': '15 dakika'},
            'high': {'min': 6, 'color': (0, 140, 255), 'response_time': '30 dakika'},
            'moderate': {'min': 4, 'color': (0, 255, 255), 'response_time': '2 saat'},
            'low': {'min': 0, 'color': (0, 255, 0), 'response_time': '24 saat'}
        }
    
    def load_model(self):
        """Pnömoni modelini yükle"""
        try:
            model_file = Path(self.model_path)
            if model_file.exists():
                with open(model_file, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Model yüklendi: {self.model_path}")
            else:
                logger.warning(f"Model dosyası bulunamadı: {self.model_path}")
                logger.warning("Sadece OpenCV analizi kullanılacak")
        except Exception as e:
            logger.error(f"Model yükleme hatası: {e}")
            self.model = None
    
    def analyze_emergency(self, image_path: str = None, image_array: np.ndarray = None,
                         image_base64: str = None) -> Dict[str, Any]:
        """
        Acil durum analizi yap
        
        Args:
            image_path: Görüntü dosya yolu
            image_array: NumPy array olarak görüntü
            image_base64: Base64 encoded görüntü
            
        Returns:
            Detaylı acil durum analiz raporu
        """
        try:
            # Görüntüyü yükle
            image = self._load_image(image_path, image_array, image_base64)
            
            if image is None:
                raise ValueError("Görüntü yüklenemedi")
            
            # Görüntüyü işle
            processed_image = self._preprocess_image(image)
            
            # OpenCV ile özellik çıkarımı
            features = self._extract_respiratory_features(processed_image)
            
            # Model tahmini (varsa)
            ml_prediction = self._get_ml_prediction(processed_image)
            
            # Acil durum skorları hesapla
            emergency_scores = self._calculate_emergency_scores(features, ml_prediction)
            
            # Genel aciliyet skoru (1-10)
            urgency_score = self._calculate_urgency_score(emergency_scores)
            
            # Aciliyet seviyesi belirle
            urgency_level = self._determine_urgency_level(urgency_score)
            
            # Tespit edilen bulgular
            findings = self._identify_findings(emergency_scores, features)
            
            # Görselleştirme
            visualization = self._create_visualization(image, features, findings)
            
            # Rapor oluştur
            report = {
                'timestamp': datetime.now().isoformat(),
                'urgency_score': round(urgency_score, 2),
                'urgency_level': urgency_level,
                'emergency_scores': emergency_scores,
                'findings': findings,
                'features': {
                    'opacity_percentage': round(features['opacity_percentage'], 2),
                    'lung_asymmetry': round(features['asymmetry_score'], 2),
                    'density_mean': round(features['density_mean'], 2),
                    'texture_variance': round(features['texture_variance'], 2)
                },
                'recommendations': self._generate_recommendations(urgency_level, findings),
                'visualization_base64': self._image_to_base64(visualization),
                'requires_immediate_attention': urgency_score >= 6.0
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Acil durum analizi hatası: {e}")
            raise
    
    def _load_image(self, image_path: str = None, image_array: np.ndarray = None,
                   image_base64: str = None) -> np.ndarray:
        """Görüntüyü farklı kaynaklardan yükle"""
        if image_array is not None:
            return image_array
        
        if image_path is not None:
            return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        if image_base64 is not None:
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'L':
                image = image.convert('L')
            return np.array(image)
        
        return None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Görüntüyü analiz için hazırla"""
        # Resize
        target_size = (512, 512)
        resized = cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)
        
        # CLAHE - Kontrast artırma
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(resized)
        
        # Denoising
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
        
        return denoised
    
    def _extract_respiratory_features(self, image: np.ndarray) -> Dict[str, float]:
        """OpenCV ile solunum yolu özellikleri çıkar"""
        features = {}
        
        # 1. Akciğer bölgesini tespit et
        lung_mask = self._detect_lung_region(image)
        
        # 2. Opacity (Mat alan) tespiti
        opacity_mask = self._detect_opacity(image, lung_mask)
        opacity_percentage = (np.sum(opacity_mask > 0) / np.sum(lung_mask > 0)) * 100
        features['opacity_percentage'] = opacity_percentage
        
        # 3. Pnömotoraks göstergeleri (serbest hava, kollaps çizgisi)
        pneumothorax_indicators = self._detect_pneumothorax_signs(image, lung_mask)
        features['pneumothorax_score'] = pneumothorax_indicators['score']
        features['lung_collapse_detected'] = pneumothorax_indicators['collapse_detected']
        
        # 4. Akciğer asimetrisi (bir akciğer diğerinden daha mat/küçük)
        asymmetry_score = self._calculate_lung_asymmetry(image, lung_mask)
        features['asymmetry_score'] = asymmetry_score
        
        # 5. Plevral efüzyon göstergeleri (dip kısımlarda yoğunluk)
        effusion_score = self._detect_pleural_effusion(image, lung_mask)
        features['pleural_effusion_score'] = effusion_score
        
        # 6. Yoğunluk dağılımı
        lung_region = cv2.bitwise_and(image, lung_mask)
        features['density_mean'] = np.mean(lung_region[lung_mask > 0])
        features['density_std'] = np.std(lung_region[lung_mask > 0])
        
        # 7. Texture analizi (pulmoner ödem için)
        texture_features = self._analyze_texture(lung_region, lung_mask)
        features.update(texture_features)
        
        # 8. Kenar tespiti (pnömotoraks çizgisi için)
        edge_features = self._analyze_edges(image, lung_mask)
        features.update(edge_features)
        
        return features
    
    def _detect_lung_region(self, image: np.ndarray) -> np.ndarray:
        """Akciğer bölgesini tespit et"""
        # Threshold ile akciğer dokusunu ayır
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological işlemler
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)
        
        # En büyük iki bölgeyi bul (sağ ve sol akciğer)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(opened)
        
        # Alanları sırala
        areas = [(i, stats[i, cv2.CC_STAT_AREA]) for i in range(1, num_labels)]
        areas.sort(key=lambda x: x[1], reverse=True)
        
        # En büyük 2 bölgeyi al (akciğerler)
        lung_mask = np.zeros_like(image)
        for i in range(min(2, len(areas))):
            component_id = areas[i][0]
            lung_mask[labels == component_id] = 255
        
        return lung_mask
    
    def _detect_opacity(self, image: np.ndarray, lung_mask: np.ndarray) -> np.ndarray:
        """Mat alanları (opacity) tespit et"""
        # Akciğer bölgesini al
        lung_region = cv2.bitwise_and(image, lung_mask)
        
        # Yüksek yoğunluk alanlarını tespit et
        mean_density = np.mean(lung_region[lung_mask > 0])
        threshold = mean_density + np.std(lung_region[lung_mask > 0]) * 0.5
        
        _, opacity_mask = cv2.threshold(lung_region, threshold, 255, cv2.THRESH_BINARY)
        
        # Küçük gürültüleri temizle
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        opacity_mask = cv2.morphologyEx(opacity_mask, cv2.MORPH_OPEN, kernel)
        
        return opacity_mask
    
    def _detect_pneumothorax_signs(self, image: np.ndarray, lung_mask: np.ndarray) -> Dict:
        """Pnömotoraks belirtilerini tespit et"""
        # Pnömotoraks: akciğer ile göğüs duvarı arasında hava
        # Görüntüde: keskin çizgi, asimetri, azalmış akciğer alanı
        
        # Canny edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Akciğer bölgesindeki dikey çizgileri ara (kollaps çizgisi)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                                minLineLength=50, maxLineGap=10)
        
        vertical_lines = 0
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                # Dikey çizgiler (80-100 derece arası)
                if 80 <= angle <= 100:
                    vertical_lines += 1
        
        # Serbest hava göstergesi (çok düşük yoğunluk alanları)
        lung_region = cv2.bitwise_and(image, lung_mask)
        very_dark_areas = np.sum(lung_region < 50) / np.sum(lung_mask > 0)
        
        # Pnömotoraks skoru
        score = min(1.0, (vertical_lines / 10.0) + very_dark_areas)
        
        return {
            'score': score,
            'collapse_detected': vertical_lines > 3,
            'vertical_lines': vertical_lines,
            'dark_area_ratio': very_dark_areas
        }
    
    def _calculate_lung_asymmetry(self, image: np.ndarray, lung_mask: np.ndarray) -> float:
        """Akciğer asimetrisini hesapla"""
        h, w = image.shape
        mid = w // 2
        
        # Sağ ve sol akciğer bölgelerini ayır
        left_mask = lung_mask.copy()
        left_mask[:, mid:] = 0
        
        right_mask = lung_mask.copy()
        right_mask[:, :mid] = 0
        
        # Her iki tarafın yoğunluklarını karşılaştır
        lung_region = cv2.bitwise_and(image, lung_mask)
        
        left_density = np.mean(lung_region[left_mask > 0]) if np.sum(left_mask) > 0 else 0
        right_density = np.mean(lung_region[right_mask > 0]) if np.sum(right_mask) > 0 else 0
        
        # Asimetri skoru (0-1 arası)
        if left_density + right_density > 0:
            asymmetry = abs(left_density - right_density) / (left_density + right_density)
        else:
            asymmetry = 0
        
        return asymmetry
    
    def _detect_pleural_effusion(self, image: np.ndarray, lung_mask: np.ndarray) -> float:
        """Plevral efüzyon (akciğer dibinde sıvı) tespit et"""
        h, w = image.shape
        
        # Akciğerin alt 1/3'ünü incele
        bottom_third = int(h * 2 / 3)
        bottom_region = lung_mask.copy()
        bottom_region[:bottom_third, :] = 0
        
        if np.sum(bottom_region) == 0:
            return 0.0
        
        # Alt bölgedeki yoğunluğu üst bölge ile karşılaştır
        top_region = lung_mask.copy()
        top_region[bottom_third:, :] = 0
        
        lung_region = cv2.bitwise_and(image, lung_mask)
        
        bottom_density = np.mean(lung_region[bottom_region > 0]) if np.sum(bottom_region) > 0 else 0
        top_density = np.mean(lung_region[top_region > 0]) if np.sum(top_region) > 0 else 0
        
        # Efüzyon skoru: alt bölge daha mat ise yüksek
        if top_density > 0:
            effusion_score = max(0, (bottom_density - top_density) / top_density)
        else:
            effusion_score = 0
        
        return min(1.0, effusion_score)
    
    def _analyze_texture(self, lung_region: np.ndarray, lung_mask: np.ndarray) -> Dict:
        """Doku analizi (pulmoner ödem için)"""
        if np.sum(lung_mask) == 0:
            return {'texture_variance': 0.0, 'texture_homogeneity': 0.0}
        
        # Gabor filtreleri ile doku analizi
        frequencies = [0.1, 0.2, 0.3]
        texture_responses = []
        
        for freq in frequencies:
            kernel = cv2.getGaborKernel((21, 21), 8.0, 0, freq, 0.5, 0, ktype=cv2.CV_32F)
            filtered = cv2.filter2D(lung_region, cv2.CV_32F, kernel)
            texture_responses.append(np.std(filtered[lung_mask > 0]))
        
        return {
            'texture_variance': np.mean(texture_responses),
            'texture_homogeneity': 1.0 / (1.0 + np.var(texture_responses))
        }
    
    def _analyze_edges(self, image: np.ndarray, lung_mask: np.ndarray) -> Dict:
        """Kenar analizi"""
        edges = cv2.Canny(image, 50, 150)
        lung_edges = cv2.bitwise_and(edges, lung_mask)
        
        edge_density = np.sum(lung_edges > 0) / np.sum(lung_mask > 0) if np.sum(lung_mask) > 0 else 0
        
        return {
            'edge_density': edge_density
        }
    
    def _get_ml_prediction(self, image: np.ndarray) -> Dict:
        """ML model tahmini (varsa)"""
        if self.model is None:
            return {'pneumonia_probability': 0.0, 'model_available': False}
        
        try:
            # Modelin beklediği formata çevir
            # Basit örnek - gerçek model için uyarlanmalı
            features = image.flatten().reshape(1, -1)
            
            # Tahmin
            prediction = self.model.predict_proba(features)[0]
            
            return {
                'pneumonia_probability': float(prediction[1]) if len(prediction) > 1 else 0.0,
                'model_available': True
            }
        except Exception as e:
            logger.warning(f"ML tahmin hatası: {e}")
            return {'pneumonia_probability': 0.0, 'model_available': False}
    
    def _calculate_emergency_scores(self, features: Dict, ml_prediction: Dict) -> Dict:
        """Acil durum skorlarını hesapla"""
        scores = {}
        
        # Pnömotoraks skoru
        scores['pneumothorax'] = features['pneumothorax_score']
        
        # Şiddetli pnömoni skoru
        pneumonia_ml = ml_prediction.get('pneumonia_probability', 0.0)
        opacity = min(1.0, features['opacity_percentage'] / 60.0)
        scores['severe_pneumonia'] = (pneumonia_ml * 0.6 + opacity * 0.4)
        
        # Pulmoner ödem skoru (yaygin bilateral opacity + texture)
        texture_abnormal = min(1.0, features['texture_variance'] / 50.0)
        bilateral = features['asymmetry_score'] < 0.3  # Bilateral = düşük asimetri
        scores['pulmonary_edema'] = opacity * 0.5 + texture_abnormal * 0.3 + (0.2 if bilateral else 0)
        
        # Plevral efüzyon skoru
        scores['pleural_effusion'] = features['pleural_effusion_score']
        
        return scores
    
    def _calculate_urgency_score(self, emergency_scores: Dict) -> float:
        """Genel aciliyet skoru hesapla (1-10)"""
        # Ağırlıklı ortalama
        weights = {
            'pneumothorax': 4.0,        # En acil
            'severe_pneumonia': 2.5,
            'pulmonary_edema': 3.0,
            'pleural_effusion': 2.0
        }
        
        total_weight = sum(weights.values())
        weighted_sum = sum(emergency_scores[key] * weights[key] 
                          for key in emergency_scores if key in weights)
        
        # 0-1'den 1-10'a çevir
        urgency_score = 1 + (weighted_sum / total_weight) * 9
        
        return urgency_score
    
    def _determine_urgency_level(self, urgency_score: float) -> str:
        """Aciliyet seviyesini belirle"""
        for level, config in self.urgency_levels.items():
            if urgency_score >= config['min']:
                return level
        return 'low'
    
    def _identify_findings(self, emergency_scores: Dict, features: Dict) -> List[Dict]:
        """Tespit edilen bulguları listele"""
        findings = []
        
        # Pnömotoraks
        if emergency_scores['pneumothorax'] > self.emergency_thresholds['pneumothorax_score']:
            findings.append({
                'name': 'Pnömotoraks Şüphesi',
                'severity': 'CRITICAL',
                'confidence': round(emergency_scores['pneumothorax'] * 100, 1),
                'description': 'Akciğer kollapsı göstergeleri tespit edildi',
                'action': 'ACİL toraks cerrahisi konsültasyonu gerekli'
            })
        
        # Şiddetli pnömoni
        if emergency_scores['severe_pneumonia'] > self.emergency_thresholds['severe_pneumonia_score']:
            findings.append({
                'name': 'Şiddetli Pnömoni',
                'severity': 'HIGH',
                'confidence': round(emergency_scores['severe_pneumonia'] * 100, 1),
                'description': f'Yaygın akciğer opasite ({features["opacity_percentage"]:.1f}%)',
                'action': 'Yoğun bakım değerlendirmesi, antibiyoterapi'
            })
        
        # Pulmoner ödem
        if emergency_scores['pulmonary_edema'] > self.emergency_thresholds['pulmonary_edema_score']:
            findings.append({
                'name': 'Pulmoner Ödem',
                'severity': 'HIGH',
                'confidence': round(emergency_scores['pulmonary_edema'] * 100, 1),
                'description': 'Akciğerlerde sıvı birikimi bulguları',
                'action': 'Kardiyoloji konsültasyonu, diüretik tedavi'
            })
        
        # Plevral efüzyon
        if emergency_scores['pleural_effusion'] > self.emergency_thresholds['pleural_effusion_score']:
            findings.append({
                'name': 'Plevral Efüzyon',
                'severity': 'MODERATE',
                'confidence': round(emergency_scores['pleural_effusion'] * 100, 1),
                'description': 'Plevral aralıkta sıvı birikimi',
                'action': 'Torasentez değerlendirmesi'
            })
        
        if not findings:
            findings.append({
                'name': 'Normal Bulgular',
                'severity': 'LOW',
                'confidence': 95.0,
                'description': 'Acil patoloji tespit edilmedi',
                'action': 'Rutin takip'
            })
        
        return findings
    
    def _generate_recommendations(self, urgency_level: str, findings: List[Dict]) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        level_config = self.urgency_levels[urgency_level]
        recommendations.append(f"Müdahale süresi: {level_config['response_time']}")
        
        if urgency_level == 'critical':
            recommendations.append("🚨 ACİL DURUM - Hemen doktora bildir")
            recommendations.append("Hasta vital bulgularını monitörize et")
            recommendations.append("Acil müdahale ekibini hazırla")
        elif urgency_level == 'high':
            recommendations.append("⚠️ YÜKSEK ÖNCELİK - Doktora hızlıca bildir")
            recommendations.append("Hasta yakın takip altına alınmalı")
        elif urgency_level == 'moderate':
            recommendations.append("⚡ ORTA ÖNCELİK - Doktor değerlendirmesi gerekli")
            recommendations.append("Rutin takip protokolü uygula")
        else:
            recommendations.append("✓ DÜŞÜK ÖNCELİK - Rutin değerlendirme")
        
        # Bulgu bazlı öneriler
        for finding in findings:
            if finding['severity'] in ['CRITICAL', 'HIGH']:
                recommendations.append(f"• {finding['name']}: {finding['action']}")
        
        return recommendations
    
    def _create_visualization(self, image: np.ndarray, features: Dict, 
                            findings: List[Dict]) -> np.ndarray:
        """Analiz sonuçlarını görselleştir"""
        # Renkli görüntü oluştur
        vis_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # Akciğer maskesini çiz
        lung_mask = self._detect_lung_region(image)
        
        # Opacity alanlarını vurgula
        opacity_mask = self._detect_opacity(image, lung_mask)
        vis_image[opacity_mask > 0] = vis_image[opacity_mask > 0] * 0.5 + np.array([0, 0, 255]) * 0.5
        
        # Bulgular için renk kodu
        severity_colors = {
            'CRITICAL': (0, 0, 255),    # Kırmızı
            'HIGH': (0, 140, 255),      # Turuncu
            'MODERATE': (0, 255, 255),  # Sarı
            'LOW': (0, 255, 0)          # Yeşil
        }
        
        # Metin ekle
        y_offset = 30
        for finding in findings:
            color = severity_colors.get(finding['severity'], (255, 255, 255))
            text = f"{finding['name']}: {finding['confidence']:.1f}%"
            cv2.putText(vis_image, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y_offset += 30
        
        return vis_image
    
    def _image_to_base64(self, image: np.ndarray) -> str:
        """Görüntüyü base64'e çevir"""
        _, buffer = cv2.imencode('.jpg', image)
        return base64.b64encode(buffer).decode('utf-8')
    
    def batch_analyze(self, image_paths: List[str]) -> List[Dict]:
        """Birden fazla görüntüyü analiz et"""
        results = []
        
        for image_path in image_paths:
            try:
                result = self.analyze_emergency(image_path=image_path)
                result['image_path'] = image_path
                results.append(result)
            except Exception as e:
                logger.error(f"Analiz hatası ({image_path}): {e}")
                results.append({
                    'image_path': image_path,
                    'error': str(e),
                    'urgency_score': 0
                })
        
        return results
    
    def compare_analyses(self, results: List[Dict]) -> Dict:
        """Birden fazla analizi karşılaştır"""
        if not results:
            return {}
        
        comparison = {
            'total_images': len(results),
            'average_urgency': np.mean([r.get('urgency_score', 0) for r in results]),
            'critical_cases': sum(1 for r in results if r.get('urgency_level') == 'critical'),
            'high_priority_cases': sum(1 for r in results if r.get('urgency_level') == 'high'),
            'urgency_distribution': {}
        }
        
        # Aciliyet dağılımı
        for level in ['critical', 'high', 'moderate', 'low']:
            count = sum(1 for r in results if r.get('urgency_level') == level)
            comparison['urgency_distribution'][level] = count
        
        # En yüksek aciliyet
        if results:
            max_urgency = max(results, key=lambda x: x.get('urgency_score', 0))
            comparison['highest_urgency_case'] = {
                'image': max_urgency.get('image_path', 'unknown'),
                'score': max_urgency.get('urgency_score', 0),
                'findings': max_urgency.get('findings', [])
            }
        
        return comparison


# Kullanım örneği
if __name__ == "__main__":
    # Logging ayarla
    logging.basicConfig(level=logging.INFO)
    
    # Detector oluştur
    detector = RespiratoryEmergencyDetector()
    
    print("=" * 60)
    print("SOLUNUM YOLU ACİL VAKA TESPİT SİSTEMİ")
    print("=" * 60)
    print("\nSistem hazır. Test için örnek görüntüler gerekli.")
    print("\nKullanım:")
    print("  detector.analyze_emergency(image_path='chest_xray.jpg')")
    print("  detector.batch_analyze(['image1.jpg', 'image2.jpg'])")

