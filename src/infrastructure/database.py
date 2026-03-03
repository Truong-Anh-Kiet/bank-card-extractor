import os
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

logging.basicConfig(level=logging.ERROR)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Database:
    """Manages the database connection and session factory."""
    
    _engine = None
    _session_factory = None

    @classmethod
    async def init_db(cls) -> None:
        if cls._engine is not None:
            return

        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL is not set in .env")
            if "asyncpg" not in database_url:
                raise ValueError("Must use postgresql+asyncpg:// for async")

            cls._engine = create_async_engine(
                database_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
            cls._session_factory = async_sessionmaker(
                cls._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            async with cls._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logging.error(f"Database initialization failed: {str(e)}")
            raise

    @classmethod
    async def close_db(cls) -> None:
        if cls._engine:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await Database.init_db()
        logging.info("Database connected successfully (async mode)")
        yield
    finally:
        await Database.close_db()
        logging.info("Database connections closed")