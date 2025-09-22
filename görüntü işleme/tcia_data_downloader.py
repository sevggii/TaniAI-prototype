"""
TCIA Veri İndirme Modülü
========================

The Cancer Imaging Archive'dan gerçek tıbbi verileri indirmek için
otomatik sistem.
"""

import requests
import os
import zipfile
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time
import hashlib

logger = logging.getLogger(__name__)


class TCIADataDownloader:
    """TCIA veri indirme sınıfı"""
    
    def __init__(self, download_dir: str = "tcia_data"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # TCIA API endpoints
        self.base_url = "https://services.cancerimagingarchive.net/services/v4"
        self.nbia_url = "https://nbia.cancerimagingarchive.net/nbia-search/services"
        
        # Desteklenen koleksiyonlar
        self.recommended_collections = {
            # Akciğer kanseri
            "CPTAC-LUAD": {
                "name": "CPTAC Lung Adenocarcinoma",
                "subjects": 244,
                "modalities": ["CT", "PT", "MR", "Histopathology"],
                "description": "Lung adenocarcinoma CT, PET-CT ve MR görüntüleri",
                "url": "https://www.cancerimagingarchive.net/collection/cptac-luad/"
            },
            "CMB-LCA": {
                "name": "CMB Lung Cancer Atlas",
                "subjects": 160,
                "modalities": ["CT", "PT", "MR", "Histopathology"],
                "description": "Akciğer kanseri multi-modal görüntüleri",
                "url": "https://www.cancerimagingarchive.net/collection/cmb-lca/"
            },
            "NSCLC-Radiomics-Genomics": {
                "name": "NSCLC Radiomics Genomics",
                "subjects": 89,
                "modalities": ["CT"],
                "description": "Non-small cell lung cancer CT görüntüleri",
                "url": "https://www.cancerimagingarchive.net/collection/nsclc-radiomics-genomics/"
            },
            
            # Meme kanseri
            "CMB-BRCA": {
                "name": "CMB Breast Cancer Atlas",
                "subjects": 77,
                "modalities": ["CT", "MR", "MG", "Histopathology"],
                "description": "Meme kanseri multi-modal görüntüleri",
                "url": "https://www.cancerimagingarchive.net/collection/cmb-brca/"
            },
            "QIN-BREAST-02": {
                "name": "QIN Breast 02",
                "subjects": 13,
                "modalities": ["MR"],
                "description": "Meme MR görüntüleri",
                "url": "https://www.cancerimagingarchive.net/collection/qin-breast-02/"
            },
            
            # Beyin tümörleri
            "UCSF-PDGM": {
                "name": "UCSF Pediatric Diffuse Glioma MRI",
                "subjects": 495,
                "modalities": ["MR"],
                "description": "Pediatrik diffüz glioma MR görüntüleri",
                "url": "https://www.cancerimagingarchive.net/collection/ucsf-pdgm/"
            },
            "Brain-Mets-Lung-MRI-Path-Segs": {
                "name": "Brain Metastases Lung MRI Pathology",
                "subjects": 103,
                "modalities": ["MR", "Histopathology"],
                "description": "Beyin metastazları MR görüntüleri",
                "url": "https://www.cancerimagingarchive.net/collection/brain-mets-lung-mri-path-segs/"
            }
        }
    
    def get_collection_info(self, collection_id: str) -> Dict:
        """Koleksiyon bilgilerini getir"""
        if collection_id not in self.recommended_collections:
            raise ValueError(f"Desteklenmeyen koleksiyon: {collection_id}")
        
        return self.recommended_collections[collection_id]
    
    def list_available_collections(self) -> Dict[str, Dict]:
        """Mevcut koleksiyonları listele"""
        return self.recommended_collections
    
    def download_collection_metadata(self, collection_id: str) -> Dict:
        """Koleksiyon metadata'sını indir"""
        try:
            collection_info = self.get_collection_info(collection_id)
            
            # TCIA API'den koleksiyon bilgilerini al
            url = f"{self.nbia_url}/getCollectionValues"
            params = {
                "Collection": collection_id
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            metadata = {
                "collection_id": collection_id,
                "collection_info": collection_info,
                "api_response": response.json(),
                "downloaded_at": datetime.now().isoformat()
            }
            
            # Metadata'yı kaydet
            metadata_file = self.download_dir / f"{collection_id}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Metadata indirildi: {collection_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata indirme hatası ({collection_id}): {str(e)}")
            raise
    
    def get_collection_images(self, collection_id: str) -> List[Dict]:
        """Koleksiyon görüntü listesini getir"""
        try:
            url = f"{self.nbia_url}/getImage"
            params = {
                "Collection": collection_id,
                "format": "json"
            }
            
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            images = response.json()
            
            logger.info(f"{len(images)} görüntü bulundu: {collection_id}")
            return images
            
        except Exception as e:
            logger.error(f"Görüntü listesi alma hatası ({collection_id}): {str(e)}")
            raise
    
    def download_image_series(self, series_uid: str, collection_id: str) -> str:
        """Görüntü serisini indir"""
        try:
            collection_dir = self.download_dir / collection_id
            collection_dir.mkdir(exist_ok=True)
            
            series_dir = collection_dir / series_uid
            series_dir.mkdir(exist_ok=True)
            
            # TCIA'dan DICOM serisini indir
            url = f"{self.nbia_url}/getImage"
            params = {
                "SeriesInstanceUID": series_uid,
                "format": "zip"
            }
            
            logger.info(f"Seri indiriliyor: {series_uid}")
            response = requests.get(url, params=params, timeout=300, stream=True)
            response.raise_for_status()
            
            # ZIP dosyasını kaydet
            zip_file = series_dir / f"{series_uid}.zip"
            with open(zip_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # ZIP'i aç
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(series_dir)
            
            # ZIP dosyasını sil
            zip_file.unlink()
            
            logger.info(f"Seri indirildi: {series_uid}")
            return str(series_dir)
            
        except Exception as e:
            logger.error(f"Seri indirme hatası ({series_uid}): {str(e)}")
            raise
    
    def download_collection_sample(self, collection_id: str, max_series: int = 10) -> Dict:
        """Koleksiyondan örnek veri indir"""
        try:
            logger.info(f"Koleksiyon örneği indiriliyor: {collection_id}")
            
            # Metadata'yı indir
            metadata = self.download_collection_metadata(collection_id)
            
            # Görüntü listesini al
            images = self.get_collection_images(collection_id)
            
            # Örnek serileri seç
            sample_series = images[:max_series]
            
            downloaded_series = []
            for i, image in enumerate(sample_series):
                try:
                    series_uid = image.get('SeriesInstanceUID')
                    if series_uid:
                        series_path = self.download_image_series(series_uid, collection_id)
                        downloaded_series.append({
                            "series_uid": series_uid,
                            "path": series_path,
                            "patient_id": image.get('PatientID'),
                            "study_date": image.get('StudyDate'),
                            "modality": image.get('Modality')
                        })
                        
                        logger.info(f"İndirilen seri {i+1}/{len(sample_series)}: {series_uid}")
                        
                        # Rate limiting
                        time.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Seri indirme hatası: {str(e)}")
                    continue
            
            result = {
                "collection_id": collection_id,
                "total_images_found": len(images),
                "downloaded_series": len(downloaded_series),
                "series_details": downloaded_series,
                "download_dir": str(self.download_dir / collection_id),
                "completed_at": datetime.now().isoformat()
            }
            
            # Sonucu kaydet
            result_file = self.download_dir / f"{collection_id}_download_result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Koleksiyon örneği tamamlandı: {collection_id}")
            return result
            
        except Exception as e:
            logger.error(f"Koleksiyon örneği indirme hatası ({collection_id}): {str(e)}")
            raise
    
    def create_dataset_summary(self) -> Dict:
        """İndirilen veri setlerinin özetini oluştur"""
        try:
            summary = {
                "total_collections": len(list(self.download_dir.glob("*/download_result.json"))),
                "collections": {},
                "total_images": 0,
                "total_size_gb": 0,
                "created_at": datetime.now().isoformat()
            }
            
            for result_file in self.download_dir.glob("*/download_result.json"):
                with open(result_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                
                collection_id = result['collection_id']
                summary['collections'][collection_id] = {
                    "downloaded_series": result['downloaded_series'],
                    "total_found": result['total_images_found'],
                    "download_dir": result['download_dir']
                }
                
                summary['total_images'] += result['downloaded_series']
                
                # Klasör boyutunu hesapla
                collection_dir = Path(result['download_dir'])
                if collection_dir.exists():
                    size_bytes = sum(f.stat().st_size for f in collection_dir.rglob('*') if f.is_file())
                    size_gb = size_bytes / (1024**3)
                    summary['total_size_gb'] += size_gb
            
            # Özeti kaydet
            summary_file = self.download_dir / "dataset_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            return summary
            
        except Exception as e:
            logger.error(f"Özet oluşturma hatası: {str(e)}")
            raise


def main():
    """Ana fonksiyon - örnek kullanım"""
    logging.basicConfig(level=logging.INFO)
    
    downloader = TCIADataDownloader()
    
    # Mevcut koleksiyonları listele
    print("🏥 Mevcut TCIA Koleksiyonları:")
    collections = downloader.list_available_collections()
    for col_id, col_info in collections.items():
        print(f"  • {col_id}: {col_info['name']} ({col_info['subjects']} hasta)")
    
    # Örnek koleksiyon indir
    collection_id = "CPTAC-LUAD"  # Akciğer kanseri
    print(f"\n📥 Örnek koleksiyon indiriliyor: {collection_id}")
    
    try:
        result = downloader.download_collection_sample(collection_id, max_series=5)
        print(f"✅ İndirme tamamlandı: {result['downloaded_series']} seri")
        
        # Özet oluştur
        summary = downloader.create_dataset_summary()
        print(f"📊 Toplam: {summary['total_images']} görüntü serisi")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")


if __name__ == "__main__":
    main()
