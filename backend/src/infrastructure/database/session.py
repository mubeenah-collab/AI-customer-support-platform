from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from backend.src.config.settings import settings

# Determine if we use SQLite in-memory or Postgres
ASYNC_DB_URL = settings.async_database_url
SYNC_DB_URL = settings.sync_database_url

# Async Engine & SessionFactory
async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Sync Engine & SessionFactory (for Alembic & sync scripts)
sync_engine = create_engine(
    SYNC_DB_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

SyncSessionFactory = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining an async database session."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Generator[Session, None, None]:
    """Dependency for obtaining a sync database session."""
    session = SyncSessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
