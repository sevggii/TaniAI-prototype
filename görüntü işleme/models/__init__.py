"""
Model Yönetim Sistemi
=====================

Bu modül eğitilmiş modellerin yüklenmesi, yönetimi ve
performans takibi için gerekli sınıfları içerir.
"""

# Basit modellerden import et (bağımlılık olmadan)
import sys
from pathlib import Path

# Üst dizindeki simple_models.py'den import et
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from simple_models import (
        SimpleRadiologyCNN as RadiologyCNN,
        SimpleDenseNetRadiology as DenseNetRadiology,
        SimpleResNetRadiology as ResNetRadiology,
        SimpleRadiologyModels as RadiologyModels,
        SimpleModelEnsemble as ModelEnsemble
    )
except ImportError:
    # Fallback: None olarak tanımla
    RadiologyCNN = None
    DenseNetRadiology = None
    ResNetRadiology = None
    RadiologyModels = None
    ModelEnsemble = None

from .model_manager import ModelManager
from .model_loader import ModelLoader

__all__ = [
    'ModelManager',
    'ModelLoader',
    'RadiologyCNN',
    'DenseNetRadiology', 
    'ResNetRadiology',
    'RadiologyModels',
    'ModelEnsemble'
]
