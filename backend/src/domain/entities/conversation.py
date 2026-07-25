import uuid
from typing import List, Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.src.infrastructure.database.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    title: Mapped[str] = mapped_column(String(255), default="New Support Conversation", nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

    def __init__(
        self,
        user_id: str,
        title: str = "New Support Conversation",
        status: str = "active",
        id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.status = status
