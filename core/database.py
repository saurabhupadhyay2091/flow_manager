from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
import os

DB_URL = os.getenv("FLOW_DB_URL", "sqlite+aiosqlite:///./flow_runs.db")

engine: AsyncEngine = create_async_engine(DB_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        # create tables
        await conn.run_sync(SQLModel.metadata.create_all)
