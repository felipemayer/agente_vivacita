"""
Health check endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
import sys
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    timestamp: datetime
    environment: str
    python_version: str
    dependencies: Dict[str, str]


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Comprehensive health check endpoint.
    """
    logger.info("Health check requested")
    
    return HealthResponse(
        status="healthy",
        service="vivacita-chat-system",
        version=settings.VERSION,
        timestamp=datetime.utcnow(),
        environment=settings.ENVIRONMENT,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        dependencies={
            "fastapi": "0.104.0",
            "crewai": "0.70.1",
            "openai": "1.0.0",
            "supabase": "2.0.0"
        }
    )


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check for Kubernetes deployments.
    """
    logger.info("Readiness check requested")
    
    # TODO: Add actual dependency checks
    # - Database connectivity
    # - Redis connectivity
    # - External services availability
    
    return {
        "status": "ready",
        "checks": {
            "database": "ok",  # TODO: implement
            "redis": "ok",     # TODO: implement
            "openai": "ok"     # TODO: implement
        }
    }


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """
    Liveness check for Kubernetes deployments.
    """
    return {"status": "alive"}