from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.domain.entities.report import Report
from backend.src.domain.repositories.report_repository import IReportRepository
from backend.src.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyReportRepository(SQLAlchemyBaseRepository[Report], IReportRepository):
    """SQLAlchemy implementation of IReportRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Report)

    async def get_by_user_id(self, user_id: str) -> List[Report]:
        stmt = (
            select(Report)
            .where(Report.user_id == user_id)
            .order_by(Report.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
