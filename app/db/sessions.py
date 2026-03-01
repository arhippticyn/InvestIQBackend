from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import DB_URL, DEBUG

clean_url = DB_URL.split("?")[0] if DB_URL else DB_URL

if DEBUG:
    engine = create_async_engine(DB_URL)
else:
    engine = create_async_engine(
        clean_url, 
        echo=True,
        connect_args={"ssl": "require"}
    )

SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as db:
        yield db