"""
Logging Utility for Petrol Pump Ledger Automation

This module provides centralized logging configuration and utilities
"""
import logging
import sys
import os
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler, SysLogHandler
import json
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Define log levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Get log level from environment variable, default to INFO
LOG_LEVEL = LOG_LEVELS.get(os.getenv('LOG_LEVEL', 'INFO').upper(), logging.INFO)


class CustomFormatter(logging.Formatter):
    """
    Custom formatter to add additional fields and structure to log messages
    """

    def format(self, record):
        # Create a dictionary with the log data
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint

        return json.dumps(log_entry)


def setup_logger(
    name: str = "petrol_pump_ledger",
    log_file: Optional[str] = None,
    log_level: int = LOG_LEVEL,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers

    Args:
        name: Logger name
        log_file: Path to log file (optional, creates file handler if provided)
        log_level: Logging level
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    # Create custom formatter
    formatter = CustomFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (rotating)
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # Default to a file based on the logger name
        default_log_file = logs_dir / f"{name.replace('.', '_')}.log"
        file_handler = RotatingFileHandler(
            default_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "petrol_pump_ledger") -> logging.Logger:
    """
    Get a logger instance (creates one if it doesn't exist)
    """
    return logging.getLogger(name)


# Initialize the main application logger
app_logger = setup_logger(
    name="app",
    log_file=str(logs_dir / "application.log"),
    log_level=LOG_LEVEL
)


def log_api_call(endpoint: str, user_id: Optional[int] = None, request_id: Optional[str] = None):
    """
    Decorator to log API calls
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            app_logger.info(
                f"API call to {endpoint}",
                extra={
                    'endpoint': endpoint,
                    'user_id': user_id,
                    'request_id': request_id
                }
            )
            try:
                result = func(*args, **kwargs)
                app_logger.info(
                    f"API call to {endpoint} completed successfully",
                    extra={
                        'endpoint': endpoint,
                        'user_id': user_id,
                        'request_id': request_id
                    }
                )
                return result
            except Exception as e:
                app_logger.error(
                    f"API call to {endpoint} failed: {str(e)}",
                    extra={
                        'endpoint': endpoint,
                        'user_id': user_id,
                        'request_id': request_id
                    }
                )
                raise
        return wrapper
    return decorator


def log_performance(operation: str, user_id: Optional[int] = None):
    """
    Decorator to log performance metrics
    """
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                app_logger.info(
                    f"Performance: {operation} took {duration:.4f}s",
                    extra={
                        'operation': operation,
                        'duration': duration,
                        'user_id': user_id
                    }
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                app_logger.error(
                    f"Performance: {operation} failed after {duration:.4f}s: {str(e)}",
                    extra={
                        'operation': operation,
                        'duration': duration,
                        'user_id': user_id
                    }
                )
                raise
        return wrapper
    return decorator


# Predefined loggers for common use cases
db_logger = setup_logger("database", str(logs_dir / "database.log"))
auth_logger = setup_logger("authentication", str(logs_dir / "auth.log"))
ocr_logger = setup_logger("ocr_processing", str(logs_dir / "ocr.log"))
api_logger = setup_logger("api", str(logs_dir / "api.log"))
error_logger = setup_logger("errors", str(logs_dir / "errors.log"), logging.ERROR)


# Context manager for request logging
class RequestLogger:
    def __init__(self, request_id: str, endpoint: str, user_id: Optional[int] = None):
        self.request_id = request_id
        self.endpoint = endpoint
        self.user_id = user_id
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.utcnow()
        app_logger.info(
            f"Starting request {self.request_id} to {self.endpoint}",
            extra={
                'request_id': self.request_id,
                'endpoint': self.endpoint,
                'user_id': self.user_id
            }
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        if exc_type:
            app_logger.error(
                f"Request {self.request_id} to {self.endpoint} failed after {duration:.4f}s: {exc_val}",
                extra={
                    'request_id': self.request_id,
                    'endpoint': self.endpoint,
                    'user_id': self.user_id,
                    'duration': duration
                }
            )
        else:
            app_logger.info(
                f"Request {self.request_id} to {self.endpoint} completed after {duration:.4f}s",
                extra={
                    'request_id': self.request_id,
                    'endpoint': self.endpoint,
                    'user_id': self.user_id,
                    'duration': duration
                }
            )


# Initialize all loggers
def init_logging():
    """
    Initialize all loggers for the application
    """
    loggers = [
        ('app', str(logs_dir / 'application.log')),
        ('database', str(logs_dir / 'database.log')),
        ('authentication', str(logs_dir / 'auth.log')),
        ('ocr_processing', str(logs_dir / 'ocr.log')),
        ('api', str(logs_dir / 'api.log')),
        ('errors', str(logs_dir / 'errors.log')),
    ]

    for name, log_file in loggers:
        setup_logger(name, log_file)


# Initialize logging when module is imported
init_logging()


# Example usage:
if __name__ == "__main__":
    # Example of how to use the logger
    logger = get_logger("example")
    logger.info("This is an example log message")
    logger.error("This is an example error message", extra={'user_id': 123})