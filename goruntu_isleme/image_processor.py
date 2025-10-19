"""
Görüntü İşleme Modülü
====================

Bu modül radyolojik görüntülerin ön işleme, temizleme,
normalizasyon ve kalite kontrol işlemlerini gerçekleştirir.
"""

import cv2
import numpy as np
import base64
import io
from PIL import Image, ImageEnhance
from typing import Dict, List, Tuple, Optional, Any
import logging
from pathlib import Path
import json

# Advanced image processing
import albumentations as A
from skimage import filters, morphology, measure, segmentation
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from skimage.segmentation import watershed, slic
from skimage.morphology import disk, ball, remove_small_objects
from skimage.measure import regionprops, label
from skimage.filters import threshold_otsu, threshold_adaptive
from skimage.restoration import denoise_tv_chambolle, denoise_bilateral
from skimage.exposure import equalize_adapthist, rescale_intensity
from skimage.transform import resize, rotate, warp
from skimage.util import random_noise

# Medical imaging
import pydicom
import nibabel as nib
import SimpleITK as sitk

from .schemas import ImageType, ImageMetadata

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Radyolojik görüntü işleme sınıfı"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.dcm', '.tiff', '.bmp']
        self.quality_thresholds = {
            'min_resolution': (256, 256),
            'max_file_size': 50 * 1024 * 1024,  # 50MB
            'min_contrast': 0.1,
            'max_noise_level': 0.3
        }
        
    def process_image(self, image_data: str, metadata: ImageMetadata) -> Dict[str, Any]:
        """
        Görüntüyü işle ve analiz için hazırla
        
        Args:
            image_data: Base64 encoded görüntü verisi
            metadata: Görüntü metadata bilgileri
            
        Returns:
            İşlenmiş görüntü ve kalite bilgileri
        """
        try:
            # Base64'ten görüntüyü decode et
            image = self._decode_base64_image(image_data)
            
            # Görüntü kalitesini kontrol et
            quality_score = self._assess_image_quality(image)
            
            # Görüntü tipine göre ön işleme
            processed_image = self._preprocess_by_type(image, metadata.image_type)
            
            # Görüntüyü normalize et
            normalized_image = self._normalize_image(processed_image)
            
            # Görüntüyü optimize et
            optimized_image = self._optimize_for_analysis(normalized_image, metadata)
            
            return {
                'processed_image': optimized_image,
                'original_image': image,
                'quality_score': quality_score,
                'processing_metadata': {
                    'original_shape': image.shape,
                    'processed_shape': optimized_image.shape,
                    'image_type': metadata.image_type.value,
                    'body_region': metadata.body_region.value
                }
            }
            
        except Exception as e:
            logger.error(f"Görüntü işleme hatası: {str(e)}")
            raise
    
    def _decode_base64_image(self, image_data: str) -> np.ndarray:
        """Base64 verisini görüntüye çevir"""
        try:
            # Base64 decode
            image_bytes = base64.b64decode(image_data)
            
            # PIL Image ile aç
            image = Image.open(io.BytesIO(image_bytes))
            
            # Grayscale'e çevir
            if image.mode != 'L':
                image = image.convert('L')
            
            # NumPy array'e çevir
            image_array = np.array(image, dtype=np.uint8)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Base64 decode hatası: {str(e)}")
            raise
    
    def _assess_image_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """Görüntü kalitesini değerlendir"""
        try:
            # Temel kalite metrikleri
            contrast = np.std(image)
            brightness = np.mean(image)
            
            # Histogram analizi
            hist, _ = np.histogram(image, bins=256, range=(0, 256))
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            
            # Gürültü seviyesi
            noise_level = self._estimate_noise_level(image)
            
            # Genel kalite skoru
            quality_score = min(1.0, (contrast / 50.0) * (entropy / 8.0) * (1.0 - noise_level))
            
            return {
                'overall_score': quality_score,
                'contrast': contrast,
                'brightness': brightness,
                'entropy': entropy,
                'noise_level': noise_level,
                'is_good_quality': quality_score > 0.5
            }
            
        except Exception as e:
            logger.error(f"Kalite değerlendirme hatası: {str(e)}")
            return {'overall_score': 0.0, 'is_good_quality': False}
    
    def _estimate_noise_level(self, image: np.ndarray) -> float:
        """Gürültü seviyesini tahmin et"""
        try:
            # Laplacian variance ile gürültü tahmini
            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
            noise_level = min(1.0, laplacian_var / 1000.0)
            return noise_level
        except:
            return 0.5
    
    def _preprocess_by_type(self, image: np.ndarray, image_type: ImageType) -> np.ndarray:
        """Görüntü tipine göre ön işleme"""
        try:
            if image_type == ImageType.XRAY:
                return self._preprocess_xray(image)
            elif image_type == ImageType.CT:
                return self._preprocess_ct(image)
            elif image_type == ImageType.MRI:
                return self._preprocess_mri(image)
            elif image_type == ImageType.MAMMOGRAPHY:
                return self._preprocess_mammography(image)
            else:
                return self._preprocess_general(image)
                
        except Exception as e:
            logger.error(f"Tip bazlı ön işleme hatası: {str(e)}")
            return image
    
    def _preprocess_xray(self, image: np.ndarray) -> np.ndarray:
        """X-Ray görüntüsü ön işleme"""
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        # Gaussian blur ile gürültü azaltma
        denoised = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        return denoised
    
    def _preprocess_ct(self, image: np.ndarray) -> np.ndarray:
        """CT görüntüsü ön işleme"""
        # CT için özel windowing
        windowed = self._apply_ct_window(image, window_center=40, window_width=400)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        processed = cv2.morphologyEx(windowed, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def _preprocess_mri(self, image: np.ndarray) -> np.ndarray:
        """MRI görüntüsü ön işleme"""
        # MRI için bias field correction (basit versiyon)
        bias_corrected = self._simple_bias_correction(image)
        
        # Intensity normalization
        normalized = cv2.normalize(bias_corrected, None, 0, 255, cv2.NORM_MINMAX)
        
        return normalized
    
    def _preprocess_mammography(self, image: np.ndarray) -> np.ndarray:
        """Mamografi ön işleme"""
        # Breast region detection (basit versiyon)
        breast_region = self._detect_breast_region(image)
        
        # Contrast enhancement
        enhanced = cv2.equalizeHist(breast_region)
        
        return enhanced
    
    def _preprocess_general(self, image: np.ndarray) -> np.ndarray:
        """Genel görüntü ön işleme"""
        # Histogram equalization
        equalized = cv2.equalizeHist(image)
        
        # Denoising
        denoised = cv2.bilateralFilter(equalized, 9, 75, 75)
        
        return denoised
    
    def _apply_ct_window(self, image: np.ndarray, window_center: int, window_width: int) -> np.ndarray:
        """CT windowing uygula"""
        window_min = window_center - window_width // 2
        window_max = window_center + window_width // 2
        
        windowed = np.clip(image, window_min, window_max)
        windowed = ((windowed - window_min) / (window_max - window_min) * 255).astype(np.uint8)
        
        return windowed
    
    def _simple_bias_correction(self, image: np.ndarray) -> np.ndarray:
        """Basit bias field correction"""
        # Gaussian blur ile bias field tahmini
        bias_field = cv2.GaussianBlur(image.astype(np.float32), (15, 15), 0)
        
        # Bias field'i çıkar
        corrected = image.astype(np.float32) / (bias_field + 1e-10)
        corrected = np.clip(corrected, 0, 255).astype(np.uint8)
        
        return corrected
    
    def _detect_breast_region(self, image: np.ndarray) -> np.ndarray:
        """Meme bölgesini tespit et (basit versiyon)"""
        # Threshold ile meme dokusunu tespit et
        _, binary = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY)
        
        # En büyük connected component'i bul
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary)
        
        if num_labels > 1:
            # En büyük component'i seç
            largest_component = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
            breast_mask = (labels == largest_component).astype(np.uint8) * 255
            
            # Mask'i uygula
            result = cv2.bitwise_and(image, breast_mask)
        else:
            result = image
        
        return result
    
    def _normalize_image(self, image: np.ndarray) -> np.ndarray:
        """Görüntüyü normalize et"""
        try:
            # Min-max normalization
            normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
            
            # Z-score normalization (opsiyonel)
            # mean = np.mean(normalized)
            # std = np.std(normalized)
            # normalized = ((normalized - mean) / std * 50 + 128).astype(np.uint8)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Normalizasyon hatası: {str(e)}")
            return image
    
    def _optimize_for_analysis(self, image: np.ndarray, metadata: ImageMetadata) -> np.ndarray:
        """Analiz için görüntüyü optimize et"""
        try:
            # Hedef boyut
            target_size = self._get_target_size(metadata.image_type)
            
            # Boyutlandır
            resized = cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)
            
            # Son temizlik
            optimized = cv2.bilateralFilter(resized, 5, 50, 50)
            
            return optimized
            
        except Exception as e:
            logger.error(f"Optimizasyon hatası: {str(e)}")
            return image
    
    def _get_target_size(self, image_type: ImageType) -> Tuple[int, int]:
        """Görüntü tipine göre hedef boyut"""
        size_mapping = {
            ImageType.XRAY: (512, 512),
            ImageType.CT: (256, 256),
            ImageType.MRI: (224, 224),
            ImageType.MAMMOGRAPHY: (512, 512),
            ImageType.ULTRASOUND: (256, 256)
        }
        
        return size_mapping.get(image_type, (256, 256))
    
    def validate_image(self, image_data: str, metadata: ImageMetadata) -> Dict[str, Any]:
        """Görüntüyü doğrula"""
        try:
            # Base64 decode
            image = self._decode_base64_image(image_data)
            
            # Boyut kontrolü
            if image.shape[0] < self.quality_thresholds['min_resolution'][0] or \
               image.shape[1] < self.quality_thresholds['min_resolution'][1]:
                return {
                    'is_valid': False,
                    'errors': ['Görüntü çözünürlüğü çok düşük']
                }
            
            # Kalite kontrolü
            quality = self._assess_image_quality(image)
            if not quality['is_good_quality']:
                return {
                    'is_valid': False,
                    'errors': ['Görüntü kalitesi yetersiz']
                }
            
            return {
                'is_valid': True,
                'errors': [],
                'quality_score': quality['overall_score']
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f'Görüntü doğrulama hatası: {str(e)}']
            }


