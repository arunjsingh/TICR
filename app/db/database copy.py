from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Using aiosqlite for async support
DATABASE_URL = "sqlite+aiosqlite:///./learning.db"

engine = create_async_engine(DATABASE_URL, echo=True)

# Use async_sessionmaker instead of the old sessionmaker
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Dependency for FastAPI
async def get_db():
    async with SessionLocal() as session:
        yield session
