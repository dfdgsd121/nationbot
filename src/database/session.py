# src/database/session.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Supabase Connection String (Async)
# Format: postgresql+asyncpg://user:pass@host:port/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/nationbot")

# Create Async Engine
# echo=True logs SQL queries for debugging
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Session Factory
async_session_factory = async_sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    """
    Dependency for FastAPI to get DB session.
    Yields async session and closes it after request.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
