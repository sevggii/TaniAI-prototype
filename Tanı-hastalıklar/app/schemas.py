from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Enums
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class DietType(str, Enum):
    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"
    LOW_CARB = "low_carb"
    OTHER = "other"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class SmokingStatus(str, Enum):
    NEVER = "never"
    FORMER = "former"
    CURRENT = "current"

class AlcoholConsumption(str, Enum):
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"

class RiskLevel(str, Enum):
    LOW = "Düşük"
    MEDIUM = "Orta"
    HIGH = "Yüksek"
    CRITICAL = "Kritik"

class NotificationType(str, Enum):
    REMINDER = "reminder"
    URGENT = "urgent"
    FOLLOW_UP = "follow_up"
    TIP = "tip"
    TEST_RESULT = "test_result"

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=1, le=120)
    gender: Gender

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    age: int
    gender: str
    access_token: Optional[str] = None
    
    class Config:
        from_attributes = True

# User Profile schemas
class UserProfileCreate(BaseModel):
    diet_type: Optional[DietType] = None
    activity_level: Optional[ActivityLevel] = None
    medical_conditions: Optional[List[str]] = []
    medications: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    smoking_status: Optional[SmokingStatus] = None
    alcohol_consumption: Optional[AlcoholConsumption] = None
    is_pregnant: Optional[bool] = False
    pregnancy_week: Optional[int] = Field(None, ge=1, le=42)
    family_history: Optional[List[str]] = []
    environmental_factors: Optional[Dict[str, Any]] = {}

class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    diet_type: Optional[str] = None
    activity_level: Optional[str] = None
    medical_conditions: Optional[List[str]] = []
    medications: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    smoking_status: Optional[str] = None
    alcohol_consumption: Optional[str] = None
    is_pregnant: Optional[bool] = False
    pregnancy_week: Optional[int] = None
    family_history: Optional[List[str]] = []
    environmental_factors: Optional[Dict[str, Any]] = {}
    updated_at: str
    
    class Config:
        from_attributes = True

# Symptom schemas
class SymptomInput(BaseModel):
    symptom_name: str
    severity: int = Field(..., ge=0, le=3, description="0: Yok, 1: Hafif, 2: Orta, 3: Şiddetli")
    duration_days: Optional[int] = Field(None, ge=1, description="Belirtinin süresi (gün)")

class SymptomRecordCreate(BaseModel):
    symptoms: List[SymptomInput]
    symptom_duration: str = Field(..., description="acute, chronic, recurring")
    severity_level: str = Field(..., description="mild, moderate, severe")
    notes: Optional[str] = None

# Diagnosis schemas
class DiagnosisRequest(BaseModel):
    symptoms: List[SymptomInput]
    user_profile: Optional[UserProfileCreate] = None
    additional_notes: Optional[str] = None

class DiagnosisResult(BaseModel):
    nutrient: str
    deficiency_probability: float = Field(..., ge=0.0, le=1.0)
    prediction: int = Field(..., ge=0, le=1)
    risk_level: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    symptoms_analyzed: List[str]
    key_indicators: List[str]

class RiskAssessment(BaseModel):
    overall_risk_level: str
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_factors: Dict[str, float]
    lifestyle_factors: Dict[str, Any]
    recommendations: List[str]
    urgent_actions: List[str]

class NutritionRecommendations(BaseModel):
    dietary_recommendations: List[str]
    supplement_recommendations: List[str]
    meal_plan_suggestions: List[Dict[str, Any]]
    foods_to_avoid: List[str]
    foods_to_include: List[str]
    daily_intake_goals: Dict[str, str]

class DiagnosisResponse(BaseModel):
    diagnosis_result: DiagnosisResult
    risk_assessment: RiskAssessment
    nutrition_recommendations: NutritionRecommendations
    clinical_warnings: List[str]
    timestamp: str

# Risk Assessment schemas
class RiskAssessmentRequest(BaseModel):
    additional_factors: Optional[Dict[str, Any]] = {}
    include_family_history: bool = True
    include_environmental: bool = True

class RiskAssessmentResponse(BaseModel):
    overall_risk_level: str
    risk_score: float
    detailed_analysis: Dict[str, Any]
    risk_factors: Dict[str, float]
    recommendations: List[str]
    monitoring_plan: Dict[str, Any]
    next_assessment_date: Optional[str] = None

# Notification schemas
class NotificationRequest(BaseModel):
    notification_type: NotificationType
    scheduled_time: datetime
    message: str
    priority: str = "normal"
    action_required: bool = False

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    priority: str
    scheduled_time: str
    is_sent: bool
    is_read: bool
    action_required: bool
    action_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# Lab Test schemas
class LabTestRecommendation(BaseModel):
    test_name: str
    test_type: str
    priority: str
    description: str
    preparation_instructions: Optional[str] = None
    normal_ranges: Optional[Dict[str, Any]] = None
    recommended_date: Optional[str] = None

class LabTestResult(BaseModel):
    test_id: int
    results: Dict[str, Any]
    interpretation: str
    recommendations: List[str]
    follow_up_required: bool

# Nutrition Plan schemas
class NutritionPlanCreate(BaseModel):
    plan_name: str
    target_nutrients: List[str]
    plan_type: str = "deficiency_correction"
    duration_weeks: int = Field(4, ge=1, le=52)

class NutritionPlanResponse(BaseModel):
    id: int
    plan_name: str
    target_nutrients: List[str]
    plan_type: str
    daily_meals: Dict[str, Any]
    food_recommendations: List[str]
    supplement_recommendations: List[str]
    duration_weeks: int
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True

# Statistics and Analytics schemas
class UserStatistics(BaseModel):
    total_diagnoses: int
    high_risk_diagnoses: int
    most_common_deficiencies: List[Dict[str, Any]]
    improvement_trend: str
    last_assessment_date: Optional[str] = None

class SystemAnalytics(BaseModel):
    total_users: int
    total_diagnoses: int
    most_common_symptoms: List[Dict[str, Any]]
    risk_distribution: Dict[str, int]
    success_rate: float

# Error schemas
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Success schemas
class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
