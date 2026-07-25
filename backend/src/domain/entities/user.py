import uuid
from typing import List, Optional
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.src.infrastructure.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="customer", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="uploader", cascade="all, delete-orphan")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="creator", cascade="all, delete-orphan")
    sessions: Mapped[List["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    def __init__(
        self,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        role: str = "customer",
        is_active: bool = True,
        is_superuser: bool = False,
        id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.id = id or str(uuid.uuid4())
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.role = role
        self.is_active = is_active
        self.is_superuser = is_superuser
