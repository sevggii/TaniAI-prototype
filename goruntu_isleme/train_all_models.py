#!/usr/bin/env python3
"""
Profesyonel Tıbbi AI Model Eğitim ve Doğrulama Sistemi
====================================================

Bu script tüm tıbbi görüntü analizi modellerini eğitir, doğrular ve
profesyonel seviyede sonuçlar üretir.

Kullanım:
    python train_all_models.py

Yazar: Dr. AI Research Team
Tarih: 2024
Versiyon: 2.0.0
"""

import sys
import logging
import argparse
from pathlib import Path
import time
from datetime import datetime

# Proje root'unu Python path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Custom imports
from models.train_models import ProfessionalModelTrainer
from models.data_manager import MedicalDatasetManager
from models.model_validator import ProfessionalModelValidator

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProfessionalTrainingPipeline:
    """Profesyonel eğitim pipeline'ı"""
    
    def __init__(self, 
                 models_dir: str = "models",
                 data_dir: str = "data",
                 results_dir: str = "results"):
        self.models_dir = models_dir
        self.data_dir = data_dir
        self.results_dir = results_dir
        
        # Bileşenleri başlat
        self.data_manager = MedicalDatasetManager(data_dir)
        self.trainer = ProfessionalModelTrainer(models_dir, data_dir, results_dir)
        self.validator = ProfessionalModelValidator(models_dir, data_dir, f"{results_dir}/validation")
        
        logger.info("🏥 Profesyonel Tıbbi AI Eğitim Pipeline'ı başlatıldı")
    
    def run_complete_pipeline(self, 
                            skip_data_preparation: bool = False,
                            skip_training: bool = False,
                            skip_validation: bool = False) -> Dict[str, Any]:
        """Tam eğitim pipeline'ını çalıştır"""
        start_time = time.time()
        pipeline_results = {
            'start_time': datetime.now().isoformat(),
            'steps_completed': [],
            'errors': [],
            'summary': {}
        }
        
        try:
            # 1. Veri Hazırlama
            if not skip_data_preparation:
                logger.info("📊 Adım 1: Veri Setleri Hazırlanıyor...")
                data_results = self._prepare_all_datasets()
                pipeline_results['steps_completed'].append('data_preparation')
                pipeline_results['data_preparation'] = data_results
                
                if not data_results['success']:
                    logger.error("Veri hazırlama başarısız!")
                    return pipeline_results
            
            # 2. Model Eğitimi
            if not skip_training:
                logger.info("🤖 Adım 2: Modeller Eğitiliyor...")
                training_results = self._train_all_models()
                pipeline_results['steps_completed'].append('training')
                pipeline_results['training'] = training_results
                
                if not training_results['success']:
                    logger.error("Model eğitimi başarısız!")
                    return pipeline_results
            
            # 3. Model Doğrulama
            if not skip_validation:
                logger.info("🔍 Adım 3: Modeller Doğrulanıyor...")
                validation_results = self._validate_all_models()
                pipeline_results['steps_completed'].append('validation')
                pipeline_results['validation'] = validation_results
            
            # 4. Özet Rapor
            logger.info("📋 Adım 4: Özet Rapor Oluşturuluyor...")
            summary = self._create_pipeline_summary(pipeline_results)
            pipeline_results['summary'] = summary
            
            # Pipeline tamamlandı
            end_time = time.time()
            pipeline_results['end_time'] = datetime.now().isoformat()
            pipeline_results['total_duration'] = end_time - start_time
            pipeline_results['success'] = True
            
            logger.info(f"🎉 Pipeline başarıyla tamamlandı! Süre: {pipeline_results['total_duration']:.2f} saniye")
            
        except Exception as e:
            logger.error(f"Pipeline hatası: {str(e)}")
            pipeline_results['errors'].append(str(e))
            pipeline_results['success'] = False
        
        return pipeline_results
    
    def _prepare_all_datasets(self) -> Dict[str, Any]:
        """Tüm veri setlerini hazırla"""
        try:
            datasets = self.data_manager.list_available_datasets()
            results = {
                'success': True,
                'datasets': {},
                'total_datasets': len(datasets),
                'successful_datasets': 0,
                'failed_datasets': 0
            }
            
            for dataset_name in datasets.keys():
                logger.info(f"Veri seti hazırlanıyor: {dataset_name}")
                
                try:
                    success = self.data_manager.download_dataset(dataset_name)
                    
                    if success:
                        # Veri setini doğrula
                        validation = self.data_manager.validate_dataset(dataset_name)
                        
                        results['datasets'][dataset_name] = {
                            'prepared': True,
                            'validation': validation,
                            'total_samples': validation.get('total_samples', 0)
                        }
                        
                        if validation['valid']:
                            results['successful_datasets'] += 1
                            logger.info(f"✅ {dataset_name}: {validation['total_samples']} örnek")
                        else:
                            results['failed_datasets'] += 1
                            logger.error(f"❌ {dataset_name}: {validation['errors']}")
                    else:
                        results['datasets'][dataset_name] = {'prepared': False, 'error': 'Hazırlama başarısız'}
                        results['failed_datasets'] += 1
                        
                except Exception as e:
                    logger.error(f"Veri seti hazırlama hatası ({dataset_name}): {str(e)}")
                    results['datasets'][dataset_name] = {'prepared': False, 'error': str(e)}
                    results['failed_datasets'] += 1
            
            if results['successful_datasets'] == 0:
                results['success'] = False
            
            return results
            
        except Exception as e:
            logger.error(f"Veri hazırlama hatası: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _train_all_models(self) -> Dict[str, Any]:
        """Tüm modelleri eğit"""
        try:
            logger.info("Model eğitimi başlatılıyor...")
            results = self.trainer.train_all_models()
            
            # Sonuçları analiz et
            successful_models = len([r for r in results.values() if 'error' not in r])
            failed_models = len([r for r in results.values() if 'error' in r])
            
            training_summary = {
                'success': successful_models > 0,
                'total_models': len(results),
                'successful_models': successful_models,
                'failed_models': failed_models,
                'results': results
            }
            
            # Başarılı modelleri logla
            logger.info("📊 Eğitim Sonuçları:")
            for model_name, result in results.items():
                if 'error' not in result:
                    logger.info(f"✅ {model_name}: {result['final_accuracy']:.2f}% accuracy")
                else:
                    logger.error(f"❌ {model_name}: {result['error']}")
            
            return training_summary
            
        except Exception as e:
            logger.error(f"Model eğitimi hatası: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _validate_all_models(self) -> Dict[str, Any]:
        """Tüm modelleri doğrula"""
        try:
            logger.info("Model doğrulaması başlatılıyor...")
            results = self.validator.validate_all_models()
            
            # Sonuçları analiz et
            successful_validations = len([r for r in results.values() if 'error' not in r])
            failed_validations = len([r for r in results.values() if 'error' in r])
            
            validation_summary = {
                'success': successful_validations > 0,
                'total_models': len(results),
                'successful_validations': successful_validations,
                'failed_validations': failed_validations,
                'results': results
            }
            
            # Doğrulama sonuçlarını logla
            logger.info("🔍 Doğrulama Sonuçları:")
            for model_name, result in results.items():
                if 'error' not in result:
                    logger.info(f"✅ {model_name}: {result['accuracy']:.4f} accuracy")
                else:
                    logger.error(f"❌ {model_name}: {result['error']}")
            
            return validation_summary
            
        except Exception as e:
            logger.error(f"Model doğrulaması hatası: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _create_pipeline_summary(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Pipeline özeti oluştur"""
        summary = {
            'pipeline_success': pipeline_results.get('success', False),
            'steps_completed': pipeline_results.get('steps_completed', []),
            'total_duration': pipeline_results.get('total_duration', 0),
            'model_performance': {},
            'recommendations': []
        }
        
        # Model performanslarını özetle
        if 'validation' in pipeline_results:
            validation_results = pipeline_results['validation']['results']
            
            for model_name, result in validation_results.items():
                if 'error' not in result:
                    summary['model_performance'][model_name] = {
                        'accuracy': result.get('accuracy', 0.0),
                        'precision': result.get('precision', 0.0),
                        'recall': result.get('recall', 0.0),
                        'f1_score': result.get('f1_score', 0.0),
                        'auc_roc': result.get('auc_roc', 0.0)
                    }
        
        # Öneriler oluştur
        if summary['model_performance']:
            best_model = max(summary['model_performance'].items(), 
                           key=lambda x: x[1]['accuracy'])
            summary['recommendations'].append(f"En iyi performans: {best_model[0]} ({best_model[1]['accuracy']:.4f})")
            
            # Düşük performanslı modelleri belirle
            low_performance = [name for name, perf in summary['model_performance'].items() 
                             if perf['accuracy'] < 0.8]
            if low_performance:
                summary['recommendations'].append(f"Düşük performanslı modeller: {', '.join(low_performance)}")
        
        return summary


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='Profesyonel Tıbbi AI Model Eğitim Sistemi')
    parser.add_argument('--skip-data', action='store_true', help='Veri hazırlamayı atla')
    parser.add_argument('--skip-training', action='store_true', help='Model eğitimini atla')
    parser.add_argument('--skip-validation', action='store_true', help='Model doğrulamasını atla')
    parser.add_argument('--models-dir', default='models', help='Modeller dizini')
    parser.add_argument('--data-dir', default='data', help='Veri dizini')
    parser.add_argument('--results-dir', default='results', help='Sonuçlar dizini')
    
    args = parser.parse_args()
    
    logger.info("🚀 Profesyonel Tıbbi AI Model Eğitim Sistemi Başlatılıyor")
    logger.info(f"Modeller dizini: {args.models_dir}")
    logger.info(f"Veri dizini: {args.data_dir}")
    logger.info(f"Sonuçlar dizini: {args.results_dir}")
    
    # Pipeline oluştur ve çalıştır
    pipeline = ProfessionalTrainingPipeline(
        models_dir=args.models_dir,
        data_dir=args.data_dir,
        results_dir=args.results_dir
    )
    
    # Tam pipeline'ı çalıştır
    results = pipeline.run_complete_pipeline(
        skip_data_preparation=args.skip_data,
        skip_training=args.skip_training,
        skip_validation=args.skip_validation
    )
    
    # Sonuçları özetle
    if results['success']:
        logger.info("🎉 Pipeline başarıyla tamamlandı!")
        
        if 'summary' in results:
            summary = results['summary']
            logger.info("📊 Özet:")
            logger.info(f"  - Tamamlanan adımlar: {', '.join(summary['steps_completed'])}")
            logger.info(f"  - Toplam süre: {summary['total_duration']:.2f} saniye")
            
            if summary['recommendations']:
                logger.info("💡 Öneriler:")
                for rec in summary['recommendations']:
                    logger.info(f"  - {rec}")
    else:
        logger.error("❌ Pipeline başarısız!")
        if results['errors']:
            logger.error("Hatalar:")
            for error in results['errors']:
                logger.error(f"  - {error}")
    
    # Sonuçları dosyaya kaydet
    import json
    results_file = Path(args.results_dir) / "pipeline_results.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Sonuçlar kaydedildi: {results_file}")


if __name__ == "__main__":
    main()
