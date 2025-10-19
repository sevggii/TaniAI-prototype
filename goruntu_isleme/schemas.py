"""
Radyolojik Görüntü Analizi için Pydantic Şemaları
================================================

Bu modül radyolojik görüntü analizi için gerekli veri yapılarını
ve doğrulama şemalarını içerir.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import base64


class ImageType(str, Enum):
    """Desteklenen görüntü tipleri"""
    XRAY = "xray"
    MRI = "mri"
    CT = "ct"
    ULTRASOUND = "ultrasound"
    MAMMOGRAPHY = "mammography"
    PET = "pet"
    SPECT = "spect"


class BodyRegion(str, Enum):
    """Vücut bölgeleri"""
    CHEST = "chest"
    ABDOMEN = "abdomen"
    HEAD = "head"
    SPINE = "spine"
    PELVIS = "pelvis"
    EXTREMITIES = "extremities"
    BREAST = "breast"
    HEART = "heart"
    LUNGS = "lungs"
    BRAIN = "brain"
    LIVER = "liver"
    KIDNEYS = "kidneys"


class SeverityLevel(str, Enum):
    """Şiddet seviyeleri"""
    NORMAL = "normal"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    """Risk seviyeleri"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImageMetadata(BaseModel):
    """Görüntü metadata bilgileri"""
    image_type: ImageType
    body_region: BodyRegion
    patient_age: Optional[int] = Field(None, ge=0, le=120)
    patient_gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    study_date: Optional[datetime] = None
    study_description: Optional[str] = None
    modality: Optional[str] = None
    image_size: Optional[Dict[str, int]] = None
    resolution: Optional[Dict[str, float]] = None
    contrast_used: Optional[bool] = False
    radiation_dose: Optional[float] = Field(None, ge=0)
    
    @validator('patient_age')
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 120):
            raise ValueError('Yaş 0-120 arasında olmalıdır')
        return v


class CriticalFinding(BaseModel):
    """Kritik bulgu bilgileri"""
    finding_id: str
    finding_name: str
    description: str
    severity: SeverityLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    location: Optional[Dict[str, Any]] = None
    measurements: Optional[Dict[str, float]] = None
    recommendations: List[str] = []
    urgency_level: RiskLevel
    follow_up_required: bool = True
    specialist_referral: Optional[str] = None
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Güven skoru 0.0-1.0 arasında olmalıdır')
        return v


class RiskScore(BaseModel):
    """Risk skoru bilgileri"""
    overall_risk: RiskLevel
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_factors: List[str] = []
    risk_breakdown: Dict[str, float] = {}
    recommendations: List[str] = []
    follow_up_timeframe: Optional[str] = None
    
    @validator('risk_score')
    def validate_risk_score(cls, v):
        if not 0.0 <= v <= 100.0:
            raise ValueError('Risk skoru 0.0-100.0 arasında olmalıdır')
        return v


class ImageAnalysisResult(BaseModel):
    """Görüntü analiz sonucu"""
    analysis_id: str
    image_id: str
    analysis_timestamp: datetime
    processing_time: float
    image_quality_score: float = Field(..., ge=0.0, le=1.0)
    findings: List[CriticalFinding] = []
    risk_assessment: RiskScore
    technical_notes: List[str] = []
    limitations: List[str] = []
    confidence_overall: float = Field(..., ge=0.0, le=1.0)


class RadiologyAnalysisRequest(BaseModel):
    """Radyolojik analiz isteği"""
    image_data: str = Field(..., description="Base64 encoded görüntü verisi")
    image_metadata: ImageMetadata
    analysis_options: Optional[Dict[str, Any]] = {}
    priority: Optional[str] = Field("normal", pattern="^(low|normal|high|urgent)$")
    request_id: Optional[str] = None
    patient_id: Optional[str] = None
    
    @validator('image_data')
    def validate_image_data(cls, v):
        try:
            # Base64 decode test
            base64.b64decode(v)
            return v
        except Exception:
            raise ValueError('Geçersiz base64 görüntü verisi')
    
    class Config:
        schema_extra = {
            "example": {
                "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                "image_metadata": {
                    "image_type": "xray",
                    "body_region": "chest",
                    "patient_age": 45,
                    "patient_gender": "male",
                    "study_date": "2024-01-15T10:30:00Z"
                },
                "analysis_options": {
                    "detect_pneumonia": True,
                    "detect_fractures": True,
                    "detect_tumors": False
                },
                "priority": "normal"
            }
        }


class RadiologyAnalysisResult(BaseModel):
    """Radyolojik analiz sonucu"""
    request_id: str
    analysis_result: ImageAnalysisResult
    processing_status: str = Field(..., pattern="^(completed|failed|processing)$")
    error_message: Optional[str] = None
    recommendations: List[str] = []
    next_steps: List[str] = []
    report_generated: bool = False
    report_url: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "req_12345",
                "analysis_result": {
                    "analysis_id": "ana_67890",
                    "image_id": "img_11111",
                    "analysis_timestamp": "2024-01-15T10:35:00Z",
                    "processing_time": 2.5,
                    "image_quality_score": 0.85,
                    "findings": [
                        {
                            "finding_id": "find_001",
                            "finding_name": "Pneumonia",
                            "description": "Bilateral lower lobe consolidation",
                            "severity": "moderate",
                            "confidence": 0.87,
                            "urgency_level": "high",
                            "follow_up_required": True,
                            "specialist_referral": "Pulmonology"
                        }
                    ],
                    "risk_assessment": {
                        "overall_risk": "high",
                        "risk_score": 75.5,
                        "risk_factors": ["Age > 65", "Bilateral involvement"],
                        "recommendations": ["Immediate antibiotic therapy", "Chest X-ray follow-up"]
                    },
                    "confidence_overall": 0.82
                },
                "processing_status": "completed",
                "recommendations": [
                    "Immediate medical attention required",
                    "Antibiotic therapy recommended",
                    "Follow-up imaging in 48-72 hours"
                ],
                "next_steps": [
                    "Schedule pulmonology consultation",
                    "Start empirical antibiotic therapy",
                    "Monitor vital signs closely"
                ]
            }
        }


class BatchAnalysisRequest(BaseModel):
    """Toplu analiz isteği"""
    images: List[RadiologyAnalysisRequest]
    batch_id: str
    priority: Optional[str] = Field("normal", pattern="^(low|normal|high|urgent)$")
    callback_url: Optional[str] = None
    
    @validator('images')
    def validate_images_count(cls, v):
        if len(v) > 50:
            raise ValueError('Maksimum 50 görüntü analiz edilebilir')
        return v


class BatchAnalysisResult(BaseModel):
    """Toplu analiz sonucu"""
    batch_id: str
    total_images: int
    completed_analyses: int
    failed_analyses: int
    results: List[RadiologyAnalysisResult]
    batch_status: str = Field(..., pattern="^(completed|processing|failed|partial)$")
    processing_time: float
    created_at: datetime
    completed_at: Optional[datetime] = None


class ModelPerformanceMetrics(BaseModel):
    """Model performans metrikleri"""
    model_name: str
    accuracy: float = Field(..., ge=0.0, le=1.0)
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1_score: float = Field(..., ge=0.0, le=1.0)
    auc_roc: float = Field(..., ge=0.0, le=1.0)
    last_updated: datetime
    training_samples: int
    validation_samples: int


class SystemHealthStatus(BaseModel):
    """Sistem sağlık durumu"""
    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    models_loaded: int
    total_models: int
    active_connections: int
    queue_size: int
    average_processing_time: float
    last_health_check: datetime
    issues: List[str] = []
