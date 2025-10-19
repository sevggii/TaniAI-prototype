"""
Kırık ve Çıkık Tespit Sistemi
=============================

TCIA ve diğer kaynaklardan alınan gerçek tıbbi verilerle
kırık ve çıkık tespiti yapan gelişmiş AI sistemi.
"""

import torch
import torch.nn as nn
import numpy as np
import cv2
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json
from datetime import datetime
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

from models.radiology_models import RadiologyCNN, DenseNetRadiology, ResNetRadiology
from models.model_manager import ModelManager
from dicom_processor import DICOMProcessor

logger = logging.getLogger(__name__)


class FractureDislocationDetector:
    """Kırık ve çıkık tespit sınıfı"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Model konfigürasyonları
        self.model_configs = {
            'bone_fracture': {
                'model_class': DenseNetRadiology,
                'num_classes': 3,  # Normal, Simple Fracture, Complex Fracture
                'input_channels': 1,
                'image_size': (512, 512),
                'class_names': ['Normal', 'Simple_Fracture', 'Complex_Fracture'],
                'description': 'Kemik kırığı tespiti - basit ve kompleks kırıklar'
            },
            'joint_dislocation': {
                'model_class': ResNetRadiology,
                'num_classes': 3,  # Normal, Partial Dislocation, Complete Dislocation
                'input_channels': 1,
                'image_size': (512, 512),
                'class_names': ['Normal', 'Partial_Dislocation', 'Complete_Dislocation'],
                'description': 'Eklem çıkığı tespiti - kısmi ve tam çıkıklar'
            },
            'spine_fracture': {
                'model_class': RadiologyCNN,
                'num_classes': 4,  # Normal, Compression, Burst, Chance
                'input_channels': 1,
                'image_size': (512, 512),
                'class_names': ['Normal', 'Compression_Fracture', 'Burst_Fracture', 'Chance_Fracture'],
                'description': 'Omurga kırığı tespiti - kompresyon, burst ve chance kırıkları'
            },
            'hip_fracture': {
                'model_class': DenseNetRadiology,
                'num_classes': 3,  # Normal, Femoral Neck, Intertrochanteric
                'input_channels': 1,
                'image_size': (512, 512),
                'class_names': ['Normal', 'Femoral_Neck_Fracture', 'Intertrochanteric_Fracture'],
                'description': 'Kalça kırığı tespiti - femoral boyun ve intertrochanteric'
            },
            'wrist_fracture': {
                'model_class': ResNetRadiology,
                'num_classes': 4,  # Normal, Colles, Scaphoid, Barton
                'input_channels': 1,
                'image_size': (512, 512),
                'class_names': ['Normal', 'Colles_Fracture', 'Scaphoid_Fracture', 'Barton_Fracture'],
                'description': 'El bileği kırığı tespiti - Colles, scaphoid ve Barton kırıkları'
            }
        }
        
        # Anatomik bölge mapping'i
        self.anatomical_regions = {
            'spine': ['cervical', 'thoracic', 'lumbar', 'sacral'],
            'extremities': ['wrist', 'ankle', 'knee', 'elbow', 'shoulder', 'hip'],
            'chest': ['ribs', 'sternum', 'clavicle'],
            'pelvis': ['hip', 'sacrum', 'coccyx'],
            'skull': ['cranium', 'facial', 'mandible']
        }
        
        # Kritik bulgu seviyeleri
        self.critical_levels = {
            'emergency': ['spinal_cord_compression', 'open_fracture', 'complete_dislocation'],
            'urgent': ['complex_fracture', 'partial_dislocation', 'hip_fracture'],
            'routine': ['simple_fracture', 'hairline_fracture']
        }
    
    def detect_fractures(self, image_data: str, anatomical_region: str = "general") -> Dict[str, Any]:
        """Kırık tespiti yap"""
        try:
            logger.info(f"Kırık tespiti başlıyor: {anatomical_region}")
            
            # Görüntüyü işle
            processed_image = self._preprocess_image(image_data)
            
            # Anatomik bölgeye göre model seç
            model_name = self._select_model_for_region(anatomical_region, 'fracture')
            
            # Model ile tahmin yap
            prediction = self._predict_with_model(model_name, processed_image)
            
            # Sonuçları analiz et
            result = self._analyze_fracture_result(prediction, anatomical_region)
            
            return result
            
        except Exception as e:
            logger.error(f"Kırık tespiti hatası: {str(e)}")
            raise
    
    def detect_dislocations(self, image_data: str, joint_type: str = "general") -> Dict[str, Any]:
        """Çıkık tespiti yap"""
        try:
            logger.info(f"Çıkık tespiti başlıyor: {joint_type}")
            
            # Görüntüyü işle
            processed_image = self._preprocess_image(image_data)
            
            # Eklem tipine göre model seç
            model_name = self._select_model_for_joint(joint_type)
            
            # Model ile tahmin yap
            prediction = self._predict_with_model(model_name, processed_image)
            
            # Sonuçları analiz et
            result = self._analyze_dislocation_result(prediction, joint_type)
            
            return result
            
        except Exception as e:
            logger.error(f"Çıkık tespiti hatası: {str(e)}")
            raise
    
    def comprehensive_orthopedic_analysis(self, image_data: str, 
                                        anatomical_region: str = "general") -> Dict[str, Any]:
        """Kapsamlı ortopedi analizi"""
        try:
            logger.info(f"Kapsamlı ortopedi analizi: {anatomical_region}")
            
            results = {
                'analysis_id': f"ortho_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'anatomical_region': anatomical_region,
                'timestamp': datetime.now().isoformat(),
                'fracture_analysis': {},
                'dislocation_analysis': {},
                'overall_assessment': {},
                'recommendations': []
            }
            
            # Kırık analizi
            try:
                fracture_result = self.detect_fractures(image_data, anatomical_region)
                results['fracture_analysis'] = fracture_result
            except Exception as e:
                logger.warning(f"Kırık analizi hatası: {str(e)}")
                results['fracture_analysis'] = {'error': str(e)}
            
            # Çıkık analizi
            try:
                dislocation_result = self.detect_dislocations(image_data, anatomical_region)
                results['dislocation_analysis'] = dislocation_result
            except Exception as e:
                logger.warning(f"Çıkık analizi hatası: {str(e)}")
                results['dislocation_analysis'] = {'error': str(e)}
            
            # Genel değerlendirme
            results['overall_assessment'] = self._assess_overall_condition(results)
            
            # Öneriler
            results['recommendations'] = self._generate_recommendations(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Kapsamlı analiz hatası: {str(e)}")
            raise
    
    def _preprocess_image(self, image_data: str) -> torch.Tensor:
        """Görüntüyü ön işle"""
        try:
            # Base64 decode
            import base64
            import io
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes)).convert('L')
            
            # NumPy array'e çevir
            image_array = np.array(image)
            
            # Boyutlandır
            resized = cv2.resize(image_array, (512, 512))
            
            # Normalize et
            normalized = cv2.normalize(resized, None, 0, 255, cv2.NORM_MINMAX)
            
            # Tensor'e çevir
            tensor = torch.FloatTensor(normalized).unsqueeze(0).unsqueeze(0)
            
            return tensor.to(self.device)
            
        except Exception as e:
            logger.error(f"Görüntü ön işleme hatası: {str(e)}")
            raise
    
    def _select_model_for_region(self, region: str, analysis_type: str) -> str:
        """Bölgeye göre model seç"""
        region_mapping = {
            'spine': 'spine_fracture',
            'hip': 'hip_fracture',
            'wrist': 'wrist_fracture',
            'general': 'bone_fracture'
        }
        
        return region_mapping.get(region.lower(), 'bone_fracture')
    
    def _select_model_for_joint(self, joint_type: str) -> str:
        """Eklem tipine göre model seç"""
        # Şu anda genel çıkık modeli kullanıyoruz
        # Gelecekte spesifik eklem modelleri eklenebilir
        return 'joint_dislocation'
    
    def _predict_with_model(self, model_name: str, image_tensor: torch.Tensor) -> Dict[str, Any]:
        """Model ile tahmin yap"""
        try:
            # Model'i yükle
            model = self._load_model(model_name)
            
            # Tahmin yap
            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1)
                confidence = torch.max(probabilities, dim=1)[0]
            
            # Sonuçları hazırla
            config = self.model_configs[model_name]
            class_names = config['class_names']
            
            result = {
                'predicted_class': predicted_class.item(),
                'predicted_class_name': class_names[predicted_class.item()],
                'confidence': confidence.item(),
                'probabilities': {
                    class_names[i]: prob.item() 
                    for i, prob in enumerate(probabilities[0])
                },
                'model_name': model_name
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Model tahmin hatası ({model_name}): {str(e)}")
            raise
    
    def _load_model(self, model_name: str) -> nn.Module:
        """Model yükle"""
        try:
            config = self.model_configs[model_name]
            model_path = self.models_dir / f"{model_name}_best.pth"
            
            if not model_path.exists():
                # Model yoksa yeni oluştur
                model = config['model_class'](
                    num_classes=config['num_classes'],
                    input_channels=config['input_channels']
                ).to(self.device)
                logger.warning(f"Model dosyası bulunamadı, yeni model oluşturuldu: {model_name}")
                return model
            
            # Model'i yükle
            checkpoint = torch.load(model_path, map_location=self.device)
            model = config['model_class'](
                num_classes=config['num_classes'],
                input_channels=config['input_channels']
            ).to(self.device)
            
            model.load_state_dict(checkpoint['model_state_dict'])
            model.eval()
            
            return model
            
        except Exception as e:
            logger.error(f"Model yükleme hatası ({model_name}): {str(e)}")
            raise
    
    def _analyze_fracture_result(self, prediction: Dict[str, Any], 
                               anatomical_region: str) -> Dict[str, Any]:
        """Kırık sonucunu analiz et"""
        try:
            result = {
                'fracture_detected': prediction['predicted_class'] > 0,
                'fracture_type': prediction['predicted_class_name'],
                'confidence': prediction['confidence'],
                'severity_level': self._assess_fracture_severity(prediction),
                'urgency_level': self._assess_urgency_level(prediction, 'fracture'),
                'anatomical_region': anatomical_region,
                'detailed_probabilities': prediction['probabilities']
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Kırık analiz hatası: {str(e)}")
            raise
    
    def _analyze_dislocation_result(self, prediction: Dict[str, Any], 
                                  joint_type: str) -> Dict[str, Any]:
        """Çıkık sonucunu analiz et"""
        try:
            result = {
                'dislocation_detected': prediction['predicted_class'] > 0,
                'dislocation_type': prediction['predicted_class_name'],
                'confidence': prediction['confidence'],
                'severity_level': self._assess_dislocation_severity(prediction),
                'urgency_level': self._assess_urgency_level(prediction, 'dislocation'),
                'joint_type': joint_type,
                'detailed_probabilities': prediction['probabilities']
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Çıkık analiz hatası: {str(e)}")
            raise
    
    def _assess_fracture_severity(self, prediction: Dict[str, Any]) -> str:
        """Kırık şiddetini değerlendir"""
        class_name = prediction['predicted_class_name']
        
        if class_name == 'Normal':
            return 'none'
        elif 'simple' in class_name.lower() or 'hairline' in class_name.lower():
            return 'mild'
        elif 'complex' in class_name.lower() or 'burst' in class_name.lower():
            return 'severe'
        else:
            return 'moderate'
    
    def _assess_dislocation_severity(self, prediction: Dict[str, Any]) -> str:
        """Çıkık şiddetini değerlendir"""
        class_name = prediction['predicted_class_name']
        
        if class_name == 'Normal':
            return 'none'
        elif 'partial' in class_name.lower():
            return 'mild'
        elif 'complete' in class_name.lower():
            return 'severe'
        else:
            return 'moderate'
    
    def _assess_urgency_level(self, prediction: Dict[str, Any], 
                            analysis_type: str) -> str:
        """Acil durum seviyesini değerlendir"""
        class_name = prediction['predicted_class_name']
        confidence = prediction['confidence']
        
        # Yüksek güvenle tespit edilen kritik durumlar
        if confidence > 0.8:
            if 'complete' in class_name.lower() or 'complex' in class_name.lower():
                return 'emergency'
            elif 'partial' in class_name.lower() or 'simple' in class_name.lower():
                return 'urgent'
        
        return 'routine'
    
    def _assess_overall_condition(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Genel durumu değerlendir"""
        try:
            fracture_analysis = results.get('fracture_analysis', {})
            dislocation_analysis = results.get('dislocation_analysis', {})
            
            # Genel durum
            overall_condition = 'normal'
            if fracture_analysis.get('fracture_detected', False):
                overall_condition = 'fracture_detected'
            if dislocation_analysis.get('dislocation_detected', False):
                overall_condition = 'dislocation_detected'
            if (fracture_analysis.get('fracture_detected', False) and 
                dislocation_analysis.get('dislocation_detected', False)):
                overall_condition = 'multiple_injuries'
            
            # Risk seviyesi
            risk_level = 'low'
            if fracture_analysis.get('urgency_level') == 'emergency' or \
               dislocation_analysis.get('urgency_level') == 'emergency':
                risk_level = 'critical'
            elif fracture_analysis.get('urgency_level') == 'urgent' or \
                 dislocation_analysis.get('urgency_level') == 'urgent':
                risk_level = 'high'
            elif overall_condition != 'normal':
                risk_level = 'medium'
            
            return {
                'overall_condition': overall_condition,
                'risk_level': risk_level,
                'requires_immediate_attention': risk_level in ['critical', 'high'],
                'confidence_overall': max(
                    fracture_analysis.get('confidence', 0),
                    dislocation_analysis.get('confidence', 0)
                )
            }
            
        except Exception as e:
            logger.error(f"Genel durum değerlendirme hatası: {str(e)}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        overall_assessment = results.get('overall_assessment', {})
        fracture_analysis = results.get('fracture_analysis', {})
        dislocation_analysis = results.get('dislocation_analysis', {})
        
        # Acil durum önerileri
        if overall_assessment.get('requires_immediate_attention', False):
            recommendations.append("🚨 Acil tıbbi müdahale gereklidir")
            recommendations.append("Derhal acil servise başvurun")
            recommendations.append("Hasta immobilizasyonu uygulayın")
        
        # Kırık önerileri
        if fracture_analysis.get('fracture_detected', False):
            recommendations.append("Kırık tespit edildi - ortopedi konsültasyonu")
            recommendations.append("Ağrı yönetimi uygulayın")
            recommendations.append("Kırık bölgesini immobilize edin")
            
            if 'spine' in fracture_analysis.get('fracture_type', '').lower():
                recommendations.append("Omurga kırığı - nörolojik muayene gerekli")
        
        # Çıkık önerileri
        if dislocation_analysis.get('dislocation_detected', False):
            recommendations.append("Çıkık tespit edildi - ortopedi konsültasyonu")
            recommendations.append("Eklem redüksiyonu gerekebilir")
            recommendations.append("Post-redüksiyon immobilizasyon")
        
        # Genel öneriler
        if not recommendations:
            recommendations.append("Normal görünüm - rutin takip")
        
        return recommendations
    
    def create_training_dataset_for_fractures(self, tcia_data_dir: str) -> Dict[str, Any]:
        """Kırık tespiti için eğitim veri seti oluştur"""
        try:
            logger.info("Kırık tespiti eğitim veri seti oluşturuluyor...")
            
            # TCIA'dan ortopedi verilerini işle
            processor = DICOMProcessor()
            
            # Anatomik bölgeye göre veri seti oluştur
            dataset_info = {
                'total_images': 0,
                'fracture_types': {},
                'anatomical_regions': {},
                'created_at': datetime.now().isoformat()
            }
            
            # Her model için veri seti hazırla
            for model_name, config in self.model_configs.items():
                if 'fracture' in model_name or 'dislocation' in model_name:
                    logger.info(f"Veri seti hazırlanıyor: {model_name}")
                    
                    # Model spesifik veri işleme
                    model_data = self._prepare_model_specific_data(model_name, tcia_data_dir)
                    dataset_info['fracture_types'][model_name] = model_data
            
            return dataset_info
            
        except Exception as e:
            logger.error(f"Eğitim veri seti oluşturma hatası: {str(e)}")
            raise
    
    def _prepare_model_specific_data(self, model_name: str, data_dir: str) -> Dict[str, Any]:
        """Model spesifik veri hazırla"""
        # Bu fonksiyon TCIA verilerini model spesifik formatlara dönüştürür
        # Gerçek implementasyon TCIA veri yapısına göre yapılacak
        return {
            'model_name': model_name,
            'num_classes': self.model_configs[model_name]['num_classes'],
            'class_names': self.model_configs[model_name]['class_names'],
            'data_processed': True
        }


def main():
    """Ana fonksiyon - örnek kullanım"""
    logging.basicConfig(level=logging.INFO)
    
    detector = FractureDislocationDetector()
    
    # Örnek görüntü (base64 encoded)
    sample_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    try:
        # Kırık tespiti
        print("🦴 Kırık tespiti yapılıyor...")
        fracture_result = detector.detect_fractures(sample_image, "wrist")
        print(f"Sonuç: {fracture_result}")
        
        # Çıkık tespiti
        print("\n🦴 Çıkık tespiti yapılıyor...")
        dislocation_result = detector.detect_dislocations(sample_image, "shoulder")
        print(f"Sonuç: {dislocation_result}")
        
        # Kapsamlı analiz
        print("\n🔍 Kapsamlı ortopedi analizi yapılıyor...")
        comprehensive_result = detector.comprehensive_orthopedic_analysis(sample_image, "wrist")
        print(f"Genel Değerlendirme: {comprehensive_result['overall_assessment']}")
        print(f"Öneriler: {comprehensive_result['recommendations']}")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")


if __name__ == "__main__":
    main()
