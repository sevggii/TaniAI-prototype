"""
Basit İlaç Takibi API
Flutter uygulaması için basit FastAPI endpoint'leri
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

app = FastAPI(title="İlaç Takibi API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic modelleri
class MedicationCreate(BaseModel):
    medication_name: str
    dosage_amount: float
    dosage_unit: str
    frequency_type: str
    reminder_times: List[str]
    start_date: Optional[str] = None
    prescribing_doctor: Optional[str] = None
    pharmacy_name: Optional[str] = None
    special_instructions: Optional[str] = None
    requires_food: bool = False
    requires_water: bool = True
    remaining_pills: Optional[int] = None
    refill_reminder_days: int = 7

class MedicationResponse(BaseModel):
    id: int
    user_id: int
    medication_name: str
    dosage_amount: float
    dosage_unit: str
    frequency_type: str
    reminder_times: List[str]
    start_date: str
    status: str
    is_active: bool
    prescribing_doctor: Optional[str] = None
    pharmacy_name: Optional[str] = None
    special_instructions: Optional[str] = None
    requires_food: bool
    requires_water: bool
    remaining_pills: Optional[int] = None
    refill_reminder_days: int
    created_at: str
    updated_at: str

class MedicationLogCreate(BaseModel):
    medication_id: int
    taken_at: Optional[str] = None
    dosage_taken: float
    dosage_unit: str
    was_taken: bool = True
    was_skipped: bool = False
    was_delayed: bool = False
    notes: Optional[str] = None

class MedicationLogResponse(BaseModel):
    id: int
    medication_id: int
    user_id: int
    taken_at: str
    dosage_taken: float
    dosage_unit: str
    was_taken: bool
    was_skipped: bool
    was_delayed: bool
    notes: Optional[str] = None
    created_at: str

class MedicationSummary(BaseModel):
    total_medications: int
    active_medications: int
    medications_due_today: int
    missed_doses_today: int
    upcoming_refills: int
    active_side_effects: int
    critical_interactions: int

class MedicationAlert(BaseModel):
    id: int
    user_id: int
    alert_type: str
    severity: str
    title: str
    message: str
    is_read: bool
    is_dismissed: bool
    requires_action: bool
    created_at: str

# Mock data
medications_db = [
    {
        "id": 1,
        "user_id": 1,
        "medication_name": "Paracetamol",
        "dosage_amount": 500,
        "dosage_unit": "mg",
        "frequency_type": "twice_daily",
        "reminder_times": ["08:00", "20:00"],
        "start_date": "2024-01-01T00:00:00",
        "status": "active",
        "is_active": True,
        "prescribing_doctor": "Dr. Ahmet Yılmaz",
        "pharmacy_name": "Merkez Eczanesi",
        "special_instructions": "Yemekle birlikte alın",
        "requires_food": True,
        "requires_water": True,
        "remaining_pills": 15,
        "refill_reminder_days": 7,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    },
    {
        "id": 2,
        "user_id": 1,
        "medication_name": "Vitamin D3",
        "dosage_amount": 1000,
        "dosage_unit": "iu",
        "frequency_type": "daily",
        "reminder_times": ["09:00"],
        "start_date": "2024-01-15T00:00:00",
        "status": "active",
        "is_active": True,
        "prescribing_doctor": "Dr. Ayşe Demir",
        "pharmacy_name": "Sağlık Eczanesi",
        "special_instructions": "Sabah alın",
        "requires_food": True,
        "requires_water": True,
        "remaining_pills": 25,
        "refill_reminder_days": 7,
        "created_at": "2024-01-15T00:00:00",
        "updated_at": "2024-01-15T00:00:00",
    }
]

medication_logs_db = [
    {
        "id": 1,
        "medication_id": 1,
        "user_id": 1,
        "taken_at": "2024-01-20T08:00:00",
        "dosage_taken": 500,
        "dosage_unit": "mg",
        "was_taken": True,
        "was_skipped": False,
        "was_delayed": False,
        "notes": None,
        "created_at": "2024-01-20T08:00:00",
    },
    {
        "id": 2,
        "medication_id": 2,
        "user_id": 1,
        "taken_at": "2024-01-20T09:00:00",
        "dosage_taken": 1000,
        "dosage_unit": "iu",
        "was_taken": True,
        "was_skipped": False,
        "was_delayed": False,
        "notes": None,
        "created_at": "2024-01-20T09:00:00",
    }
]

alerts_db = [
    {
        "id": 1,
        "user_id": 1,
        "alert_type": "refill",
        "severity": "mild",
        "title": "İlaç Yenileme Hatırlatması",
        "message": "Paracetamol yenilenmesi gerekiyor",
        "is_read": False,
        "is_dismissed": False,
        "requires_action": True,
        "created_at": "2024-01-20T10:00:00",
    }
]

# API Endpoints
@app.get("/")
async def root():
    return {"message": "İlaç Takibi API", "version": "1.0.0"}

@app.get("/medications/", response_model=List[MedicationResponse])
async def get_medications():
    """Kullanıcının ilaçlarını getir"""
    return [MedicationResponse(**med) for med in medications_db]

@app.get("/medications/{medication_id}", response_model=MedicationResponse)
async def get_medication(medication_id: int):
    """Belirli bir ilacı getir"""
    for med in medications_db:
        if med["id"] == medication_id:
            return MedicationResponse(**med)
    raise HTTPException(status_code=404, detail="İlaç bulunamadı")

@app.post("/medications/", response_model=MedicationResponse, status_code=201)
async def create_medication(medication: MedicationCreate):
    """Yeni ilaç ekle"""
    new_id = max([med["id"] for med in medications_db]) + 1 if medications_db else 1
    now = datetime.now().isoformat()
    
    new_medication = {
        "id": new_id,
        "user_id": 1,  # Mock user ID
        "medication_name": medication.medication_name,
        "dosage_amount": medication.dosage_amount,
        "dosage_unit": medication.dosage_unit,
        "frequency_type": medication.frequency_type,
        "reminder_times": medication.reminder_times,
        "start_date": medication.start_date or now,
        "status": "active",
        "is_active": True,
        "prescribing_doctor": medication.prescribing_doctor,
        "pharmacy_name": medication.pharmacy_name,
        "special_instructions": medication.special_instructions,
        "requires_food": medication.requires_food,
        "requires_water": medication.requires_water,
        "remaining_pills": medication.remaining_pills,
        "refill_reminder_days": medication.refill_reminder_days,
        "created_at": now,
        "updated_at": now,
    }
    
    medications_db.append(new_medication)
    return MedicationResponse(**new_medication)

@app.put("/medications/{medication_id}", response_model=MedicationResponse)
async def update_medication(medication_id: int, medication: MedicationCreate):
    """İlaç güncelle"""
    for i, med in enumerate(medications_db):
        if med["id"] == medication_id:
            updated_medication = {
                **med,
                "medication_name": medication.medication_name,
                "dosage_amount": medication.dosage_amount,
                "dosage_unit": medication.dosage_unit,
                "frequency_type": medication.frequency_type,
                "reminder_times": medication.reminder_times,
                "prescribing_doctor": medication.prescribing_doctor,
                "pharmacy_name": medication.pharmacy_name,
                "special_instructions": medication.special_instructions,
                "requires_food": medication.requires_food,
                "requires_water": medication.requires_water,
                "remaining_pills": medication.remaining_pills,
                "refill_reminder_days": medication.refill_reminder_days,
                "updated_at": datetime.now().isoformat(),
            }
            medications_db[i] = updated_medication
            return MedicationResponse(**updated_medication)
    raise HTTPException(status_code=404, detail="İlaç bulunamadı")

@app.delete("/medications/{medication_id}", status_code=204)
async def delete_medication(medication_id: int):
    """İlaç sil"""
    for i, med in enumerate(medications_db):
        if med["id"] == medication_id:
            medications_db[i]["is_active"] = False
            medications_db[i]["status"] = "discontinued"
            medications_db[i]["updated_at"] = datetime.now().isoformat()
            return
    raise HTTPException(status_code=404, detail="İlaç bulunamadı")

@app.get("/medications/logs", response_model=List[MedicationLogResponse])
async def get_medication_logs():
    """İlaç kullanım kayıtlarını getir"""
    return [MedicationLogResponse(**log) for log in medication_logs_db]

@app.post("/medications/logs", response_model=MedicationLogResponse, status_code=201)
async def log_medication_taken(log: MedicationLogCreate):
    """İlaç kullanım kaydı oluştur"""
    new_id = max([log["id"] for log in medication_logs_db]) + 1 if medication_logs_db else 1
    now = datetime.now().isoformat()
    
    new_log = {
        "id": new_id,
        "medication_id": log.medication_id,
        "user_id": 1,  # Mock user ID
        "taken_at": log.taken_at or now,
        "dosage_taken": log.dosage_taken,
        "dosage_unit": log.dosage_unit,
        "was_taken": log.was_taken,
        "was_skipped": log.was_skipped,
        "was_delayed": log.was_delayed,
        "notes": log.notes,
        "created_at": now,
    }
    
    medication_logs_db.append(new_log)
    return MedicationLogResponse(**new_log)

@app.post("/medications/{medication_id}/take", response_model=MedicationLogResponse, status_code=201)
async def take_medication_now(medication_id: int, dosage_taken: Optional[float] = None, notes: Optional[str] = None):
    """İlacı şimdi al olarak kaydet"""
    # İlaç bilgilerini bul
    medication = None
    for med in medications_db:
        if med["id"] == medication_id:
            medication = med
            break
    
    if not medication:
        raise HTTPException(status_code=404, detail="İlaç bulunamadı")
    
    new_id = max([log["id"] for log in medication_logs_db]) + 1 if medication_logs_db else 1
    now = datetime.now().isoformat()
    
    new_log = {
        "id": new_id,
        "medication_id": medication_id,
        "user_id": 1,
        "taken_at": now,
        "dosage_taken": dosage_taken or medication["dosage_amount"],
        "dosage_unit": medication["dosage_unit"],
        "was_taken": True,
        "was_skipped": False,
        "was_delayed": False,
        "notes": notes,
        "created_at": now,
    }
    
    medication_logs_db.append(new_log)
    
    # Kalan hap sayısını güncelle
    if medication["remaining_pills"] is not None:
        medication["remaining_pills"] = max(0, medication["remaining_pills"] - 1)
        medication["updated_at"] = now
    
    return MedicationLogResponse(**new_log)

@app.post("/medications/{medication_id}/skip", response_model=MedicationLogResponse, status_code=201)
async def skip_medication(medication_id: int, reason: Optional[str] = None):
    """İlacı atla olarak kaydet"""
    # İlaç bilgilerini bul
    medication = None
    for med in medications_db:
        if med["id"] == medication_id:
            medication = med
            break
    
    if not medication:
        raise HTTPException(status_code=404, detail="İlaç bulunamadı")
    
    new_id = max([log["id"] for log in medication_logs_db]) + 1 if medication_logs_db else 1
    now = datetime.now().isoformat()
    
    new_log = {
        "id": new_id,
        "medication_id": medication_id,
        "user_id": 1,
        "taken_at": now,
        "dosage_taken": 0.0,
        "dosage_unit": medication["dosage_unit"],
        "was_taken": False,
        "was_skipped": True,
        "was_delayed": False,
        "notes": f"İlaç atlandı: {reason}" if reason else "İlaç atlandı",
        "created_at": now,
    }
    
    medication_logs_db.append(new_log)
    return MedicationLogResponse(**new_log)

@app.get("/medications/today/due", response_model=List[MedicationResponse])
async def get_medications_due_today():
    """Bugün alınması gereken ilaçlar"""
    return [MedicationResponse(**med) for med in medications_db if med["is_active"] and med["status"] == "active"]

@app.get("/medications/summary", response_model=MedicationSummary)
async def get_medication_summary():
    """İlaç özeti"""
    active_medications = [med for med in medications_db if med["is_active"] and med["status"] == "active"]
    missed_doses_today = len([log for log in medication_logs_db if log["was_skipped"]])
    
    return MedicationSummary(
        total_medications=len(medications_db),
        active_medications=len(active_medications),
        medications_due_today=len(active_medications),
        missed_doses_today=missed_doses_today,
        upcoming_refills=len([med for med in active_medications if med["remaining_pills"] is not None and med["remaining_pills"] <= 7]),
        active_side_effects=0,
        critical_interactions=0,
    )

@app.get("/medications/alerts", response_model=List[MedicationAlert])
async def get_medication_alerts():
    """İlaç uyarılarını getir"""
    return [MedicationAlert(**alert) for alert in alerts_db if not alert["is_dismissed"]]

@app.patch("/medications/alerts/{alert_id}/read", status_code=204)
async def mark_alert_as_read(alert_id: int):
    """Uyarıyı okundu olarak işaretle"""
    for alert in alerts_db:
        if alert["id"] == alert_id:
            alert["is_read"] = True
            return
    raise HTTPException(status_code=404, detail="Uyarı bulunamadı")

@app.patch("/medications/alerts/{alert_id}/dismiss", status_code=204)
async def dismiss_alert(alert_id: int):
    """Uyarıyı kapat"""
    for alert in alerts_db:
        if alert["id"] == alert_id:
            alert["is_dismissed"] = True
            return
    raise HTTPException(status_code=404, detail="Uyarı bulunamadı")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
