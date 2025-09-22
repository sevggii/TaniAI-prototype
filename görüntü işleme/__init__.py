"""
TanıAI Profesyonel Radyolojik Görüntü Analizi Modülü
===================================================

Bu modül profesyonel seviyede X-Ray, MR, Tomografi gibi radyolojik görüntülerin
otomatik analizi için geliştirilmiştir.

Özellikler:
- Profesyonel model eğitimi
- Gerçek tıbbi veri setleri
- Kapsamlı model doğrulama
- Otomatik pipeline
- Production-ready API
"""

# Profesyonel model sistemi
from .models.model_manager import ModelManager
from .models.data_manager import MedicalDatasetManager
from .models.model_validator import ProfessionalModelValidator
from .models.train_models import ProfessionalModelTrainer

# Temel bileşenler
from .models import RadiologyModels, ModelEnsemble
from .image_processor import ImageProcessor

# API sistemi
from .api import app

# Schemas
from .schemas import (
    RadiologyAnalysisRequest,
    RadiologyAnalysisResult,
    ImageMetadata,
    ImageType,
    BodyRegion,
    SeverityLevel,
    RiskLevel
)

__version__ = "2.0.0"
__author__ = "Dr. AI Research Team"

__all__ = [
    "ModelManager",
    "MedicalDatasetManager", 
    "ProfessionalModelValidator",
    "ProfessionalModelTrainer",
    "RadiologyModels",
    "ModelEnsemble",
    "ImageProcessor",
    "app",
    "RadiologyAnalysisRequest",
    "RadiologyAnalysisResult",
    "ImageMetadata",
    "ImageType",
    "BodyRegion",
    "SeverityLevel",
    "RiskLevel"
]
