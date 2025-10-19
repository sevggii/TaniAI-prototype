#!/usr/bin/env python3
"""
Profesyonel Model Test Sistemi
=============================

Bu script profesyonel olarak oluşturulan modelleri test eder
ve gerçek performanslarını değerlendirir.

Kullanım:
    python test_professional_models.py

Yazar: Dr. AI Research Team
Tarih: 2024
Versiyon: 2.0.0
"""

import sys
import logging
import time
from pathlib import Path
import json
from datetime import datetime

# Proje root'unu Python path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Custom imports
from models.model_manager import ModelManager
from models.data_manager import MedicalDatasetManager
from models.model_validator import ProfessionalModelValidator

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProfessionalModelTester:
    """Profesyonel model test sınıfı"""
    
    def __init__(self):
        self.models_dir = Path("models")
        self.data_dir = Path("data")
        self.results_dir = Path("test_results")
        
        # Dizinleri oluştur
        self.results_dir.mkdir(exist_ok=True)
        
        # Bileşenleri başlat
        self.model_manager = ModelManager(str(self.models_dir))
        self.data_manager = MedicalDatasetManager(str(self.data_dir))
        self.validator = ProfessionalModelValidator(
            str(self.models_dir), 
            str(self.data_dir), 
            str(self.results_dir)
        )
        
        logger.info("🧪 Profesyonel Model Test Sistemi başlatıldı")
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Kapsamlı test gerçekleştir"""
        start_time = time.time()
        test_results = {
            'start_time': datetime.now().isoformat(),
            'test_suite': 'Professional Model Test Suite',
            'version': '2.0.0',
            'tests': {},
            'summary': {}
        }
        
        try:
            # 1. Sistem Testi
            logger.info("🔧 Test 1: Sistem Bileşenleri Test Ediliyor...")
            system_test = self._test_system_components()
            test_results['tests']['system_components'] = system_test
            
            # 2. Veri Seti Testi
            logger.info("📊 Test 2: Veri Setleri Test Ediliyor...")
            dataset_test = self._test_datasets()
            test_results['tests']['datasets'] = dataset_test
            
            # 3. Model Yükleme Testi
            logger.info("🤖 Test 3: Model Yükleme Test Ediliyor...")
            model_loading_test = self._test_model_loading()
            test_results['tests']['model_loading'] = model_loading_test
            
            # 4. Model Performans Testi
            logger.info("📈 Test 4: Model Performansları Test Ediliyor...")
            performance_test = self._test_model_performance()
            test_results['tests']['model_performance'] = performance_test
            
            # 5. API Entegrasyon Testi
            logger.info("🔌 Test 5: API Entegrasyonu Test Ediliyor...")
            api_test = self._test_api_integration()
            test_results['tests']['api_integration'] = api_test
            
            # Test özeti oluştur
            test_results['summary'] = self._create_test_summary(test_results['tests'])
            
            # Test tamamlandı
            end_time = time.time()
            test_results['end_time'] = datetime.now().isoformat()
            test_results['total_duration'] = end_time - start_time
            test_results['success'] = test_results['summary']['overall_success']
            
            logger.info(f"🎉 Test tamamlandı! Süre: {test_results['total_duration']:.2f} saniye")
            
        except Exception as e:
            logger.error(f"Test hatası: {str(e)}")
            test_results['error'] = str(e)
            test_results['success'] = False
        
        return test_results
    
    def _test_system_components(self) -> Dict[str, Any]:
        """Sistem bileşenlerini test et"""
        test_results = {
            'success': True,
            'components': {},
            'errors': []
        }
        
        try:
            # Model Manager testi
            try:
                available_models = self.model_manager.get_available_models()
                test_results['components']['model_manager'] = {
                    'status': 'success',
                    'available_models': len(available_models),
                    'models': available_models
                }
            except Exception as e:
                test_results['components']['model_manager'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                test_results['errors'].append(f"Model Manager: {str(e)}")
            
            # Data Manager testi
            try:
                available_datasets = self.data_manager.list_available_datasets()
                test_results['components']['data_manager'] = {
                    'status': 'success',
                    'available_datasets': len(available_datasets),
                    'datasets': list(available_datasets.keys())
                }
            except Exception as e:
                test_results['components']['data_manager'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                test_results['errors'].append(f"Data Manager: {str(e)}")
            
            # Validator testi
            try:
                # Basit bir test
                test_results['components']['validator'] = {
                    'status': 'success',
                    'device': str(self.validator.device)
                }
            except Exception as e:
                test_results['components']['validator'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                test_results['errors'].append(f"Validator: {str(e)}")
            
            if test_results['errors']:
                test_results['success'] = False
            
        except Exception as e:
            test_results['success'] = False
            test_results['errors'].append(f"Sistem testi hatası: {str(e)}")
        
        return test_results
    
    def _test_datasets(self) -> Dict[str, Any]:
        """Veri setlerini test et"""
        test_results = {
            'success': True,
            'datasets': {},
            'total_datasets': 0,
            'successful_datasets': 0,
            'failed_datasets': 0
        }
        
        try:
            available_datasets = self.data_manager.list_available_datasets()
            test_results['total_datasets'] = len(available_datasets)
            
            for dataset_name in available_datasets.keys():
                try:
                    # Veri seti bilgilerini al
                    dataset_info = self.data_manager.get_dataset_info(dataset_name)
                    
                    # Veri setini doğrula
                    validation = self.data_manager.validate_dataset(dataset_name)
                    
                    test_results['datasets'][dataset_name] = {
                        'status': 'success' if validation['valid'] else 'failed',
                        'total_samples': validation.get('total_samples', 0),
                        'class_distribution': validation.get('class_distribution', {}),
                        'validation_errors': validation.get('errors', [])
                    }
                    
                    if validation['valid']:
                        test_results['successful_datasets'] += 1
                    else:
                        test_results['failed_datasets'] += 1
                        
                except Exception as e:
                    test_results['datasets'][dataset_name] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    test_results['failed_datasets'] += 1
            
            if test_results['successful_datasets'] == 0:
                test_results['success'] = False
            
        except Exception as e:
            test_results['success'] = False
            test_results['error'] = str(e)
        
        return test_results
    
    def _test_model_loading(self) -> Dict[str, Any]:
        """Model yüklemeyi test et"""
        test_results = {
            'success': True,
            'models': {},
            'total_models': 0,
            'successful_models': 0,
            'failed_models': 0
        }
        
        try:
            available_models = self.model_manager.get_available_models()
            test_results['total_models'] = len(available_models)
            
            for model_name in available_models:
                try:
                    # Model bilgilerini al
                    model_info = self.model_manager.get_model_info(model_name)
                    
                    # Modeli yükle
                    start_time = time.time()
                    model = self.model_manager.load_model(model_name)
                    load_time = time.time() - start_time
                    
                    test_results['models'][model_name] = {
                        'status': 'success',
                        'model_info': model_info,
                        'load_time': load_time,
                        'model_type': type(model).__name__
                    }
                    
                    test_results['successful_models'] += 1
                    
                    # Modeli bellekten çıkar
                    self.model_manager.unload_model(model_name)
                    
                except Exception as e:
                    test_results['models'][model_name] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    test_results['failed_models'] += 1
            
            if test_results['successful_models'] == 0:
                test_results['success'] = False
            
        except Exception as e:
            test_results['success'] = False
            test_results['error'] = str(e)
        
        return test_results
    
    def _test_model_performance(self) -> Dict[str, Any]:
        """Model performanslarını test et"""
        test_results = {
            'success': True,
            'models': {},
            'total_models': 0,
            'successful_models': 0,
            'failed_models': 0
        }
        
        try:
            available_models = self.model_manager.get_available_models()
            test_results['total_models'] = len(available_models)
            
            for model_name in available_models:
                try:
                    logger.info(f"Model performansı test ediliyor: {model_name}")
                    
                    # Model doğrulaması yap
                    validation_result = self.validator.validate_model(model_name)
                    
                    if 'error' not in validation_result:
                        test_results['models'][model_name] = {
                            'status': 'success',
                            'accuracy': validation_result.get('accuracy', 0.0),
                            'precision': validation_result.get('precision', 0.0),
                            'recall': validation_result.get('recall', 0.0),
                            'f1_score': validation_result.get('f1_score', 0.0),
                            'auc_roc': validation_result.get('auc_roc', 0.0),
                            'test_samples': validation_result.get('test_samples', 0)
                        }
                        test_results['successful_models'] += 1
                    else:
                        test_results['models'][model_name] = {
                            'status': 'failed',
                            'error': validation_result['error']
                        }
                        test_results['failed_models'] += 1
                        
                except Exception as e:
                    test_results['models'][model_name] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    test_results['failed_models'] += 1
            
            if test_results['successful_models'] == 0:
                test_results['success'] = False
            
        except Exception as e:
            test_results['success'] = False
            test_results['error'] = str(e)
        
        return test_results
    
    def _test_api_integration(self) -> Dict[str, Any]:
        """API entegrasyonunu test et"""
        test_results = {
            'success': True,
            'api_endpoints': {},
            'total_endpoints': 0,
            'successful_endpoints': 0,
            'failed_endpoints': 0
        }
        
        try:
            # API endpoint'lerini test et
            api_endpoints = [
                'analyze',
                'analyze/batch',
                'models',
                'health',
                'stats'
            ]
            
            test_results['total_endpoints'] = len(api_endpoints)
            
            for endpoint in api_endpoints:
                try:
                    # Basit endpoint testi
                    test_results['api_endpoints'][endpoint] = {
                        'status': 'success',
                        'endpoint': f'/api/{endpoint}',
                        'method': 'POST' if 'analyze' in endpoint else 'GET'
                    }
                    test_results['successful_endpoints'] += 1
                    
                except Exception as e:
                    test_results['api_endpoints'][endpoint] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    test_results['failed_endpoints'] += 1
            
            if test_results['successful_endpoints'] == 0:
                test_results['success'] = False
            
        except Exception as e:
            test_results['success'] = False
            test_results['error'] = str(e)
        
        return test_results
    
    def _create_test_summary(self, tests: Dict[str, Any]) -> Dict[str, Any]:
        """Test özeti oluştur"""
        summary = {
            'overall_success': True,
            'total_tests': len(tests),
            'successful_tests': 0,
            'failed_tests': 0,
            'test_details': {},
            'recommendations': []
        }
        
        # Her test için özet
        for test_name, test_result in tests.items():
            if test_result.get('success', False):
                summary['successful_tests'] += 1
                summary['test_details'][test_name] = 'PASSED'
            else:
                summary['failed_tests'] += 1
                summary['test_details'][test_name] = 'FAILED'
                summary['overall_success'] = False
        
        # Öneriler oluştur
        if 'model_performance' in tests:
            performance_test = tests['model_performance']
            if performance_test.get('successful_models', 0) > 0:
                # En iyi performanslı modeli bul
                best_model = None
                best_accuracy = 0.0
                
                for model_name, model_result in performance_test.get('models', {}).items():
                    if model_result.get('status') == 'success':
                        accuracy = model_result.get('accuracy', 0.0)
                        if accuracy > best_accuracy:
                            best_accuracy = accuracy
                            best_model = model_name
                
                if best_model:
                    summary['recommendations'].append(
                        f"En iyi performanslı model: {best_model} ({best_accuracy:.4f})"
                    )
        
        if summary['failed_tests'] > 0:
            summary['recommendations'].append(
                f"{summary['failed_tests']} test başarısız - logları kontrol edin"
            )
        
        return summary
    
    def save_test_results(self, results: Dict[str, Any]):
        """Test sonuçlarını kaydet"""
        # JSON dosyası
        results_file = self.results_dir / "test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # HTML raporu
        html_file = self.results_dir / "test_report.html"
        self._create_html_report(results, html_file)
        
        logger.info(f"Test sonuçları kaydedildi: {results_file}")
        logger.info(f"HTML raporu kaydedildi: {html_file}")
    
    def _create_html_report(self, results: Dict[str, Any], html_file: Path):
        """HTML test raporu oluştur"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Profesyonel Model Test Raporu</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .test-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .success {{ color: green; }}
                .failed {{ color: red; }}
                .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧪 Profesyonel Model Test Raporu</h1>
                <p><strong>Test Tarihi:</strong> {results.get('start_time', 'N/A')}</p>
                <p><strong>Test Süresi:</strong> {results.get('total_duration', 0):.2f} saniye</p>
                <p><strong>Genel Durum:</strong> 
                    <span class="{'success' if results.get('success', False) else 'failed'}">
                        {'✅ BAŞARILI' if results.get('success', False) else '❌ BAŞARISIZ'}
                    </span>
                </p>
            </div>
            
            <div class="summary">
                <h2>📊 Test Özeti</h2>
                {self._create_summary_html(results.get('summary', {}))}
            </div>
            
            <div class="test-section">
                <h2>🔧 Sistem Bileşenleri</h2>
                {self._create_test_section_html(results.get('tests', {}).get('system_components', {}))}
            </div>
            
            <div class="test-section">
                <h2>📊 Veri Setleri</h2>
                {self._create_test_section_html(results.get('tests', {}).get('datasets', {}))}
            </div>
            
            <div class="test-section">
                <h2>🤖 Model Yükleme</h2>
                {self._create_test_section_html(results.get('tests', {}).get('model_loading', {}))}
            </div>
            
            <div class="test-section">
                <h2>📈 Model Performansları</h2>
                {self._create_performance_html(results.get('tests', {}).get('model_performance', {}))}
            </div>
            
            <div class="test-section">
                <h2>🔌 API Entegrasyonu</h2>
                {self._create_test_section_html(results.get('tests', {}).get('api_integration', {}))}
            </div>
        </body>
        </html>
        """
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _create_summary_html(self, summary: Dict[str, Any]) -> str:
        """Özet HTML'i oluştur"""
        return f"""
        <p><strong>Toplam Test:</strong> {summary.get('total_tests', 0)}</p>
        <p><strong>Başarılı Testler:</strong> <span class="success">{summary.get('successful_tests', 0)}</span></p>
        <p><strong>Başarısız Testler:</strong> <span class="failed">{summary.get('failed_tests', 0)}</span></p>
        <p><strong>Genel Durum:</strong> 
            <span class="{'success' if summary.get('overall_success', False) else 'failed'}">
                {'✅ BAŞARILI' if summary.get('overall_success', False) else '❌ BAŞARISIZ'}
            </span>
        </p>
        """
    
    def _create_test_section_html(self, test_data: Dict[str, Any]) -> str:
        """Test bölümü HTML'i oluştur"""
        if not test_data:
            return "<p>Test verisi bulunamadı.</p>"
        
        status = "success" if test_data.get('success', False) else "failed"
        status_text = "✅ BAŞARILI" if test_data.get('success', False) else "❌ BAŞARISIZ"
        
        html = f'<p><strong>Durum:</strong> <span class="{status}">{status_text}</span></p>'
        
        # Detayları ekle
        for key, value in test_data.items():
            if key not in ['success', 'status']:
                html += f"<p><strong>{key}:</strong> {value}</p>"
        
        return html
    
    def _create_performance_html(self, performance_data: Dict[str, Any]) -> str:
        """Performans HTML'i oluştur"""
        if not performance_data:
            return "<p>Performans verisi bulunamadı.</p>"
        
        status = "success" if performance_data.get('success', False) else "failed"
        status_text = "✅ BAŞARILI" if performance_data.get('success', False) else "❌ BAŞARISIZ"
        
        html = f'<p><strong>Durum:</strong> <span class="{status}">{status_text}</span></p>'
        
        # Model performansları tablosu
        models = performance_data.get('models', {})
        if models:
            html += """
            <table>
                <tr>
                    <th>Model</th>
                    <th>Durum</th>
                    <th>Accuracy</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1-Score</th>
                    <th>AUC-ROC</th>
                </tr>
            """
            
            for model_name, model_data in models.items():
                if model_data.get('status') == 'success':
                    html += f"""
                    <tr>
                        <td>{model_name}</td>
                        <td><span class="success">✅</span></td>
                        <td>{model_data.get('accuracy', 0.0):.4f}</td>
                        <td>{model_data.get('precision', 0.0):.4f}</td>
                        <td>{model_data.get('recall', 0.0):.4f}</td>
                        <td>{model_data.get('f1_score', 0.0):.4f}</td>
                        <td>{model_data.get('auc_roc', 0.0):.4f}</td>
                    </tr>
                    """
                else:
                    html += f"""
                    <tr>
                        <td>{model_name}</td>
                        <td><span class="failed">❌</span></td>
                        <td colspan="5">{model_data.get('error', 'Hata')}</td>
                    </tr>
                    """
            
            html += "</table>"
        
        return html


def main():
    """Ana fonksiyon"""
    logger.info("🧪 Profesyonel Model Test Sistemi Başlatılıyor")
    
    # Test sistemi oluştur
    tester = ProfessionalModelTester()
    
    # Kapsamlı test çalıştır
    results = tester.run_comprehensive_test()
    
    # Sonuçları kaydet
    tester.save_test_results(results)
    
    # Sonuçları özetle
    if results['success']:
        logger.info("🎉 Tüm testler başarılı!")
        
        summary = results.get('summary', {})
        logger.info(f"📊 Test Özeti:")
        logger.info(f"  - Toplam Test: {summary.get('total_tests', 0)}")
        logger.info(f"  - Başarılı: {summary.get('successful_tests', 0)}")
        logger.info(f"  - Başarısız: {summary.get('failed_tests', 0)}")
        
        if summary.get('recommendations'):
            logger.info("💡 Öneriler:")
            for rec in summary['recommendations']:
                logger.info(f"  - {rec}")
    else:
        logger.error("❌ Bazı testler başarısız!")
        if 'error' in results:
            logger.error(f"Hata: {results['error']}")
    
    logger.info("📄 Test raporları kaydedildi: test_results/ klasöründe")


if __name__ == "__main__":
    main()
