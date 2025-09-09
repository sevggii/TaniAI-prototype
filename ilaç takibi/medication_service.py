"""
Profesyonel İlaç Takip Sistemi - Ana Servis
Gerçek uygulama için güvenli ve kapsamlı ilaç yönetimi servisi
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
import json
import re

from .models import (
    Medication, MedicationLog, SideEffect, DrugInteraction, 
    MedicationReminder, MedicationAlert, MedicationRefill,
    MedicationStatus, DosageUnit, FrequencyType, SeverityLevel
)
from .schemas import (
    MedicationCreate, MedicationUpdate, MedicationResponse,
    MedicationLogCreate, MedicationLogResponse,
    SideEffectCreate, SideEffectResponse,
    MedicationReminderCreate, MedicationReminderResponse,
    MedicationRefillCreate, MedicationRefillResponse,
    MedicationSummary, MedicationComplianceReport,
    MedicationSearch, MedicationLogSearch
)

logger = logging.getLogger(__name__)

class MedicationService:
    """Ana ilaç takip servisi"""
    
    def __init__(self, db: Session):
        self.db = db
        self.drug_interaction_service = DrugInteractionService(db)
        self.side_effect_service = SideEffectService(db)
        self.reminder_service = MedicationReminderService(db)
        self.alert_service = MedicationAlertService(db)
    
    # İlaç CRUD İşlemleri
    async def create_medication(self, user_id: int, medication_data: MedicationCreate) -> MedicationResponse:
        """Yeni ilaç ekleme"""
        try:
            # İlaç etkileşimlerini kontrol et
            await self._check_drug_interactions(user_id, medication_data.medication_name)
            
            # İlaç oluştur
            medication = Medication(
                user_id=user_id,
                **medication_data.dict()
            )
            
            self.db.add(medication)
            self.db.commit()
            self.db.refresh(medication)
            
            # Hatırlatmaları oluştur
            await self.reminder_service.create_medication_reminders(medication)
            
            # Uyarıları kontrol et
            await self.alert_service.check_medication_alerts(user_id, medication)
            
            logger.info(f"İlaç oluşturuldu: {medication.id} - {medication.medication_name}")
            return MedicationResponse.from_orm(medication)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"İlaç oluşturma hatası: {str(e)}")
            raise
    
    async def get_medication(self, user_id: int, medication_id: int) -> Optional[MedicationResponse]:
        """İlaç getirme"""
        try:
            medication = self.db.query(Medication).filter(
                and_(
                    Medication.id == medication_id,
                    Medication.user_id == user_id
                )
            ).first()
            
            if not medication:
                return None
            
            return MedicationResponse.from_orm(medication)
            
        except Exception as e:
            logger.error(f"İlaç getirme hatası: {str(e)}")
            raise
    
    async def get_user_medications(self, user_id: int, search_params: MedicationSearch) -> List[MedicationResponse]:
        """Kullanıcının ilaçlarını getirme"""
        try:
            query = self.db.query(Medication).filter(Medication.user_id == user_id)
            
            # Filtreleme
            if search_params.medication_name:
                query = query.filter(Medication.medication_name.ilike(f"%{search_params.medication_name}%"))
            
            if search_params.status:
                query = query.filter(Medication.status == search_params.status)
            
            if search_params.is_active is not None:
                query = query.filter(Medication.is_active == search_params.is_active)
            
            if search_params.prescribing_doctor:
                query = query.filter(Medication.prescribing_doctor.ilike(f"%{search_params.prescribing_doctor}%"))
            
            if search_params.pharmacy_name:
                query = query.filter(Medication.pharmacy_name.ilike(f"%{search_params.pharmacy_name}%"))
            
            if search_params.start_date_from:
                query = query.filter(Medication.start_date >= search_params.start_date_from)
            
            if search_params.start_date_to:
                query = query.filter(Medication.start_date <= search_params.start_date_to)
            
            # Sıralama ve sayfalama
            medications = query.order_by(desc(Medication.created_at)).offset(
                search_params.offset
            ).limit(search_params.limit).all()
            
            return [MedicationResponse.from_orm(med) for med in medications]
            
        except Exception as e:
            logger.error(f"Kullanıcı ilaçları getirme hatası: {str(e)}")
            raise
    
    async def update_medication(self, user_id: int, medication_id: int, update_data: MedicationUpdate) -> Optional[MedicationResponse]:
        """İlaç güncelleme"""
        try:
            medication = self.db.query(Medication).filter(
                and_(
                    Medication.id == medication_id,
                    Medication.user_id == user_id
                )
            ).first()
            
            if not medication:
                return None
            
            # Güncelleme verilerini uygula
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(medication, field, value)
            
            medication.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(medication)
            
            # Uyarıları kontrol et
            await self.alert_service.check_medication_alerts(user_id, medication)
            
            logger.info(f"İlaç güncellendi: {medication.id}")
            return MedicationResponse.from_orm(medication)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"İlaç güncelleme hatası: {str(e)}")
            raise
    
    async def delete_medication(self, user_id: int, medication_id: int) -> bool:
        """İlaç silme (soft delete)"""
        try:
            medication = self.db.query(Medication).filter(
                and_(
                    Medication.id == medication_id,
                    Medication.user_id == user_id
                )
            ).first()
            
            if not medication:
                return False
            
            # Soft delete
            medication.is_active = False
            medication.status = MedicationStatus.DISCONTINUED
            medication.updated_at = datetime.now()
            
            self.db.commit()
            
            logger.info(f"İlaç silindi: {medication.id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"İlaç silme hatası: {str(e)}")
            raise
    
    # İlaç Kullanım Takibi
    async def log_medication_taken(self, user_id: int, log_data: MedicationLogCreate) -> MedicationLogResponse:
        """İlaç alındı olarak kaydetme"""
        try:
            # İlaç kontrolü
            medication = self.db.query(Medication).filter(
                and_(
                    Medication.id == log_data.medication_id,
                    Medication.user_id == user_id,
                    Medication.is_active == True
                )
            ).first()
            
            if not medication:
                raise ValueError("İlaç bulunamadı veya aktif değil")
            
            # Doz kontrolü
            await self._validate_dosage(medication, log_data.dosage_taken)
            
            # Kullanım kaydı oluştur
            medication_log = MedicationLog(
                user_id=user_id,
                **log_data.dict()
            )
            
            self.db.add(medication_log)
            self.db.commit()
            self.db.refresh(medication_log)
            
            # Kalan hap sayısını güncelle
            if medication.remaining_pills is not None:
                medication.remaining_pills = max(0, medication.remaining_pills - 1)
                self.db.commit()
            
            # Yenileme uyarısını kontrol et
            await self._check_refill_reminder(medication)
            
            logger.info(f"İlaç kullanımı kaydedildi: {medication_log.id}")
            return MedicationLogResponse.from_orm(medication_log)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"İlaç kullanım kaydı hatası: {str(e)}")
            raise
    
    async def get_medication_logs(self, user_id: int, search_params: MedicationLogSearch) -> List[MedicationLogResponse]:
        """İlaç kullanım kayıtlarını getirme"""
        try:
            query = self.db.query(MedicationLog).filter(MedicationLog.user_id == user_id)
            
            # Filtreleme
            if search_params.medication_id:
                query = query.filter(MedicationLog.medication_id == search_params.medication_id)
            
            if search_params.date_from:
                query = query.filter(MedicationLog.taken_at >= search_params.date_from)
            
            if search_params.date_to:
                query = query.filter(MedicationLog.taken_at <= search_params.date_to)
            
            if search_params.was_taken is not None:
                query = query.filter(MedicationLog.was_taken == search_params.was_taken)
            
            if search_params.was_skipped is not None:
                query = query.filter(MedicationLog.was_skipped == search_params.was_skipped)
            
            if search_params.was_delayed is not None:
                query = query.filter(MedicationLog.was_delayed == search_params.was_delayed)
            
            # Sıralama ve sayfalama
            logs = query.order_by(desc(MedicationLog.taken_at)).offset(
                search_params.offset
            ).limit(search_params.limit).all()
            
            return [MedicationLogResponse.from_orm(log) for log in logs]
            
        except Exception as e:
            logger.error(f"İlaç kullanım kayıtları getirme hatası: {str(e)}")
            raise
    
    # Özet ve Raporlama
    async def get_medication_summary(self, user_id: int) -> MedicationSummary:
        """İlaç özeti"""
        try:
            today = datetime.now().date()
            
            # Toplam ilaç sayısı
            total_medications = self.db.query(Medication).filter(
                and_(
                    Medication.user_id == user_id,
                    Medication.is_active == True
                )
            ).count()
            
            # Aktif ilaç sayısı
            active_medications = self.db.query(Medication).filter(
                and_(
                    Medication.user_id == user_id,
                    Medication.is_active == True,
                    Medication.status == MedicationStatus.ACTIVE
                )
            ).count()
            
            # Bugün alınması gereken ilaçlar
            medications_due_today = await self._get_medications_due_today(user_id)
            
            # Bugün atlanan dozlar
            missed_doses_today = await self._get_missed_doses_today(user_id)
            
            # Yaklaşan yenilemeler
            upcoming_refills = await self._get_upcoming_refills(user_id)
            
            # Aktif yan etkiler
            active_side_effects = self.db.query(SideEffect).filter(
                and_(
                    SideEffect.user_id == user_id,
                    SideEffect.ended_at.is_(None)
                )
            ).count()
            
            # Kritik etkileşimler
            critical_interactions = self.db.query(DrugInteraction).filter(
                and_(
                    DrugInteraction.user_id == user_id,
                    DrugInteraction.is_active == True,
                    DrugInteraction.severity == SeverityLevel.CRITICAL
                )
            ).count()
            
            return MedicationSummary(
                total_medications=total_medications,
                active_medications=active_medications,
                medications_due_today=len(medications_due_today),
                missed_doses_today=missed_doses_today,
                upcoming_refills=upcoming_refills,
                active_side_effects=active_side_effects,
                critical_interactions=critical_interactions
            )
            
        except Exception as e:
            logger.error(f"İlaç özeti getirme hatası: {str(e)}")
            raise
    
    async def get_compliance_report(self, user_id: int, medication_id: int, days: int = 30) -> Optional[MedicationComplianceReport]:
        """İlaç uyum raporu"""
        try:
            medication = self.db.query(Medication).filter(
                and_(
                    Medication.id == medication_id,
                    Medication.user_id == user_id
                )
            ).first()
            
            if not medication:
                return None
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Toplam doz sayısı (beklenen)
            total_doses = await self._calculate_expected_doses(medication, start_date, end_date)
            
            # Alınan dozlar
            taken_doses = self.db.query(MedicationLog).filter(
                and_(
                    MedicationLog.medication_id == medication_id,
                    MedicationLog.taken_at >= start_date,
                    MedicationLog.taken_at <= end_date,
                    MedicationLog.was_taken == True
                )
            ).count()
            
            # Atlanan dozlar
            missed_doses = self.db.query(MedicationLog).filter(
                and_(
                    MedicationLog.medication_id == medication_id,
                    MedicationLog.taken_at >= start_date,
                    MedicationLog.taken_at <= end_date,
                    MedicationLog.was_skipped == True
                )
            ).count()
            
            # Geciken dozlar
            delayed_doses = self.db.query(MedicationLog).filter(
                and_(
                    MedicationLog.medication_id == medication_id,
                    MedicationLog.taken_at >= start_date,
                    MedicationLog.taken_at <= end_date,
                    MedicationLog.was_delayed == True
                )
            ).count()
            
            # Uyum oranı
            compliance_rate = (taken_doses / total_doses * 100) if total_doses > 0 else 0
            
            return MedicationComplianceReport(
                medication_id=medication_id,
                medication_name=medication.medication_name,
                compliance_rate=compliance_rate,
                total_doses=total_doses,
                taken_doses=taken_doses,
                missed_doses=missed_doses,
                delayed_doses=delayed_doses,
                period_start=start_date,
                period_end=end_date
            )
            
        except Exception as e:
            logger.error(f"Uyum raporu getirme hatası: {str(e)}")
            raise
    
    # Yardımcı Metodlar
    async def _check_drug_interactions(self, user_id: int, medication_name: str):
        """İlaç etkileşimlerini kontrol et"""
        try:
            # Kullanıcının aktif ilaçlarını al
            active_medications = self.db.query(Medication).filter(
                and_(
                    Medication.user_id == user_id,
                    Medication.is_active == True,
                    Medication.status == MedicationStatus.ACTIVE
                )
            ).all()
            
            # Etkileşim kontrolü
            for med in active_medications:
                interaction = await self.drug_interaction_service.check_interaction(
                    med.medication_name, medication_name
                )
                
                if interaction:
                    # Kritik etkileşim uyarısı
                    await self.alert_service.create_interaction_alert(
                        user_id, med.id, interaction
                    )
                    
        except Exception as e:
            logger.error(f"İlaç etkileşim kontrolü hatası: {str(e)}")
    
    async def _validate_dosage(self, medication: Medication, dosage_taken: float):
        """Doz doğrulama"""
        try:
            # Maksimum günlük doz kontrolü
            if medication.max_daily_dose:
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
                
                if today_total + dosage_taken > medication.max_daily_dose:
                    raise ValueError(f"Günlük maksimum doz aşılıyor: {medication.max_daily_dose}")
            
            # Minimum günlük doz kontrolü
            if medication.min_daily_dose and dosage_taken < medication.min_daily_dose:
                logger.warning(f"Düşük doz uyarısı: {dosage_taken} < {medication.min_daily_dose}")
                
        except Exception as e:
            logger.error(f"Doz doğrulama hatası: {str(e)}")
            raise
    
    async def _check_refill_reminder(self, medication: Medication):
        """Yenileme hatırlatması kontrolü"""
        try:
            if medication.remaining_pills is not None and medication.remaining_pills <= medication.refill_reminder_days:
                await self.alert_service.create_refill_alert(medication.user_id, medication)
                
        except Exception as e:
            logger.error(f"Yenileme hatırlatması kontrolü hatası: {str(e)}")
    
    async def _get_medications_due_today(self, user_id: int) -> List[Medication]:
        """Bugün alınması gereken ilaçlar"""
        try:
            today = datetime.now().date()
            
            medications = self.db.query(Medication).filter(
                and_(
                    Medication.user_id == user_id,
                    Medication.is_active == True,
                    Medication.status == MedicationStatus.ACTIVE,
                    Medication.start_date <= today,
                    or_(
                        Medication.end_date.is_(None),
                        Medication.end_date >= today
                    )
                )
            ).all()
            
            return medications
            
        except Exception as e:
            logger.error(f"Bugünkü ilaçlar getirme hatası: {str(e)}")
            return []
    
    async def _get_missed_doses_today(self, user_id: int) -> int:
        """Bugün atlanan doz sayısı"""
        try:
            today = datetime.now().date()
            today_start = datetime.combine(today, time.min)
            today_end = datetime.combine(today, time.max)
            
            missed_count = self.db.query(MedicationLog).filter(
                and_(
                    MedicationLog.user_id == user_id,
                    MedicationLog.taken_at >= today_start,
                    MedicationLog.taken_at <= today_end,
                    MedicationLog.was_skipped == True
                )
            ).count()
            
            return missed_count
            
        except Exception as e:
            logger.error(f"Atlanan doz sayısı getirme hatası: {str(e)}")
            return 0
    
    async def _get_upcoming_refills(self, user_id: int) -> int:
        """Yaklaşan yenileme sayısı"""
        try:
            upcoming_count = self.db.query(Medication).filter(
                and_(
                    Medication.user_id == user_id,
                    Medication.is_active == True,
                    Medication.remaining_pills.isnot(None),
                    Medication.remaining_pills <= 7  # 7 gün veya daha az
                )
            ).count()
            
            return upcoming_count
            
        except Exception as e:
            logger.error(f"Yaklaşan yenileme sayısı getirme hatası: {str(e)}")
            return 0
    
    async def _calculate_expected_doses(self, medication: Medication, start_date: datetime, end_date: datetime) -> int:
        """Beklenen doz sayısını hesapla"""
        try:
            frequency_map = {
                FrequencyType.DAILY: 1,
                FrequencyType.TWICE_DAILY: 2,
                FrequencyType.THREE_TIMES_DAILY: 3,
                FrequencyType.FOUR_TIMES_DAILY: 4,
                FrequencyType.WEEKLY: 1/7,
                FrequencyType.MONTHLY: 1/30,
                FrequencyType.AS_NEEDED: 0
            }
            
            daily_frequency = frequency_map.get(medication.frequency_type, 1)
            days = (end_date - start_date).days
            
            return int(days * daily_frequency)
            
        except Exception as e:
            logger.error(f"Beklenen doz hesaplama hatası: {str(e)}")
            return 0


class DrugInteractionService:
    """İlaç etkileşim servisi"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def check_interaction(self, medication1: str, medication2: str) -> Optional[Dict[str, Any]]:
        """İlaç etkileşimini kontrol et"""
        try:
            # Basit etkileşim kontrolü (gerçek uygulamada daha kapsamlı olmalı)
            known_interactions = {
                ("WARFARIN", "ASPIRIN"): {
                    "type": "major",
                    "severity": "critical",
                    "description": "Kanama riski artışı",
                    "recommendation": "Doktor kontrolü gerekli"
                },
                ("DIGOXIN", "FUROSEMIDE"): {
                    "type": "moderate",
                    "severity": "severe",
                    "description": "Digoksin toksisitesi riski",
                    "recommendation": "Kan seviyeleri takip edilmeli"
                }
            }
            
            # Etkileşim kontrolü
            interaction_key = tuple(sorted([medication1.upper(), medication2.upper()]))
            return known_interactions.get(interaction_key)
            
        except Exception as e:
            logger.error(f"İlaç etkileşim kontrolü hatası: {str(e)}")
            return None


class SideEffectService:
    """Yan etki takip servisi"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_side_effect(self, user_id: int, side_effect_data: SideEffectCreate) -> SideEffectResponse:
        """Yan etki kaydı oluşturma"""
        try:
            side_effect = SideEffect(
                user_id=user_id,
                **side_effect_data.dict()
            )
            
            self.db.add(side_effect)
            self.db.commit()
            self.db.refresh(side_effect)
            
            # Kritik yan etki uyarısı
            if side_effect.severity == SeverityLevel.CRITICAL:
                await self._create_critical_side_effect_alert(user_id, side_effect)
            
            logger.info(f"Yan etki kaydedildi: {side_effect.id}")
            return SideEffectResponse.from_orm(side_effect)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Yan etki kaydı hatası: {str(e)}")
            raise
    
    async def _create_critical_side_effect_alert(self, user_id: int, side_effect: SideEffect):
        """Kritik yan etki uyarısı oluşturma"""
        try:
            alert = MedicationAlert(
                user_id=user_id,
                alert_type="critical_side_effect",
                severity=SeverityLevel.CRITICAL,
                title="Kritik Yan Etki Tespit Edildi",
                message=f"{side_effect.side_effect_name} - Acil tıbbi müdahale gerekebilir",
                requires_action=True
            )
            
            self.db.add(alert)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Kritik yan etki uyarısı hatası: {str(e)}")


class MedicationReminderService:
    """İlaç hatırlatma servisi"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_medication_reminders(self, medication: Medication):
        """İlaç hatırlatmaları oluşturma"""
        try:
            for reminder_time in medication.reminder_times:
                reminder = MedicationReminder(
                    medication_id=medication.id,
                    user_id=medication.user_id,
                    reminder_time=reminder_time,
                    reminder_type="medication",
                    message=f"{medication.medication_name} alınma zamanı",
                    next_reminder=await self._calculate_next_reminder(reminder_time)
                )
                
                self.db.add(reminder)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"İlaç hatırlatması oluşturma hatası: {str(e)}")
    
    async def _calculate_next_reminder(self, reminder_time: str) -> datetime:
        """Sonraki hatırlatma zamanını hesapla"""
        try:
            hour, minute = map(int, reminder_time.split(':'))
            now = datetime.now()
            next_reminder = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if next_reminder <= now:
                next_reminder += timedelta(days=1)
            
            return next_reminder
            
        except Exception as e:
            logger.error(f"Sonraki hatırlatma hesaplama hatası: {str(e)}")
            return datetime.now() + timedelta(hours=1)


class MedicationAlertService:
    """İlaç uyarı servisi"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def check_medication_alerts(self, user_id: int, medication: Medication):
        """İlaç uyarılarını kontrol et"""
        try:
            # Son kullanma tarihi kontrolü
            if medication.end_date and medication.end_date <= datetime.now():
                await self.create_expiry_alert(user_id, medication)
            
            # Doz kontrolü
            if medication.max_daily_dose:
                await self.check_dosage_alerts(user_id, medication)
                
        except Exception as e:
            logger.error(f"İlaç uyarı kontrolü hatası: {str(e)}")
    
    async def create_expiry_alert(self, user_id: int, medication: Medication):
        """Son kullanma tarihi uyarısı"""
        try:
            alert = MedicationAlert(
                user_id=user_id,
                alert_type="expiry",
                severity=SeverityLevel.MODERATE,
                title="İlaç Son Kullanma Tarihi",
                message=f"{medication.medication_name} son kullanma tarihi geçti",
                requires_action=True
            )
            
            self.db.add(alert)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Son kullanma uyarısı hatası: {str(e)}")
    
    async def create_refill_alert(self, user_id: int, medication: Medication):
        """Yenileme uyarısı"""
        try:
            alert = MedicationAlert(
                user_id=user_id,
                alert_type="refill",
                severity=SeverityLevel.MILD,
                title="İlaç Yenileme Hatırlatması",
                message=f"{medication.medication_name} yenilenmesi gerekiyor",
                requires_action=True
            )
            
            self.db.add(alert)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Yenileme uyarısı hatası: {str(e)}")
    
    async def create_interaction_alert(self, user_id: int, medication_id: int, interaction: Dict[str, Any]):
        """Etkileşim uyarısı"""
        try:
            alert = MedicationAlert(
                user_id=user_id,
                alert_type="interaction",
                severity=SeverityLevel(interaction["severity"]),
                title="İlaç Etkileşimi Uyarısı",
                message=interaction["description"],
                requires_action=True
            )
            
            self.db.add(alert)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Etkileşim uyarısı hatası: {str(e)}")
    
    async def check_dosage_alerts(self, user_id: int, medication: Medication):
        """Doz uyarıları kontrolü"""
        try:
            # Günlük doz kontrolü
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
            
            if medication.max_daily_dose and today_total >= medication.max_daily_dose:
                alert = MedicationAlert(
                    user_id=user_id,
                    alert_type="overdose",
                    severity=SeverityLevel.CRITICAL,
                    title="Maksimum Günlük Doz Aşıldı",
                    message=f"{medication.medication_name} için günlük maksimum doz aşıldı",
                    requires_action=True
                )
                
                self.db.add(alert)
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Doz uyarı kontrolü hatası: {str(e)}")
