import logging
import os
import time
from typing import List, Tuple
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

try:
    import psutil
except ImportError:
    psutil = None

from backend.src.ai.rag.chroma_vector_store import ChromaVectorStore
from backend.src.presentation.schemas.health_schemas import ComponentHealth, SystemMetricsResponse

logger = logging.getLogger("health_service")


class HealthService:
    """Service performing system health checks, database readiness probes, and resource metrics collection."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_database_health(self) -> ComponentHealth:
        """Check PostgreSQL database connectivity."""
        try:
            await self.session.execute(text("SELECT 1"))
            return ComponentHealth(name="database", status="healthy", details="PostgreSQL/SQLite database connected")
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return ComponentHealth(name="database", status="unhealthy", details=f"Database error: {str(e)}")

    def check_vector_store_health(self) -> ComponentHealth:
        """Check ChromaDB vector database connectivity."""
        try:
            store = ChromaVectorStore()
            count = store.collection.count()
            return ComponentHealth(
                name="vector_store",
                status="healthy",
                details=f"ChromaDB operational with {count} indexed vectors",
            )
        except Exception as e:
            logger.error(f"Vector store health check failed: {str(e)}")
            return ComponentHealth(name="vector_store", status="unhealthy", details=f"ChromaDB error: {str(e)}")

    async def get_readiness_status(self) -> Tuple[str, List[ComponentHealth]]:
        """Run all readiness probes and determine overall system readiness."""
        db_health = await self.check_database_health()
        chroma_health = self.check_vector_store_health()

        components = [db_health, chroma_health]
        overall_status = "healthy"

        for c in components:
            if c.status == "unhealthy":
                overall_status = "unhealthy"
                break
            elif c.status == "degraded":
                overall_status = "degraded"

        return overall_status, components

    def get_system_metrics(self) -> SystemMetricsResponse:
        """Collect CPU, RAM, and Disk resource utilization metrics."""
        cpu = 0.0
        memory = 0.0
        disk = 0.0

        if psutil:
            try:
                cpu = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory().percent
                disk = psutil.disk_usage(os.getcwd()).percent
            except Exception as e:
                logger.warning(f"Error gathering psutil metrics: {str(e)}")

        return SystemMetricsResponse(
            cpu_usage_percent=cpu,
            memory_usage_percent=memory,
            disk_usage_percent=disk,
            active_db_pool_status="connected",
            timestamp=time.time(),
        )
