"""
Professional Monitoring Configuration
Production-ready monitoring setup with best practices
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = 'json'  # json, text
    LOG_FILE: str = os.getenv('LOG_FILE', '/var/log/taniai/app.log')
    LOG_ROTATION: str = 'daily'  # daily, weekly, size-based
    
    # Metrics Configuration
    METRICS_ENABLED: bool = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
    METRICS_PORT: int = int(os.getenv('METRICS_PORT', '9090'))
    METRICS_PATH: str = os.getenv('METRICS_PATH', '/metrics')
    
    # Alerting Configuration
    ALERTS_ENABLED: bool = os.getenv('ALERTS_ENABLED', 'true').lower() == 'true'
    ALERT_EMAIL_ENABLED: bool = os.getenv('ALERT_EMAIL_ENABLED', 'false').lower() == 'true'
    ALERT_SLACK_ENABLED: bool = os.getenv('ALERT_SLACK_ENABLED', 'false').lower() == 'true'
    ALERT_WEBHOOK_ENABLED: bool = os.getenv('ALERT_WEBHOOK_ENABLED', 'false').lower() == 'true'
    
    # Email Configuration
    SMTP_SERVER: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    ALERT_EMAIL_USER: str = os.getenv('ALERT_EMAIL_USER', '')
    ALERT_EMAIL_PASS: str = os.getenv('ALERT_EMAIL_PASS', '')
    ALERT_EMAIL_TO: List[str] = os.getenv('ALERT_EMAIL_TO', '').split(',') if os.getenv('ALERT_EMAIL_TO') else []
    
    # Slack Configuration
    SLACK_WEBHOOK_URL: str = os.getenv('SLACK_WEBHOOK_URL', '')
    SLACK_CHANNEL: str = os.getenv('SLACK_CHANNEL', '#alerts')
    
    # Webhook Configuration
    ALERT_WEBHOOK_URL: str = os.getenv('ALERT_WEBHOOK_URL', '')
    
    # Performance Thresholds
    SLOW_OPERATION_THRESHOLD: float = float(os.getenv('SLOW_OPERATION_THRESHOLD', '1.0'))
    HIGH_CPU_THRESHOLD: float = float(os.getenv('HIGH_CPU_THRESHOLD', '80.0'))
    HIGH_MEMORY_THRESHOLD: float = float(os.getenv('HIGH_MEMORY_THRESHOLD', '85.0'))
    LOW_DISK_THRESHOLD: float = float(os.getenv('LOW_DISK_THRESHOLD', '90.0'))
    
    # Health Check Configuration
    HEALTH_CHECK_INTERVAL: int = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
    HEALTH_CHECK_TIMEOUT: int = int(os.getenv('HEALTH_CHECK_TIMEOUT', '10'))
    
    # Retention Configuration
    LOG_RETENTION_DAYS: int = int(os.getenv('LOG_RETENTION_DAYS', '30'))
    METRICS_RETENTION_DAYS: int = int(os.getenv('METRICS_RETENTION_DAYS', '7'))
    
    # Security Configuration
    ENABLE_AUDIT_LOGGING: bool = os.getenv('ENABLE_AUDIT_LOGGING', 'true').lower() == 'true'
    ENABLE_SECURITY_MONITORING: bool = os.getenv('ENABLE_SECURITY_MONITORING', 'true').lower() == 'true'
    
    # External Services
    PROMETHEUS_ENABLED: bool = os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true'
    GRAFANA_ENABLED: bool = os.getenv('GRAFANA_ENABLED', 'false').lower() == 'true'
    SENTRY_DSN: str = os.getenv('SENTRY_DSN', '')
    
    @classmethod
    def get_alert_rules(cls) -> List[Dict[str, Any]]:
        """Get default alert rules"""
        return [
            {
                'name': 'high_cpu',
                'condition': 'cpu_percent > 80',
                'severity': 'warning',
                'cooldown': 300,
                'description': 'High CPU usage detected'
            },
            {
                'name': 'high_memory',
                'condition': 'memory_percent > 85',
                'severity': 'critical',
                'cooldown': 300,
                'description': 'High memory usage detected'
            },
            {
                'name': 'low_disk',
                'condition': 'disk_percent > 90',
                'severity': 'critical',
                'cooldown': 600,
                'description': 'Low disk space detected'
            },
            {
                'name': 'high_error_rate',
                'condition': 'error_rate > 5',
                'severity': 'warning',
                'cooldown': 300,
                'description': 'High error rate detected'
            },
            {
                'name': 'slow_response',
                'condition': 'p95_response_time > 2000',
                'severity': 'warning',
                'cooldown': 300,
                'description': 'Slow response times detected'
            }
        ]
    
    @classmethod
    def get_health_checks(cls) -> List[Dict[str, Any]]:
        """Get health check configurations"""
        return [
            {
                'name': 'database',
                'type': 'database_connection',
                'timeout': 5,
                'critical': True
            },
            {
                'name': 'redis',
                'type': 'redis_connection',
                'timeout': 3,
                'critical': False
            },
            {
                'name': 'external_api',
                'type': 'http_endpoint',
                'url': 'https://api.example.com/health',
                'timeout': 10,
                'critical': False
            }
        ]
    
    @classmethod
    def get_metrics_config(cls) -> Dict[str, Any]:
        """Get metrics configuration"""
        return {
            'enabled': cls.METRICS_ENABLED,
            'port': cls.METRICS_PORT,
            'path': cls.METRICS_PATH,
            'retention_days': cls.METRICS_RETENTION_DAYS,
            'custom_metrics': [
                'api_requests_total',
                'api_request_duration_seconds',
                'api_errors_total',
                'system_cpu_percent',
                'system_memory_percent',
                'system_disk_percent',
                'database_connections_active',
                'database_query_duration_seconds'
            ]
        }
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return warnings"""
        warnings = []
        
        if cls.ALERTS_ENABLED and not any([
            cls.ALERT_EMAIL_ENABLED,
            cls.ALERT_SLACK_ENABLED,
            cls.ALERT_WEBHOOK_ENABLED
        ]):
            warnings.append("Alerts enabled but no alert channels configured")
        
        if cls.ALERT_EMAIL_ENABLED and not cls.ALERT_EMAIL_USER:
            warnings.append("Email alerts enabled but SMTP username not configured")
        
        if cls.ALERT_SLACK_ENABLED and not cls.SLACK_WEBHOOK_URL:
            warnings.append("Slack alerts enabled but webhook URL not configured")
        
        if cls.LOG_LEVEL not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            warnings.append(f"Invalid log level: {cls.LOG_LEVEL}")
        
        return warnings

# Global configuration instance
config = MonitoringConfig()

# Export configuration
__all__ = ['MonitoringConfig', 'config']
