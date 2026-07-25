import logging
import time
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.infrastructure.database.session import get_async_db
from backend.src.monitoring.health_service import HealthService
from backend.src.presentation.schemas.health_schemas import (
    LivenessResponse,
    ReadinessResponse,
    SystemMetricsResponse,
)

logger = logging.getLogger("health_router")

router = APIRouter(prefix="/health", tags=["System Health & Monitoring"])


def get_health_service(session: AsyncSession = Depends(get_async_db)) -> HealthService:
    return HealthService(session=session)


@router.get(
    "/live",
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe endpoint",
)
async def liveness_probe():
    return LivenessResponse(timestamp=time.time())


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness probe checking database and ChromaDB connectivity",
)
async def readiness_probe(
    health_service: HealthService = Depends(get_health_service),
):
    overall_status, components = await health_service.get_readiness_status()
    return ReadinessResponse(
        status=overall_status,
        components=components,
        timestamp=time.time(),
    )


@router.get(
    "/metrics",
    response_model=SystemMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="System resource utilization metrics (CPU, RAM, Disk)",
)
async def system_metrics(
    health_service: HealthService = Depends(get_health_service),
):
    return health_service.get_system_metrics()
