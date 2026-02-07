"""
Health Check API Endpoints for Petrol Pump Ledger Automation

This module provides health check endpoints for monitoring the application
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import time
from datetime import datetime

from ...database.connection import get_db_session
from ...services.monitoring_service import get_monitoring_service, HealthCheckType
from ...models.User import User

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=Dict[str, Any])
async def health_check(db: Session = Depends(get_db_session)):
    """
    Basic health check endpoint
    """
    try:
        # Test database connection
        db.query(User).limit(1).first()

        # Test basic operations
        timestamp = datetime.utcnow().isoformat()

        return {
            "status": "healthy",
            "timestamp": timestamp,
            "checks": {
                "database": "connected",
                "basic_operations": "ok"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "checks": {
                    "database": "failed"
                }
            }
        )


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check(db: Session = Depends(get_db_session)):
    """
    Detailed health check with multiple system checks
    """
    monitoring_service = get_monitoring_service()

    # Run detailed health checks
    health_status = monitoring_service.get_health_status()

    return {
        "status": health_status.status,
        "timestamp": health_status.timestamp.isoformat(),
        "uptime_seconds": health_status.uptime,
        "checks": health_status.checks
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db_session)):
    """
    Readiness check - verifies the application is ready to serve traffic
    """
    try:
        # Test database connection
        db.execute("SELECT 1")

        # Additional readiness checks can be added here

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )


@router.get("/live")
async def liveness_check():
    """
    Liveness check - verifies the application is alive and responding
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": (datetime.utcnow() - get_monitoring_service().start_time).total_seconds()
    }


@router.get("/metrics")
async def metrics_endpoint():
    """
    Metrics endpoint that returns application metrics
    """
    monitoring_service = get_monitoring_service()
    metrics = monitoring_service.get_metrics_summary()

    return metrics


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for basic connectivity check
    """
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}


@router.get("/status")
async def application_status(db: Session = Depends(get_db_session)):
    """
    Application status with detailed information
    """
    monitoring_service = get_monitoring_service()

    try:
        # Test database
        start_time = time.time()
        db.query(User).limit(1).first()
        db_ping_time = time.time() - start_time

        # Get system metrics
        import psutil
        system_status = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "db_ping_ms": round(db_ping_time * 1000, 2)
        }

        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",  # This should come from your app version
            "system": system_status,
            "uptime_seconds": (datetime.utcnow() - monitoring_service.start_time).total_seconds()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "uptime_seconds": (datetime.utcnow() - monitoring_service.start_time).total_seconds()
            }
        )