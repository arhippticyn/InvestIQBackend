from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import DB_URL

engine = create_async_engine(DB_URL)

SessionLocal = sessionmaker(engine, class_=AsyncSession)

async def get_db():
    async with SessionLocal() as db:
        yield db