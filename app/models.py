from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    """Kullanıcı modeli"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)  # 'male', 'female', 'other'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    diagnosis_history = relationship("DiagnosisHistory", back_populates="user")
    symptom_records = relationship("SymptomRecord", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class UserProfile(Base):
    """Kullanıcı profil modeli - detaylı sağlık bilgileri"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Beslenme ve yaşam tarzı
    diet_type = Column(String)  # 'omnivore', 'vegetarian', 'vegan', 'keto', etc.
    activity_level = Column(String)  # 'sedentary', 'light', 'moderate', 'active', 'very_active'
    
    # Sağlık durumu
    medical_conditions = Column(JSON)  # List of medical conditions
    medications = Column(JSON)  # List of current medications
    allergies = Column(JSON)  # List of allergies
    
    # Yaşam tarzı faktörleri
    smoking_status = Column(String)  # 'never', 'former', 'current'
    alcohol_consumption = Column(String)  # 'none', 'light', 'moderate', 'heavy'
    
    # Gebelik durumu (kadınlar için)
    is_pregnant = Column(Boolean, default=False)
    pregnancy_week = Column(Integer, nullable=True)
    
    # Risk faktörleri
    family_history = Column(JSON)  # Family medical history
    environmental_factors = Column(JSON)  # Sun exposure, pollution, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    user = relationship("User", back_populates="profile")

class SymptomRecord(Base):
    """Belirti kayıtları"""
    __tablename__ = "symptom_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Belirti bilgileri
    symptoms = Column(JSON)  # Dictionary of symptoms and severity levels
    symptom_duration = Column(String)  # 'acute', 'chronic', 'recurring'
    severity_level = Column(String)  # 'mild', 'moderate', 'severe'
    
    # Ek bilgiler
    notes = Column(Text)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    user = relationship("User", back_populates="symptom_records")

class DiagnosisHistory(Base):
    """Teşhis geçmişi"""
    __tablename__ = "diagnosis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Teşhis bilgileri
    nutrient = Column(String, nullable=False)  # Vitamin/mineral name
    deficiency_probability = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)  # 'Düşük', 'Orta', 'Yüksek', 'Kritik'
    confidence_score = Column(Float)
    
    # Belirti ve öneriler
    symptoms = Column(Text)  # Comma-separated symptoms
    recommendations = Column(Text)  # JSON string of recommendations
    
    # Risk değerlendirmesi
    risk_factors = Column(JSON)  # Identified risk factors
    lifestyle_factors = Column(JSON)  # Lifestyle-related factors
    
    # Takip bilgileri
    follow_up_recommended = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    user = relationship("User", back_populates="diagnosis_history")

class NutritionPlan(Base):
    """Kişiselleştirilmiş beslenme planları"""
    __tablename__ = "nutrition_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Plan bilgileri
    plan_name = Column(String, nullable=False)
    target_nutrients = Column(JSON)  # List of nutrients to focus on
    plan_type = Column(String)  # 'deficiency_correction', 'maintenance', 'prevention'
    
    # Beslenme önerileri
    daily_meals = Column(JSON)  # Detailed meal plans
    food_recommendations = Column(JSON)  # Specific food suggestions
    supplement_recommendations = Column(JSON)  # Supplement suggestions
    
    # Takip bilgileri
    duration_weeks = Column(Integer, default=4)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    user = relationship("User")

class Notification(Base):
    """Bildirim sistemi"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Bildirim bilgileri
    notification_type = Column(String, nullable=False)  # 'reminder', 'urgent', 'follow_up', 'tip'
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    
    # Zamanlama
    scheduled_time = Column(DateTime, nullable=False)
    sent_time = Column(DateTime, nullable=True)
    is_sent = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    
    # Ek bilgiler
    priority = Column(String, default='normal')  # 'low', 'normal', 'high', 'urgent'
    action_required = Column(Boolean, default=False)
    action_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    user = relationship("User", back_populates="notifications")

class RiskAssessment(Base):
    """Risk değerlendirme kayıtları"""
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Risk değerlendirmesi
    overall_risk_level = Column(String, nullable=False)  # 'Düşük', 'Orta', 'Yüksek', 'Kritik'
    risk_score = Column(Float, nullable=False)  # 0-100 risk score
    
    # Risk faktörleri
    age_risk = Column(Float, default=0.0)
    gender_risk = Column(Float, default=0.0)
    lifestyle_risk = Column(Float, default=0.0)
    medical_risk = Column(Float, default=0.0)
    environmental_risk = Column(Float, default=0.0)
    
    # Detaylı analiz
    risk_factors = Column(JSON)  # Detailed risk factors
    recommendations = Column(JSON)  # Risk reduction recommendations
    
    # Takip
    next_assessment_date = Column(DateTime, nullable=True)
    is_monitored = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    user = relationship("User")

class LabTestRecommendation(Base):
    """Laboratuvar test önerileri"""
    __tablename__ = "lab_test_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    diagnosis_id = Column(Integer, ForeignKey("diagnosis_history.id"))
    
    # Test bilgileri
    test_name = Column(String, nullable=False)
    test_type = Column(String, nullable=False)  # 'blood', 'urine', 'imaging', 'other'
    priority = Column(String, default='normal')  # 'low', 'normal', 'high', 'urgent'
    
    # Test detayları
    description = Column(Text)
    preparation_instructions = Column(Text)
    normal_ranges = Column(JSON)
    
    # Takip
    is_scheduled = Column(Boolean, default=False)
    scheduled_date = Column(DateTime, nullable=True)
    results_received = Column(Boolean, default=False)
    results = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    user = relationship("User")
    diagnosis = relationship("DiagnosisHistory")
