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
