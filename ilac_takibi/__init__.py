"""
Profesyonel İlaç Takip Sistemi
Gerçek uygulama için güvenli ve kapsamlı ilaç yönetimi
"""

__version__ = "1.0.0"
__author__ = "TanıAI Team"
__description__ = "Profesyonel İlaç Takip Sistemi"

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
    MedicationSummary, MedicationComplianceReport
)

from .medication_service import (
    MedicationService, DrugInteractionService,
    SideEffectService, MedicationReminderService, MedicationAlertService
)

from .safety_validations import (
    SafetyValidationService, CriticalSafetyChecks
)

__all__ = [
    # Models
    "Medication", "MedicationLog", "SideEffect", "DrugInteraction",
    "MedicationReminder", "MedicationAlert", "MedicationRefill",
    "MedicationStatus", "DosageUnit", "FrequencyType", "SeverityLevel",
    
    # Schemas
    "MedicationCreate", "MedicationUpdate", "MedicationResponse",
    "MedicationLogCreate", "MedicationLogResponse",
    "SideEffectCreate", "SideEffectResponse",
    "MedicationReminderCreate", "MedicationReminderResponse",
    "MedicationRefillCreate", "MedicationRefillResponse",
    "MedicationSummary", "MedicationComplianceReport",
    
    # Services
    "MedicationService", "DrugInteractionService",
    "SideEffectService", "MedicationReminderService", "MedicationAlertService",
    
    # Safety
    "SafetyValidationService", "CriticalSafetyChecks"
]
