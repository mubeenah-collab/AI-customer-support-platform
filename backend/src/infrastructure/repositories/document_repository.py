from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.domain.entities.document import Document
from backend.src.domain.repositories.document_repository import IDocumentRepository
from backend.src.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyDocumentRepository(SQLAlchemyBaseRepository[Document], IDocumentRepository):
    """SQLAlchemy implementation of Document Repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)

    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
        stmt = select(Document).where(Document.user_id == user_id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, document_id: str, status: str, error_message: Optional[str] = None) -> Optional[Document]:
        doc = await self.get_by_id(document_id)
        if doc:
            doc.status = status
            if error_message is not None:
                doc.error_message = error_message
            await self.session.flush()
            await self.session.refresh(doc)
        return doc
