from typing import List, Optional
from backend.src.domain.entities.document import Document
from backend.src.domain.repositories.base_repository import IBaseRepository


class IDocumentRepository(IBaseRepository[Document]):
    """Repository contract for Document entity."""

    async def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
        raise NotImplementedError

    async def update_status(self, document_id: str, status: str, error_message: Optional[str] = None) -> Optional[Document]:
        raise NotImplementedError
