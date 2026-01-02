import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from app.core.config import get_settings

settings = get_settings()

# 检查是否为测试环境
IS_TESTING = os.getenv("TESTING", "false").lower() == "true"

# 只在非测试环境创建生产数据库引擎
if not IS_TESTING:
    # 根据数据库类型创建引擎
    if "sqlite" in settings.DATABASE_URL.lower():
        # SQLite配置
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
        )
    else:
        # PostgreSQL/MySQL配置（带连接池）
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )

    # 创建异步SessionLocal类
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,  # 保持autocommit=False，手动管理事务
        autoflush=False
    )
else:
    # 测试环境使用占位符
    engine = None
    AsyncSessionLocal = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话"""
    if IS_TESTING:
        # 测试环境不应该调用这个函数
        raise RuntimeError("测试环境应该使用test_db fixture")

    # 创建session但不使用context manager，避免自动rollback
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        # 在finally中关闭session，但不commit/rollback
        # 让SQLAlchemy的implicit transaction在request结束时自然结束
        await session.close()


async def init_db():
    """初始化数据库（仅在非测试环境）"""
    if IS_TESTING:
        # 测试环境跳过初始化
        return
    from app.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
