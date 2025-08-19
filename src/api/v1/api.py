"""
API v1 router configuration.
"""

from fastapi import APIRouter
from src.api.v1.endpoints import webhook, health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    webhook.router,
    prefix="/webhook",
    tags=["webhook"]
)

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)