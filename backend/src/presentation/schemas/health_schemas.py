from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class LivenessResponse(BaseModel):
    status: str = "healthy"
    service: str = "AI Customer Support Platform API"
    timestamp: float


class ComponentHealth(BaseModel):
    name: str
    status: str  # healthy, unhealthy, degraded
    details: Optional[str] = None


class ReadinessResponse(BaseModel):
    status: str  # healthy, degraded, unhealthy
    components: List[ComponentHealth] = Field(default_factory=list)
    timestamp: float


class SystemMetricsResponse(BaseModel):
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    active_db_pool_status: str = "connected"
    timestamp: float
