"""
Pytest配置文件
提供测试fixtures和共享测试工具
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker

from app.models import Base


# 使用内存SQLite数据库进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环实例"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture
def sample_product_data():
    """示例商品数据"""
    return {
        "title": "测试商品",
        "category_id": 1,
        "local_image_path": "/images/test.jpg",
        "price": 29.99,
        "stock": 100,
        "description": "这是一个测试商品",
        "status": "active"
    }


@pytest.fixture
def sample_content_section_data():
    """示例内容区块数据"""
    return {
        "section_type": "story",
        "title": "品牌故事",
        "content": "<p>这是一个精彩的品牌故事</p>",
        "display_order": 1
    }


@pytest.fixture
def sample_nutrition_data():
    """示例营养数据"""
    return {
        "serving_size": "1份(200g)",
        "calories": 150.0,
        "protein": 8.5,
        "fat": 5.2,
        "carbohydrates": 18.0,
        "sodium": 450.0,
        "dietary_fiber": 2.5,
        "sugars": 3.0
    }
