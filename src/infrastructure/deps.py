from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure import Database

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async with Database._session_factory() as session:
        yield session