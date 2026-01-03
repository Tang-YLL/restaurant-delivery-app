"""
单元测试
使用pytest和pytest-asyncio进行异步测试
"""
import pytest
import os
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.core.config import get_settings

# 设置测试环境标志
os.environ["TESTING"] = "true"

settings = get_settings()

# 创建测试数据库引擎(使用SQLite内存数据库)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 延迟导入app，避免初始化生产数据库
def get_app():
    """获取FastAPI应用实例"""
    from main import app
    return app


@pytest.fixture(scope="function")
async def test_db():
    """创建测试数据库"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession):
    """创建测试客户端"""
    from app.core.database import get_db

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "phone": "13800138000",
        "password": "test123456",
        "nickname": "测试用户"
    }


@pytest.fixture
def test_admin_data():
    """测试管理员数据"""
    return {
        "username": "testadmin",
        "password": "admin123456",
        "email": "testadmin@example.com"
    }
