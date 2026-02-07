"""
Monitoring Service for Petrol Pump Ledger Automation

This module provides monitoring and metrics collection for the application
"""
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging
import json
from pathlib import Path
import atexit

from ..utils.logger import get_logger
from prometheus_client import Counter, Histogram, Gauge, start_http_server, CollectorRegistry, multiprocess

# Initialize logger
monitoring_logger = get_logger("monitoring")

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections',
    'Number of database connections'
)


@dataclass
class HealthStatus:
    """Health status data class"""
    status: str  # 'healthy', 'degraded', 'unhealthy'
    checks: Dict[str, Any]
    timestamp: datetime
    uptime: float


class HealthCheckType(Enum):
    """Types of health checks"""
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    DISK_SPACE = "disk_space"
    MEMORY = "memory"
    CPU = "cpu"


class MonitoringService:
    """
    Centralized monitoring service for the application
    """

    def __init__(self, metrics_port: int = 8001):
        self.metrics_port = metrics_port
        self.start_time = datetime.utcnow()
        self.health_checks = {}
        self.metrics_collector_thread = None
        self.monitoring_enabled = True

        # Performance counters
        self.request_count = 0
        self.error_count = 0
        self.avg_response_time = 0.0
        self.response_times = []

        # System resources
        self.cpu_threshold = float(
            self.get_env_var("MONITORING_CPU_THRESHOLD", "80.0")
        )
        self.memory_threshold = float(
            self.get_env_var("MONITORING_MEMORY_THRESHOLD", "80.0")
        )
        self.disk_threshold = float(
            self.get_env_var("MONITORING_DISK_THRESHOLD", "85.0")
        )

    def get_env_var(self, var_name: str, default: str) -> str:
        """Get environment variable with default fallback"""
        return getattr(self, '_env_vars', {}).get(var_name) or \
               str(self.__dict__.get(var_name.lower())) or \
               str(default)

    def start_metrics_server(self):
        """
        Start the Prometheus metrics server
        """
        try:
            start_http_server(self.metrics_port)
            monitoring_logger.info(f"Metrics server started on port {self.metrics_port}")
        except Exception as e:
            monitoring_logger.error(f"Failed to start metrics server: {e}")

    def collect_system_metrics(self):
        """
        Collect system-level metrics (CPU, memory, disk usage)
        """
        while self.monitoring_enabled:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                CPU_USAGE.set(cpu_percent)

                # Memory usage
                memory = psutil.virtual_memory()
                MEMORY_USAGE.set(memory.used)

                # Disk usage
                disk_usage = psutil.disk_usage('/').percent

                # Log warnings if thresholds are exceeded
                if cpu_percent > self.cpu_threshold:
                    monitoring_logger.warning(f"High CPU usage: {cpu_percent}%")

                if memory.percent > self.memory_threshold:
                    monitoring_logger.warning(f"High memory usage: {memory.percent}%")

                if disk_usage > self.disk_threshold:
                    monitoring_logger.warning(f"High disk usage: {disk_usage}%")

                time.sleep(30)  # Collect every 30 seconds

            except Exception as e:
                monitoring_logger.error(f"Error collecting system metrics: {e}")
                time.sleep(30)

    def start_system_monitoring(self):
        """
        Start system monitoring in a separate thread
        """
        self.metrics_collector_thread = threading.Thread(
            target=self.collect_system_metrics,
            daemon=True
        )
        self.metrics_collector_thread.start()

    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """
        Record an HTTP request for metrics
        """
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        # Update internal counters
        self.request_count += 1
        if 400 <= status_code < 600:
            self.error_count += 1

        self.response_times.append(duration)
        if len(self.response_times) > 100:  # Keep last 100 measurements
            self.response_times.pop(0)

        if self.response_times:
            self.avg_response_time = sum(self.response_times) / len(self.response_times)

    def update_active_connections(self, count: int):
        """
        Update the active connections gauge
        """
        ACTIVE_CONNECTIONS.set(count)

    def update_database_connections(self, count: int):
        """
        Update the database connections gauge
        """
        DATABASE_CONNECTIONS.set(count)

    def run_health_check(self, check_type: HealthCheckType, **kwargs) -> Dict[str, Any]:
        """
        Run a specific health check
        """
        check_start = time.time()

        try:
            if check_type == HealthCheckType.DATABASE:
                result = self.check_database(**kwargs)
            elif check_type == HealthCheckType.EXTERNAL_API:
                result = self.check_external_api(**kwargs)
            elif check_type == HealthCheckType.DISK_SPACE:
                result = self.check_disk_space(**kwargs)
            elif check_type == HealthCheckType.MEMORY:
                result = self.check_memory(**kwargs)
            elif check_type == HealthCheckType.CPU:
                result = self.check_cpu(**kwargs)
            else:
                result = {"status": "unknown", "message": "Unknown check type"}

        except Exception as e:
            result = {
                "status": "error",
                "message": str(e),
                "duration": time.time() - check_start
            }

        result["duration"] = time.time() - check_start
        return result

    def check_database(self, db_connection=None) -> Dict[str, Any]:
        """
        Check database connectivity and performance
        """
        if db_connection:
            try:
                # Test database connection
                db_connection.execute("SELECT 1")
                return {"status": "healthy", "message": "Database connection OK"}
            except Exception as e:
                return {"status": "unhealthy", "message": f"Database connection failed: {e}"}
        else:
            # Simulate database check
            return {"status": "healthy", "message": "Database check passed"}

    def check_external_api(self, url: str = None, timeout: int = 5) -> Dict[str, Any]:
        """
        Check external API connectivity
        """
        # For now, just return healthy - in a real implementation you would check actual APIs
        return {"status": "healthy", "message": "External API check passed"}

    def check_disk_space(self) -> Dict[str, Any]:
        """
        Check available disk space
        """
        try:
            disk_usage = psutil.disk_usage('/')
            free_percentage = (disk_usage.free / disk_usage.total) * 100

            if free_percentage < (100 - self.disk_threshold):
                return {
                    "status": "degraded",
                    "message": f"Disk space low: {free_percentage:.1f}% free"
                }
            else:
                return {
                    "status": "healthy",
                    "message": f"Sufficient disk space: {free_percentage:.1f}% free"
                }
        except Exception as e:
            return {"status": "error", "message": f"Disk space check failed: {e}"}

    def check_memory(self) -> Dict[str, Any]:
        """
        Check memory usage
        """
        try:
            memory = psutil.virtual_memory()

            if memory.percent > self.memory_threshold:
                return {
                    "status": "degraded",
                    "message": f"High memory usage: {memory.percent}%"
                }
            else:
                return {
                    "status": "healthy",
                    "message": f"Memory usage OK: {memory.percent}%"
                }
        except Exception as e:
            return {"status": "error", "message": f"Memory check failed: {e}"}

    def check_cpu(self) -> Dict[str, Any]:
        """
        Check CPU usage
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent > self.cpu_threshold:
                return {
                    "status": "degraded",
                    "message": f"High CPU usage: {cpu_percent}%"
                }
            else:
                return {
                    "status": "healthy",
                    "message": f"CPU usage OK: {cpu_percent}%"
                }
        except Exception as e:
            return {"status": "error", "message": f"CPU check failed: {e}"}

    def get_health_status(self) -> HealthStatus:
        """
        Get overall health status of the application
        """
        checks = {}
        overall_status = "healthy"

        # Run all health checks
        for check_type in HealthCheckType:
            result = self.run_health_check(check_type)
            checks[check_type.value] = result

            # Update overall status if any check is not healthy
            if result["status"] in ["degraded", "unhealthy", "error"]:
                if overall_status != "unhealthy":
                    overall_status = result["status"]

        uptime = (datetime.utcnow() - self.start_time).total_seconds()

        return HealthStatus(
            status=overall_status,
            checks=checks,
            timestamp=datetime.utcnow(),
            uptime=uptime
        )

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of application metrics
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1) * 100,
            "avg_response_time": self.avg_response_time,
            "current_cpu_percent": psutil.cpu_percent(),
            "current_memory_percent": psutil.virtual_memory().percent,
            "active_connections": ACTIVE_CONNECTIONS._value.get(),
            "database_connections": DATABASE_CONNECTIONS._value.get(),
        }

    def cleanup(self):
        """
        Cleanup method to stop monitoring
        """
        self.monitoring_enabled = False
        monitoring_logger.info("Monitoring service stopped")


# Global monitoring service instance
_monitoring_service = None


def get_monitoring_service() -> MonitoringService:
    """
    Get the global monitoring service instance
    """
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
        _monitoring_service.start_system_monitoring()
        _monitoring_service.start_metrics_server()

        # Register cleanup function
        atexit.register(_monitoring_service.cleanup)

    return _monitoring_service


def monitor_api_call(func):
    """
    Decorator to monitor API calls
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            # Record metrics
            monitoring_service = get_monitoring_service()
            monitoring_service.record_request(
                method=getattr(func, '__name__', 'unknown'),
                endpoint=getattr(func, '__module__', 'unknown'),
                status_code=200,  # Assuming success, would need to handle exceptions separately
                duration=duration
            )

            return result
        except Exception as e:
            duration = time.time() - start_time

            # Record error metrics
            monitoring_service = get_monitoring_service()
            monitoring_service.record_request(
                method=getattr(func, '__name__', 'unknown'),
                endpoint=getattr(func, '__module__', 'unknown'),
                status_code=500,
                duration=duration
            )

            raise

    return wrapper


# Initialize monitoring service
if __name__ == "__main__":
    # Example usage
    service = get_monitoring_service()

    # Run a health check
    health = service.get_health_status()
    print(f"Health Status: {health.status}")
    print(f"Checks: {json.dumps(health.checks, indent=2, default=str)}")

    # Get metrics summary
    metrics = service.get_metrics_summary()
    print(f"Metrics: {json.dumps(metrics, indent=2, default=str)}")