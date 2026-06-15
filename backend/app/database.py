"""
FloweringAgents — Database connection
PostgreSQL + SQLAlchemy async
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://fa_user:password@localhost:5432/floweringagents"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Additive migration: agents table may pre-date the status/genesis_mult
        # columns introduced alongside the Passive/Dead lifecycle feature.
        await conn.execute(text(
            "ALTER TABLE agents ADD COLUMN IF NOT EXISTS status VARCHAR(10) NOT NULL DEFAULT 'active'"
        ))
        await conn.execute(text(
            "ALTER TABLE agents ADD COLUMN IF NOT EXISTS genesis_mult FLOAT DEFAULT 0.14"
        ))
