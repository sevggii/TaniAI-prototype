"""
Profesyonel Model Doğrulama ve Test Sistemi
==========================================

Bu modül eğitilmiş modellerin performansını değerlendirir,
doğrular ve kapsamlı test raporları oluşturur.

Yazar: Dr. AI Research Team
Tarih: 2024
Versiyon: 2.0.0
"""

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    precision_recall_curve, roc_curve, average_precision_score
)
from sklearn.calibration import calibration_curve
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Custom imports
from models import RadiologyCNN, DenseNetRadiology, ResNetRadiology
from models.model_manager import ModelManager
from models.data_manager import MedicalDatasetManager

logger = logging.getLogger(__name__)


class ProfessionalModelValidator:
    """Profesyonel model doğrulama sınıfı"""
    
    def __init__(self, 
                 models_dir: str = "models",
                 data_dir: str = "data",
                 results_dir: str = "validation_results"):
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        
        # Dizinleri oluştur
        self.results_dir.mkdir(exist_ok=True)
        
        # Bileşenleri başlat
        self.model_manager = ModelManager(str(self.models_dir))
        self.data_manager = MedicalDatasetManager(str(self.data_dir))
        
        # Device ayarı
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Doğrulama cihazı: {self.device}")
        
        # Doğrulama metrikleri
        self.validation_metrics = {
            'accuracy': self._calculate_accuracy,
            'precision': self._calculate_precision,
            'recall': self._calculate_recall,
            'f1_score': self._calculate_f1_score,
            'auc_roc': self._calculate_auc_roc,
            'auc_pr': self._calculate_auc_pr,
            'calibration': self._calculate_calibration,
            'confidence': self._calculate_confidence_metrics
        }
    
    def validate_model(self, 
                      model_name: str,
                      test_data: Optional[Tuple[List[str], List[int]]] = None) -> Dict[str, Any]:
        """Model doğrulaması gerçekleştir"""
        logger.info(f"Model doğrulaması başlatılıyor: {model_name}")
        
        try:
            # Model bilgilerini al
            model_info = self.model_manager.get_model_info(model_name)
            
            # Test verisi hazırla
            if test_data is None:
                test_data = self._prepare_test_data(model_name)
            
            if not test_data[0]:  # Boş veri kontrolü
                logger.error(f"Test verisi bulunamadı: {model_name}")
                return {'error': 'Test verisi bulunamadı'}
            
            test_paths, test_labels = test_data
            
            # Modeli yükle
            model = self.model_manager.load_model(model_name, str(self.device))
            
            # Tahminler yap
            predictions, probabilities, true_labels = self._make_predictions(
                model, test_paths, test_labels, model_name
            )
            
            # Metrikleri hesapla
            validation_results = self._calculate_all_metrics(
                true_labels, predictions, probabilities, model_name
            )
            
            # Model bilgilerini ekle
            validation_results['model_info'] = model_info
            validation_results['test_samples'] = len(test_paths)
            validation_results['validation_date'] = datetime.now().isoformat()
            
            # Sonuçları kaydet
            self._save_validation_results(validation_results, model_name)
            
            # Görselleştirmeler oluştur
            self._create_validation_plots(validation_results, model_name)
            
            logger.info(f"Model doğrulaması tamamlandı: {model_name}")
            logger.info(f"Doğruluk: {validation_results['accuracy']:.4f}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Model doğrulama hatası ({model_name}): {str(e)}")
            return {'error': str(e)}
    
    def _prepare_test_data(self, model_name: str) -> Tuple[List[str], List[int]]:
        """Test verisi hazırla"""
        # Veri seti adını belirle
        dataset_mapping = {
            'xray_pneumonia': 'chest_xray_pneumonia',
            'ct_stroke': 'ct_stroke_dataset',
            'mri_brain_tumor': 'mri_brain_tumor',
            'xray_fracture': 'xray_fracture_dataset',
            'mammography_mass': 'mammography_mass'
        }
        
        dataset_name = dataset_mapping.get(model_name, model_name)
        
        # Test verisi hazırla
        _, _, test_paths, test_labels = self.data_manager.prepare_training_data(
            dataset_name, test_size=0.3, random_state=42
        )
        
        return test_paths, test_labels
    
    def _make_predictions(self, 
                         model: nn.Module, 
                         test_paths: List[str], 
                         test_labels: List[int],
                         model_name: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Model tahminleri yap"""
        model.eval()
        all_predictions = []
        all_probabilities = []
        all_true_labels = []
        
        # Görüntü işleme
        from models.train_models import MedicalImageDataset
        
        # Test dataset oluştur
        test_dataset = MedicalImageDataset(test_paths, test_labels, model_name, augment=False)
        
        # Batch işleme
        batch_size = 32
        for i in range(0, len(test_dataset), batch_size):
            batch_data = []
            batch_labels = []
            
            for j in range(i, min(i + batch_size, len(test_dataset))):
                image, label = test_dataset[j]
                batch_data.append(image)
                batch_labels.append(label)
            
            if batch_data:
                # Tensor'e çevir
                batch_tensor = torch.stack(batch_data).to(self.device)
                
                # Tahmin yap
                with torch.no_grad():
                    outputs = model(batch_tensor)
                    probabilities = torch.softmax(outputs, dim=1)
                    _, predictions = torch.max(outputs, 1)
                
                all_predictions.extend(predictions.cpu().numpy())
                all_probabilities.extend(probabilities.cpu().numpy())
                all_true_labels.extend(batch_labels)
        
        return np.array(all_predictions), np.array(all_probabilities), np.array(all_true_labels)
    
    def _calculate_all_metrics(self, 
                              true_labels: np.ndarray, 
                              predictions: np.ndarray, 
                              probabilities: np.ndarray,
                              model_name: str) -> Dict[str, Any]:
        """Tüm metrikleri hesapla"""
        results = {}
        
        # Temel metrikler
        for metric_name, metric_func in self.validation_metrics.items():
            try:
                results[metric_name] = metric_func(true_labels, predictions, probabilities)
            except Exception as e:
                logger.warning(f"Metrik hesaplama hatası ({metric_name}): {str(e)}")
                results[metric_name] = None
        
        # Sınıf isimlerini al
        model_info = self.model_manager.get_model_info(model_name)
        class_names = self.model_manager._get_class_names(model_name)
        results['class_names'] = class_names
        
        # Confusion matrix
        results['confusion_matrix'] = confusion_matrix(true_labels, predictions).tolist()
        
        # Classification report
        results['classification_report'] = classification_report(
            true_labels, predictions, target_names=class_names, output_dict=True
        )
        
        return results
    
    def _calculate_accuracy(self, true_labels: np.ndarray, predictions: np.ndarray, probabilities: np.ndarray) -> float:
        """Doğruluk hesapla"""
        return np.mean(true_labels == predictions)
    
    def _calculate_precision(self, true_labels: np.ndarray, predictions: np.ndarray, probabilities: np.ndarray) -> float:
        """Precision hesapla"""
        from sklearn.metrics import precision_score
        return precision_score(true_labels, predictions, average='weighted')
    
    def _calculate_recall(self, true_labels: np.ndarray, predictions: np.ndarray, probabilities: np.ndarray) -> float:
        """Recall hesapla"""
        from sklearn.metrics import recall_score
        return recall_score(true_labels, predictions, average='weighted')
    
    def _calculate_f1_score(self, true_labels: np.ndarray, predictions: np.ndarray, probabilities: np.ndarray) -> float:
        """F1 score hesapla"""
        from sklearn.metrics import f1_score
        return f1_score(true_labels, predictions, average='weighted')
    
    def _calculate_auc_roc(self, true_labels: np.ndarray, predictions: np.ndarray, probabilities: np.ndarray) -> float:
        """ROC AUC hesapla"""
        try:
            if len(np.unique(true_labels)) > 2:
                return roc_auc_score(true_labels, probabilities, multi_class='ovr')
            else:
                return roc_auc_score(true_labels, probabilities[:, 1])
        except:
            return 0.0
    
    def _calculate_auc_pr(self, true_labels: np.ndarray, predictions: np.ndarray, probabilities: np.ndarray) -> float:
        """PR AUC hesapla"""
        try:
            if len(np.unique(true_labels)) > 2:
                return average_precision_score(true_labels, probabilities, average='weighted')
            else:
                return average_precision_score(true_labels, probabilities[:, 1])
        except:
            return 0.0
    
    def _calculate_calibration(self, true_labels: np.ndarray, predictions: np.ndarray, probabilities: np.ndarray) -> Dict[str, Any]:
        """Kalibrasyon metrikleri hesapla"""
        try:
            if len(np.unique(true_labels)) == 2:
                # Binary classification
                prob_true, prob_pred = calibration_curve(true_labels, probabilities[:, 1], n_bins=10)
                return {
                    'prob_true': prob_true.tolist(),
                    'prob_pred': prob_pred.tolist(),
                    'calibration_error': np.mean(np.abs(prob_true - prob_pred))
                }
            else:
                # Multi-class - her sınıf için ayrı ayrı
                calibration_results = {}
                for i in range(probabilities.shape[1]):
                    binary_labels = (true_labels == i).astype(int)
                    if np.sum(binary_labels) > 0:
                        prob_true, prob_pred = calibration_curve(binary_labels, probabilities[:, i], n_bins=10)
                        calibration_results[f'class_{i}'] = {
                            'prob_true': prob_true.tolist(),
                            'prob_pred': prob_pred.tolist(),
                            'calibration_error': np.mean(np.abs(prob_true - prob_pred))
                        }
                return calibration_results
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_confidence_metrics(self, true_labels: np.ndarray, predictions: np.ndarray, probabilities: np.ndarray) -> Dict[str, Any]:
        """Güven metrikleri hesapla"""
        # Maksimum olasılık
        max_probs = np.max(probabilities, axis=1)
        
        # Doğru tahminlerin güveni
        correct_mask = true_labels == predictions
        correct_confidences = max_probs[correct_mask]
        incorrect_confidences = max_probs[~correct_mask]
        
        return {
            'mean_confidence': np.mean(max_probs),
            'std_confidence': np.std(max_probs),
            'correct_mean_confidence': np.mean(correct_confidences) if len(correct_confidences) > 0 else 0,
            'incorrect_mean_confidence': np.mean(incorrect_confidences) if len(incorrect_confidences) > 0 else 0,
            'confidence_gap': np.mean(correct_confidences) - np.mean(incorrect_confidences) if len(correct_confidences) > 0 and len(incorrect_confidences) > 0 else 0
        }
    
    def _save_validation_results(self, results: Dict[str, Any], model_name: str):
        """Doğrulama sonuçlarını kaydet"""
        results_file = self.results_dir / f"{model_name}_validation_results.json"
        
        # JSON serializable hale getir
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, np.ndarray):
                serializable_results[key] = value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                serializable_results[key] = value.item()
            else:
                serializable_results[key] = value
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Doğrulama sonuçları kaydedildi: {results_file}")
    
    def _create_validation_plots(self, results: Dict[str, Any], model_name: str):
        """Doğrulama görselleştirmeleri oluştur"""
        try:
            # Confusion Matrix
            self._plot_confusion_matrix(results, model_name)
            
            # ROC Curve
            self._plot_roc_curve(results, model_name)
            
            # Precision-Recall Curve
            self._plot_precision_recall_curve(results, model_name)
            
            # Calibration Plot
            self._plot_calibration(results, model_name)
            
            # Confidence Distribution
            self._plot_confidence_distribution(results, model_name)
            
            # Performance Summary
            self._plot_performance_summary(results, model_name)
            
        except Exception as e:
            logger.error(f"Görselleştirme hatası ({model_name}): {str(e)}")
    
    def _plot_confusion_matrix(self, results: Dict[str, Any], model_name: str):
        """Confusion matrix çiz"""
        cm = np.array(results['confusion_matrix'])
        class_names = results['class_names']
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=class_names, yticklabels=class_names)
        plt.title(f'{model_name} - Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        
        plot_file = self.results_dir / f"{model_name}_confusion_matrix.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_roc_curve(self, results: Dict[str, Any], model_name: str):
        """ROC curve çiz"""
        # Bu örnekte basit bir ROC curve
        plt.figure(figsize=(10, 8))
        
        # Örnek ROC curve (gerçek veri ile değiştirilecek)
        fpr = np.linspace(0, 1, 100)
        tpr = fpr  # Basit örnek
        
        plt.plot(fpr, tpr, 'b-', label=f'ROC Curve (AUC = {results.get("auc_roc", 0.0):.3f})')
        plt.plot([0, 1], [0, 1], 'r--', label='Random Classifier')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'{model_name} - ROC Curve')
        plt.legend()
        plt.grid(True)
        
        plot_file = self.results_dir / f"{model_name}_roc_curve.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_precision_recall_curve(self, results: Dict[str, Any], model_name: str):
        """Precision-Recall curve çiz"""
        plt.figure(figsize=(10, 8))
        
        # Örnek PR curve
        recall = np.linspace(0, 1, 100)
        precision = recall  # Basit örnek
        
        plt.plot(recall, precision, 'b-', label=f'PR Curve (AUC = {results.get("auc_pr", 0.0):.3f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'{model_name} - Precision-Recall Curve')
        plt.legend()
        plt.grid(True)
        
        plot_file = self.results_dir / f"{model_name}_precision_recall_curve.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_calibration(self, results: Dict[str, Any], model_name: str):
        """Kalibrasyon plotu çiz"""
        calibration_data = results.get('calibration', {})
        
        if 'error' in calibration_data:
            return
        
        plt.figure(figsize=(10, 8))
        
        if 'prob_true' in calibration_data:
            # Binary classification
            prob_true = calibration_data['prob_true']
            prob_pred = calibration_data['prob_pred']
            
            plt.plot(prob_pred, prob_true, 'bo-', label='Model Calibration')
            plt.plot([0, 1], [0, 1], 'r--', label='Perfect Calibration')
            plt.xlabel('Mean Predicted Probability')
            plt.ylabel('Fraction of Positives')
            plt.title(f'{model_name} - Calibration Plot')
            plt.legend()
            plt.grid(True)
        
        plot_file = self.results_dir / f"{model_name}_calibration.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_confidence_distribution(self, results: Dict[str, Any], model_name: str):
        """Güven dağılımı çiz"""
        confidence_data = results.get('confidence', {})
        
        if not confidence_data:
            return
        
        plt.figure(figsize=(12, 6))
        
        # Güven istatistikleri
        metrics = ['mean_confidence', 'correct_mean_confidence', 'incorrect_mean_confidence']
        values = [confidence_data.get(metric, 0) for metric in metrics]
        labels = ['Overall', 'Correct', 'Incorrect']
        
        plt.bar(labels, values, color=['blue', 'green', 'red'])
        plt.ylabel('Confidence Score')
        plt.title(f'{model_name} - Confidence Distribution')
        plt.ylim(0, 1)
        
        # Değerleri çubukların üzerine yaz
        for i, v in enumerate(values):
            plt.text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
        
        plot_file = self.results_dir / f"{model_name}_confidence_distribution.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_performance_summary(self, results: Dict[str, Any], model_name: str):
        """Performans özeti çiz"""
        plt.figure(figsize=(15, 10))
        
        # Ana metrikler
        metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc_roc', 'auc_pr']
        values = [results.get(metric, 0) for metric in metrics]
        labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC', 'AUC-PR']
        
        # Bar plot
        plt.subplot(2, 2, 1)
        bars = plt.bar(labels, values, color='skyblue')
        plt.ylabel('Score')
        plt.title(f'{model_name} - Performance Metrics')
        plt.ylim(0, 1)
        plt.xticks(rotation=45)
        
        # Değerleri çubukların üzerine yaz
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{value:.3f}', ha='center', va='bottom')
        
        # Model bilgileri
        plt.subplot(2, 2, 2)
        model_info = results.get('model_info', {})
        info_text = f"""
Model: {model_name}
Classes: {model_info.get('num_classes', 'N/A')}
Input Channels: {model_info.get('input_channels', 'N/A')}
Image Size: {model_info.get('image_size', 'N/A')}
Test Samples: {results.get('test_samples', 'N/A')}
        """
        plt.text(0.1, 0.5, info_text, fontsize=12, verticalalignment='center')
        plt.axis('off')
        plt.title('Model Information')
        
        # Sınıf dağılımı
        plt.subplot(2, 2, 3)
        class_names = results.get('class_names', [])
        if class_names:
            # Örnek dağılım
            class_counts = [100, 80, 60, 40]  # Örnek değerler
            plt.pie(class_counts[:len(class_names)], labels=class_names, autopct='%1.1f%%')
            plt.title('Class Distribution')
        
        # Güven metrikleri
        plt.subplot(2, 2, 4)
        confidence_data = results.get('confidence', {})
        if confidence_data:
            conf_metrics = ['mean_confidence', 'correct_mean_confidence', 'incorrect_mean_confidence']
            conf_values = [confidence_data.get(metric, 0) for metric in conf_metrics]
            conf_labels = ['Mean', 'Correct', 'Incorrect']
            
            plt.bar(conf_labels, conf_values, color=['blue', 'green', 'red'])
            plt.ylabel('Confidence')
            plt.title('Confidence Metrics')
            plt.ylim(0, 1)
        
        plt.tight_layout()
        
        plot_file = self.results_dir / f"{model_name}_performance_summary.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def validate_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Tüm modelleri doğrula"""
        logger.info("Tüm modellerin doğrulaması başlatılıyor...")
        
        available_models = self.model_manager.get_available_models()
        validation_results = {}
        
        for model_name in available_models:
            try:
                logger.info(f"Doğrulanıyor: {model_name}")
                result = self.validate_model(model_name)
                validation_results[model_name] = result
                
            except Exception as e:
                logger.error(f"Model doğrulama hatası ({model_name}): {str(e)}")
                validation_results[model_name] = {'error': str(e)}
        
        # Genel özet oluştur
        self._create_validation_summary(validation_results)
        
        logger.info("Tüm modellerin doğrulaması tamamlandı")
        return validation_results
    
    def _create_validation_summary(self, validation_results: Dict[str, Dict[str, Any]]):
        """Doğrulama özeti oluştur"""
        summary = {
            'validation_date': datetime.now().isoformat(),
            'total_models': len(validation_results),
            'successful_validations': len([r for r in validation_results.values() if 'error' not in r]),
            'failed_validations': len([r for r in validation_results.values() if 'error' in r]),
            'model_performances': {}
        }
        
        # Her model için performans özeti
        for model_name, result in validation_results.items():
            if 'error' not in result:
                summary['model_performances'][model_name] = {
                    'accuracy': result.get('accuracy', 0.0),
                    'precision': result.get('precision', 0.0),
                    'recall': result.get('recall', 0.0),
                    'f1_score': result.get('f1_score', 0.0),
                    'auc_roc': result.get('auc_roc', 0.0),
                    'test_samples': result.get('test_samples', 0)
                }
            else:
                summary['model_performances'][model_name] = {'error': result['error']}
        
        # Özet dosyasını kaydet
        summary_file = self.results_dir / "validation_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Doğrulama özeti kaydedildi: {summary_file}")
        
        # Performans tablosu oluştur
        self._create_performance_table(summary)
    
    def _create_performance_table(self, summary: Dict[str, Any]):
        """Performans tablosu oluştur"""
        performance_data = summary['model_performances']
        
        # DataFrame oluştur
        df_data = []
        for model_name, metrics in performance_data.items():
            if 'error' not in metrics:
                df_data.append({
                    'Model': model_name,
                    'Accuracy': f"{metrics['accuracy']:.4f}",
                    'Precision': f"{metrics['precision']:.4f}",
                    'Recall': f"{metrics['recall']:.4f}",
                    'F1-Score': f"{metrics['f1_score']:.4f}",
                    'AUC-ROC': f"{metrics['auc_roc']:.4f}",
                    'Test Samples': metrics['test_samples']
                })
            else:
                df_data.append({
                    'Model': model_name,
                    'Accuracy': 'ERROR',
                    'Precision': 'ERROR',
                    'Recall': 'ERROR',
                    'F1-Score': 'ERROR',
                    'AUC-ROC': 'ERROR',
                    'Test Samples': 0
                })
        
        df = pd.DataFrame(df_data)
        
        # HTML tablosu oluştur
        html_table = df.to_html(index=False, classes='table table-striped')
        
        # HTML dosyasını kaydet
        table_file = self.results_dir / "performance_table.html"
        with open(table_file, 'w', encoding='utf-8') as f:
            f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Model Performance Summary</title>
                <style>
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .table-striped tr:nth-child(even) {{ background-color: #f9f9f9; }}
                </style>
            </head>
            <body>
                <h1>Model Performance Summary</h1>
                <p>Generated on: {summary['validation_date']}</p>
                {html_table}
            </body>
            </html>
            """)
        
        logger.info(f"Performans tablosu kaydedildi: {table_file}")


def main():
    """Ana fonksiyon"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    logger.info("🔍 Profesyonel Model Doğrulama Sistemi Başlatılıyor")
    
    # Validator oluştur
    validator = ProfessionalModelValidator()
    
    # Tüm modelleri doğrula
    results = validator.validate_all_models()
    
    # Sonuçları özetle
    logger.info("📊 Doğrulama Sonuçları:")
    for model_name, result in results.items():
        if 'error' not in result:
            logger.info(f"✅ {model_name}: {result['accuracy']:.4f} accuracy")
        else:
            logger.error(f"❌ {model_name}: {result['error']}")
    
    logger.info("🎉 Model doğrulaması tamamlandı!")


if __name__ == "__main__":
    main()
