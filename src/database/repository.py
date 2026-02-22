# src/database/repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Type
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .session import Base

T = TypeVar("T", bound=Base)

class AbstractRepository(ABC, Generic[T]):
    """
    Interface for Data Access.
    Business logic should depend on this, not SQLAlchemy/Supabase directly.
    """
    
    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0) -> List[T]:
        pass

    @abstractmethod
    async def create(self, obj: T) -> T:
        pass

    @abstractmethod
    async def update(self, id: str, data: dict) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass

class SQLAlchemyRepository(AbstractRepository[T]):
    """
    SQLAlchemy implementation of the Repository Pattern.
    Works with Supabase (via postgresql+asyncpg).
    """
    
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get(self, id: str) -> Optional[T]:
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def list(self, limit: int = 100, offset: int = 0) -> List[T]:
        result = await self.session.execute(select(self.model).limit(limit).offset(offset))
        return result.scalars().all()

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: str, data: dict) -> Optional[T]:
        # Fetch first
        obj = await self.get(id)
        if not obj:
            return None
            
        # Update attributes
        for key, value in data.items():
            setattr(obj, key, value)
            
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: str) -> bool:
        obj = await self.get(id)
        if not obj:
            return False
        
        await self.session.delete(obj)
        await self.session.commit()
        return True
