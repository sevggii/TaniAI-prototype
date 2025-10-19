"""
Profesyonel İlaç Takip Sistemi - Güvenlik Validasyonları
Gerçek uygulama için kritik güvenlik kontrolleri
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import re
import math

from .models import (
    Medication, MedicationLog, SideEffect, DrugInteraction,
    MedicationStatus, DosageUnit, FrequencyType, SeverityLevel
)
from .schemas import MedicationCreate, MedicationUpdate

logger = logging.getLogger(__name__)

class SafetyValidationService:
    """Güvenlik validasyon servisi"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Kritik ilaç listesi (gerçek uygulamada veritabanından gelmeli)
        self.critical_medications = {
            "WARFARIN", "DIGOXIN", "LITHIUM", "PHENYTOIN", "CARBAMAZEPINE",
            "VALPROIC_ACID", "METHOTREXATE", "CYCLOSPORINE", "TACROLIMUS",
            "INSULIN", "HEPARIN", "ENOXAPARIN", "CLOPIDOGREL", "PRASUGREL"
        }
        
        # Yüksek riskli etkileşimler
        self.high_risk_interactions = {
            ("WARFARIN", "ASPIRIN"): "Kanama riski",
            ("WARFARIN", "IBUPROFEN"): "Kanama riski",
            ("DIGOXIN", "FUROSEMIDE"): "Digoksin toksisitesi",
            ("LITHIUM", "FUROSEMIDE"): "Lityum toksisitesi",
            ("METHOTREXATE", "ASPIRIN"): "Methotrexate toksisitesi"
        }
        
        # Doz limitleri (mg/gün)
        self.max_daily_doses = {
            "ACETAMINOPHEN": 4000,
            "IBUPROFEN": 2400,
            "ASPIRIN": 4000,
            "METHOTREXATE": 25,
            "LITHIUM": 2400,
            "DIGOXIN": 0.5
        }
    
    async def validate_medication_creation(self, user_id: int, medication_data: MedicationCreate) -> Tuple[bool, List[str]]:
        """İlaç oluşturma validasyonu"""
        warnings = []
        errors = []
        
        try:
            # 1. İlaç adı validasyonu
            name_validation = await self._validate_medication_name(medication_data.medication_name)
            if not name_validation[0]:
                errors.extend(name_validation[1])
            
            # 2. Doz validasyonu
            dose_validation = await self._validate_dosage(medication_data.dosage_amount, medication_data.dosage_unit, medication_data.medication_name)
            if not dose_validation[0]:
                errors.extend(dose_validation[1])
            warnings.extend(dose_validation[2])
            
            # 3. Tarih validasyonu
            date_validation = await self._validate_dates(medication_data.start_date, medication_data.end_date)
            if not date_validation[0]:
                errors.extend(date_validation[1])
            
            # 4. Hatırlatma saatleri validasyonu
            reminder_validation = await self._validate_reminder_times(medication_data.reminder_times, medication_data.frequency_type)
            if not reminder_validation[0]:
                errors.extend(reminder_validation[1])
            
            # 5. İlaç etkileşimi kontrolü
            interaction_warnings = await self._check_drug_interactions(user_id, medication_data.medication_name)
            warnings.extend(interaction_warnings)
            
            # 6. Kritik ilaç uyarıları
            if medication_data.medication_name.upper() in self.critical_medications:
                warnings.append(f"⚠️ {medication_data.medication_name} kritik bir ilaçtır. Dikkatli takip gereklidir.")
            
            # 7. Yaş ve cinsiyet kontrolleri (kullanıcı profilinden)
            profile_warnings = await self._check_profile_contraindications(user_id, medication_data)
            warnings.extend(profile_warnings)
            
            is_valid = len(errors) == 0
            all_warnings = warnings
            
            return is_valid, errors + all_warnings
            
        except Exception as e:
            logger.error(f"İlaç oluşturma validasyonu hatası: {str(e)}")
            return False, [f"Validasyon hatası: {str(e)}"]
    
    async def validate_medication_update(self, user_id: int, medication_id: int, update_data: MedicationUpdate) -> Tuple[bool, List[str]]:
        """İlaç güncelleme validasyonu"""
        warnings = []
        errors = []
        
        try:
            # Mevcut ilaç bilgilerini al
            medication = self.db.query(Medication).filter(
                and_(
                    Medication.id == medication_id,
                    Medication.user_id == user_id
                )
            ).first()
            
            if not medication:
                return False, ["İlaç bulunamadı"]
            
            # Güncellenecek alanları kontrol et
            if update_data.medication_name:
                name_validation = await self._validate_medication_name(update_data.medication_name)
                if not name_validation[0]:
                    errors.extend(name_validation[1])
            
            if update_data.dosage_amount:
                dose_validation = await self._validate_dosage(
                    update_data.dosage_amount, 
                    update_data.dosage_unit or medication.dosage_unit,
                    update_data.medication_name or medication.medication_name
                )
                if not dose_validation[0]:
                    errors.extend(dose_validation[1])
                warnings.extend(dose_validation[2])
            
            if update_data.reminder_times:
                reminder_validation = await self._validate_reminder_times(
                    update_data.reminder_times, 
                    update_data.frequency_type or medication.frequency_type
                )
                if not reminder_validation[0]:
                    errors.extend(reminder_validation[1])
            
            # Durum değişikliği kontrolleri
            if update_data.status:
                status_validation = await self._validate_status_change(medication, update_data.status)
                if not status_validation[0]:
                    errors.extend(status_validation[1])
                warnings.extend(status_validation[2])
            
            is_valid = len(errors) == 0
            all_warnings = warnings
            
            return is_valid, errors + all_warnings
            
        except Exception as e:
            logger.error(f"İlaç güncelleme validasyonu hatası: {str(e)}")
            return False, [f"Validasyon hatası: {str(e)}"]
    
    async def validate_medication_log(self, user_id: int, medication_id: int, dosage_taken: float) -> Tuple[bool, List[str]]:
        """İlaç kullanım kaydı validasyonu"""
        warnings = []
        errors = []
        
        try:
            # İlaç bilgilerini al
            medication = self.db.query(Medication).filter(
                and_(
                    Medication.id == medication_id,
                    Medication.user_id == user_id,
                    Medication.is_active == True
                )
            ).first()
            
            if not medication:
                return False, ["İlaç bulunamadı veya aktif değil"]
            
            # 1. Doz limiti kontrolü
            dose_validation = await self._validate_single_dose(medication, dosage_taken)
            if not dose_validation[0]:
                errors.extend(dose_validation[1])
            warnings.extend(dose_validation[2])
            
            # 2. Günlük toplam doz kontrolü
            daily_dose_validation = await self._validate_daily_total_dose(medication, dosage_taken)
            if not daily_dose_validation[0]:
                errors.extend(daily_dose_validation[1])
            warnings.extend(daily_dose_validation[2])
            
            # 3. Zamanlama kontrolü
            timing_validation = await self._validate_timing(medication)
            warnings.extend(timing_validation)
            
            # 4. Son kullanım kontrolü
            last_use_validation = await self._validate_last_use(medication)
            warnings.extend(last_use_validation)
            
            is_valid = len(errors) == 0
            all_warnings = warnings
            
            return is_valid, errors + all_warnings
            
        except Exception as e:
            logger.error(f"İlaç kullanım kaydı validasyonu hatası: {str(e)}")
            return False, [f"Validasyon hatası: {str(e)}"]
    
    # Yardımcı Validasyon Metodları
    async def _validate_medication_name(self, medication_name: str) -> Tuple[bool, List[str]]:
        """İlaç adı validasyonu"""
        errors = []
        
        # Boş kontrol
        if not medication_name or not medication_name.strip():
            errors.append("İlaç adı boş olamaz")
            return False, errors
        
        # Uzunluk kontrolü
        if len(medication_name) < 2:
            errors.append("İlaç adı en az 2 karakter olmalıdır")
        
        if len(medication_name) > 255:
            errors.append("İlaç adı en fazla 255 karakter olabilir")
        
        # Geçersiz karakter kontrolü
        if not re.match(r'^[a-zA-Z0-9\s\-\.\(\)]+$', medication_name):
            errors.append("İlaç adında geçersiz karakterler bulunmaktadır")
        
        # Sayısal kontrol (sadece sayı olamaz)
        if medication_name.isdigit():
            errors.append("İlaç adı sadece sayılardan oluşamaz")
        
        return len(errors) == 0, errors
    
    async def _validate_dosage(self, dosage_amount: float, dosage_unit: DosageUnit, medication_name: str) -> Tuple[bool, List[str], List[str]]:
        """Doz validasyonu"""
        errors = []
        warnings = []
        
        # Pozitif değer kontrolü
        if dosage_amount <= 0:
            errors.append("Doz miktarı pozitif olmalıdır")
            return False, errors, warnings
        
        # Maksimum değer kontrolü
        if dosage_amount > 10000:
            errors.append("Doz miktarı çok yüksek (maksimum 10000)")
        
        # Kritik ilaç doz kontrolü
        med_name_upper = medication_name.upper()
        if med_name_upper in self.max_daily_doses:
            max_daily = self.max_daily_doses[med_name_upper]
            
            # Günlük doz kontrolü (varsayılan günde 3 kez)
            estimated_daily = dosage_amount * 3
            if estimated_daily > max_daily:
                warnings.append(f"⚠️ {medication_name} için günlük toplam doz ({estimated_daily:.1f}mg) maksimum limiti ({max_daily}mg) aşabilir")
        
        # Birim-spesifik kontroller
        if dosage_unit == DosageUnit.MG and dosage_amount > 1000:
            warnings.append("⚠️ Yüksek mg dozu - doktor onayı önerilir")
        
        if dosage_unit == DosageUnit.MCG and dosage_amount > 10000:
            warnings.append("⚠️ Yüksek mcg dozu - doktor onayı önerilir")
        
        if dosage_unit == DosageUnit.TABLET and dosage_amount > 10:
            warnings.append("⚠️ Yüksek tablet sayısı - doktor onayı önerilir")
        
        return len(errors) == 0, errors, warnings
    
    async def _validate_dates(self, start_date: datetime, end_date: Optional[datetime]) -> Tuple[bool, List[str]]:
        """Tarih validasyonu"""
        errors = []
        
        # Geçmiş tarih kontrolü
        if start_date < datetime.now() - timedelta(days=365):
            errors.append("Başlangıç tarihi çok eski (1 yıldan fazla)")
        
        # Gelecek tarih kontrolü
        if start_date > datetime.now() + timedelta(days=365):
            errors.append("Başlangıç tarihi çok ileri (1 yıldan fazla)")
        
        # Bitiş tarihi kontrolü
        if end_date:
            if end_date <= start_date:
                errors.append("Bitiş tarihi başlangıç tarihinden sonra olmalıdır")
            
            if end_date < datetime.now():
                errors.append("Bitiş tarihi geçmiş olamaz")
            
            # Çok uzun süre kontrolü
            duration = end_date - start_date
            if duration.days > 365:
                errors.append("İlaç kullanım süresi çok uzun (1 yıldan fazla)")
        
        return len(errors) == 0, errors
    
    async def _validate_reminder_times(self, reminder_times: List[str], frequency_type: FrequencyType) -> Tuple[bool, List[str]]:
        """Hatırlatma saatleri validasyonu"""
        errors = []
        
        # Boş liste kontrolü
        if not reminder_times:
            errors.append("En az bir hatırlatma saati belirtilmelidir")
            return False, errors
        
        # Saat formatı kontrolü
        time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
        for time_str in reminder_times:
            if not time_pattern.match(time_str):
                errors.append(f"Geçersiz saat formatı: {time_str}. HH:MM formatında olmalıdır.")
        
        # Sıklık ile uyumluluk kontrolü
        expected_count = {
            FrequencyType.DAILY: 1,
            FrequencyType.TWICE_DAILY: 2,
            FrequencyType.THREE_TIMES_DAILY: 3,
            FrequencyType.FOUR_TIMES_DAILY: 4,
            FrequencyType.WEEKLY: 1,
            FrequencyType.MONTHLY: 1,
            FrequencyType.AS_NEEDED: 0,
            FrequencyType.CUSTOM: len(reminder_times)
        }
        
        expected = expected_count.get(frequency_type, 1)
        if frequency_type != FrequencyType.CUSTOM and len(reminder_times) != expected:
            errors.append(f"{frequency_type.value} için {expected} hatırlatma saati bekleniyor, {len(reminder_times)} verildi")
        
        # Saat aralığı kontrolü
        if len(reminder_times) > 1:
            times = []
            for time_str in reminder_times:
                hour, minute = map(int, time_str.split(':'))
                times.append(hour * 60 + minute)
            
            times.sort()
            for i in range(1, len(times)):
                interval = times[i] - times[i-1]
                if interval < 60:  # 1 saatten az
                    errors.append("Hatırlatma saatleri arasında en az 1 saat olmalıdır")
        
        return len(errors) == 0, errors
    
    async def _check_drug_interactions(self, user_id: int, new_medication: str) -> List[str]:
        """İlaç etkileşimi kontrolü"""
        warnings = []
        
        try:
            # Kullanıcının aktif ilaçlarını al
            active_medications = self.db.query(Medication).filter(
                and_(
                    Medication.user_id == user_id,
                    Medication.is_active == True,
                    Medication.status == MedicationStatus.ACTIVE
                )
            ).all()
            
            new_med_upper = new_medication.upper()
            
            for med in active_medications:
                med_upper = med.medication_name.upper()
                
                # Yüksek riskli etkileşim kontrolü
                interaction_key = tuple(sorted([new_med_upper, med_upper]))
                if interaction_key in self.high_risk_interactions:
                    warning = f"🚨 YÜKSEK RİSK: {new_medication} ve {med.medication_name} arasında etkileşim: {self.high_risk_interactions[interaction_key]}"
                    warnings.append(warning)
                
                # Aynı ilaç kontrolü
                if new_med_upper == med_upper:
                    warnings.append(f"⚠️ {new_medication} zaten kullanılıyor - çift doz riski")
            
            return warnings
            
        except Exception as e:
            logger.error(f"İlaç etkileşim kontrolü hatası: {str(e)}")
            return []
    
    async def _check_profile_contraindications(self, user_id: int, medication_data: MedicationCreate) -> List[str]:
        """Profil kontrendikasyonları kontrolü"""
        warnings = []
        
        try:
            # Kullanıcı profilini al (gerçek uygulamada UserProfile tablosundan)
            # Şimdilik basit kontroller
            
            medication_name = medication_data.medication_name.upper()
            
            # Yaş kontrolleri (kullanıcı yaşı bilgisi gerekli)
            # if user_age < 18 and medication_name in ["ASPIRIN", "WARFARIN"]:
            #     warnings.append("⚠️ 18 yaş altı için bu ilaç önerilmez")
            
            # Cinsiyet kontrolleri
            # if user_gender == "female" and medication_name in ["WARFARIN", "METHOTREXATE"]:
            #     warnings.append("⚠️ Gebelik planlayan kadınlar için bu ilaç riskli olabilir")
            
            return warnings
            
        except Exception as e:
            logger.error(f"Profil kontrendikasyon kontrolü hatası: {str(e)}")
            return []
    
    async def _validate_single_dose(self, medication: Medication, dosage_taken: float) -> Tuple[bool, List[str], List[str]]:
        """Tek doz validasyonu"""
        errors = []
        warnings = []
        
        # Pozitif değer kontrolü
        if dosage_taken <= 0:
            errors.append("Alınan doz pozitif olmalıdır")
            return False, errors, warnings
        
        # Maksimum tek doz kontrolü
        if medication.max_daily_dose and dosage_taken > medication.max_daily_dose:
            errors.append(f"Alınan doz ({dosage_taken}) maksimum günlük dozdan ({medication.max_daily_dose}) fazla")
        
        # Minimum doz kontrolü
        if medication.min_daily_dose and dosage_taken < medication.min_daily_dose:
            warnings.append(f"⚠️ Alınan doz ({dosage_taken}) minimum günlük dozdan ({medication.min_daily_dose}) az")
        
        # Normal doz aralığı kontrolü
        normal_dose = medication.dosage_amount
        if dosage_taken > normal_dose * 2:
            warnings.append(f"⚠️ Alınan doz ({dosage_taken}) normal dozdan ({normal_dose}) 2 kat fazla")
        
        if dosage_taken < normal_dose * 0.5:
            warnings.append(f"⚠️ Alınan doz ({dosage_taken}) normal dozdan ({normal_dose}) yarısından az")
        
        return len(errors) == 0, errors, warnings
    
    async def _validate_daily_total_dose(self, medication: Medication, additional_dose: float) -> Tuple[bool, List[str], List[str]]:
        """Günlük toplam doz validasyonu"""
        errors = []
        warnings = []
        
        try:
            # Bugünkü toplam dozu hesapla
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            today_total = self.db.query(func.sum(MedicationLog.dosage_taken)).filter(
                and_(
                    MedicationLog.medication_id == medication.id,
                    MedicationLog.taken_at >= today_start,
                    MedicationLog.taken_at < today_end,
                    MedicationLog.was_taken == True
                )
            ).scalar() or 0
            
            new_total = today_total + additional_dose
            
            # Maksimum günlük doz kontrolü
            if medication.max_daily_dose and new_total > medication.max_daily_dose:
                errors.append(f"Günlük toplam doz ({new_total}) maksimum limiti ({medication.max_daily_dose}) aşacak")
            
            # Kritik ilaç kontrolü
            med_name_upper = medication.medication_name.upper()
            if med_name_upper in self.max_daily_doses:
                max_allowed = self.max_daily_doses[med_name_upper]
                if new_total > max_allowed:
                    errors.append(f"🚨 KRİTİK: {medication.medication_name} için günlük maksimum doz ({max_allowed}mg) aşılacak")
            
            # Uyarı seviyeleri
            if medication.max_daily_dose:
                percentage = (new_total / medication.max_daily_dose) * 100
                if percentage > 90:
                    warnings.append(f"⚠️ Günlük doz limitinin %{percentage:.0f}'i kullanıldı")
                elif percentage > 80:
                    warnings.append(f"⚠️ Günlük doz limitinin %{percentage:.0f}'i kullanıldı")
            
            return len(errors) == 0, errors, warnings
            
        except Exception as e:
            logger.error(f"Günlük doz validasyonu hatası: {str(e)}")
            return False, [f"Günlük doz hesaplama hatası: {str(e)}"], []
    
    async def _validate_timing(self, medication: Medication) -> List[str]:
        """Zamanlama validasyonu"""
        warnings = []
        
        try:
            # Son kullanım zamanını al
            last_log = self.db.query(MedicationLog).filter(
                and_(
                    MedicationLog.medication_id == medication.id,
                    MedicationLog.was_taken == True
                )
            ).order_by(desc(MedicationLog.taken_at)).first()
            
            if last_log:
                time_since_last = datetime.now() - last_log.taken_at
                
                # Çok sık kullanım kontrolü
                if time_since_last < timedelta(hours=1):
                    warnings.append("⚠️ Son dozdan 1 saatten az zaman geçti")
                elif time_since_last < timedelta(hours=2):
                    warnings.append("⚠️ Son dozdan 2 saatten az zaman geçti")
                
                # Çok geç kullanım kontrolü
                expected_interval = self._get_expected_interval(medication.frequency_type)
                if time_since_last > expected_interval * 1.5:
                    warnings.append(f"⚠️ Son dozdan {time_since_last} geçti - normal aralık: {expected_interval}")
            
            return warnings
            
        except Exception as e:
            logger.error(f"Zamanlama validasyonu hatası: {str(e)}")
            return []
    
    async def _validate_last_use(self, medication: Medication) -> List[str]:
        """Son kullanım validasyonu"""
        warnings = []
        
        try:
            # Son kullanım zamanını al
            last_log = self.db.query(MedicationLog).filter(
                and_(
                    MedicationLog.medication_id == medication.id,
                    MedicationLog.was_taken == True
                )
            ).order_by(desc(MedicationLog.taken_at)).first()
            
            if last_log:
                time_since_last = datetime.now() - last_log.taken_at
                
                # Çok uzun süre geçmişse
                if time_since_last > timedelta(days=7):
                    warnings.append("⚠️ Son dozdan 1 haftadan fazla zaman geçti")
                elif time_since_last > timedelta(days=3):
                    warnings.append("⚠️ Son dozdan 3 günden fazla zaman geçti")
            
            return warnings
            
        except Exception as e:
            logger.error(f"Son kullanım validasyonu hatası: {str(e)}")
            return []
    
    async def _validate_status_change(self, medication: Medication, new_status: MedicationStatus) -> Tuple[bool, List[str], List[str]]:
        """Durum değişikliği validasyonu"""
        errors = []
        warnings = []
        
        current_status = medication.status
        
        # Geçersiz geçişler
        invalid_transitions = {
            MedicationStatus.COMPLETED: [MedicationStatus.ACTIVE],
            MedicationStatus.DISCONTINUED: [MedicationStatus.ACTIVE, MedicationStatus.PAUSED]
        }
        
        if new_status in invalid_transitions.get(current_status, []):
            errors.append(f"{current_status.value} durumundan {new_status.value} durumuna geçiş geçersiz")
        
        # Uyarı gerektiren geçişler
        if current_status == MedicationStatus.ACTIVE and new_status == MedicationStatus.DISCONTINUED:
            warnings.append("⚠️ Aktif ilaç durduruluyor - doktor onayı önerilir")
        
        if current_status == MedicationStatus.PAUSED and new_status == MedicationStatus.ACTIVE:
            warnings.append("⚠️ Durdurulan ilaç tekrar aktif ediliyor - doz kontrolü önerilir")
        
        return len(errors) == 0, errors, warnings
    
    def _get_expected_interval(self, frequency_type: FrequencyType) -> timedelta:
        """Beklenen kullanım aralığını hesapla"""
        intervals = {
            FrequencyType.DAILY: timedelta(days=1),
            FrequencyType.TWICE_DAILY: timedelta(hours=12),
            FrequencyType.THREE_TIMES_DAILY: timedelta(hours=8),
            FrequencyType.FOUR_TIMES_DAILY: timedelta(hours=6),
            FrequencyType.WEEKLY: timedelta(weeks=1),
            FrequencyType.MONTHLY: timedelta(days=30),
            FrequencyType.AS_NEEDED: timedelta(hours=24),
            FrequencyType.CUSTOM: timedelta(hours=8)
        }
        
        return intervals.get(frequency_type, timedelta(hours=8))


class CriticalSafetyChecks:
    """Kritik güvenlik kontrolleri"""
    
    @staticmethod
    async def check_overdose_risk(user_id: int, medication_id: int, db: Session) -> List[str]:
        """Aşırı doz riski kontrolü"""
        warnings = []
        
        try:
            # Son 24 saatteki kullanımı kontrol et
            last_24h = datetime.now() - timedelta(hours=24)
            
            total_dose = db.query(func.sum(MedicationLog.dosage_taken)).filter(
                and_(
                    MedicationLog.medication_id == medication_id,
                    MedicationLog.user_id == user_id,
                    MedicationLog.taken_at >= last_24h,
                    MedicationLog.was_taken == True
                )
            ).scalar() or 0
            
            medication = db.query(Medication).filter(Medication.id == medication_id).first()
            if medication and medication.max_daily_dose:
                if total_dose >= medication.max_daily_dose:
                    warnings.append("🚨 KRİTİK: 24 saatte maksimum günlük doz aşıldı")
                elif total_dose >= medication.max_daily_dose * 0.8:
                    warnings.append("⚠️ UYARI: 24 saatte günlük doz limitinin %80'i aşıldı")
            
            return warnings
            
        except Exception as e:
            logger.error(f"Aşırı doz riski kontrolü hatası: {str(e)}")
            return []
    
    @staticmethod
    async def check_missed_doses_risk(user_id: int, medication_id: int, db: Session) -> List[str]:
        """Atlanan doz riski kontrolü"""
        warnings = []
        
        try:
            medication = db.query(Medication).filter(Medication.id == medication_id).first()
            if not medication:
                return warnings
            
            # Son 3 gündeki atlanan dozları kontrol et
            last_3_days = datetime.now() - timedelta(days=3)
            
            missed_count = db.query(MedicationLog).filter(
                and_(
                    MedicationLog.medication_id == medication_id,
                    MedicationLog.user_id == user_id,
                    MedicationLog.taken_at >= last_3_days,
                    MedicationLog.was_skipped == True
                )
            ).count()
            
            if missed_count >= 3:
                warnings.append("🚨 KRİTİK: Son 3 günde 3 veya daha fazla doz atlandı")
            elif missed_count >= 2:
                warnings.append("⚠️ UYARI: Son 3 günde 2 doz atlandı")
            
            return warnings
            
        except Exception as e:
            logger.error(f"Atlanan doz riski kontrolü hatası: {str(e)}")
            return []
    
    @staticmethod
    async def check_medication_expiry(user_id: int, db: Session) -> List[str]:
        """İlaç son kullanma tarihi kontrolü"""
        warnings = []
        
        try:
            # Son kullanma tarihi geçen veya yaklaşan ilaçları kontrol et
            today = datetime.now().date()
            next_week = today + timedelta(days=7)
            
            expired_medications = db.query(Medication).filter(
                and_(
                    Medication.user_id == user_id,
                    Medication.is_active == True,
                    Medication.end_date.isnot(None),
                    Medication.end_date <= today
                )
            ).all()
            
            expiring_medications = db.query(Medication).filter(
                and_(
                    Medication.user_id == user_id,
                    Medication.is_active == True,
                    Medication.end_date.isnot(None),
                    Medication.end_date > today,
                    Medication.end_date <= next_week
                )
            ).all()
            
            for med in expired_medications:
                warnings.append(f"🚨 KRİTİK: {med.medication_name} son kullanma tarihi geçti ({med.end_date})")
            
            for med in expiring_medications:
                warnings.append(f"⚠️ UYARI: {med.medication_name} son kullanma tarihi yaklaşıyor ({med.end_date})")
            
            return warnings
            
        except Exception as e:
            logger.error(f"Son kullanma tarihi kontrolü hatası: {str(e)}")
            return []
