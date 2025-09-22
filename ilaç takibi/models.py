"""
Profesyonel İlaç Takip Sistemi - Veritabanı Modelleri
Gerçek uygulama için güvenli ve kapsamlı ilaç yönetimi
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from enum import Enum as PyEnum
import json

Base = declarative_base()

class MedicationStatus(PyEnum):
    """İlaç durumu"""
    ACTIVE = "active"           # Aktif kullanımda
    PAUSED = "paused"          # Geçici olarak durdurulmuş
    COMPLETED = "completed"    # Tedavi tamamlanmış
    DISCONTINUED = "discontinued"  # Doktor tarafından durdurulmuş
    EXPIRED = "expired"        # Son kullanma tarihi geçmiş

class DosageUnit(PyEnum):
    """Doz birimleri"""
    MG = "mg"                  # Miligram
    MCG = "mcg"               # Mikrogram
    G = "g"                   # Gram
    ML = "ml"                 # Mililitre
    TABLET = "tablet"         # Tablet
    CAPSULE = "capsule"       # Kapsül
    DROP = "drop"             # Damla
    PUFF = "puff"             # Puf
    UNIT = "unit"             # Ünite
    IU = "iu"                 # Uluslararası ünite

class FrequencyType(PyEnum):
    """Kullanım sıklığı türleri"""
    DAILY = "daily"           # Günlük
    TWICE_DAILY = "twice_daily"  # Günde 2 kez
    THREE_TIMES_DAILY = "three_times_daily"  # Günde 3 kez
    FOUR_TIMES_DAILY = "four_times_daily"    # Günde 4 kez
    WEEKLY = "weekly"         # Haftalık
    MONTHLY = "monthly"       # Aylık
    AS_NEEDED = "as_needed"   # Gerektiğinde
    CUSTOM = "custom"         # Özel

class SeverityLevel(PyEnum):
    """Yan etki şiddeti"""
    MILD = "mild"             # Hafif
    MODERATE = "moderate"     # Orta
    SEVERE = "severe"         # Şiddetli
    CRITICAL = "critical"     # Kritik

class Medication(Base):
    """İlaç bilgileri tablosu"""
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # İlaç temel bilgileri
    medication_name = Column(String(255), nullable=False, index=True)
    generic_name = Column(String(255), nullable=True)
    brand_name = Column(String(255), nullable=True)
    drug_id = Column(String(50), nullable=True, index=True)  # RXDDRGID
    
    # Dozaj bilgileri
    dosage_amount = Column(Float, nullable=False)
    dosage_unit = Column(Enum(DosageUnit), nullable=False)
    frequency_type = Column(Enum(FrequencyType), nullable=False)
    custom_frequency = Column(String(100), nullable=True)  # Özel sıklık için
    
    # Kullanım zamanları (JSON formatında)
    reminder_times = Column(JSON, nullable=False)  # ["08:00", "20:00"]
    
    # Tarih bilgileri
    start_date = Column(DateTime, nullable=False, default=func.now())
    end_date = Column(DateTime, nullable=True)
    prescribed_date = Column(DateTime, nullable=True)
    
    # Durum ve takip
    status = Column(Enum(MedicationStatus), default=MedicationStatus.ACTIVE)
    is_active = Column(Boolean, default=True, index=True)
    
    # Reçete bilgileri
    prescription_number = Column(String(100), nullable=True)
    prescribing_doctor = Column(String(255), nullable=True)
    pharmacy_name = Column(String(255), nullable=True)
    
    # Tıbbi bilgiler
    indication = Column(Text, nullable=True)  # Kullanım amacı
    contraindications = Column(Text, nullable=True)  # Kontrendikasyonlar
    special_instructions = Column(Text, nullable=True)  # Özel talimatlar
    
    # Güvenlik bilgileri
    max_daily_dose = Column(Float, nullable=True)
    min_daily_dose = Column(Float, nullable=True)
    requires_food = Column(Boolean, default=False)
    requires_water = Column(Boolean, default=True)
    
    # Takip bilgileri
    total_prescribed = Column(Integer, nullable=True)  # Toplam reçete edilen
    remaining_pills = Column(Integer, nullable=True)   # Kalan hap sayısı
    refill_reminder_days = Column(Integer, default=7)  # Yenileme hatırlatma günü
    
    # Sistem bilgileri
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # İlişkiler
    user = relationship("User", back_populates="medications")
    medication_logs = relationship("MedicationLog", back_populates="medication", cascade="all, delete-orphan")
    side_effects = relationship("SideEffect", back_populates="medication", cascade="all, delete-orphan")
    interactions = relationship("DrugInteraction", back_populates="medication", cascade="all, delete-orphan")

class MedicationLog(Base):
    """İlaç kullanım kayıtları"""
    __tablename__ = "medication_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Kullanım bilgileri
    taken_at = Column(DateTime, nullable=False, default=func.now())
    scheduled_time = Column(DateTime, nullable=True)
    dosage_taken = Column(Float, nullable=False)
    dosage_unit = Column(Enum(DosageUnit), nullable=False)
    
    # Durum bilgileri
    was_taken = Column(Boolean, default=True)
    was_skipped = Column(Boolean, default=False)
    was_delayed = Column(Boolean, default=False)
    delay_minutes = Column(Integer, nullable=True)
    
    # Kullanım notları
    notes = Column(Text, nullable=True)
    side_effects_noted = Column(Boolean, default=False)
    
    # Sistem bilgileri
    created_at = Column(DateTime, default=func.now())
    
    # İlişkiler
    medication = relationship("Medication", back_populates="medication_logs")
    user = relationship("User")

class SideEffect(Base):
    """Yan etki kayıtları"""
    __tablename__ = "side_effects"
    
    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Yan etki bilgileri
    side_effect_name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    severity = Column(Enum(SeverityLevel), nullable=False)
    
    # Tarih bilgileri
    started_at = Column(DateTime, nullable=False, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    duration_days = Column(Integer, nullable=True)
    
    # Etki bilgileri
    frequency = Column(String(50), nullable=True)  # "günde 2-3 kez"
    intensity = Column(Integer, nullable=True)     # 1-10 arası şiddet
    impact_on_daily_life = Column(String(100), nullable=True)
    
    # Tıbbi bilgiler
    requires_medical_attention = Column(Boolean, default=False)
    reported_to_doctor = Column(Boolean, default=False)
    doctor_notes = Column(Text, nullable=True)
    
    # Sistem bilgileri
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # İlişkiler
    medication = relationship("Medication", back_populates="side_effects")
    user = relationship("User")

class DrugInteraction(Base):
    """İlaç etkileşimleri"""
    __tablename__ = "drug_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Etkileşim bilgileri
    interacting_medication = Column(String(255), nullable=False, index=True)
    interaction_type = Column(String(100), nullable=False)  # "major", "moderate", "minor"
    severity = Column(Enum(SeverityLevel), nullable=False)
    
    # Etkileşim detayları
    description = Column(Text, nullable=False)
    clinical_effect = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=False)
    
    # Güvenlik bilgileri
    requires_monitoring = Column(Boolean, default=False)
    requires_dose_adjustment = Column(Boolean, default=False)
    contraindicated = Column(Boolean, default=False)
    
    # Sistem bilgileri
    detected_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # İlişkiler
    medication = relationship("Medication", back_populates="interactions")
    user = relationship("User")

class MedicationReminder(Base):
    """İlaç hatırlatmaları"""
    __tablename__ = "medication_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Hatırlatma bilgileri
    reminder_time = Column(String(5), nullable=False)  # "08:00"
    reminder_type = Column(String(50), nullable=False)  # "medication", "refill", "appointment"
    message = Column(Text, nullable=False)
    
    # Zamanlama
    is_active = Column(Boolean, default=True)
    next_reminder = Column(DateTime, nullable=True)
    last_sent = Column(DateTime, nullable=True)
    
    # Tekrar ayarları
    repeat_daily = Column(Boolean, default=True)
    repeat_weekly = Column(Boolean, default=False)
    repeat_monthly = Column(Boolean, default=False)
    
    # Sistem bilgileri
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # İlişkiler
    medication = relationship("Medication")
    user = relationship("User")

class MedicationAlert(Base):
    """İlaç uyarıları"""
    __tablename__ = "medication_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Uyarı bilgileri
    alert_type = Column(String(100), nullable=False)  # "overdose", "interaction", "allergy", "expiry"
    severity = Column(Enum(SeverityLevel), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Durum
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    requires_action = Column(Boolean, default=False)
    
    # Sistem bilgileri
    created_at = Column(DateTime, default=func.now())
    read_at = Column(DateTime, nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
    
    # İlişkiler
    user = relationship("User")

class MedicationRefill(Base):
    """İlaç yenileme takibi"""
    __tablename__ = "medication_refills"
    
    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Yenileme bilgileri
    refill_date = Column(DateTime, nullable=False, default=func.now())
    quantity_received = Column(Integer, nullable=False)
    pharmacy_name = Column(String(255), nullable=True)
    prescription_number = Column(String(100), nullable=True)
    
    # Maliyet bilgileri
    cost = Column(Float, nullable=True)
    insurance_coverage = Column(Float, nullable=True)
    copay = Column(Float, nullable=True)
    
    # Sistem bilgileri
    created_at = Column(DateTime, default=func.now())
    
    # İlişkiler
    medication = relationship("Medication")
    user = relationship("User")

# User modeline eklenmesi gereken ilişki
# User modelinde şu satır eklenmeli:
# medications = relationship("Medication", back_populates="user", cascade="all, delete-orphan")
