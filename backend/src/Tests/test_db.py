import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.config import setting
from src.main import app
from src.database import get_async_session

engine = create_async_engine(
  setting.DATABASE_URL_asyncpg +"/testing",
  connect_args={"check_same_thread": False},
  poolclass=StaticPool
)

testing_async_session_factory = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def override_get_async_session():
    async with testing_async_session_factory() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session