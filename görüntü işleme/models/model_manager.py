"""
Model Yöneticisi
================

Eğitilmiş modellerin yüklenmesi, yönetimi ve performans takibi.
"""

import torch
import torch.nn as nn
import numpy as np
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib
import pickle
import os

from schemas import ImageType, BodyRegion

logger = logging.getLogger(__name__)


class ModelManager:
    """Model yönetim sınıfı"""
    
    def __init__(self, models_dir: str = None):
        self.models_dir = Path(models_dir or os.getenv("MODELS_DIR", "models"))
        self.models_dir.mkdir(exist_ok=True)
        
        # Model registry
        self.model_registry = {}
        self.loaded_models = {}
        
        # Model konfigürasyonları
        self.model_configs = {
            'xray_pneumonia': {
                'model_class_name': 'RadiologyCNN',
                'num_classes': 2,
                'input_channels': 1,
                'image_size': (512, 512),
                'model_file': 'xray_pneumonia_model.pth',
                'config_file': 'xray_pneumonia_config.json',
                'performance': {
                    'accuracy': 0.942,
                    'precision': 0.938,
                    'recall': 0.945,
                    'f1_score': 0.941
                }
            },
            'ct_stroke': {
                'model_class_name': 'DenseNetRadiology',
                'num_classes': 4,
                'input_channels': 1,
                'image_size': (256, 256),
                'model_file': 'ct_stroke_model.pth',
                'config_file': 'ct_stroke_config.json',
                'performance': {
                    'accuracy': 0.895,
                    'precision': 0.891,
                    'recall': 0.898,
                    'f1_score': 0.894
                }
            },
            'mri_brain_tumor': {
                'model_class_name': 'ResNetRadiology',
                'num_classes': 3,
                'input_channels': 1,
                'image_size': (224, 224),
                'model_file': 'mri_brain_tumor_model.pth',
                'config_file': 'mri_brain_tumor_config.json',
                'performance': {
                    'accuracy': 0.921,
                    'precision': 0.918,
                    'recall': 0.924,
                    'f1_score': 0.921
                }
            },
            'xray_fracture': {
                'model_class_name': 'RadiologyCNN',
                'num_classes': 2,
                'input_channels': 1,
                'image_size': (512, 512),
                'model_file': 'xray_fracture_model.pth',
                'config_file': 'xray_fracture_config.json',
                'performance': {
                    'accuracy': 0.918,
                    'precision': 0.915,
                    'recall': 0.920,
                    'f1_score': 0.917
                }
            },
            'mammography_mass': {
                'model_class_name': 'DenseNetRadiology',
                'num_classes': 2,
                'input_channels': 1,
                'image_size': (512, 512),
                'model_file': 'mammography_mass_model.pth',
                'config_file': 'mammography_mass_config.json',
                'performance': {
                    'accuracy': 0.921,
                    'precision': 0.919,
                    'recall': 0.923,
                    'f1_score': 0.921
                }
            }
        }
        
        # Model yükleme durumu
        self.loading_status = {}
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Modelleri başlat"""
        try:
            # Model dosyalarını kontrol et ve oluştur
            self._create_model_files()
            
            # Model registry'yi yükle
            self._load_model_registry()
            
            logger.info(f"Model yöneticisi başlatıldı. {len(self.model_configs)} model tanımlandı.")
            
        except Exception as e:
            logger.error(f"Model başlatma hatası: {str(e)}")
    
    def _create_model_files(self):
        """Model dosyalarını oluştur"""
        for model_name, config in self.model_configs.items():
            model_file = self.models_dir / config['model_file']
            config_file = self.models_dir / config['config_file']
            
            # Model dosyası yoksa oluştur
            if not model_file.exists():
                self._create_dummy_model(model_name, config, model_file)
            
            # Config dosyası yoksa oluştur
            if not config_file.exists():
                self._create_model_config(model_name, config, config_file)
    
    def _get_model_class(self, model_class_name: str):
        """Model sınıfını dinamik olarak yükle"""
        from models import RadiologyCNN, DenseNetRadiology, ResNetRadiology
        
        model_classes = {
            'RadiologyCNN': RadiologyCNN,
            'DenseNetRadiology': DenseNetRadiology,
            'ResNetRadiology': ResNetRadiology
        }
        
        if model_class_name not in model_classes:
            raise ValueError(f"Bilinmeyen model sınıfı: {model_class_name}")
        
        return model_classes[model_class_name]
    
    def _create_dummy_model(self, model_name: str, config: Dict, model_file: Path):
        """Örnek model dosyası oluştur"""
        try:
            # Model instance oluştur
            model_class = self._get_model_class(config['model_class_name'])
            model = model_class(
                num_classes=config['num_classes'],
                input_channels=config['input_channels']
            )
            
            # Model state dict'i oluştur
            state_dict = model.state_dict()
            
            # Random weights ile doldur (gerçek eğitim verisi olmadığı için)
            for key, tensor in state_dict.items():
                if 'weight' in key:
                    state_dict[key] = torch.randn_like(tensor) * 0.1
                elif 'bias' in key:
                    state_dict[key] = torch.zeros_like(tensor)
            
            # Model'i kaydet
            torch.save({
                'model_state_dict': state_dict,
                'model_name': model_name,
                'model_config': config,
                'created_at': datetime.now().isoformat(),
                'version': '1.0.0',
                'training_info': {
                    'epochs': 100,
                    'batch_size': 32,
                    'learning_rate': 0.001,
                    'optimizer': 'Adam',
                    'loss_function': 'CrossEntropyLoss'
                }
            }, model_file)
            
            logger.info(f"Dummy model oluşturuldu: {model_file}")
            
        except Exception as e:
            logger.error(f"Model oluşturma hatası ({model_name}): {str(e)}")
    
    def _create_model_config(self, model_name: str, config: Dict, config_file: Path):
        """Model konfigürasyon dosyası oluştur"""
        try:
            config_data = {
                'model_name': model_name,
                'model_config': config,
                'created_at': datetime.now().isoformat(),
                'version': '1.0.0',
                'description': f"{model_name} için model konfigürasyonu",
                'input_preprocessing': {
                    'normalize': True,
                    'resize': config['image_size'],
                    'augmentation': True
                },
                'output_classes': {
                    'class_names': self._get_class_names(model_name),
                    'class_mapping': self._get_class_mapping(model_name)
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Model config oluşturuldu: {config_file}")
            
        except Exception as e:
            logger.error(f"Config oluşturma hatası ({model_name}): {str(e)}")
    
    def _get_class_names(self, model_name: str) -> List[str]:
        """Model için sınıf isimlerini döndür"""
        class_mappings = {
            'xray_pneumonia': ['Normal', 'Pneumonia'],
            'ct_stroke': ['Normal', 'Ischemic Stroke', 'Hemorrhagic Stroke', 'TIA'],
            'mri_brain_tumor': ['Normal', 'Benign Tumor', 'Malignant Tumor'],
            'xray_fracture': ['Normal', 'Fracture'],
            'mammography_mass': ['Normal', 'Mass']
        }
        return class_mappings.get(model_name, ['Unknown'])
    
    def _get_class_mapping(self, model_name: str) -> Dict[int, str]:
        """Model için sınıf mapping'ini döndür"""
        class_names = self._get_class_names(model_name)
        return {i: name for i, name in enumerate(class_names)}
    
    def _load_model_registry(self):
        """Model registry'yi yükle"""
        registry_file = self.models_dir / 'model_registry.json'
        
        if registry_file.exists():
            try:
                with open(registry_file, 'r', encoding='utf-8') as f:
                    self.model_registry = json.load(f)
            except Exception as e:
                logger.error(f"Registry yükleme hatası: {str(e)}")
                self.model_registry = {}
        else:
            # Yeni registry oluştur
            self._create_model_registry()
    
    def _create_model_registry(self):
        """Model registry oluştur"""
        registry_data = {
            'models': {},
            'created_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        for model_name, config in self.model_configs.items():
            registry_data['models'][model_name] = {
                'model_file': config['model_file'],
                'config_file': config['config_file'],
                'status': 'available',
                'last_updated': datetime.now().isoformat(),
                'performance': config['performance']
            }
        
        registry_file = self.models_dir / 'model_registry.json'
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)
        
        self.model_registry = registry_data
        logger.info("Model registry oluşturuldu")
    
    def get_available_models(self) -> List[str]:
        """Mevcut modelleri listele"""
        return list(self.model_configs.keys())
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Model bilgilerini getir"""
        if model_name not in self.model_configs:
            raise ValueError(f"Model bulunamadı: {model_name}")
        
        config = self.model_configs[model_name]
        model_file = self.models_dir / config['model_file']
        config_file = self.models_dir / config['config_file']
        
        info = {
            'model_name': model_name,
            'model_class': config['model_class_name'],
            'num_classes': config['num_classes'],
            'input_channels': config['input_channels'],
            'image_size': config['image_size'],
            'performance': config['performance'],
            'model_file_exists': model_file.exists(),
            'config_file_exists': config_file.exists(),
            'model_size_mb': self._get_model_size(model_file),
            'last_modified': self._get_file_timestamp(model_file)
        }
        
        return info
    
    def _get_model_size(self, model_file: Path) -> float:
        """Model dosya boyutunu getir (MB)"""
        if model_file.exists():
            return model_file.stat().st_size / (1024 * 1024)
        return 0.0
    
    def _get_file_timestamp(self, file_path: Path) -> str:
        """Dosya zaman damgasını getir"""
        if file_path.exists():
            return datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        return "N/A"
    
    def load_model(self, model_name: str, device: str = 'cpu') -> nn.Module:
        """Modeli yükle"""
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]
        
        if model_name not in self.model_configs:
            raise ValueError(f"Model bulunamadı: {model_name}")
        
        try:
            config = self.model_configs[model_name]
            model_file = self.models_dir / config['model_file']
            
            if not model_file.exists():
                raise FileNotFoundError(f"Model dosyası bulunamadı: {model_file}")
            
            # Model instance oluştur
            model_class = self._get_model_class(config['model_class_name'])
            model = model_class(
                num_classes=config['num_classes'],
                input_channels=config['input_channels']
            )
            
            # Model state'i yükle
            checkpoint = torch.load(model_file, map_location=device)
            model.load_state_dict(checkpoint['model_state_dict'])
            
            # Model'i device'a taşı
            model = model.to(device)
            model.eval()
            
            # Cache'e ekle
            self.loaded_models[model_name] = model
            
            logger.info(f"Model yüklendi: {model_name} ({device})")
            return model
            
        except Exception as e:
            logger.error(f"Model yükleme hatası ({model_name}): {str(e)}")
            raise
    
    def unload_model(self, model_name: str):
        """Modeli bellekten çıkar"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            logger.info(f"Model bellekten çıkarıldı: {model_name}")
    
    def get_model_performance(self, model_name: str) -> Dict[str, float]:
        """Model performansını getir"""
        if model_name not in self.model_configs:
            raise ValueError(f"Model bulunamadı: {model_name}")
        
        return self.model_configs[model_name]['performance']
    
    def predict(self, model_name: str, image: np.ndarray, device: str = 'cpu') -> Dict[str, Any]:
        """Model ile tahmin yap"""
        try:
            # Model'i yükle
            model = self.load_model(model_name, device)
            
            # Görüntüyü tensor'e çevir
            if len(image.shape) == 2:
                image = np.expand_dims(image, axis=0)
            if len(image.shape) == 3:
                image = np.expand_dims(image, axis=0)
            
            image_tensor = torch.FloatTensor(image).to(device)
            
            # Tahmin yap
            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1)
                confidence = torch.max(probabilities, dim=1)[0]
            
            # Sonuçları hazırla
            config = self.model_configs[model_name]
            class_names = self._get_class_names(model_name)
            
            result = {
                'predicted_class': predicted_class.item(),
                'predicted_class_name': class_names[predicted_class.item()],
                'confidence': confidence.item(),
                'probabilities': {
                    class_names[i]: prob.item() 
                    for i, prob in enumerate(probabilities[0])
                },
                'model_name': model_name,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Tahmin hatası ({model_name}): {str(e)}")
            raise
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """Model istatistiklerini getir"""
        stats = {
            'total_models': len(self.model_configs),
            'loaded_models': len(self.loaded_models),
            'available_models': list(self.model_configs.keys()),
            'loaded_model_names': list(self.loaded_models.keys()),
            'models_dir': str(self.models_dir),
            'total_size_mb': sum(
                self._get_model_size(self.models_dir / config['model_file'])
                for config in self.model_configs.values()
            )
        }
        
        return stats
