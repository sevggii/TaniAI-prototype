from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import datetime, timedelta
import logging

from .database import get_db, engine, Base
from .models import User, SymptomRecord, DiagnosisHistory, UserProfile
from .schemas import (
    UserCreate, UserResponse, SymptomInput, DiagnosisRequest, 
    DiagnosisResponse, UserProfileCreate, UserProfileResponse,
    NotificationRequest, RiskAssessmentRequest, RiskAssessmentResponse
)
from .services import (
    VitaminDiagnosisService, RiskAssessmentService, 
    NutritionRecommendationService, NotificationService
)
from .auth import create_access_token, verify_token, get_current_user

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI uygulaması
app = FastAPI(
    title="Vitamin Diagnosis System API",
    description="AI-powered vitamin deficiency diagnosis and recommendation system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da specific domain'ler kullanın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

# Servisler
diagnosis_service = VitaminDiagnosisService()
risk_service = RiskAssessmentService()
nutrition_service = NutritionRecommendationService()
notification_service = NotificationService()

@app.get("/")
async def root():
    """API ana endpoint"""
    return {
        "message": "Vitamin Diagnosis System API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "auth": "/auth",
            "diagnosis": "/diagnosis",
            "profile": "/profile",
            "history": "/history",
            "recommendations": "/recommendations",
            "notifications": "/notifications"
        }
    }

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Kullanıcı kaydı"""
    try:
        # Kullanıcı var mı kontrol et
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Yeni kullanıcı oluştur
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            age=user_data.age,
            gender=user_data.gender
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Access token oluştur
        access_token = create_access_token(data={"sub": str(db_user.id)})
        
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            age=db_user.age,
            gender=db_user.gender,
            access_token=access_token
        )
    except Exception as e:
        logger.error(f"User registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login", response_model=UserResponse)
async def login_user(email: str, db: Session = Depends(get_db)):
    """Kullanıcı girişi"""
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            age=user.age,
            gender=user.gender,
            access_token=access_token
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

# Diagnosis endpoints
@app.post("/diagnosis/analyze", response_model=DiagnosisResponse)
async def analyze_symptoms(
    diagnosis_request: DiagnosisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Belirtilere göre vitamin eksikliği analizi"""
    try:
        # Teşhis yap
        diagnosis_result = await diagnosis_service.analyze_symptoms(
            symptoms=diagnosis_request.symptoms,
            user_profile=diagnosis_request.user_profile
        )
        
        # Risk değerlendirmesi
        risk_assessment = await risk_service.assess_risk(
            diagnosis_result=diagnosis_result,
            user_profile=diagnosis_request.user_profile
        )
        
        # Beslenme önerileri
        nutrition_recommendations = await nutrition_service.get_recommendations(
            diagnosis_result=diagnosis_result,
            user_profile=diagnosis_request.user_profile
        )
        
        # Teşhis geçmişini kaydet
        background_tasks.add_task(
            save_diagnosis_history,
            user_id=current_user.id,
            diagnosis_result=diagnosis_result,
            db=db
        )
        
        # Yüksek risk durumunda bildirim planla
        if risk_assessment.overall_risk_level in ["Yüksek", "Kritik"]:
            background_tasks.add_task(
                schedule_urgent_notification,
                user_id=current_user.id,
                risk_level=risk_assessment.overall_risk_level
            )
        
        return DiagnosisResponse(
            diagnosis_result=diagnosis_result,
            risk_assessment=risk_assessment,
            nutrition_recommendations=nutrition_recommendations,
            clinical_warnings=[
                "Bu sonuçlar ön tanı niteliğindedir.",
                "Kesin teşhis için mutlaka doktor kontrolü gereklidir.",
                "Laboratuvar testleri ile doğrulama yapılmalıdır.",
                "Acil durumlarda derhal tıbbi yardım alın."
            ],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Diagnosis analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.get("/diagnosis/history", response_model=List[Dict[str, Any]])
async def get_diagnosis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının teşhis geçmişini getir"""
    try:
        history = db.query(DiagnosisHistory).filter(
            DiagnosisHistory.user_id == current_user.id
        ).order_by(DiagnosisHistory.created_at.desc()).limit(10).all()
        
        return [
            {
                "id": record.id,
                "nutrient": record.nutrient,
                "deficiency_probability": record.deficiency_probability,
                "risk_level": record.risk_level,
                "created_at": record.created_at.isoformat(),
                "symptoms_count": len(record.symptoms.split(",")) if record.symptoms else 0
            }
            for record in history
        ]
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")

# Profile endpoints
@app.post("/profile/update", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcı profilini güncelle"""
    try:
        # Mevcut profili bul veya oluştur
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()
        
        if not profile:
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
        
        # Profil bilgilerini güncelle
        profile.diet_type = profile_data.diet_type
        profile.activity_level = profile_data.activity_level
        profile.medical_conditions = profile_data.medical_conditions
        profile.medications = profile_data.medications
        profile.allergies = profile_data.allergies
        profile.smoking_status = profile_data.smoking_status
        profile.alcohol_consumption = profile_data.alcohol_consumption
        
        db.commit()
        db.refresh(profile)
        
        return UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            diet_type=profile.diet_type,
            activity_level=profile.activity_level,
            medical_conditions=profile.medical_conditions,
            medications=profile.medications,
            allergies=profile.allergies,
            smoking_status=profile.smoking_status,
            alcohol_consumption=profile.alcohol_consumption,
            updated_at=profile.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(status_code=500, detail="Profile update failed")

@app.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcı profilini getir"""
    try:
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            diet_type=profile.diet_type,
            activity_level=profile.activity_level,
            medical_conditions=profile.medical_conditions,
            medications=profile.medications,
            allergies=profile.allergies,
            smoking_status=profile.smoking_status,
            alcohol_consumption=profile.alcohol_consumption,
            updated_at=profile.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")

# Risk assessment endpoint
@app.post("/risk/assess", response_model=RiskAssessmentResponse)
async def assess_risk(
    risk_request: RiskAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kapsamlı risk değerlendirmesi"""
    try:
        # Kullanıcı profilini al
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()
        
        risk_assessment = await risk_service.comprehensive_risk_assessment(
            user_profile=profile,
            additional_factors=risk_request.additional_factors
        )
        
        return risk_assessment
        
    except Exception as e:
        logger.error(f"Risk assessment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Risk assessment failed")

# Notification endpoints
@app.post("/notifications/schedule")
async def schedule_notification(
    notification_request: NotificationRequest,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """Hatırlatma bildirimi planla"""
    try:
        await notification_service.schedule_notification(
            user_id=current_user.id,
            notification_type=notification_request.notification_type,
            scheduled_time=notification_request.scheduled_time,
            message=notification_request.message
        )
        
        return {"message": "Notification scheduled successfully"}
        
    except Exception as e:
        logger.error(f"Notification scheduling error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to schedule notification")

@app.get("/notifications")
async def get_notifications(
    current_user: User = Depends(get_current_user)
):
    """Kullanıcının bildirimlerini getir"""
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=current_user.id
        )
        return notifications
        
    except Exception as e:
        logger.error(f"Notification retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve notifications")

# Background tasks
async def save_diagnosis_history(user_id: int, diagnosis_result: Dict[str, Any], db: Session):
    """Teşhis geçmişini kaydet"""
    try:
        history_record = DiagnosisHistory(
            user_id=user_id,
            nutrient=diagnosis_result.get('nutrient', 'Unknown'),
            deficiency_probability=diagnosis_result.get('deficiency_probability', 0.0),
            risk_level=diagnosis_result.get('risk_level', 'Düşük'),
            symptoms=','.join(diagnosis_result.get('symptoms', [])),
            recommendations=diagnosis_result.get('recommendations', '')
        )
        db.add(history_record)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save diagnosis history: {str(e)}")

async def schedule_urgent_notification(user_id: int, risk_level: str):
    """Acil durum bildirimi planla"""
    try:
        await notification_service.schedule_urgent_notification(
            user_id=user_id,
            risk_level=risk_level
        )
    except Exception as e:
        logger.error(f"Failed to schedule urgent notification: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
