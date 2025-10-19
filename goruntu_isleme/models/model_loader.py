"""
Model Yükleme Sistemi
=====================

Eğitilmiş modellerin yüklenmesi, cache'lenmesi ve
performans optimizasyonu için gerekli sınıflar.
"""

import torch
import torch.nn as nn
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import threading
import time
import gc

from schemas import ImageType, BodyRegion

logger = logging.getLogger(__name__)


class ModelCache:
    """Model cache yöneticisi"""
    
    def __init__(self, max_models: int = 5, max_memory_mb: int = 2048):
        self.max_models = max_models
        self.max_memory_mb = max_memory_mb
        self.cache = {}
        self.access_times = {}
        self.model_sizes = {}
        self.lock = threading.RLock()
    
    def get(self, model_name: str) -> Optional[nn.Module]:
        """Cache'den model getir"""
        with self.lock:
            if model_name in self.cache:
                self.access_times[model_name] = time.time()
                logger.debug(f"Model cache'den yüklendi: {model_name}")
                return self.cache[model_name]
            return None
    
    def put(self, model_name: str, model: nn.Module):
        """Cache'e model ekle"""
        with self.lock:
            # Model boyutunu hesapla
            model_size = self._calculate_model_size(model)
            self.model_sizes[model_name] = model_size
            
            # Memory kontrolü
            if self._should_evict():
                self._evict_least_recently_used()
            
            # Model'i cache'e ekle
            self.cache[model_name] = model
            self.access_times[model_name] = time.time()
            
            logger.info(f"Model cache'e eklendi: {model_name} ({model_size:.1f}MB)")
    
    def remove(self, model_name: str):
        """Cache'den model çıkar"""
        with self.lock:
            if model_name in self.cache:
                del self.cache[model_name]
                del self.access_times[model_name]
                del self.model_sizes[model_name]
                logger.info(f"Model cache'den çıkarıldı: {model_name}")
    
    def clear(self):
        """Cache'i temizle"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.model_sizes.clear()
            logger.info("Model cache temizlendi")
    
    def _calculate_model_size(self, model: nn.Module) -> float:
        """Model boyutunu hesapla (MB)"""
        try:
            # Model parametrelerini say
            total_params = sum(p.numel() for p in model.parameters())
            # Her parametre 4 byte (float32)
            size_mb = (total_params * 4) / (1024 * 1024)
            return size_mb
        except Exception as e:
            logger.error(f"Model boyutu hesaplama hatası: {str(e)}")
            return 0.0
    
    def _should_evict(self) -> bool:
        """Model çıkarılmalı mı?"""
        # Model sayısı kontrolü
        if len(self.cache) >= self.max_models:
            return True
        
        # Memory kontrolü
        current_memory = sum(self.model_sizes.values())
        if current_memory >= self.max_memory_mb:
            return True
        
        return False
    
    def _evict_least_recently_used(self):
        """En az kullanılan modeli çıkar"""
        if not self.access_times:
            return
        
        # En eski erişim zamanını bul
        oldest_model = min(self.access_times.items(), key=lambda x: x[1])[0]
        self.remove(oldest_model)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Cache istatistiklerini getir"""
        with self.lock:
            total_size = sum(self.model_sizes.values())
            return {
                'cached_models': len(self.cache),
                'max_models': self.max_models,
                'total_size_mb': total_size,
                'max_memory_mb': self.max_memory_mb,
                'memory_usage_percent': (total_size / self.max_memory_mb) * 100,
                'cached_model_names': list(self.cache.keys()),
                'model_sizes': dict(self.model_sizes)
            }


class ModelLoader:
    """Model yükleme sınıfı"""
    
    def __init__(self, models_dir: str = "models", device: str = "auto"):
        self.models_dir = Path(models_dir)
        self.device = self._determine_device(device)
        self.cache = ModelCache()
        
        # Model konfigürasyonları
        self.model_configs = {
            'xray_pneumonia': {
                'model_class_name': 'RadiologyCNN',
                'num_classes': 2,
                'input_channels': 1,
                'image_size': (512, 512),
                'model_file': 'xray_pneumonia_model.pth'
            },
            'ct_stroke': {
                'model_class_name': 'DenseNetRadiology',
                'num_classes': 4,
                'input_channels': 1,
                'image_size': (256, 256),
                'model_file': 'ct_stroke_model.pth'
            },
            'mri_brain_tumor': {
                'model_class_name': 'ResNetRadiology',
                'num_classes': 3,
                'input_channels': 1,
                'image_size': (224, 224),
                'model_file': 'mri_brain_tumor_model.pth'
            },
            'xray_fracture': {
                'model_class_name': 'RadiologyCNN',
                'num_classes': 2,
                'input_channels': 1,
                'image_size': (512, 512),
                'model_file': 'xray_fracture_model.pth'
            },
            'mammography_mass': {
                'model_class_name': 'DenseNetRadiology',
                'num_classes': 2,
                'input_channels': 1,
                'image_size': (512, 512),
                'model_file': 'mammography_mass_model.pth'
            }
        }
        
        logger.info(f"Model loader başlatıldı. Device: {self.device}")
    
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
    
    def _determine_device(self, device: str) -> str:
        """Cihazı belirle"""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def load_model(self, model_name: str, force_reload: bool = False) -> nn.Module:
        """Modeli yükle"""
        try:
            # Cache'den kontrol et
            if not force_reload:
                cached_model = self.cache.get(model_name)
                if cached_model is not None:
                    return cached_model
            
            # Model konfigürasyonunu kontrol et
            if model_name not in self.model_configs:
                raise ValueError(f"Model bulunamadı: {model_name}")
            
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
            checkpoint = torch.load(model_file, map_location=self.device)
            model.load_state_dict(checkpoint['model_state_dict'])
            
            # Model'i device'a taşı
            model = model.to(self.device)
            model.eval()
            
            # Cache'e ekle
            self.cache.put(model_name, model)
            
            logger.info(f"Model yüklendi: {model_name} ({self.device})")
            return model
            
        except Exception as e:
            logger.error(f"Model yükleme hatası ({model_name}): {str(e)}")
            raise
    
    def unload_model(self, model_name: str):
        """Modeli bellekten çıkar"""
        self.cache.remove(model_name)
        gc.collect()  # Garbage collection
        logger.info(f"Model bellekten çıkarıldı: {model_name}")
    
    def preload_models(self, model_names: List[str]):
        """Modelleri önceden yükle"""
        logger.info(f"Modeller önceden yükleniyor: {model_names}")
        
        for model_name in model_names:
            try:
                self.load_model(model_name)
            except Exception as e:
                logger.error(f"Model ön yükleme hatası ({model_name}): {str(e)}")
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Model bilgilerini getir"""
        if model_name not in self.model_configs:
            raise ValueError(f"Model bulunamadı: {model_name}")
        
        config = self.model_configs[model_name]
        model_file = self.models_dir / config['model_file']
        
        info = {
            'model_name': model_name,
            'model_class': config['model_class_name'],
            'num_classes': config['num_classes'],
            'input_channels': config['input_channels'],
            'image_size': config['image_size'],
            'model_file': str(model_file),
            'file_exists': model_file.exists(),
            'file_size_mb': model_file.stat().st_size / (1024 * 1024) if model_file.exists() else 0,
            'device': self.device,
            'is_cached': model_name in self.cache.cache,
            'cache_size_mb': self.cache.model_sizes.get(model_name, 0)
        }
        
        return info
    
    def predict(self, model_name: str, image: np.ndarray) -> Dict[str, Any]:
        """Model ile tahmin yap"""
        try:
            # Model'i yükle
            model = self.load_model(model_name)
            
            # Görüntüyü tensor'e çevir
            if len(image.shape) == 2:
                image = np.expand_dims(image, axis=0)
            if len(image.shape) == 3:
                image = np.expand_dims(image, axis=0)
            
            image_tensor = torch.FloatTensor(image).to(self.device)
            
            # Tahmin yap
            with torch.no_grad():
                start_time = time.time()
                outputs = model(image_tensor)
                inference_time = time.time() - start_time
                
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
                'inference_time': inference_time,
                'device': self.device,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Tahmin hatası ({model_name}): {str(e)}")
            raise
    
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
    
    def get_available_models(self) -> List[str]:
        """Mevcut modelleri listele"""
        return list(self.model_configs.keys())
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Sistem istatistiklerini getir"""
        # GPU bilgileri (varsa)
        gpu_info = {}
        if torch.cuda.is_available():
            gpu_info = {
                'gpu_count': torch.cuda.device_count(),
                'gpu_name': torch.cuda.get_device_name(0),
                'gpu_memory_allocated': torch.cuda.memory_allocated(0) / (1024**3),  # GB
                'gpu_memory_reserved': torch.cuda.memory_reserved(0) / (1024**3)  # GB
            }
        
        # Cache istatistikleri
        cache_stats = self.cache.get_cache_stats()
        
        return {
            'device': self.device,
            'gpu_info': gpu_info,
            'cache_stats': cache_stats,
            'available_models': len(self.model_configs),
            'loaded_models': len(self.cache.cache)
        }
    
    def cleanup(self):
        """Temizlik işlemleri"""
        logger.info("Model loader temizleniyor...")
        self.cache.clear()
        gc.collect()
        
        # GPU memory temizle
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Model loader temizlendi")
