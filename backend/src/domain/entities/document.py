import uuid
from typing import List, Optional
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.src.infrastructure.database.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    uploader: Mapped["User"] = relationship("User", back_populates="documents")
    chunks: Mapped[List["Chunk"]] = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    def __init__(
        self,
        title: str,
        filename: str,
        file_path: str,
        file_type: str,
        file_size: int,
        mime_type: str,
        user_id: str,
        status: str = "pending",
        chunk_count: int = 0,
        error_message: Optional[str] = None,
        id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.filename = filename
        self.file_path = file_path
        self.file_type = file_type
        self.file_size = file_size
        self.mime_type = mime_type
        self.user_id = user_id
        self.status = status
        self.chunk_count = chunk_count
        self.error_message = error_message
