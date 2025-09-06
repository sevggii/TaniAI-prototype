"""
TanıAI Güvenlik ve Konfigürasyon Ayarları
"""

import os
from typing import List

class SecurityConfig:
    """Güvenlik konfigürasyonu"""
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
    MAX_REQUESTS_PER_HOUR = int(os.getenv("MAX_REQUESTS_PER_HOUR", "1000"))
    
    # CORS ayarları
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000"
    ]
    
    # Trusted hosts
    TRUSTED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "*.localhost"
    ]
    
    # API güvenlik
    API_KEY_HEADER = "X-API-Key"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    # Veri doğrulama
    MAX_SYMPTOMS_PER_REQUEST = 50
    MAX_PATIENT_NAME_LENGTH = 100
    MIN_PATIENT_NAME_LENGTH = 2
    MAX_AGE = 120
    MIN_AGE = 0
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Model güvenlik
    MODEL_CONFIDENCE_THRESHOLD = 0.30  # Minimum güven eşiği
    MAX_PREDICTION_PROBABILITY = 0.95  # Maksimum olasılık eşiği

class MedicalConfig:
    """Tıbbi konfigürasyon"""
    
    # Risk eşikleri (tıbbi literatüre dayalı)
    HIGH_RISK_THRESHOLD = 0.75
    MEDIUM_RISK_THRESHOLD = 0.50
    LOW_RISK_THRESHOLD = 0.30
    
    # Nutrient prevalans oranları (gerçek dünya verilerine dayalı)
    NUTRIENT_PREVALENCE = {
        'D': 0.35,      # D vitamini eksikliği yaygın
        'B12': 0.15,    # B12 eksikliği orta
        'Demir': 0.25,  # Demir eksikliği yaygın
        'Cinko': 0.20,  # Çinko eksikliği orta
        'Magnezyum': 0.30,  # Magnezyum eksikliği yaygın
        'A': 0.10,      # A vitamini eksikliği nadir
        'C': 0.05,      # C vitamini eksikliği nadir
        'E': 0.08,      # E vitamini eksikliği nadir
        'B9': 0.12,     # Folat eksikliği orta
        'Kalsiyum': 0.18,  # Kalsiyum eksikliği orta
        'Potasyum': 0.15,  # Potasyum eksikliği orta
        'Selenyum': 0.10,  # Selenyum eksikliği nadir
        'HepatitB': 0.05,  # Hepatit B nadir
        'Gebelik': 0.08,   # Gebelik durumu
        'Tiroid': 0.12     # Tiroid bozukluğu orta
    }
    
    # Tıbbi uyarı mesajları
    MEDICAL_DISCLAIMER = "Bu teşhis yapay zeka destekli bir ön değerlendirmedir. Kesin tanı için doktor kontrolü gereklidir."
    HIGH_RISK_WARNING = "Yüksek risk tespit edildi. Acil doktor kontrolü önerilir."
    MEDIUM_RISK_WARNING = "Orta risk tespit edildi. Doktor kontrolü önerilir."

class ModelConfig:
    """Model konfigürasyonu"""
    
    # Model parametreleri
    RANDOM_FOREST_PARAMS = {
        'n_estimators': 300,
        'max_depth': 12,
        'min_samples_split': 3,
        'min_samples_leaf': 1,
        'max_features': 'sqrt',
        'class_weight': 'balanced',
        'random_state': 42,
        'n_jobs': -1
    }
    
    # Cross-validation
    CV_FOLDS = 5
    CV_RANDOM_STATE = 42
    
    # Eğitim verisi
    TRAINING_SAMPLES = 2000
    TEST_SIZE = 0.3
    VALIDATION_SIZE = 0.5
    
    # Model dosya yolları
    MODEL_DIR = "models"
    MODEL_EXTENSION = ".pkl"

# Konfigürasyon örnekleri
SECURITY_CONFIG = SecurityConfig()
MEDICAL_CONFIG = MedicalConfig()
MODEL_CONFIG = ModelConfig()






