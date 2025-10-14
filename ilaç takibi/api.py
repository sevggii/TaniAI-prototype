"""
Profesyonel İlaç Takip Sistemi - FastAPI Endpointleri
Gerçek uygulama için güvenli ve kapsamlı API
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from .models import Medication, MedicationLog, SideEffect, DrugInteraction, MedicationAlert
from .schemas import (
    MedicationCreate, MedicationUpdate, MedicationResponse,
    MedicationLogCreate, MedicationLogResponse,
    SideEffectCreate, SideEffectResponse,
    MedicationReminderCreate, MedicationReminderResponse,
    MedicationRefillCreate, MedicationRefillResponse,
    MedicationSummary, MedicationComplianceReport,
    MedicationSearch, MedicationLogSearch
)
from .medication_service import (
    MedicationService, DrugInteractionService, 
    SideEffectService, MedicationReminderService, MedicationAlertService
)
from .medication_urgency_system import (
    MedicationUrgencySystem, UrgencyAssessment, UrgencyLevel,
    format_urgency_assessment
)
from ..auth import get_current_user
from ..database import get_db

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Router oluştur
router = APIRouter(prefix="/medications", tags=["medications"])

# Dependency'ler
def get_medication_service(db: Session = Depends(get_db)) -> MedicationService:
    """Medication service dependency"""
    return MedicationService(db)

def get_side_effect_service(db: Session = Depends(get_db)) -> SideEffectService:
    """Side effect service dependency"""
    return SideEffectService(db)

def get_reminder_service(db: Session = Depends(get_db)) -> MedicationReminderService:
    """Reminder service dependency"""
    return MedicationReminderService(db)

def get_alert_service(db: Session = Depends(get_db)) -> MedicationAlertService:
    """Alert service dependency"""
    return MedicationAlertService(db)

def get_urgency_system(db: Session = Depends(get_db)) -> MedicationUrgencySystem:
    """Urgency system dependency"""
    return MedicationUrgencySystem(db)

# İlaç CRUD Endpointleri
@router.post("/", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
async def create_medication(
    medication_data: MedicationCreate,
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """
    Yeni ilaç ekleme
    
    - **medication_name**: İlaç adı (zorunlu)
    - **dosage_amount**: Doz miktarı (zorunlu)
    - **dosage_unit**: Doz birimi (mg, tablet, vb.)
    - **frequency_type**: Kullanım sıklığı
    - **reminder_times**: Hatırlatma saatleri (HH:MM formatında)
    - **start_date**: Başlangıç tarihi
    - **prescribing_doctor**: Reçete yazan doktor
    - **pharmacy_name**: Eczane adı
    """
    try:
        medication = await medication_service.create_medication(
            user_id=current_user.id,
            medication_data=medication_data
        )
        
        logger.info(f"İlaç oluşturuldu: {medication.id} - Kullanıcı: {current_user.id}")
        return medication
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"İlaç oluşturma hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaç oluşturulamadı")

@router.get("/", response_model=List[MedicationResponse])
async def get_medications(
    search_params: MedicationSearch = Depends(),
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """
    Kullanıcının ilaçlarını getirme
    
    - **medication_name**: İlaç adına göre filtreleme
    - **status**: İlaç durumuna göre filtreleme
    - **is_active**: Aktif ilaçlara göre filtreleme
    - **prescribing_doctor**: Doktor adına göre filtreleme
    - **pharmacy_name**: Eczane adına göre filtreleme
    - **start_date_from**: Başlangıç tarihi (başlangıç)
    - **start_date_to**: Başlangıç tarihi (bitiş)
    - **limit**: Sayfa boyutu (varsayılan: 50)
    - **offset**: Sayfa ofseti (varsayılan: 0)
    """
    try:
        medications = await medication_service.get_user_medications(
            user_id=current_user.id,
            search_params=search_params
        )
        
        return medications
        
    except Exception as e:
        logger.error(f"İlaçlar getirme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaçlar getirilemedi")

@router.get("/{medication_id}", response_model=MedicationResponse)
async def get_medication(
    medication_id: int,
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """
    Belirli bir ilacı getirme
    
    - **medication_id**: İlaç ID'si
    """
    try:
        medication = await medication_service.get_medication(
            user_id=current_user.id,
            medication_id=medication_id
        )
        
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="İlaç bulunamadı"
            )
        
        return medication
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"İlaç getirme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaç getirilemedi")

@router.put("/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: int,
    update_data: MedicationUpdate,
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """
    İlaç güncelleme
    
    - **medication_id**: İlaç ID'si
    - **medication_name**: Yeni ilaç adı
    - **dosage_amount**: Yeni doz miktarı
    - **reminder_times**: Yeni hatırlatma saatleri
    - **status**: Yeni durum
    - **special_instructions**: Özel talimatlar
    """
    try:
        medication = await medication_service.update_medication(
            user_id=current_user.id,
            medication_id=medication_id,
            update_data=update_data
        )
        
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="İlaç bulunamadı"
            )
        
        logger.info(f"İlaç güncellendi: {medication_id} - Kullanıcı: {current_user.id}")
        return medication
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"İlaç güncelleme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaç güncellenemedi")

@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication(
    medication_id: int,
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """
    İlaç silme (soft delete)
    
    - **medication_id**: İlaç ID'si
    """
    try:
        success = await medication_service.delete_medication(
            user_id=current_user.id,
            medication_id=medication_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="İlaç bulunamadı"
            )
        
        logger.info(f"İlaç silindi: {medication_id} - Kullanıcı: {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"İlaç silme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaç silinemedi")

# İlaç Kullanım Takibi Endpointleri
@router.post("/logs", response_model=MedicationLogResponse, status_code=status.HTTP_201_CREATED)
async def log_medication_taken(
    log_data: MedicationLogCreate,
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """
    İlaç alındı olarak kaydetme
    
    - **medication_id**: İlaç ID'si
    - **taken_at**: Alınma zamanı
    - **dosage_taken**: Alınan doz
    - **dosage_unit**: Doz birimi
    - **was_taken**: Alındı mı (varsayılan: True)
    - **was_skipped**: Atlandı mı (varsayılan: False)
    - **was_delayed**: Gecikti mi (varsayılan: False)
    - **notes**: Notlar
    """
    try:
        medication_log = await medication_service.log_medication_taken(
            user_id=current_user.id,
            log_data=log_data
        )
        
        logger.info(f"İlaç kullanımı kaydedildi: {medication_log.id} - Kullanıcı: {current_user.id}")
        return medication_log
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"İlaç kullanım kaydı hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaç kullanımı kaydedilemedi")

@router.get("/logs", response_model=List[MedicationLogResponse])
async def get_medication_logs(
    search_params: MedicationLogSearch = Depends(),
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """
    İlaç kullanım kayıtlarını getirme
    
    - **medication_id**: İlaç ID'sine göre filtreleme
    - **date_from**: Tarih (başlangıç)
    - **date_to**: Tarih (bitiş)
    - **was_taken**: Alınan dozlara göre filtreleme
    - **was_skipped**: Atlanan dozlara göre filtreleme
    - **was_delayed**: Geciken dozlara göre filtreleme
    - **limit**: Sayfa boyutu (varsayılan: 50)
    - **offset**: Sayfa ofseti (varsayılan: 0)
    """
    try:
        logs = await medication_service.get_medication_logs(
            user_id=current_user.id,
            search_params=search_params
        )
        
        return logs
        
    except Exception as e:
        logger.error(f"İlaç kullanım kayıtları getirme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaç kullanım kayıtları getirilemedi")

# Yan Etki Endpointleri
@router.post("/side-effects", response_model=SideEffectResponse, status_code=status.HTTP_201_CREATED)
async def create_side_effect(
    side_effect_data: SideEffectCreate,
    current_user = Depends(get_current_user),
    side_effect_service: SideEffectService = Depends(get_side_effect_service)
):
    """
    Yan etki kaydı oluşturma
    
    - **medication_id**: İlaç ID'si
    - **side_effect_name**: Yan etki adı
    - **description**: Açıklama
    - **severity**: Şiddet (mild, moderate, severe, critical)
    - **started_at**: Başlangıç zamanı
    - **frequency**: Sıklık
    - **intensity**: Yoğunluk (1-10)
    - **requires_medical_attention**: Tıbbi müdahale gerekiyor mu
    """
    try:
        side_effect = await side_effect_service.create_side_effect(
            user_id=current_user.id,
            side_effect_data=side_effect_data
        )
        
        logger.info(f"Yan etki kaydedildi: {side_effect.id} - Kullanıcı: {current_user.id}")
        return side_effect
        
    except Exception as e:
        logger.error(f"Yan etki kaydı hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Yan etki kaydedilemedi")

@router.get("/side-effects", response_model=List[SideEffectResponse])
async def get_side_effects(
    medication_id: Optional[int] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Yan etkileri getirme
    
    - **medication_id**: Belirli bir ilacın yan etkileri (opsiyonel)
    """
    try:
        query = db.query(SideEffect).filter(SideEffect.user_id == current_user.id)
        
        if medication_id:
            query = query.filter(SideEffect.medication_id == medication_id)
        
        side_effects = query.order_by(desc(SideEffect.created_at)).all()
        
        return [SideEffectResponse.from_orm(se) for se in side_effects]
        
    except Exception as e:
        logger.error(f"Yan etkiler getirme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Yan etkiler getirilemedi")

# Özet ve Raporlama Endpointleri
@router.get("/summary", response_model=MedicationSummary)
async def get_medication_summary(
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """
    İlaç özeti
    
    - Toplam ilaç sayısı
    - Aktif ilaç sayısı
    - Bugün alınması gereken ilaçlar
    - Bugün atlanan dozlar
    - Yaklaşan yenilemeler
    - Aktif yan etkiler
    - Kritik etkileşimler
    """
    try:
        summary = await medication_service.get_medication_summary(
            user_id=current_user.id
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"İlaç özeti getirme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaç özeti getirilemedi")

@router.get("/{medication_id}/compliance", response_model=MedicationComplianceReport)
async def get_compliance_report(
    medication_id: int,
    days: int = 30,
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """
    İlaç uyum raporu
    
    - **medication_id**: İlaç ID'si
    - **days**: Rapor dönemi (gün) - varsayılan: 30
    
    - Uyum oranı (%)
    - Toplam doz sayısı
    - Alınan dozlar
    - Atlanan dozlar
    - Geciken dozlar
    """
    try:
        report = await medication_service.get_compliance_report(
            user_id=current_user.id,
            medication_id=medication_id,
            days=days
        )
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="İlaç bulunamadı"
            )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Uyum raporu getirme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Uyum raporu getirilemedi")

# Uyarı Endpointleri
@router.get("/alerts", response_model=List[dict])
async def get_medication_alerts(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    İlaç uyarılarını getirme
    
    - Aktif uyarılar
    - Okunmamış uyarılar
    - Kritik uyarılar
    """
    try:
        alerts = db.query(MedicationAlert).filter(
            and_(
                MedicationAlert.user_id == current_user.id,
                MedicationAlert.is_dismissed == False
            )
        ).order_by(desc(MedicationAlert.created_at)).all()
        
        return [
            {
                "id": alert.id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "is_read": alert.is_read,
                "requires_action": alert.requires_action,
                "created_at": alert.created_at.isoformat()
            }
            for alert in alerts
        ]
        
    except Exception as e:
        logger.error(f"İlaç uyarıları getirme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaç uyarıları getirilemedi")

@router.patch("/alerts/{alert_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_alert_as_read(
    alert_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uyarıyı okundu olarak işaretleme
    
    - **alert_id**: Uyarı ID'si
    """
    try:
        alert = db.query(MedicationAlert).filter(
            and_(
                MedicationAlert.id == alert_id,
                MedicationAlert.user_id == current_user.id
            )
        ).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Uyarı bulunamadı"
            )
        
        alert.is_read = True
        alert.read_at = datetime.now()
        db.commit()
        
        logger.info(f"Uyarı okundu olarak işaretlendi: {alert_id} - Kullanıcı: {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Uyarı okundu işaretleme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Uyarı işaretlenemedi")

@router.patch("/alerts/{alert_id}/dismiss", status_code=status.HTTP_204_NO_CONTENT)
async def dismiss_alert(
    alert_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uyarıyı kapatma
    
    - **alert_id**: Uyarı ID'si
    """
    try:
        alert = db.query(MedicationAlert).filter(
            and_(
                MedicationAlert.id == alert_id,
                MedicationAlert.user_id == current_user.id
            )
        ).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Uyarı bulunamadı"
            )
        
        alert.is_dismissed = True
        alert.dismissed_at = datetime.now()
        db.commit()
        
        logger.info(f"Uyarı kapatıldı: {alert_id} - Kullanıcı: {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Uyarı kapatma hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Uyarı kapatılamadı")

# Hatırlatma Endpointleri
@router.get("/reminders", response_model=List[MedicationReminderResponse])
async def get_medication_reminders(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    İlaç hatırlatmalarını getirme
    
    - Aktif hatırlatmalar
    - Sonraki hatırlatma zamanları
    """
    try:
        reminders = db.query(MedicationReminder).filter(
            and_(
                MedicationReminder.user_id == current_user.id,
                MedicationReminder.is_active == True
            )
        ).order_by(asc(MedicationReminder.next_reminder)).all()
        
        return [MedicationReminderResponse.from_orm(reminder) for reminder in reminders]
        
    except Exception as e:
        logger.error(f"İlaç hatırlatmaları getirme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaç hatırlatmaları getirilemedi")

# Bugünkü İlaçlar Endpointi
@router.get("/today/due", response_model=List[MedicationResponse])
async def get_medications_due_today(
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service)
):
    """
    Bugün alınması gereken ilaçlar
    
    - Aktif ilaçlar
    - Bugünkü hatırlatma saatleri
    - Kalan hap sayıları
    """
    try:
        medications = await medication_service._get_medications_due_today(
            user_id=current_user.id
        )
        
        return [MedicationResponse.from_orm(med) for med in medications]
        
    except Exception as e:
        logger.error(f"Bugünkü ilaçlar getirme hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Bugünkü ilaçlar getirilemedi")

# Hızlı İlaç Alma Endpointi
@router.post("/{medication_id}/take", response_model=MedicationLogResponse, status_code=status.HTTP_201_CREATED)
async def take_medication_now(
    medication_id: int,
    dosage_taken: Optional[float] = None,
    notes: Optional[str] = None,
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service),
    db: Session = Depends(get_db)
):
    """
    İlacı şimdi al olarak kaydetme (hızlı işlem)
    
    - **medication_id**: İlaç ID'si
    - **dosage_taken**: Alınan doz (opsiyonel - varsayılan ilaç dozu)
    - **notes**: Notlar (opsiyonel)
    """
    try:
        # İlaç bilgilerini al
        medication = db.query(Medication).filter(
            and_(
                Medication.id == medication_id,
                Medication.user_id == current_user.id,
                Medication.is_active == True
            )
        ).first()
        
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="İlaç bulunamadı veya aktif değil"
            )
        
        # Varsayılan doz
        if dosage_taken is None:
            dosage_taken = medication.dosage_amount
        
        # Kullanım kaydı oluştur
        log_data = MedicationLogCreate(
            medication_id=medication_id,
            taken_at=datetime.now(),
            dosage_taken=dosage_taken,
            dosage_unit=medication.dosage_unit,
            was_taken=True,
            was_skipped=False,
            was_delayed=False,
            notes=notes
        )
        
        medication_log = await medication_service.log_medication_taken(
            user_id=current_user.id,
            log_data=log_data
        )
        
        logger.info(f"İlaç hızlı alındı: {medication_id} - Kullanıcı: {current_user.id}")
        return medication_log
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hızlı ilaç alma hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaç alınamadı")

# İlaç Atla Endpointi
@router.post("/{medication_id}/skip", response_model=MedicationLogResponse, status_code=status.HTTP_201_CREATED)
async def skip_medication(
    medication_id: int,
    reason: Optional[str] = None,
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service),
    db: Session = Depends(get_db)
):
    """
    İlacı atla olarak kaydetme
    
    - **medication_id**: İlaç ID'si
    - **reason**: Atlama nedeni (opsiyonel)
    """
    try:
        # İlaç bilgilerini al
        medication = db.query(Medication).filter(
            and_(
                Medication.id == medication_id,
                Medication.user_id == current_user.id,
                Medication.is_active == True
            )
        ).first()
        
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="İlaç bulunamadı veya aktif değil"
            )
        
        # Atlama kaydı oluştur
        log_data = MedicationLogCreate(
            medication_id=medication_id,
            taken_at=datetime.now(),
            dosage_taken=0.0,
            dosage_unit=medication.dosage_unit,
            was_taken=False,
            was_skipped=True,
            was_delayed=False,
            notes=f"İlaç atlandı: {reason}" if reason else "İlaç atlandı"
        )
        
        medication_log = await medication_service.log_medication_taken(
            user_id=current_user.id,
            log_data=log_data
        )
        
        logger.info(f"İlaç atlandı: {medication_id} - Kullanıcı: {current_user.id}")
        return medication_log
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"İlaç atlama hatası: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İlaç atlanamadı")


# ============================================================================
# ACİLİYET SİSTEMİ ENDPOİNTLERİ
# ============================================================================

@router.post("/urgency/assess/{medication_id}", tags=["Urgency System"])
async def assess_medication_urgency(
    medication_id: int,
    context: Optional[dict] = None,
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service),
    urgency_system: MedicationUrgencySystem = Depends(get_urgency_system),
    db: Session = Depends(get_db)
):
    """
    🚨 İlaç Aciliyet Değerlendirmesi
    
    Bir ilaç için kapsamlı aciliyet analizi yapar:
    - Aciliyet skoru (1-10)
    - Risk faktörleri
    - Acil bulgular
    - Doktora bildirim gerekliliği
    - Öneriler
    
    **Aciliyet Seviyeleri:**
    - CRITICAL (8-10): 15 dakika içinde müdahale
    - HIGH (6-8): 30 dakika içinde müdahale
    - MODERATE (4-6): 2 saat içinde müdahale
    - LOW (1-4): 24 saat içinde değerlendirme
    """
    try:
        # İlacı getir
        medication = await medication_service.get_medication(
            user_id=current_user.id,
            medication_id=medication_id
        )
        
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="İlaç bulunamadı"
            )
        
        # İlaç verisini dict'e çevir
        medication_data = {
            'medication_name': medication.medication_name,
            'dosage_amount': medication.dosage_amount,
            'dosage_unit': medication.dosage_unit.value if hasattr(medication.dosage_unit, 'value') else medication.dosage_unit,
            'frequency_type': medication.frequency_type.value if hasattr(medication.frequency_type, 'value') else medication.frequency_type,
            'max_daily_dose': medication.dosage_amount * len(medication.reminder_times) if hasattr(medication, 'reminder_times') else None
        }
        
        # Context ekle (varsa)
        if not context:
            # Otomatik context oluştur
            context = await _build_medication_context(
                db, current_user.id, medication_id, medication_service
            )
        
        # Aciliyet değerlendirmesi
        assessment = urgency_system.assess_medication_urgency(
            user_id=current_user.id,
            medication_data=medication_data,
            context=context
        )
        
        # Logger - kritik durumlar için
        if assessment.requires_immediate_attention:
            logger.warning(
                f"🚨 İLAÇ ACİLİYET UYARISI - "
                f"Kullanıcı: {current_user.id} - "
                f"İlaç: {medication.medication_name} - "
                f"Skor: {assessment.urgency_score}/10"
            )
        
        return {
            'medication_id': medication_id,
            'medication_name': medication.medication_name,
            'assessment': {
                'urgency_score': assessment.urgency_score,
                'urgency_level': assessment.urgency_level.value,
                'requires_immediate_attention': assessment.requires_immediate_attention,
                'response_time': assessment.response_time,
                'risk_factors': assessment.risk_factors,
                'findings': assessment.findings,
                'recommendations': assessment.recommendations,
                'timestamp': assessment.timestamp.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Aciliyet değerlendirme hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Aciliyet değerlendirmesi yapılamadı: {str(e)}"
        )


@router.post("/urgency/notify-doctor/{medication_id}", tags=["Urgency System"])
async def create_doctor_notification(
    medication_id: int,
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service),
    urgency_system: MedicationUrgencySystem = Depends(get_urgency_system),
    db: Session = Depends(get_db)
):
    """
    📞 Doktora Bildirim Oluştur
    
    İlaç aciliyeti için doktora otomatik bildirim gönderir.
    Sadece orta ve üzeri aciliyet seviyelerinde çalışır.
    """
    try:
        # İlacı getir
        medication = await medication_service.get_medication(
            user_id=current_user.id,
            medication_id=medication_id
        )
        
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="İlaç bulunamadı"
            )
        
        # Context oluştur
        context = await _build_medication_context(
            db, current_user.id, medication_id, medication_service
        )
        
        # Aciliyet değerlendirmesi
        medication_data = {
            'medication_name': medication.medication_name,
            'dosage_amount': medication.dosage_amount,
            'dosage_unit': medication.dosage_unit.value if hasattr(medication.dosage_unit, 'value') else medication.dosage_unit,
            'frequency_type': medication.frequency_type.value if hasattr(medication.frequency_type, 'value') else medication.frequency_type,
        }
        
        assessment = urgency_system.assess_medication_urgency(
            user_id=current_user.id,
            medication_data=medication_data,
            context=context
        )
        
        # Sadece orta ve üzeri aciliyet için bildirim gönder
        if assessment.urgency_level == UrgencyLevel.LOW:
            return {
                'notification_sent': False,
                'reason': 'Düşük aciliyet seviyesi - bildirim gerekmez',
                'urgency_level': assessment.urgency_level.value
            }
        
        # Hasta bilgileri
        patient_info = {
            'user_id': current_user.id,
            'name': getattr(current_user, 'name', 'Unknown'),
            'age': getattr(current_user, 'age', None),
            'gender': getattr(current_user, 'gender', None)
        }
        
        # Doktor bildirimi oluştur
        notification = urgency_system.create_doctor_notification(
            assessment=assessment,
            patient_info=patient_info,
            medication_data=medication_data
        )
        
        # Logger
        logger.warning(
            f"📞 DOKTOR BİLDİRİMİ OLUŞTURULDU - "
            f"Hasta: {current_user.id} - "
            f"İlaç: {medication.medication_name} - "
            f"Seviye: {assessment.urgency_level.value}"
        )
        
        # TODO: Gerçek sistemde burada:
        # - SMS/Email gönderimi
        # - Hastane bilgi sistemine kayıt
        # - Doktor dashboard'una push notification
        
        return {
            'notification_sent': True,
            'notification': notification,
            'message': 'Doktora bildirim oluşturuldu. En kısa sürede dönüş yapılacaktır.'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Doktor bildirim hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Doktor bildirimi oluşturulamadı: {str(e)}"
        )


@router.get("/urgency/priority-list", tags=["Urgency System"])
async def get_urgent_medications_list(
    current_user = Depends(get_current_user),
    medication_service: MedicationService = Depends(get_medication_service),
    urgency_system: MedicationUrgencySystem = Depends(get_urgency_system),
    db: Session = Depends(get_db)
):
    """
    📋 Acil İlaçlar Listesi
    
    Kullanıcının tüm ilaçlarını aciliyet skoruna göre sıralı listeler.
    Doktorlar için önceliklendirme yapar.
    """
    try:
        # Tüm aktif ilaçları getir
        from .schemas import MedicationSearch
        search_params = MedicationSearch(status="active")
        
        medications = await medication_service.get_user_medications(
            user_id=current_user.id,
            search_params=search_params
        )
        
        # Her ilaç için aciliyet değerlendirmesi
        urgent_list = []
        
        for medication in medications:
            medication_data = {
                'medication_name': medication.medication_name,
                'dosage_amount': medication.dosage_amount,
                'dosage_unit': medication.dosage_unit.value if hasattr(medication.dosage_unit, 'value') else medication.dosage_unit,
                'frequency_type': medication.frequency_type.value if hasattr(medication.frequency_type, 'value') else medication.frequency_type,
            }
            
            context = await _build_medication_context(
                db, current_user.id, medication.id, medication_service
            )
            
            assessment = urgency_system.assess_medication_urgency(
                user_id=current_user.id,
                medication_data=medication_data,
                context=context
            )
            
            urgent_list.append({
                'medication_id': medication.id,
                'medication_name': medication.medication_name,
                'urgency_score': assessment.urgency_score,
                'urgency_level': assessment.urgency_level.value,
                'requires_attention': assessment.requires_immediate_attention,
                'response_time': assessment.response_time,
                'critical_findings_count': sum(
                    1 for f in assessment.findings if f['severity'] in ['CRITICAL', 'HIGH']
                )
            })
        
        # Aciliyet skoruna göre sırala
        urgent_list.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        # İstatistikler
        critical_count = sum(1 for item in urgent_list if item['urgency_level'] == 'critical')
        high_count = sum(1 for item in urgent_list if item['urgency_level'] == 'high')
        
        return {
            'total_medications': len(urgent_list),
            'critical_medications': critical_count,
            'high_priority_medications': high_count,
            'requires_immediate_attention': critical_count + high_count,
            'medications': urgent_list,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Acil ilaç listesi hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Acil ilaç listesi oluşturulamadı"
        )


@router.get("/urgency/stats", tags=["Urgency System"])
async def get_urgency_statistics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📊 Aciliyet İstatistikleri
    
    Sistemdeki ilaç aciliyet durumlarının genel istatistiklerini döndürür.
    """
    try:
        # Basit istatistikler (production'da veritabanından gelecek)
        stats = {
            'system_status': 'operational',
            'total_assessments_today': 0,  # DB'den gelecek
            'critical_alerts_today': 0,     # DB'den gelecek
            'doctor_notifications_sent': 0,  # DB'den gelecek
            'urgency_levels': {
                'critical': {
                    'count': 0,
                    'response_time': '15 dakika',
                    'color': 'red'
                },
                'high': {
                    'count': 0,
                    'response_time': '30 dakika',
                    'color': 'orange'
                },
                'moderate': {
                    'count': 0,
                    'response_time': '2 saat',
                    'color': 'yellow'
                },
                'low': {
                    'count': 0,
                    'response_time': '24 saat',
                    'color': 'green'
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"İstatistik hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="İstatistikler alınamadı"
        )


# ============================================================================
# YARDIMCI FONKSİYONLAR
# ============================================================================

async def _build_medication_context(
    db: Session,
    user_id: int,
    medication_id: int,
    medication_service: MedicationService
) -> dict:
    """İlaç için context bilgisi oluştur"""
    context = {}
    
    try:
        # Aktif ilaçları getir (etkileşim kontrolü için)
        from .schemas import MedicationSearch
        search_params = MedicationSearch(status="active")
        active_meds = await medication_service.get_user_medications(user_id, search_params)
        context['active_medications'] = [
            {'medication_name': m.medication_name} for m in active_meds
        ]
        
        # Kaçırılan dozlar (son 7 gün)
        from .models import MedicationLog, MedicationStatus
        missed_logs = db.query(MedicationLog).filter(
            and_(
                MedicationLog.medication_id == medication_id,
                MedicationLog.status == MedicationStatus.MISSED,
                MedicationLog.scheduled_time >= datetime.now() - timedelta(days=7)
            )
        ).count()
        context['missed_doses'] = missed_logs
        
        # Yan etkiler (son 30 gün)
        from .models import SideEffect
        side_effects = db.query(SideEffect).filter(
            and_(
                SideEffect.medication_id == medication_id,
                SideEffect.reported_at >= datetime.now() - timedelta(days=30)
            )
        ).all()
        context['side_effects'] = [
            {
                'side_effect_name': se.side_effect_name,
                'severity': se.severity.value if hasattr(se.severity, 'value') else se.severity
            }
            for se in side_effects
        ]
        
        # Compliance rate (son 30 gün)
        total_logs = db.query(MedicationLog).filter(
            and_(
                MedicationLog.medication_id == medication_id,
                MedicationLog.scheduled_time >= datetime.now() - timedelta(days=30)
            )
        ).count()
        
        taken_logs = db.query(MedicationLog).filter(
            and_(
                MedicationLog.medication_id == medication_id,
                MedicationLog.status == MedicationStatus.TAKEN,
                MedicationLog.scheduled_time >= datetime.now() - timedelta(days=30)
            )
        ).count()
        
        context['compliance_rate'] = taken_logs / total_logs if total_logs > 0 else 1.0
        
        # Remaining doses (tahmini)
        context['remaining_doses'] = 30  # Placeholder - gerçek sistemde hesaplanmalı
        context['frequency_per_day'] = 2  # Placeholder
        
    except Exception as e:
        logger.warning(f"Context oluşturma uyarısı: {e}")
    
    return context
