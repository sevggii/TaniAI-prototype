"""
TCIA Gerçek Verilerle Model Eğitimi
===================================

TCIA'dan indirilen gerçek tıbbi verilerle radyolojik modelleri eğitmek için
geliştirilmiş profesyonel eğitim sistemi.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
import numpy as np
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
from torchvision import transforms
from PIL import Image
import cv2
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Custom imports
from models.radiology_models import RadiologyCNN, DenseNetRadiology, ResNetRadiology
from models.model_manager import ModelManager
from dicom_processor import DICOMProcessor

logger = logging.getLogger(__name__)


class TCIAImageDataset(Dataset):
    """TCIA görüntü veri seti"""
    
    def __init__(self, image_paths: List[str], labels: List[int], transform=None, 
                 is_training: bool = True):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
        self.is_training = is_training
        
        # Sınıf isimleri
        self.class_names = {
            0: "Normal",
            1: "Lung_Cancer",
            2: "Breast_Cancer", 
            3: "Brain_Tumor"
        }
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        label = self.labels[idx]
        
        # Görüntüyü yükle
        try:
            image = Image.open(image_path).convert('L')  # Grayscale
            image = np.array(image)
            
            # Görüntü kalitesini kontrol et
            if self._is_valid_image(image):
                # Transform uygula
                if self.transform:
                    image = self.transform(image)
                else:
                    # Default transform
                    image = torch.FloatTensor(image).unsqueeze(0)
                
                return image, label
            else:
                # Geçersiz görüntü için random görüntü döndür
                return self._get_random_valid_image()
                
        except Exception as e:
            logger.warning(f"Görüntü yükleme hatası ({image_path}): {str(e)}")
            return self._get_random_valid_image()
    
    def _is_valid_image(self, image: np.ndarray) -> bool:
        """Görüntü kalitesini kontrol et"""
        if image is None or image.size == 0:
            return False
        
        # Boş görüntü kontrolü
        if np.sum(image) == 0:
            return False
        
        # Kontrast kontrolü
        if np.std(image) < 10:
            return False
        
        return True
    
    def _get_random_valid_image(self):
        """Geçerli random görüntü döndür"""
        random_idx = np.random.randint(0, len(self.image_paths))
        return self.__getitem__(random_idx)


class TCIAImageTransforms:
    """TCIA görüntüleri için transform'lar"""
    
    @staticmethod
    def get_training_transforms():
        """Eğitim için transform'lar"""
        return transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((512, 512)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=10),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])
    
    @staticmethod
    def get_validation_transforms():
        """Validasyon için transform'lar"""
        return transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])


class TCIAModelTrainer:
    """TCIA verileri ile model eğitimi"""
    
    def __init__(self, data_dir: str = "training_dataset", models_dir: str = "models"):
        self.data_dir = Path(data_dir)
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Device: {self.device}")
        
        # Model konfigürasyonları
        self.model_configs = {
            'lung_cancer_detection': {
                'model_class': DenseNetRadiology,
                'num_classes': 2,
                'input_channels': 1,
                'image_size': (512, 512),
                'class_names': ['Normal', 'Lung_Cancer']
            },
            'breast_cancer_detection': {
                'model_class': ResNetRadiology,
                'num_classes': 2,
                'input_channels': 1,
                'image_size': (512, 512),
                'class_names': ['Normal', 'Breast_Cancer']
            },
            'brain_tumor_detection': {
                'model_class': RadiologyCNN,
                'num_classes': 2,
                'input_channels': 1,
                'image_size': (512, 512),
                'class_names': ['Normal', 'Brain_Tumor']
            },
            'multi_class_classification': {
                'model_class': DenseNetRadiology,
                'num_classes': 4,
                'input_channels': 1,
                'image_size': (512, 512),
                'class_names': ['Normal', 'Lung_Cancer', 'Breast_Cancer', 'Brain_Tumor']
            }
        }
        
        # Eğitim parametreleri
        self.training_params = {
            'batch_size': 16,
            'num_epochs': 50,
            'learning_rate': 0.001,
            'weight_decay': 1e-4,
            'patience': 10,  # Early stopping
            'scheduler_step': 15
        }
    
    def load_dataset(self) -> Tuple[List[str], List[int], Dict[str, Any]]:
        """Veri setini yükle"""
        try:
            logger.info("Veri seti yükleniyor...")
            
            # Sınıf klasörlerini bul
            train_dir = self.data_dir / "train"
            val_dir = self.data_dir / "val"
            test_dir = self.data_dir / "test"
            
            if not all([train_dir.exists(), val_dir.exists(), test_dir.exists()]):
                raise ValueError("Veri seti klasörleri bulunamadı. Önce DICOM işleme yapın.")
            
            # Görüntü yollarını ve etiketleri topla
            all_images = []
            all_labels = []
            class_mapping = {}
            
            # Sınıf mapping'i oluştur
            class_dirs = [d for d in train_dir.iterdir() if d.is_dir()]
            for i, class_dir in enumerate(sorted(class_dirs)):
                class_name = class_dir.name
                class_mapping[class_name] = i
                logger.info(f"Sınıf {i}: {class_name}")
            
            # Train verilerini yükle
            train_images, train_labels = self._load_class_images(train_dir, class_mapping)
            val_images, val_labels = self._load_class_images(val_dir, class_mapping)
            test_images, test_labels = self._load_class_images(test_dir, class_mapping)
            
            dataset_info = {
                'train_size': len(train_images),
                'val_size': len(val_images),
                'test_size': len(test_images),
                'num_classes': len(class_mapping),
                'class_mapping': class_mapping,
                'class_names': list(class_mapping.keys())
            }
            
            logger.info(f"Veri seti yüklendi: Train={len(train_images)}, Val={len(val_images)}, Test={len(test_images)}")
            
            return {
                'train': (train_images, train_labels),
                'val': (val_images, val_labels),
                'test': (test_images, test_labels)
            }, dataset_info
            
        except Exception as e:
            logger.error(f"Veri seti yükleme hatası: {str(e)}")
            raise
    
    def _load_class_images(self, data_dir: Path, class_mapping: Dict[str, int]) -> Tuple[List[str], List[int]]:
        """Sınıf görüntülerini yükle"""
        images = []
        labels = []
        
        for class_name, class_id in class_mapping.items():
            class_dir = data_dir / class_name
            if class_dir.exists():
                image_files = list(class_dir.glob("*.png")) + list(class_dir.glob("*.jpg"))
                for img_file in image_files:
                    images.append(str(img_file))
                    labels.append(class_id)
        
        return images, labels
    
    def create_data_loaders(self, dataset_info: Dict[str, Any]) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Data loader'ları oluştur"""
        try:
            # Transform'ları al
            train_transform = TCIAImageTransforms.get_training_transforms()
            val_transform = TCIAImageTransforms.get_validation_transforms()
            
            # Veri setlerini yükle
            datasets, info = self.load_dataset()
            
            # Dataset'leri oluştur
            train_dataset = TCIAImageDataset(
                datasets['train'][0], datasets['train'][1], 
                transform=train_transform, is_training=True
            )
            val_dataset = TCIAImageDataset(
                datasets['val'][0], datasets['val'][1],
                transform=val_transform, is_training=False
            )
            test_dataset = TCIAImageDataset(
                datasets['test'][0], datasets['test'][1],
                transform=val_transform, is_training=False
            )
            
            # Class weights hesapla (imbalanced data için)
            train_labels = np.array(datasets['train'][1])
            class_counts = np.bincount(train_labels)
            class_weights = 1.0 / class_counts
            class_weights = class_weights / class_weights.sum() * len(class_weights)
            
            # Weighted sampler
            sample_weights = [class_weights[label] for label in train_labels]
            sampler = WeightedRandomSampler(
                weights=sample_weights,
                num_samples=len(train_dataset),
                replacement=True
            )
            
            # Data loader'ları oluştur
            train_loader = DataLoader(
                train_dataset,
                batch_size=self.training_params['batch_size'],
                sampler=sampler,
                num_workers=4,
                pin_memory=True
            )
            
            val_loader = DataLoader(
                val_dataset,
                batch_size=self.training_params['batch_size'],
                shuffle=False,
                num_workers=4,
                pin_memory=True
            )
            
            test_loader = DataLoader(
                test_dataset,
                batch_size=self.training_params['batch_size'],
                shuffle=False,
                num_workers=4,
                pin_memory=True
            )
            
            logger.info("Data loader'lar oluşturuldu")
            return train_loader, val_loader, test_loader
            
        except Exception as e:
            logger.error(f"Data loader oluşturma hatası: {str(e)}")
            raise
    
    def train_model(self, model_name: str, train_loader: DataLoader, val_loader: DataLoader) -> nn.Module:
        """Model eğit"""
        try:
            logger.info(f"Model eğitimi başlıyor: {model_name}")
            
            # Model konfigürasyonunu al
            config = self.model_configs[model_name]
            
            # Model oluştur
            model = config['model_class'](
                num_classes=config['num_classes'],
                input_channels=config['input_channels']
            ).to(self.device)
            
            # Loss ve optimizer
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(
                model.parameters(),
                lr=self.training_params['learning_rate'],
                weight_decay=self.training_params['weight_decay']
            )
            
            # Scheduler
            scheduler = optim.lr_scheduler.StepLR(
                optimizer,
                step_size=self.training_params['scheduler_step'],
                gamma=0.1
            )
            
            # Eğitim geçmişi
            train_history = {
                'train_loss': [],
                'train_acc': [],
                'val_loss': [],
                'val_acc': []
            }
            
            best_val_acc = 0.0
            patience_counter = 0
            
            # Eğitim döngüsü
            for epoch in range(self.training_params['num_epochs']):
                # Train
                train_loss, train_acc = self._train_epoch(model, train_loader, criterion, optimizer)
                
                # Validation
                val_loss, val_acc = self._validate_epoch(model, val_loader, criterion)
                
                # Geçmişi güncelle
                train_history['train_loss'].append(train_loss)
                train_history['train_acc'].append(train_acc)
                train_history['val_loss'].append(val_loss)
                train_history['val_acc'].append(val_acc)
                
                # Scheduler step
                scheduler.step()
                
                # Log
                logger.info(
                    f"Epoch {epoch+1}/{self.training_params['num_epochs']}: "
                    f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, "
                    f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}"
                )
                
                # Best model kaydet
                if val_acc > best_val_acc:
                    best_val_acc = val_acc
                    patience_counter = 0
                    
                    # Model kaydet
                    model_path = self.models_dir / f"{model_name}_best.pth"
                    torch.save({
                        'model_state_dict': model.state_dict(),
                        'model_config': config,
                        'val_acc': val_acc,
                        'epoch': epoch,
                        'train_history': train_history
                    }, model_path)
                    
                    logger.info(f"Yeni en iyi model kaydedildi: {val_acc:.4f}")
                else:
                    patience_counter += 1
                
                # Early stopping
                if patience_counter >= self.training_params['patience']:
                    logger.info(f"Early stopping: {patience_counter} epoch iyileşme yok")
                    break
            
            # Eğitim geçmişini kaydet
            history_path = self.models_dir / f"{model_name}_history.json"
            with open(history_path, 'w') as f:
                json.dump(train_history, f, indent=2)
            
            logger.info(f"Model eğitimi tamamlandı: {model_name}")
            return model
            
        except Exception as e:
            logger.error(f"Model eğitimi hatası ({model_name}): {str(e)}")
            raise
    
    def _train_epoch(self, model: nn.Module, train_loader: DataLoader, 
                     criterion: nn.Module, optimizer: optim.Optimizer) -> Tuple[float, float]:
        """Bir epoch eğit"""
        model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(tqdm(train_loader, desc="Training")):
            data, target = data.to(self.device), target.to(self.device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += target.size(0)
        
        avg_loss = total_loss / len(train_loader)
        accuracy = 100.0 * correct / total
        
        return avg_loss, accuracy
    
    def _validate_epoch(self, model: nn.Module, val_loader: DataLoader, 
                        criterion: nn.Module) -> Tuple[float, float]:
        """Bir epoch validate et"""
        model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in tqdm(val_loader, desc="Validation"):
                data, target = data.to(self.device), target.to(self.device)
                output = model(data)
                loss = criterion(output, target)
                
                total_loss += loss.item()
                pred = output.argmax(dim=1)
                correct += pred.eq(target).sum().item()
                total += target.size(0)
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100.0 * correct / total
        
        return avg_loss, accuracy
    
    def evaluate_model(self, model: nn.Module, test_loader: DataLoader, 
                       class_names: List[str]) -> Dict[str, Any]:
        """Model değerlendirmesi"""
        try:
            model.eval()
            all_preds = []
            all_targets = []
            all_probs = []
            
            with torch.no_grad():
                for data, target in tqdm(test_loader, desc="Testing"):
                    data, target = data.to(self.device), target.to(self.device)
                    output = model(data)
                    probs = torch.softmax(output, dim=1)
                    
                    pred = output.argmax(dim=1)
                    all_preds.extend(pred.cpu().numpy())
                    all_targets.extend(target.cpu().numpy())
                    all_probs.extend(probs.cpu().numpy())
            
            # Metrikleri hesapla
            accuracy = 100.0 * sum(p == t for p, t in zip(all_preds, all_targets)) / len(all_targets)
            
            # Classification report
            report = classification_report(
                all_targets, all_preds, 
                target_names=class_names,
                output_dict=True
            )
            
            # Confusion matrix
            cm = confusion_matrix(all_targets, all_preds)
            
            # ROC AUC (multi-class için)
            try:
                auc = roc_auc_score(all_targets, all_probs, multi_class='ovr')
            except:
                auc = 0.0
            
            results = {
                'accuracy': accuracy,
                'classification_report': report,
                'confusion_matrix': cm.tolist(),
                'roc_auc': auc,
                'class_names': class_names
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Model değerlendirme hatası: {str(e)}")
            raise
    
    def plot_training_history(self, model_name: str):
        """Eğitim geçmişini çiz"""
        try:
            history_path = self.models_dir / f"{model_name}_history.json"
            if not history_path.exists():
                logger.warning(f"Geçmiş dosyası bulunamadı: {history_path}")
                return
            
            with open(history_path, 'r') as f:
                history = json.load(f)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            
            # Loss plot
            ax1.plot(history['train_loss'], label='Train Loss')
            ax1.plot(history['val_loss'], label='Validation Loss')
            ax1.set_title(f'{model_name} - Loss')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Loss')
            ax1.legend()
            ax1.grid(True)
            
            # Accuracy plot
            ax2.plot(history['train_acc'], label='Train Accuracy')
            ax2.plot(history['val_acc'], label='Validation Accuracy')
            ax2.set_title(f'{model_name} - Accuracy')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Accuracy (%)')
            ax2.legend()
            ax2.grid(True)
            
            plt.tight_layout()
            
            # Kaydet
            plot_path = self.models_dir / f"{model_name}_training_plot.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Eğitim grafiği kaydedildi: {plot_path}")
            
        except Exception as e:
            logger.error(f"Grafik çizme hatası: {str(e)}")
    
    def train_all_models(self):
        """Tüm modelleri eğit"""
        try:
            logger.info("Tüm modellerin eğitimi başlıyor...")
            
            # Data loader'ları oluştur
            train_loader, val_loader, test_loader = self.create_data_loaders({})
            
            # Her model için eğitim
            trained_models = {}
            evaluation_results = {}
            
            for model_name in self.model_configs.keys():
                try:
                    logger.info(f"Model eğitimi: {model_name}")
                    
                    # Model eğit
                    model = self.train_model(model_name, train_loader, val_loader)
                    trained_models[model_name] = model
                    
                    # Eğitim geçmişini çiz
                    self.plot_training_history(model_name)
                    
                    # Model değerlendirmesi
                    class_names = self.model_configs[model_name]['class_names']
                    results = self.evaluate_model(model, test_loader, class_names)
                    evaluation_results[model_name] = results
                    
                    logger.info(f"Model tamamlandı: {model_name} - Accuracy: {results['accuracy']:.2f}%")
                    
                except Exception as e:
                    logger.error(f"Model eğitimi hatası ({model_name}): {str(e)}")
                    continue
            
            # Genel sonuçları kaydet
            final_results = {
                'trained_models': list(trained_models.keys()),
                'evaluation_results': evaluation_results,
                'training_completed_at': datetime.now().isoformat()
            }
            
            results_path = self.models_dir / "training_results.json"
            with open(results_path, 'w') as f:
                json.dump(final_results, f, indent=2)
            
            logger.info("Tüm model eğitimleri tamamlandı!")
            return trained_models, evaluation_results
            
        except Exception as e:
            logger.error(f"Genel eğitim hatası: {str(e)}")
            raise


def main():
    """Ana fonksiyon"""
    logging.basicConfig(level=logging.INFO)
    
    # Trainer oluştur
    trainer = TCIAModelTrainer()
    
    # Eğitim başlat
    try:
        models, results = trainer.train_all_models()
        
        print("\n🏆 Eğitim Sonuçları:")
        for model_name, result in results.items():
            print(f"  • {model_name}: {result['accuracy']:.2f}% accuracy")
        
    except Exception as e:
        print(f"❌ Eğitim hatası: {str(e)}")


if __name__ == "__main__":
    main()
