"""
Profesyonel İlaç Takip Sistemi - Pydantic Şemaları
API için veri doğrulama ve serileştirme
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, time
from enum import Enum
import re

class DosageUnit(str, Enum):
    """Doz birimleri"""
    MG = "mg"
    MCG = "mcg"
    G = "g"
    ML = "ml"
    TABLET = "tablet"
    CAPSULE = "capsule"
    DROP = "drop"
    PUFF = "puff"
    UNIT = "unit"
    IU = "iu"

class FrequencyType(str, Enum):
    """Kullanım sıklığı türleri"""
    DAILY = "daily"
    TWICE_DAILY = "twice_daily"
    THREE_TIMES_DAILY = "three_times_daily"
    FOUR_TIMES_DAILY = "four_times_daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    AS_NEEDED = "as_needed"
    CUSTOM = "custom"

class MedicationStatus(str, Enum):
    """İlaç durumu"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"
    EXPIRED = "expired"

class SeverityLevel(str, Enum):
    """Yan etki şiddeti"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

# İlaç Oluşturma Şemaları
class MedicationCreate(BaseModel):
    """Yeni ilaç ekleme şeması"""
    medication_name: str = Field(..., min_length=1, max_length=255, description="İlaç adı")
    generic_name: Optional[str] = Field(None, max_length=255, description="Jenerik adı")
    brand_name: Optional[str] = Field(None, max_length=255, description="Marka adı")
    drug_id: Optional[str] = Field(None, max_length=50, description="İlaç ID")
    
    # Dozaj bilgileri
    dosage_amount: float = Field(..., gt=0, description="Doz miktarı")
    dosage_unit: DosageUnit = Field(..., description="Doz birimi")
    frequency_type: FrequencyType = Field(..., description="Kullanım sıklığı")
    custom_frequency: Optional[str] = Field(None, max_length=100, description="Özel sıklık")
    
    # Hatırlatma saatleri
    reminder_times: List[str] = Field(..., min_items=1, description="Hatırlatma saatleri")
    
    # Tarih bilgileri
    start_date: datetime = Field(default_factory=datetime.now, description="Başlangıç tarihi")
    end_date: Optional[datetime] = Field(None, description="Bitiş tarihi")
    prescribed_date: Optional[datetime] = Field(None, description="Reçete tarihi")
    
    # Reçete bilgileri
    prescription_number: Optional[str] = Field(None, max_length=100, description="Reçete numarası")
    prescribing_doctor: Optional[str] = Field(None, max_length=255, description="Reçete yazan doktor")
    pharmacy_name: Optional[str] = Field(None, max_length=255, description="Eczane adı")
    
    # Tıbbi bilgiler
    indication: Optional[str] = Field(None, description="Kullanım amacı")
    contraindications: Optional[str] = Field(None, description="Kontrendikasyonlar")
    special_instructions: Optional[str] = Field(None, description="Özel talimatlar")
    
    # Güvenlik bilgileri
    max_daily_dose: Optional[float] = Field(None, gt=0, description="Maksimum günlük doz")
    min_daily_dose: Optional[float] = Field(None, gt=0, description="Minimum günlük doz")
    requires_food: bool = Field(False, description="Yemekle birlikte alınması gerekiyor mu")
    requires_water: bool = Field(True, description="Su ile birlikte alınması gerekiyor mu")
    
    # Takip bilgileri
    total_prescribed: Optional[int] = Field(None, ge=0, description="Toplam reçete edilen")
    remaining_pills: Optional[int] = Field(None, ge=0, description="Kalan hap sayısı")
    refill_reminder_days: int = Field(7, ge=1, le=30, description="Yenileme hatırlatma günü")
    
    @validator('reminder_times')
    def validate_reminder_times(cls, v):
        """Hatırlatma saatlerini doğrula"""
        time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
        for time_str in v:
            if not time_pattern.match(time_str):
                raise ValueError(f"Geçersiz saat formatı: {time_str}. HH:MM formatında olmalıdır.")
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Bitiş tarihini doğrula"""
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError("Bitiş tarihi başlangıç tarihinden sonra olmalıdır.")
        return v
    
    @validator('max_daily_dose', 'min_daily_dose')
    def validate_dose_limits(cls, v, values):
        """Doz limitlerini doğrula"""
        if v and 'dosage_amount' in values:
            if v < values['dosage_amount']:
                raise ValueError("Günlük doz limiti tek dozdan küçük olamaz.")
        return v
    
    @root_validator
    def validate_dose_consistency(cls, values):
        """Doz tutarlılığını kontrol et"""
        max_dose = values.get('max_daily_dose')
        min_dose = values.get('min_daily_dose')
        
        if max_dose and min_dose and max_dose < min_dose:
            raise ValueError("Maksimum günlük doz minimum günlük dozdan küçük olamaz.")
        
        return values

class MedicationUpdate(BaseModel):
    """İlaç güncelleme şeması"""
    medication_name: Optional[str] = Field(None, min_length=1, max_length=255)
    generic_name: Optional[str] = Field(None, max_length=255)
    brand_name: Optional[str] = Field(None, max_length=255)
    
    dosage_amount: Optional[float] = Field(None, gt=0)
    dosage_unit: Optional[DosageUnit] = None
    frequency_type: Optional[FrequencyType] = None
    custom_frequency: Optional[str] = Field(None, max_length=100)
    
    reminder_times: Optional[List[str]] = Field(None, min_items=1)
    end_date: Optional[datetime] = None
    status: Optional[MedicationStatus] = None
    
    indication: Optional[str] = None
    special_instructions: Optional[str] = None
    remaining_pills: Optional[int] = Field(None, ge=0)
    refill_reminder_days: Optional[int] = Field(None, ge=1, le=30)
    
    @validator('reminder_times')
    def validate_reminder_times(cls, v):
        """Hatırlatma saatlerini doğrula"""
        if v:
            time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
            for time_str in v:
                if not time_pattern.match(time_str):
                    raise ValueError(f"Geçersiz saat formatı: {time_str}. HH:MM formatında olmalıdır.")
        return v

class MedicationResponse(BaseModel):
    """İlaç yanıt şeması"""
    id: int
    user_id: int
    medication_name: str
    generic_name: Optional[str]
    brand_name: Optional[str]
    drug_id: Optional[str]
    
    dosage_amount: float
    dosage_unit: DosageUnit
    frequency_type: FrequencyType
    custom_frequency: Optional[str]
    reminder_times: List[str]
    
    start_date: datetime
    end_date: Optional[datetime]
    prescribed_date: Optional[datetime]
    status: MedicationStatus
    is_active: bool
    
    prescription_number: Optional[str]
    prescribing_doctor: Optional[str]
    pharmacy_name: Optional[str]
    
    indication: Optional[str]
    contraindications: Optional[str]
    special_instructions: Optional[str]
    
    max_daily_dose: Optional[float]
    min_daily_dose: Optional[float]
    requires_food: bool
    requires_water: bool
    
    total_prescribed: Optional[int]
    remaining_pills: Optional[int]
    refill_reminder_days: int
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# İlaç Kullanım Kayıt Şemaları
class MedicationLogCreate(BaseModel):
    """İlaç kullanım kaydı oluşturma"""
    medication_id: int = Field(..., description="İlaç ID")
    taken_at: datetime = Field(default_factory=datetime.now, description="Alınma zamanı")
    scheduled_time: Optional[datetime] = Field(None, description="Planlanan zaman")
    dosage_taken: float = Field(..., gt=0, description="Alınan doz")
    dosage_unit: DosageUnit = Field(..., description="Doz birimi")
    
    was_taken: bool = Field(True, description="Alındı mı")
    was_skipped: bool = Field(False, description="Atlandı mı")
    was_delayed: bool = Field(False, description="Gecikti mi")
    delay_minutes: Optional[int] = Field(None, ge=0, description="Gecikme dakikası")
    
    notes: Optional[str] = Field(None, description="Notlar")
    side_effects_noted: bool = Field(False, description="Yan etki kaydedildi mi")

class MedicationLogResponse(BaseModel):
    """İlaç kullanım kaydı yanıtı"""
    id: int
    medication_id: int
    user_id: int
    taken_at: datetime
    scheduled_time: Optional[datetime]
    dosage_taken: float
    dosage_unit: DosageUnit
    
    was_taken: bool
    was_skipped: bool
    was_delayed: bool
    delay_minutes: Optional[int]
    
    notes: Optional[str]
    side_effects_noted: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Yan Etki Şemaları
class SideEffectCreate(BaseModel):
    """Yan etki kaydı oluşturma"""
    medication_id: int = Field(..., description="İlaç ID")
    side_effect_name: str = Field(..., min_length=1, max_length=255, description="Yan etki adı")
    description: Optional[str] = Field(None, description="Açıklama")
    severity: SeverityLevel = Field(..., description="Şiddet")
    
    started_at: datetime = Field(default_factory=datetime.now, description="Başlangıç zamanı")
    ended_at: Optional[datetime] = Field(None, description="Bitiş zamanı")
    duration_days: Optional[int] = Field(None, ge=0, description="Süre (gün)")
    
    frequency: Optional[str] = Field(None, max_length=50, description="Sıklık")
    intensity: Optional[int] = Field(None, ge=1, le=10, description="Yoğunluk (1-10)")
    impact_on_daily_life: Optional[str] = Field(None, max_length=100, description="Günlük yaşama etkisi")
    
    requires_medical_attention: bool = Field(False, description="Tıbbi müdahale gerekiyor mu")
    reported_to_doctor: bool = Field(False, description="Doktora bildirildi mi")
    doctor_notes: Optional[str] = Field(None, description="Doktor notları")

class SideEffectResponse(BaseModel):
    """Yan etki yanıtı"""
    id: int
    medication_id: int
    user_id: int
    side_effect_name: str
    description: Optional[str]
    severity: SeverityLevel
    
    started_at: datetime
    ended_at: Optional[datetime]
    duration_days: Optional[int]
    
    frequency: Optional[str]
    intensity: Optional[int]
    impact_on_daily_life: Optional[str]
    
    requires_medical_attention: bool
    reported_to_doctor: bool
    doctor_notes: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# İlaç Etkileşimi Şemaları
class DrugInteractionResponse(BaseModel):
    """İlaç etkileşimi yanıtı"""
    id: int
    medication_id: int
    user_id: int
    interacting_medication: str
    interaction_type: str
    severity: SeverityLevel
    
    description: str
    clinical_effect: Optional[str]
    recommendation: str
    
    requires_monitoring: bool
    requires_dose_adjustment: bool
    contraindicated: bool
    
    detected_at: datetime
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Hatırlatma Şemaları
class MedicationReminderCreate(BaseModel):
    """İlaç hatırlatması oluşturma"""
    medication_id: int = Field(..., description="İlaç ID")
    reminder_time: str = Field(..., description="Hatırlatma saati")
    reminder_type: str = Field(..., description="Hatırlatma türü")
    message: str = Field(..., min_length=1, description="Mesaj")
    
    repeat_daily: bool = Field(True, description="Günlük tekrar")
    repeat_weekly: bool = Field(False, description="Haftalık tekrar")
    repeat_monthly: bool = Field(False, description="Aylık tekrar")
    
    @validator('reminder_time')
    def validate_reminder_time(cls, v):
        """Hatırlatma saatini doğrula"""
        time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
        if not time_pattern.match(v):
            raise ValueError(f"Geçersiz saat formatı: {v}. HH:MM formatında olmalıdır.")
        return v

class MedicationReminderResponse(BaseModel):
    """İlaç hatırlatması yanıtı"""
    id: int
    medication_id: int
    user_id: int
    reminder_time: str
    reminder_type: str
    message: str
    
    is_active: bool
    next_reminder: Optional[datetime]
    last_sent: Optional[datetime]
    
    repeat_daily: bool
    repeat_weekly: bool
    repeat_monthly: bool
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Uyarı Şemaları
class MedicationAlertResponse(BaseModel):
    """İlaç uyarısı yanıtı"""
    id: int
    user_id: int
    alert_type: str
    severity: SeverityLevel
    title: str
    message: str
    
    is_read: bool
    is_dismissed: bool
    requires_action: bool
    
    created_at: datetime
    read_at: Optional[datetime]
    dismissed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Yenileme Şemaları
class MedicationRefillCreate(BaseModel):
    """İlaç yenileme oluşturma"""
    medication_id: int = Field(..., description="İlaç ID")
    refill_date: datetime = Field(default_factory=datetime.now, description="Yenileme tarihi")
    quantity_received: int = Field(..., gt=0, description="Alınan miktar")
    pharmacy_name: Optional[str] = Field(None, max_length=255, description="Eczane adı")
    prescription_number: Optional[str] = Field(None, max_length=100, description="Reçete numarası")
    
    cost: Optional[float] = Field(None, ge=0, description="Maliyet")
    insurance_coverage: Optional[float] = Field(None, ge=0, le=100, description="Sigorta kapsamı (%)")
    copay: Optional[float] = Field(None, ge=0, description="Katkı payı")

class MedicationRefillResponse(BaseModel):
    """İlaç yenileme yanıtı"""
    id: int
    medication_id: int
    user_id: int
    refill_date: datetime
    quantity_received: int
    pharmacy_name: Optional[str]
    prescription_number: Optional[str]
    
    cost: Optional[float]
    insurance_coverage: Optional[float]
    copay: Optional[float]
    
    created_at: datetime
    
    class Config:
        from_attributes = True

# Özet Şemaları
class MedicationSummary(BaseModel):
    """İlaç özeti"""
    total_medications: int
    active_medications: int
    medications_due_today: int
    missed_doses_today: int
    upcoming_refills: int
    active_side_effects: int
    critical_interactions: int

class MedicationComplianceReport(BaseModel):
    """İlaç uyum raporu"""
    medication_id: int
    medication_name: str
    compliance_rate: float = Field(..., ge=0, le=100, description="Uyum oranı (%)")
    total_doses: int
    taken_doses: int
    missed_doses: int
    delayed_doses: int
    period_start: datetime
    period_end: datetime

# Arama ve Filtreleme Şemaları
class MedicationSearch(BaseModel):
    """İlaç arama parametreleri"""
    medication_name: Optional[str] = Field(None, description="İlaç adı")
    status: Optional[MedicationStatus] = Field(None, description="Durum")
    is_active: Optional[bool] = Field(None, description="Aktif mi")
    prescribing_doctor: Optional[str] = Field(None, description="Reçete yazan doktor")
    pharmacy_name: Optional[str] = Field(None, description="Eczane adı")
    start_date_from: Optional[datetime] = Field(None, description="Başlangıç tarihi (başlangıç)")
    start_date_to: Optional[datetime] = Field(None, description="Başlangıç tarihi (bitiş)")
    limit: int = Field(50, ge=1, le=100, description="Sayfa boyutu")
    offset: int = Field(0, ge=0, description="Sayfa ofseti")

class MedicationLogSearch(BaseModel):
    """İlaç kullanım kaydı arama parametreleri"""
    medication_id: Optional[int] = Field(None, description="İlaç ID")
    date_from: Optional[datetime] = Field(None, description="Tarih (başlangıç)")
    date_to: Optional[datetime] = Field(None, description="Tarih (bitiş)")
    was_taken: Optional[bool] = Field(None, description="Alındı mı")
    was_skipped: Optional[bool] = Field(None, description="Atlandı mı")
    was_delayed: Optional[bool] = Field(None, description="Gecikti mi")
    limit: int = Field(50, ge=1, le=100, description="Sayfa boyutu")
    offset: int = Field(0, ge=0, description="Sayfa ofseti")
