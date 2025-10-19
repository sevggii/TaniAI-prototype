"""
DICOM Görüntü İşleme Modülü
===========================

TCIA'dan indirilen DICOM görüntülerini işlemek ve
model eğitimi için hazırlamak için geliştirilmiş modül.
"""

import pydicom
import numpy as np
import cv2
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json
from datetime import datetime
import nibabel as nib
import SimpleITK as sitk
from skimage import exposure, filters, morphology
from skimage.transform import resize
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class DICOMProcessor:
    """DICOM görüntü işleme sınıfı"""
    
    def __init__(self, output_dir: str = "processed_dicom"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Desteklenen DICOM tag'leri
        self.required_tags = [
            'PatientID', 'StudyDate', 'StudyDescription',
            'Modality', 'SeriesDescription', 'BodyPartExamined',
            'SliceThickness', 'SpacingBetweenSlices',
            'Rows', 'Columns', 'PixelSpacing'
        ]
        
        # Görüntü kalite eşikleri
        self.quality_thresholds = {
            'min_slices': 10,
            'max_slice_thickness': 10.0,  # mm
            'min_resolution': (128, 128),
            'max_resolution': (2048, 2048)
        }
    
    def load_dicom_series(self, series_path: str) -> List[pydicom.Dataset]:
        """DICOM serisini yükle"""
        try:
            series_path = Path(series_path)
            dicom_files = list(series_path.glob("*.dcm"))
            
            if not dicom_files:
                logger.warning(f"DICOM dosyası bulunamadı: {series_path}")
                return []
            
            # DICOM dosyalarını yükle
            datasets = []
            for file_path in dicom_files:
                try:
                    ds = pydicom.dcmread(file_path)
                    datasets.append(ds)
                except Exception as e:
                    logger.error(f"DICOM yükleme hatası ({file_path}): {str(e)}")
                    continue
            
            # Slice location'a göre sırala
            datasets.sort(key=lambda x: float(x.get('SliceLocation', 0)))
            
            logger.info(f"DICOM serisi yüklendi: {len(datasets)} slice")
            return datasets
            
        except Exception as e:
            logger.error(f"DICOM seri yükleme hatası: {str(e)}")
            return []
    
    def extract_dicom_metadata(self, datasets: List[pydicom.Dataset]) -> Dict[str, Any]:
        """DICOM metadata'sını çıkar"""
        try:
            if not datasets:
                return {}
            
            first_ds = datasets[0]
            metadata = {}
            
            # Temel bilgiler
            metadata['patient_id'] = str(first_ds.get('PatientID', 'Unknown'))
            metadata['study_date'] = str(first_ds.get('StudyDate', 'Unknown'))
            metadata['study_description'] = str(first_ds.get('StudyDescription', 'Unknown'))
            metadata['modality'] = str(first_ds.get('Modality', 'Unknown'))
            metadata['series_description'] = str(first_ds.get('SeriesDescription', 'Unknown'))
            metadata['body_part'] = str(first_ds.get('BodyPartExamined', 'Unknown'))
            
            # Görüntü boyutları
            metadata['rows'] = int(first_ds.get('Rows', 0))
            metadata['columns'] = int(first_ds.get('Columns', 0))
            metadata['num_slices'] = len(datasets)
            
            # Pixel spacing
            pixel_spacing = first_ds.get('PixelSpacing', [1.0, 1.0])
            metadata['pixel_spacing'] = [float(pixel_spacing[0]), float(pixel_spacing[1])]
            
            # Slice bilgileri
            slice_thickness = first_ds.get('SliceThickness', 1.0)
            metadata['slice_thickness'] = float(slice_thickness)
            
            # Voxel boyutu hesapla
            metadata['voxel_size'] = [
                metadata['pixel_spacing'][0],
                metadata['pixel_spacing'][1],
                metadata['slice_thickness']
            ]
            
            # Rescale slope ve intercept
            rescale_slope = first_ds.get('RescaleSlope', 1.0)
            rescale_intercept = first_ds.get('RescaleIntercept', 0.0)
            metadata['rescale_slope'] = float(rescale_slope)
            metadata['rescale_intercept'] = float(rescale_intercept)
            
            # Window/Level bilgileri
            window_center = first_ds.get('WindowCenter', [0])
            window_width = first_ds.get('WindowWidth', [0])
            metadata['window_center'] = float(window_center[0]) if isinstance(window_center, list) else float(window_center)
            metadata['window_width'] = float(window_width[0]) if isinstance(window_width, list) else float(window_width)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata çıkarma hatası: {str(e)}")
            return {}
    
    def convert_to_numpy_array(self, datasets: List[pydicom.Dataset]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """DICOM serisini numpy array'e çevir"""
        try:
            if not datasets:
                raise ValueError("DICOM serisi boş")
            
            # Metadata'yı çıkar
            metadata = self.extract_dicom_metadata(datasets)
            
            # 3D array oluştur
            rows = metadata['rows']
            cols = metadata['columns']
            slices = metadata['num_slices']
            
            volume = np.zeros((slices, rows, cols), dtype=np.float32)
            
            for i, ds in enumerate(datasets):
                # Pixel array'i al
                pixel_array = ds.pixel_array.astype(np.float32)
                
                # Rescale slope ve intercept uygula
                if 'RescaleSlope' in ds and 'RescaleIntercept' in ds:
                    slope = float(ds.RescaleSlope)
                    intercept = float(ds.RescaleIntercept)
                    pixel_array = pixel_array * slope + intercept
                
                volume[i] = pixel_array
            
            logger.info(f"3D volume oluşturuldu: {volume.shape}")
            return volume, metadata
            
        except Exception as e:
            logger.error(f"Numpy array dönüştürme hatası: {str(e)}")
            raise
    
    def apply_window_level(self, image: np.ndarray, window_center: float, window_width: float) -> np.ndarray:
        """Window/Level uygula"""
        try:
            window_min = window_center - window_width // 2
            window_max = window_center + window_width // 2
            
            # Window/Level uygula
            windowed = np.clip(image, window_min, window_max)
            windowed = ((windowed - window_min) / (window_max - window_min) * 255).astype(np.uint8)
            
            return windowed
            
        except Exception as e:
            logger.error(f"Window/Level uygulama hatası: {str(e)}")
            return image
    
    def normalize_volume(self, volume: np.ndarray, metadata: Dict[str, Any]) -> np.ndarray:
        """3D volume'u normalize et"""
        try:
            # Window/Level uygula (CT için)
            if metadata.get('modality') == 'CT':
                window_center = metadata.get('window_center', 40)
                window_width = metadata.get('window_width', 400)
                
                normalized = self.apply_window_level(volume, window_center, window_width)
            else:
                # Diğer modaliteler için min-max normalizasyon
                min_val = np.min(volume)
                max_val = np.max(volume)
                normalized = ((volume - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Volume normalizasyon hatası: {str(e)}")
            return volume
    
    def extract_2d_slices(self, volume: np.ndarray, metadata: Dict[str, Any]) -> List[np.ndarray]:
        """3D volume'dan 2D slice'ları çıkar"""
        try:
            slices = []
            
            for i in range(volume.shape[0]):
                slice_2d = volume[i]
                
                # Görüntü kalitesini kontrol et
                if self._is_good_quality_slice(slice_2d):
                    # Boyutlandır
                    target_size = (512, 512)
                    resized = resize(slice_2d, target_size, preserve_range=True).astype(np.uint8)
                    slices.append(resized)
            
            logger.info(f"{len(slices)} kaliteli slice çıkarıldı")
            return slices
            
        except Exception as e:
            logger.error(f"2D slice çıkarma hatası: {str(e)}")
            return []
    
    def _is_good_quality_slice(self, slice_2d: np.ndarray) -> bool:
        """Slice kalitesini kontrol et"""
        try:
            # Boş slice kontrolü
            if np.sum(slice_2d) == 0:
                return False
            
            # Kontrast kontrolü
            contrast = np.std(slice_2d)
            if contrast < 10:
                return False
            
            # Entropy kontrolü
            hist, _ = np.histogram(slice_2d, bins=256, range=(0, 256))
            hist = hist / np.sum(hist)
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            if entropy < 3.0:
                return False
            
            return True
            
        except:
            return False
    
    def process_dicom_series(self, series_path: str, output_format: str = "png") -> Dict[str, Any]:
        """DICOM serisini işle"""
        try:
            series_path = Path(series_path)
            logger.info(f"DICOM serisi işleniyor: {series_path}")
            
            # DICOM serisini yükle
            datasets = self.load_dicom_series(series_path)
            if not datasets:
                raise ValueError("DICOM serisi yüklenemedi")
            
            # 3D volume oluştur
            volume, metadata = self.convert_to_numpy_array(datasets)
            
            # Normalize et
            normalized_volume = self.normalize_volume(volume, metadata)
            
            # 2D slice'ları çıkar
            slices_2d = self.extract_2d_slices(normalized_volume, metadata)
            
            if not slices_2d:
                raise ValueError("Kaliteli slice bulunamadı")
            
            # Çıktı klasörü oluştur
            patient_id = metadata.get('patient_id', 'unknown')
            modality = metadata.get('modality', 'unknown').lower()
            output_subdir = self.output_dir / f"{patient_id}_{modality}"
            output_subdir.mkdir(exist_ok=True)
            
            # Slice'ları kaydet
            saved_files = []
            for i, slice_2d in enumerate(slices_2d):
                filename = f"slice_{i:03d}.{output_format}"
                filepath = output_subdir / filename
                
                if output_format == "png":
                    cv2.imwrite(str(filepath), slice_2d)
                elif output_format == "jpg":
                    cv2.imwrite(str(filepath), slice_2d, [cv2.IMWRITE_JPEG_QUALITY, 95])
                elif output_format == "npy":
                    np.save(str(filepath), slice_2d)
                
                saved_files.append(str(filepath))
            
            # Metadata'yı kaydet
            metadata_file = output_subdir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            result = {
                "series_path": str(series_path),
                "output_dir": str(output_subdir),
                "num_slices": len(slices_2d),
                "metadata": metadata,
                "saved_files": saved_files,
                "processed_at": datetime.now().isoformat()
            }
            
            logger.info(f"DICOM serisi işlendi: {len(slices_2d)} slice kaydedildi")
            return result
            
        except Exception as e:
            logger.error(f"DICOM seri işleme hatası: {str(e)}")
            raise
    
    def batch_process_collection(self, collection_dir: str) -> Dict[str, Any]:
        """Koleksiyon içindeki tüm DICOM serilerini işle"""
        try:
            collection_path = Path(collection_dir)
            logger.info(f"Koleksiyon işleniyor: {collection_path}")
            
            # Tüm seri klasörlerini bul
            series_dirs = [d for d in collection_path.iterdir() if d.is_dir()]
            
            results = {
                "collection_dir": str(collection_path),
                "total_series": len(series_dirs),
                "processed_series": 0,
                "failed_series": 0,
                "series_results": [],
                "processed_at": datetime.now().isoformat()
            }
            
            for series_dir in series_dirs:
                try:
                    logger.info(f"Seri işleniyor: {series_dir.name}")
                    result = self.process_dicom_series(series_dir)
                    results["series_results"].append(result)
                    results["processed_series"] += 1
                    
                except Exception as e:
                    logger.error(f"Seri işleme hatası ({series_dir.name}): {str(e)}")
                    results["failed_series"] += 1
                    continue
            
            # Sonucu kaydet
            result_file = self.output_dir / f"{collection_path.name}_batch_result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Koleksiyon işlendi: {results['processed_series']}/{results['total_series']} seri")
            return results
            
        except Exception as e:
            logger.error(f"Koleksiyon işleme hatası: {str(e)}")
            raise
    
    def create_training_dataset(self, processed_collections: List[str], output_dir: str = "training_dataset") -> Dict[str, Any]:
        """Eğitim veri seti oluştur"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Klasör yapısı oluştur
            train_dir = output_path / "train"
            val_dir = output_path / "val"
            test_dir = output_path / "test"
            
            for dir_path in [train_dir, val_dir, test_dir]:
                dir_path.mkdir(exist_ok=True)
            
            dataset_info = {
                "total_images": 0,
                "train_images": 0,
                "val_images": 0,
                "test_images": 0,
                "classes": {},
                "created_at": datetime.now().isoformat()
            }
            
            # Her koleksiyon için işle
            for collection_path in processed_collections:
                collection_path = Path(collection_path)
                
                # Koleksiyon tipini belirle
                if "lung" in collection_path.name.lower():
                    class_name = "lung_cancer"
                elif "breast" in collection_path.name.lower():
                    class_name = "breast_cancer"
                elif "brain" in collection_path.name.lower():
                    class_name = "brain_tumor"
                else:
                    class_name = "other"
                
                # Sınıf klasörü oluştur
                for split_dir in [train_dir, val_dir, test_dir]:
                    class_dir = split_dir / class_name
                    class_dir.mkdir(exist_ok=True)
                
                # Görüntüleri dağıt
                image_files = list(collection_path.glob("**/*.png"))
                total_images = len(image_files)
                
                # Train/Val/Test split (70/20/10)
                train_size = int(total_images * 0.7)
                val_size = int(total_images * 0.2)
                
                for i, image_file in enumerate(image_files):
                    if i < train_size:
                        target_dir = train_dir / class_name
                        dataset_info["train_images"] += 1
                    elif i < train_size + val_size:
                        target_dir = val_dir / class_name
                        dataset_info["val_images"] += 1
                    else:
                        target_dir = test_dir / class_name
                        dataset_info["test_images"] += 1
                    
                    # Dosyayı kopyala
                    target_file = target_dir / image_file.name
                    import shutil
                    shutil.copy2(image_file, target_file)
                
                # Sınıf bilgisini güncelle
                if class_name not in dataset_info["classes"]:
                    dataset_info["classes"][class_name] = 0
                dataset_info["classes"][class_name] += total_images
                dataset_info["total_images"] += total_images
            
            # Dataset bilgisini kaydet
            info_file = output_path / "dataset_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(dataset_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Eğitim veri seti oluşturuldu: {dataset_info['total_images']} görüntü")
            return dataset_info
            
        except Exception as e:
            logger.error(f"Eğitim veri seti oluşturma hatası: {str(e)}")
            raise


def main():
    """Ana fonksiyon - örnek kullanım"""
    logging.basicConfig(level=logging.INFO)
    
    processor = DICOMProcessor()
    
    # Örnek DICOM serisi işle
    series_path = "tcia_data/CPTAC-LUAD/sample_series"
    if Path(series_path).exists():
        try:
            result = processor.process_dicom_series(series_path)
            print(f"✅ DICOM serisi işlendi: {result['num_slices']} slice")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
    else:
        print("📁 DICOM serisi bulunamadı. Önce TCIA'dan veri indirin.")


if __name__ == "__main__":
    main()
