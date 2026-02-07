"""
Monitoring Configuration for Petrol Pump Ledger Automation

This module contains configuration settings for the monitoring system
"""

import os
from typing import Dict, Any

# Monitoring configuration
MONITORING_CONFIG = {
    # General monitoring settings
    "enabled": os.getenv("MONITORING_ENABLED", "true").lower() == "true",
    "metrics_port": int(os.getenv("METRICS_PORT", "8001")),

    # Health check settings
    "health_check_interval": int(os.getenv("HEALTH_CHECK_INTERVAL", "30")),  # seconds
    "health_check_timeout": int(os.getenv("HEALTH_CHECK_TIMEOUT", "10")),    # seconds

    # Thresholds for alerts
    "thresholds": {
        "cpu_percent": float(os.getenv("CPU_THRESHOLD_PERCENT", "80.0")),
        "memory_percent": float(os.getenv("MEMORY_THRESHOLD_PERCENT", "80.0")),
        "disk_percent": float(os.getenv("DISK_THRESHOLD_PERCENT", "85.0")),
        "response_time_ms": float(os.getenv("RESPONSE_TIME_THRESHOLD_MS", "5000.0")),
        "error_rate_percent": float(os.getenv("ERROR_RATE_THRESHOLD_PERCENT", "5.0")),
    },

    # Logging settings
    "log_level": os.getenv("MONITORING_LOG_LEVEL", "INFO"),
    "log_retention_days": int(os.getenv("LOG_RETENTION_DAYS", "30")),
    "log_rotation_max_bytes": int(os.getenv("LOG_ROTATION_MAX_BYTES", "10485760")),  # 10MB

    # Alert settings
    "alerts": {
        "enabled": os.getenv("ALERTS_ENABLED", "true").lower() == "true",
        "email_notifications": os.getenv("EMAIL_ALERTS_ENABLED", "false").lower() == "true",
        "webhook_notifications": os.getenv("WEBHOOK_ALERTS_ENABLED", "false").lower() == "true",
        "webhook_url": os.getenv("ALERT_WEBHOOK_URL", ""),
        "email_recipients": os.getenv("ALERT_EMAIL_RECIPIENTS", "").split(","),
    },

    # Performance monitoring
    "performance": {
        "collect_db_metrics": os.getenv("COLLECT_DB_METRICS", "true").lower() == "true",
        "collect_api_metrics": os.getenv("COLLECT_API_METRICS", "true").lower() == "true",
        "collect_system_metrics": os.getenv("COLLECT_SYSTEM_METRICS", "true").lower() == "true",
        "metrics_retention_hours": int(os.getenv("METRICS_RETENTION_HOURS", "24")),
    },

    # Database monitoring
    "database": {
        "connection_pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
    },

    # External service monitoring
    "external_services": {
        "qdrant_host": os.getenv("QDRANT_HOST", "localhost"),
        "qdrant_port": int(os.getenv("QDRANT_PORT", "6333")),
        "qdrant_timeout": int(os.getenv("QDRANT_TIMEOUT", "10")),

        "openai_api_timeout": int(os.getenv("OPENAI_API_TIMEOUT", "30")),
        "ocr_service_timeout": int(os.getenv("OCR_SERVICE_TIMEOUT", "60")),
    },

    # Security monitoring
    "security": {
        "log_authentication_attempts": os.getenv("LOG_AUTH_ATTEMPTS", "true").lower() == "true",
        "log_authorization_failures": os.getenv("LOG_AUTH_FAILURES", "true").lower() == "true",
        "track_failed_login_attempts": os.getenv("TRACK_FAILED_LOGINS", "true").lower() == "true",
    }
}


def get_monitoring_config(key: str = None) -> Any:
    """
    Get monitoring configuration value(s)

    Args:
        key: Specific configuration key to retrieve. If None, returns entire config

    Returns:
        Configuration value or entire config dict
    """
    if key:
        # Handle nested keys (e.g., "thresholds.cpu_percent")
        keys = key.split('.')
        value = MONITORING_CONFIG
        for k in keys:
            value = value[k]
        return value
    else:
        return MONITORING_CONFIG


def update_monitoring_config(key: str, value: Any) -> None:
    """
    Update a monitoring configuration value

    Args:
        key: Configuration key to update (supports dot notation for nested keys)
        value: New value to set
    """
    keys = key.split('.')
    config = MONITORING_CONFIG

    # Navigate to the parent of the target key
    for k in keys[:-1]:
        config = config[k]

    # Set the final key to the new value
    config[keys[-1]] = value


# Environment-specific configurations
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

if ENVIRONMENT == "production":
    # Production-specific overrides
    PRODUCTION_OVERRIDES = {
        "thresholds": {
            "cpu_percent": 90.0,
            "memory_percent": 85.0,
            "response_time_ms": 2000.0,
        },
        "log_retention_days": 90,
        "performance": {
            "metrics_retention_hours": 168,  # 1 week
        },
        "alerts": {
            "enabled": True,
            "email_notifications": True,
        }
    }

    # Apply production overrides
    def merge_dict(base_dict: Dict, update_dict: Dict) -> None:
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                merge_dict(base_dict[key], value)
            else:
                base_dict[key] = value

    merge_dict(MONITORING_CONFIG, PRODUCTION_OVERRIDES)

elif ENVIRONMENT == "staging":
    # Staging-specific overrides
    STAGING_OVERRIDES = {
        "thresholds": {
            "response_time_ms": 3000.0,
        },
        "log_retention_days": 60,
        "alerts": {
            "email_notifications": False,  # Usually disabled in staging
        }
    }

    def merge_dict(base_dict: Dict, update_dict: Dict) -> None:
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                merge_dict(base_dict[key], value)
            else:
                base_dict[key] = value

    merge_dict(MONITORING_CONFIG, STAGING_OVERRIDES)


# Validation function to check if configuration values are valid
def validate_config() -> Dict[str, str]:
    """
    Validate monitoring configuration values

    Returns:
        Dictionary of validation errors (empty if all valid)
    """
    errors = {}

    config = MONITORING_CONFIG

    # Validate thresholds
    if config["thresholds"]["cpu_percent"] < 0 or config["thresholds"]["cpu_percent"] > 100:
        errors["cpu_percent"] = "Must be between 0 and 100"

    if config["thresholds"]["memory_percent"] < 0 or config["thresholds"]["memory_percent"] > 100:
        errors["memory_percent"] = "Must be between 0 and 100"

    if config["thresholds"]["disk_percent"] < 0 or config["thresholds"]["disk_percent"] > 100:
        errors["disk_percent"] = "Must be between 0 and 100"

    if config["thresholds"]["error_rate_percent"] < 0 or config["thresholds"]["error_rate_percent"] > 100:
        errors["error_rate_percent"] = "Must be between 0 and 100"

    # Validate ports
    if config["metrics_port"] < 1 or config["metrics_port"] > 65535:
        errors["metrics_port"] = "Must be between 1 and 65535"

    # Validate timeouts and intervals
    if config["health_check_timeout"] <= 0:
        errors["health_check_timeout"] = "Must be positive"

    if config["health_check_interval"] <= 0:
        errors["health_check_interval"] = "Must be positive"

    return errors


# Validate the configuration on import
validation_errors = validate_config()
if validation_errors:
    print(f"Warning: Invalid monitoring configuration values: {validation_errors}")


# Convenience functions for common configuration access
def is_monitoring_enabled() -> bool:
    """Check if monitoring is enabled"""
    return MONITORING_CONFIG["enabled"]


def get_metrics_port() -> int:
    """Get the metrics port number"""
    return MONITORING_CONFIG["metrics_port"]


def get_alert_recipients() -> list:
    """Get alert email recipients"""
    return [email.strip() for email in MONITORING_CONFIG["alerts"]["email_recipients"] if email.strip()]


def should_collect_db_metrics() -> bool:
    """Check if DB metrics should be collected"""
    return MONITORING_CONFIG["performance"]["collect_db_metrics"]


def should_collect_api_metrics() -> bool:
    """Check if API metrics should be collected"""
    return MONITORING_CONFIG["performance"]["collect_api_metrics"]


def should_collect_system_metrics() -> bool:
    """Check if system metrics should be collected"""
    return MONITORING_CONFIG["performance"]["collect_system_metrics"]