"""
Enterprise-Grade Güvenlik konfigürasyon dosyası
Production-ready security settings with comprehensive protection
"""

import os
import hashlib
import secrets
from typing import List, Dict, Any
from datetime import timedelta

class SecurityConfig:
    """Enterprise-grade güvenlik ayarları"""
    
    # JWT Ayarları - Enhanced
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        # Development için fallback (production'da hata verecek)
        SECRET_KEY = "dev-secret-key-change-in-production"
        print("⚠️ WARNING: Using default SECRET_KEY. Set SECRET_KEY environment variable for production!")
    
    # Enhanced JWT settings
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    TOKEN_ISSUER = os.getenv("TOKEN_ISSUER", "taniai.com")
    TOKEN_AUDIENCE = os.getenv("TOKEN_AUDIENCE", "taniai-users")
    
    # CORS Ayarları - Enhanced
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080,http://localhost:5000").split(",")
    ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()]
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    ALLOWED_HEADERS = ["Authorization", "Content-Type", "X-Requested-With", "Accept", "X-API-Key"]
    
    # Rate Limiting - Enhanced
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "100"))
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    RATE_LIMIT_PER_DAY = int(os.getenv("RATE_LIMIT_PER_DAY", "10000"))
    
    # Enhanced Security Headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "X-Permitted-Cross-Domain-Policies": "none"
    }
    
    # Database Security - Enhanced
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # Encryption Settings
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", secrets.token_hex(32))
    HASH_ALGORITHM = "sha256"
    SALT_LENGTH = 32
    
    # Session Security
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))
    
    # API Security
    API_KEY_LENGTH = 32
    API_RATE_LIMIT_PER_MINUTE = int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "100"))
    
    # File Upload Security
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_FILE_TYPES = [".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"]
    UPLOAD_PATH = os.getenv("UPLOAD_PATH", "/tmp/uploads")
    
    # Audit Logging
    AUDIT_LOG_ENABLED = os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true"
    AUDIT_LOG_RETENTION_DAYS = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "90"))
    
    # Security Monitoring
    SECURITY_MONITORING_ENABLED = os.getenv("SECURITY_MONITORING_ENABLED", "true").lower() == "true"
    SUSPICIOUS_ACTIVITY_THRESHOLD = int(os.getenv("SUSPICIOUS_ACTIVITY_THRESHOLD", "10"))
    
    # Compliance Settings
    GDPR_COMPLIANCE = os.getenv("GDPR_COMPLIANCE", "true").lower() == "true"
    KVKK_COMPLIANCE = os.getenv("KVKK_COMPLIANCE", "true").lower() == "true"
    DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "2555"))  # 7 years
    
    # Backup Security
    BACKUP_ENCRYPTION = os.getenv("BACKUP_ENCRYPTION", "true").lower() == "true"
    BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    
    @classmethod
    def get_cors_config(cls) -> dict:
        """Enhanced CORS konfigürasyonu"""
        return {
            "allow_origins": cls.ALLOWED_ORIGINS,
            "allow_credentials": True,
            "allow_methods": cls.ALLOWED_METHODS,
            "allow_headers": cls.ALLOWED_HEADERS,
            "expose_headers": ["X-Total-Count", "X-Page-Count"],
            "max_age": 3600
        }
    
    @classmethod
    def is_production(cls) -> bool:
        """Production ortamı kontrolü"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    @classmethod
    def get_security_warnings(cls) -> List[str]:
        """Enhanced güvenlik uyarıları"""
        warnings = []
        
        if cls.SECRET_KEY == "dev-secret-key-change-in-production":
            warnings.append("SECRET_KEY environment variable not set")
        
        if "*" in cls.ALLOWED_ORIGINS:
            warnings.append("CORS allows all origins - security risk")
        
        if not cls.is_production():
            warnings.append("Running in development mode")
        
        if cls.ENCRYPTION_KEY == secrets.token_hex(32):
            warnings.append("Using default encryption key - set ENCRYPTION_KEY")
        
        if not cls.AUDIT_LOG_ENABLED:
            warnings.append("Audit logging is disabled")
        
        if not cls.SECURITY_MONITORING_ENABLED:
            warnings.append("Security monitoring is disabled")
        
        return warnings
    
    @classmethod
    def generate_api_key(cls) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(cls.API_KEY_LENGTH)
    
    @classmethod
    def hash_password(cls, password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(cls.SALT_LENGTH)
        
        password_hash = hashlib.pbkdf2_hmac(
            cls.HASH_ALGORITHM,
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        
        return password_hash.hex(), salt
    
    @classmethod
    def verify_password(cls, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        computed_hash, _ = cls.hash_password(password, salt)
        return computed_hash == password_hash
    
    @classmethod
    def get_rate_limit_config(cls) -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            "per_minute": cls.RATE_LIMIT_PER_MINUTE,
            "per_hour": cls.RATE_LIMIT_PER_HOUR,
            "per_day": cls.RATE_LIMIT_PER_DAY,
            "burst": cls.RATE_LIMIT_BURST
        }
    
    @classmethod
    def get_session_config(cls) -> Dict[str, Any]:
        """Get session configuration"""
        return {
            "timeout_minutes": cls.SESSION_TIMEOUT_MINUTES,
            "max_login_attempts": cls.MAX_LOGIN_ATTEMPTS,
            "lockout_duration_minutes": cls.LOCKOUT_DURATION_MINUTES
        }
    
    @classmethod
    def get_compliance_config(cls) -> Dict[str, Any]:
        """Get compliance configuration"""
        return {
            "gdpr_compliance": cls.GDPR_COMPLIANCE,
            "kvkk_compliance": cls.KVKK_COMPLIANCE,
            "data_retention_days": cls.DATA_RETENTION_DAYS,
            "audit_log_enabled": cls.AUDIT_LOG_ENABLED,
            "audit_log_retention_days": cls.AUDIT_LOG_RETENTION_DAYS
        }
    
    @classmethod
    def get_file_upload_config(cls) -> Dict[str, Any]:
        """Get file upload security configuration"""
        return {
            "max_file_size_mb": cls.MAX_FILE_SIZE_MB,
            "allowed_file_types": cls.ALLOWED_FILE_TYPES,
            "upload_path": cls.UPLOAD_PATH
        }
    
    @classmethod
    def validate_security_config(cls) -> Dict[str, Any]:
        """Validate security configuration"""
        validation_result = {
            "valid": True,
            "warnings": cls.get_security_warnings(),
            "errors": [],
            "recommendations": []
        }
        
        # Check for critical errors
        if cls.SECRET_KEY == "dev-secret-key-change-in-production" and cls.is_production():
            validation_result["errors"].append("SECRET_KEY must be set in production")
            validation_result["valid"] = False
        
        if "*" in cls.ALLOWED_ORIGINS and cls.is_production():
            validation_result["errors"].append("CORS wildcard not allowed in production")
            validation_result["valid"] = False
        
        # Add recommendations
        if not cls.AUDIT_LOG_ENABLED:
            validation_result["recommendations"].append("Enable audit logging for compliance")
        
        if not cls.SECURITY_MONITORING_ENABLED:
            validation_result["recommendations"].append("Enable security monitoring")
        
        if cls.RATE_LIMIT_PER_MINUTE > 1000:
            validation_result["recommendations"].append("Consider lowering rate limit for better security")
        
        return validation_result
