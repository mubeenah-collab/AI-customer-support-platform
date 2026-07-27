import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import logging
from sqlalchemy import select
from backend.src.infrastructure.database.base import Base
from backend.src.infrastructure.database.session import AsyncSessionFactory, async_engine
from backend.src.domain.entities.user import User
from backend.src.infrastructure.security.password import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("create_admin")


async def seed_users():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionFactory() as session:
        # 1. Admin Account
        result = await session.execute(select(User).where(User.email == "admin@support.com"))
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            existing_admin.role = "admin"
            existing_admin.is_superuser = True
            existing_admin.hashed_password = hash_password("admin12345")
            logger.info("Admin user 'admin@support.com' reset to 'admin12345'.")
        else:
            admin_user = User(
                email="admin@support.com",
                hashed_password=hash_password("admin12345"),
                full_name="Platform Administrator",
                role="admin",
                is_active=True,
                is_superuser=True,
            )
            session.add(admin_user)
            logger.info("Created default Admin user 'admin@support.com'.")

        # 2. Customer Account
        cust_result = await session.execute(select(User).where(User.email == "customer@support.com"))
        existing_cust = cust_result.scalar_one_or_none()

        if existing_cust:
            existing_cust.role = "customer"
            existing_cust.hashed_password = hash_password("customer12345")
            logger.info("Customer user 'customer@support.com' reset to 'customer12345'.")
        else:
            cust_user = User(
                email="customer@support.com",
                hashed_password=hash_password("customer12345"),
                full_name="Jane Customer",
                role="customer",
                is_active=True,
                is_superuser=False,
            )
            session.add(cust_user)
            logger.info("Created default Customer user 'customer@support.com'.")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_users())
