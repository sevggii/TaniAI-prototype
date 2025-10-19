"""
Enhanced Professional Monitoring System
Production-ready monitoring with comprehensive metrics and alerting
"""

import logging
import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
import os
import psutil
import threading
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Structured logging setup
class StructuredLogger:
    """JSON tabanlı structured logging"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def log(self, level: str, message: str, **kwargs):
        """Structured log entry"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))

# Global structured logger
structured_logger = StructuredLogger('taniai')

@dataclass
class Metric:
    """Metric data structure"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = None
    
    def to_dict(self):
        return asdict(self)

class MetricsCollector:
    """Comprehensive metrics collection"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.start_time = time.time()
    
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Counter metric"""
        self.counters[name] += value
        self._record_metric('counter', name, value, tags)
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Gauge metric"""
        self.gauges[name] = value
        self._record_metric('gauge', name, value, tags)
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Histogram metric"""
        self.histograms[name].append(value)
        self._record_metric('histogram', name, value, tags)
    
    def _record_metric(self, metric_type: str, name: str, value: float, tags: Dict[str, str] = None):
        """Record metric with metadata"""
        metric = Metric(
            name=f"{metric_type}.{name}",
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.metrics[metric_type].append(metric)
        
        # Log metric
        structured_logger.log('INFO', f'Metric recorded', 
                            metric_type=metric_type, 
                            metric_name=name, 
                            value=value, 
                            tags=tags)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        uptime = time.time() - self.start_time
        
        # Calculate percentiles for histograms
        histogram_stats = {}
        for name, values in self.histograms.items():
            if values:
                sorted_values = sorted(values)
                n = len(sorted_values)
                histogram_stats[name] = {
                    'count': n,
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / n,
                    'p50': sorted_values[int(n * 0.5)],
                    'p95': sorted_values[int(n * 0.95)],
                    'p99': sorted_values[int(n * 0.99)]
                }
        
        return {
            'uptime_seconds': uptime,
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histograms': histogram_stats,
            'total_metrics': sum(len(metrics) for metrics in self.metrics.values())
        }

# Global metrics collector
metrics_collector = MetricsCollector()

class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self):
        self.last_check = time.time()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free = disk.free / (1024**3)  # GB
            
            # Network metrics
            network = psutil.net_io_counters()
            
            metrics = {
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'memory_percent': memory_percent,
                'memory_available_gb': memory_available,
                'disk_percent': disk_percent,
                'disk_free_gb': disk_free,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'timestamp': datetime.now().isoformat()
            }
            
            # Record metrics
            metrics_collector.set_gauge('system.cpu_percent', cpu_percent)
            metrics_collector.set_gauge('system.memory_percent', memory_percent)
            metrics_collector.set_gauge('system.disk_percent', disk_percent)
            
            return metrics
            
        except Exception as e:
            structured_logger.log('ERROR', 'Failed to get system metrics', error=str(e))
            return {}
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check system health thresholds"""
        metrics = self.get_system_metrics()
        alerts = []
        
        # CPU threshold
        if metrics.get('cpu_percent', 0) > 80:
            alerts.append({
                'type': 'high_cpu',
                'severity': 'warning',
                'message': f"High CPU usage: {metrics['cpu_percent']:.1f}%"
            })
        
        # Memory threshold
        if metrics.get('memory_percent', 0) > 85:
            alerts.append({
                'type': 'high_memory',
                'severity': 'critical',
                'message': f"High memory usage: {metrics['memory_percent']:.1f}%"
            })
        
        # Disk threshold
        if metrics.get('disk_percent', 0) > 90:
            alerts.append({
                'type': 'low_disk',
                'severity': 'critical',
                'message': f"Low disk space: {metrics['disk_percent']:.1f}% used"
            })
        
        return {
            'healthy': len(alerts) == 0,
            'alerts': alerts,
            'metrics': metrics
        }

# Global system monitor
system_monitor = SystemMonitor()

class AlertManager:
    """Alert management system"""
    
    def __init__(self):
        self.alert_rules = []
        self.alert_history = deque(maxlen=1000)
        self.alert_cooldowns = {}
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('ALERT_EMAIL_USER'),
            'password': os.getenv('ALERT_EMAIL_PASS'),
            'to_emails': os.getenv('ALERT_EMAIL_TO', '').split(',')
        }
    
    def add_alert_rule(self, name: str, condition: Callable, severity: str = 'warning', cooldown: int = 300):
        """Add alert rule"""
        self.alert_rules.append({
            'name': name,
            'condition': condition,
            'severity': severity,
            'cooldown': cooldown
        })
    
    def check_alerts(self):
        """Check all alert rules"""
        current_time = time.time()
        
        for rule in self.alert_rules:
            try:
                # Check cooldown
                last_alert = self.alert_cooldowns.get(rule['name'], 0)
                if current_time - last_alert < rule['cooldown']:
                    continue
                
                # Check condition
                if rule['condition']():
                    self._trigger_alert(rule, current_time)
                    
            except Exception as e:
                structured_logger.log('ERROR', 'Alert check failed', 
                                    rule_name=rule['name'], error=str(e))
    
    def _trigger_alert(self, rule: Dict, timestamp: float):
        """Trigger alert"""
        alert = {
            'name': rule['name'],
            'severity': rule['severity'],
            'timestamp': datetime.now().isoformat(),
            'message': f"Alert triggered: {rule['name']}"
        }
        
        # Add to history
        self.alert_history.append(alert)
        
        # Update cooldown
        self.alert_cooldowns[rule['name']] = timestamp
        
        # Log alert
        structured_logger.log('WARNING', 'Alert triggered', **alert)
        
        # Send notification
        self._send_notification(alert)
    
    def _send_notification(self, alert: Dict):
        """Send alert notification"""
        try:
            if not self.email_config['username'] or not self.email_config['to_emails']:
                return
            
            # Create email
            msg = MimeMultipart()
            msg['From'] = self.email_config['username']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = f"TaniAI Alert: {alert['name']}"
            
            body = f"""
            Alert Details:
            - Name: {alert['name']}
            - Severity: {alert['severity']}
            - Time: {alert['timestamp']}
            - Message: {alert['message']}
            
            Please check the system immediately.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            structured_logger.log('INFO', 'Alert notification sent', alert_name=alert['name'])
            
        except Exception as e:
            structured_logger.log('ERROR', 'Failed to send alert notification', 
                                alert_name=alert['name'], error=str(e))

# Global alert manager
alert_manager = AlertManager()

class APM:
    """Application Performance Monitoring"""
    
    def __init__(self):
        self.request_times = deque(maxlen=10000)
        self.error_counts = defaultdict(int)
        self.endpoint_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'errors': 0})
    
    def record_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Record API request metrics"""
        # Record request time
        self.request_times.append(duration)
        metrics_collector.record_histogram('api.request_duration', duration, 
                                         {'endpoint': endpoint, 'method': method})
        
        # Update endpoint stats
        stats = self.endpoint_stats[f"{method} {endpoint}"]
        stats['count'] += 1
        stats['total_time'] += duration
        if status_code >= 400:
            stats['errors'] += 1
            metrics_collector.increment_counter('api.errors', tags={'endpoint': endpoint, 'status': str(status_code)})
        
        # Record status code
        metrics_collector.increment_counter('api.requests', tags={'status': str(status_code)})
        
        # Log request
        structured_logger.log('INFO', 'API request', 
                            endpoint=endpoint, 
                            method=method, 
                            status_code=status_code, 
                            duration_ms=duration * 1000)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.request_times:
            return {}
        
        sorted_times = sorted(self.request_times)
        n = len(sorted_times)
        
        return {
            'total_requests': n,
            'avg_response_time': sum(self.request_times) / n,
            'p50_response_time': sorted_times[int(n * 0.5)],
            'p95_response_time': sorted_times[int(n * 0.95)],
            'p99_response_time': sorted_times[int(n * 0.99)],
            'max_response_time': max(self.request_times),
            'error_rate': sum(self.error_counts.values()) / n if n > 0 else 0,
            'endpoint_stats': dict(self.endpoint_stats)
        }

# Global APM
apm = APM()

def monitor_performance(operation_name: str):
    """Enhanced performance monitoring decorator"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record metrics
                metrics_collector.record_histogram('operation.duration', duration, 
                                                 {'operation': operation_name})
                metrics_collector.increment_counter('operation.success', tags={'operation': operation_name})
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics_collector.increment_counter('operation.error', tags={'operation': operation_name})
                structured_logger.log('ERROR', 'Operation failed', 
                                    operation=operation_name, 
                                    error=str(e), 
                                    duration=duration)
                raise
            finally:
                duration = time.time() - start_time
                if duration > 1.0:  # Slow operation threshold
                    structured_logger.log('WARNING', 'Slow operation detected', 
                                        operation=operation_name, 
                                        duration=duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record metrics
                metrics_collector.record_histogram('operation.duration', duration, 
                                                 {'operation': operation_name})
                metrics_collector.increment_counter('operation.success', tags={'operation': operation_name})
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics_collector.increment_counter('operation.error', tags={'operation': operation_name})
                structured_logger.log('ERROR', 'Operation failed', 
                                    operation=operation_name, 
                                    error=str(e), 
                                    duration=duration)
                raise
            finally:
                duration = time.time() - start_time
                if duration > 1.0:  # Slow operation threshold
                    structured_logger.log('WARNING', 'Slow operation detected', 
                                        operation=operation_name, 
                                        duration=duration)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class MonitoringService:
    """Main monitoring service"""
    
    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Setup default alert rules"""
        # High CPU alert
        alert_manager.add_alert_rule(
            'high_cpu',
            lambda: system_monitor.get_system_metrics().get('cpu_percent', 0) > 80,
            severity='warning',
            cooldown=300
        )
        
        # High memory alert
        alert_manager.add_alert_rule(
            'high_memory',
            lambda: system_monitor.get_system_metrics().get('memory_percent', 0) > 85,
            severity='critical',
            cooldown=300
        )
        
        # Low disk space alert
        alert_manager.add_alert_rule(
            'low_disk',
            lambda: system_monitor.get_system_metrics().get('disk_percent', 0) > 90,
            severity='critical',
            cooldown=600
        )
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        structured_logger.log('INFO', 'Monitoring service started')
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        structured_logger.log('INFO', 'Monitoring service stopped')
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                # Check system health
                system_monitor.get_system_metrics()
                
                # Check alerts
                alert_manager.check_alerts()
                
                # Sleep for 30 seconds
                time.sleep(30)
                
            except Exception as e:
                structured_logger.log('ERROR', 'Monitoring loop error', error=str(e))
                time.sleep(60)  # Wait longer on error
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        system_health = system_monitor.check_system_health()
        performance_summary = apm.get_performance_summary()
        metrics_summary = metrics_collector.get_metrics_summary()
        
        return {
            'overall_status': 'healthy' if system_health['healthy'] else 'unhealthy',
            'system': system_health,
            'performance': performance_summary,
            'metrics': metrics_summary,
            'alerts': list(alert_manager.alert_history)[-10:],  # Last 10 alerts
            'timestamp': datetime.now().isoformat()
        }

# Global monitoring service
monitoring_service = MonitoringService()

# Initialize monitoring
monitoring_service.start_monitoring()

# Export main components
__all__ = [
    'structured_logger',
    'metrics_collector', 
    'system_monitor',
    'alert_manager',
    'apm',
    'monitoring_service',
    'monitor_performance'
]
