#!/usr/bin/env python3
"""
TCIA Tam Entegrasyon Pipeline'ı
==============================

TCIA'dan veri indirme → DICOM işleme → Model eğitimi → Değerlendirme
tüm süreci otomatik olarak yöneten ana script.
"""

import logging
import argparse
from pathlib import Path
from datetime import datetime
import json
import sys

# Proje root'unu Python path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Custom imports
from tcia_data_downloader import TCIADataDownloader
from dicom_processor import DICOMProcessor
from train_tcia_models import TCIAModelTrainer

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tcia_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TCIAFullPipeline:
    """TCIA tam entegrasyon pipeline'ı"""
    
    def __init__(self, 
                 download_dir: str = "tcia_data",
                 processed_dir: str = "processed_dicom", 
                 training_dir: str = "training_dataset",
                 models_dir: str = "models"):
        
        self.download_dir = Path(download_dir)
        self.processed_dir = Path(processed_dir)
        self.training_dir = Path(training_dir)
        self.models_dir = Path(models_dir)
        
        # Pipeline bileşenleri
        self.downloader = TCIADataDownloader(str(self.download_dir))
        self.processor = DICOMProcessor(str(self.processed_dir))
        self.trainer = TCIAModelTrainer(str(self.training_dir), str(self.models_dir))
        
        # Pipeline durumu
        self.pipeline_status = {
            'download_completed': False,
            'processing_completed': False,
            'training_completed': False,
            'evaluation_completed': False
        }
    
    def run_full_pipeline(self, 
                         collections: list = None,
                         max_series_per_collection: int = 10,
                         train_models: bool = True) -> dict:
        """Tam pipeline'ı çalıştır"""
        try:
            logger.info("🚀 TCIA Full Pipeline başlatılıyor...")
            
            if collections is None:
                collections = ["CPTAC-LUAD", "CMB-BRCA", "UCSF-PDGM"]
            
            pipeline_results = {
                'started_at': datetime.now().isoformat(),
                'collections': collections,
                'max_series_per_collection': max_series_per_collection,
                'steps_completed': [],
                'errors': []
            }
            
            # 1. Veri İndirme
            try:
                logger.info("📥 Adım 1: TCIA Verileri İndiriliyor...")
                download_results = self._download_collections(collections, max_series_per_collection)
                pipeline_results['download_results'] = download_results
                pipeline_results['steps_completed'].append('download')
                self.pipeline_status['download_completed'] = True
                logger.info("✅ Veri indirme tamamlandı")
                
            except Exception as e:
                error_msg = f"Veri indirme hatası: {str(e)}"
                logger.error(error_msg)
                pipeline_results['errors'].append(error_msg)
                return pipeline_results
            
            # 2. DICOM İşleme
            try:
                logger.info("🔧 Adım 2: DICOM Görüntüleri İşleniyor...")
                processing_results = self._process_collections(collections)
                pipeline_results['processing_results'] = processing_results
                pipeline_results['steps_completed'].append('processing')
                self.pipeline_status['processing_completed'] = True
                logger.info("✅ DICOM işleme tamamlandı")
                
            except Exception as e:
                error_msg = f"DICOM işleme hatası: {str(e)}"
                logger.error(error_msg)
                pipeline_results['errors'].append(error_msg)
                return pipeline_results
            
            # 3. Eğitim Veri Seti Oluşturma
            try:
                logger.info("📊 Adım 3: Eğitim Veri Seti Oluşturuluyor...")
                dataset_results = self._create_training_dataset()
                pipeline_results['dataset_results'] = dataset_results
                pipeline_results['steps_completed'].append('dataset_creation')
                logger.info("✅ Eğitim veri seti oluşturuldu")
                
            except Exception as e:
                error_msg = f"Veri seti oluşturma hatası: {str(e)}"
                logger.error(error_msg)
                pipeline_results['errors'].append(error_msg)
                return pipeline_results
            
            # 4. Model Eğitimi (opsiyonel)
            if train_models:
                try:
                    logger.info("🧠 Adım 4: Modeller Eğitiliyor...")
                    training_results = self._train_models()
                    pipeline_results['training_results'] = training_results
                    pipeline_results['steps_completed'].append('training')
                    self.pipeline_status['training_completed'] = True
                    logger.info("✅ Model eğitimi tamamlandı")
                    
                except Exception as e:
                    error_msg = f"Model eğitimi hatası: {str(e)}"
                    logger.error(error_msg)
                    pipeline_results['errors'].append(error_msg)
            
            # 5. Pipeline Özeti
            pipeline_results['completed_at'] = datetime.now().isoformat()
            pipeline_results['pipeline_status'] = self.pipeline_status
            
            # Sonuçları kaydet
            self._save_pipeline_results(pipeline_results)
            
            logger.info("🎉 TCIA Full Pipeline tamamlandı!")
            return pipeline_results
            
        except Exception as e:
            logger.error(f"Pipeline hatası: {str(e)}")
            raise
    
    def _download_collections(self, collections: list, max_series: int) -> dict:
        """Koleksiyonları indir"""
        download_results = {}
        
        for collection_id in collections:
            try:
                logger.info(f"Koleksiyon indiriliyor: {collection_id}")
                result = self.downloader.download_collection_sample(
                    collection_id, max_series_per_collection=max_series
                )
                download_results[collection_id] = result
                
            except Exception as e:
                logger.error(f"Koleksiyon indirme hatası ({collection_id}): {str(e)}")
                download_results[collection_id] = {'error': str(e)}
        
        return download_results
    
    def _process_collections(self, collections: list) -> dict:
        """Koleksiyonları işle"""
        processing_results = {}
        
        for collection_id in collections:
            try:
                collection_dir = self.download_dir / collection_id
                if collection_dir.exists():
                    logger.info(f"Koleksiyon işleniyor: {collection_id}")
                    result = self.processor.batch_process_collection(str(collection_dir))
                    processing_results[collection_id] = result
                else:
                    logger.warning(f"Koleksiyon klasörü bulunamadı: {collection_dir}")
                    processing_results[collection_id] = {'error': 'Collection directory not found'}
                    
            except Exception as e:
                logger.error(f"Koleksiyon işleme hatası ({collection_id}): {str(e)}")
                processing_results[collection_id] = {'error': str(e)}
        
        return processing_results
    
    def _create_training_dataset(self) -> dict:
        """Eğitim veri seti oluştur"""
        try:
            # İşlenmiş koleksiyon klasörlerini bul
            processed_dirs = []
            for item in self.processed_dir.iterdir():
                if item.is_dir() and any(col in item.name for col in ["CPTAC", "CMB", "UCSF"]):
                    processed_dirs.append(str(item))
            
            if not processed_dirs:
                raise ValueError("İşlenmiş DICOM klasörü bulunamadı")
            
            # Eğitim veri seti oluştur
            dataset_result = self.processor.create_training_dataset(
                processed_dirs, str(self.training_dir)
            )
            
            return dataset_result
            
        except Exception as e:
            logger.error(f"Eğitim veri seti oluşturma hatası: {str(e)}")
            raise
    
    def _train_models(self) -> dict:
        """Modelleri eğit"""
        try:
            models, results = self.trainer.train_all_models()
            
            training_results = {
                'trained_models': list(models.keys()),
                'model_results': results,
                'training_completed': True
            }
            
            return training_results
            
        except Exception as e:
            logger.error(f"Model eğitimi hatası: {str(e)}")
            raise
    
    def _save_pipeline_results(self, results: dict):
        """Pipeline sonuçlarını kaydet"""
        try:
            results_file = Path("tcia_pipeline_results.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Pipeline sonuçları kaydedildi: {results_file}")
            
        except Exception as e:
            logger.error(f"Sonuç kaydetme hatası: {str(e)}")
    
    def get_pipeline_status(self) -> dict:
        """Pipeline durumunu getir"""
        return {
            'pipeline_status': self.pipeline_status,
            'directories': {
                'download_dir': str(self.download_dir),
                'processed_dir': str(self.processed_dir),
                'training_dir': str(self.training_dir),
                'models_dir': str(self.models_dir)
            }
        }
    
    def cleanup_intermediate_files(self):
        """Ara dosyaları temizle"""
        try:
            logger.info("Ara dosyalar temizleniyor...")
            
            # DICOM işleme ara dosyalarını temizle
            if self.processed_dir.exists():
                import shutil
                shutil.rmtree(self.processed_dir)
                logger.info("İşlenmiş DICOM dosyaları temizlendi")
            
            logger.info("Temizlik tamamlandı")
            
        except Exception as e:
            logger.error(f"Temizlik hatası: {str(e)}")


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="TCIA Full Pipeline")
    parser.add_argument("--collections", nargs="+", 
                       default=["CPTAC-LUAD", "CMB-BRCA", "UCSF-PDGM"],
                       help="İndirilecek koleksiyonlar")
    parser.add_argument("--max-series", type=int, default=10,
                       help="Koleksiyon başına maksimum seri sayısı")
    parser.add_argument("--no-training", action="store_true",
                       help="Model eğitimi yapma")
    parser.add_argument("--cleanup", action="store_true",
                       help="Ara dosyaları temizle")
    
    args = parser.parse_args()
    
    # Pipeline oluştur
    pipeline = TCIAFullPipeline()
    
    try:
        if args.cleanup:
            pipeline.cleanup_intermediate_files()
            return
        
        # Pipeline durumunu göster
        status = pipeline.get_pipeline_status()
        print("🔍 Pipeline Durumu:")
        print(f"  • İndirme Klasörü: {status['directories']['download_dir']}")
        print(f"  • İşleme Klasörü: {status['directories']['processed_dir']}")
        print(f"  • Eğitim Klasörü: {status['directories']['training_dir']}")
        print(f"  • Modeller Klasörü: {status['directories']['models_dir']}")
        
        # Pipeline'ı çalıştır
        results = pipeline.run_full_pipeline(
            collections=args.collections,
            max_series_per_collection=args.max_series,
            train_models=not args.no_training
        )
        
        # Sonuçları göster
        print("\n📊 Pipeline Sonuçları:")
        print(f"  • Tamamlanan Adımlar: {', '.join(results['steps_completed'])}")
        
        if 'download_results' in results:
            total_downloaded = sum(
                r.get('downloaded_series', 0) 
                for r in results['download_results'].values() 
                if 'downloaded_series' in r
            )
            print(f"  • İndirilen Seri Sayısı: {total_downloaded}")
        
        if 'dataset_results' in results:
            print(f"  • Toplam Görüntü: {results['dataset_results']['total_images']}")
            print(f"  • Eğitim Görüntüleri: {results['dataset_results']['train_images']}")
            print(f"  • Validasyon Görüntüleri: {results['dataset_results']['val_images']}")
            print(f"  • Test Görüntüleri: {results['dataset_results']['test_images']}")
        
        if 'training_results' in results:
            print(f"  • Eğitilen Modeller: {len(results['training_results']['trained_models'])}")
            for model_name, result in results['training_results']['model_results'].items():
                print(f"    - {model_name}: {result['accuracy']:.2f}% accuracy")
        
        if results['errors']:
            print(f"\n⚠️ Hatalar:")
            for error in results['errors']:
                print(f"  • {error}")
        
        print(f"\n✅ Pipeline tamamlandı: {results['completed_at']}")
        
    except Exception as e:
        print(f"❌ Pipeline hatası: {str(e)}")
        logger.error(f"Pipeline hatası: {str(e)}")


if __name__ == "__main__":
    main()
