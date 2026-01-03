#!/usr/bin/env python3
"""
创建默认管理员账户
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin():
    """创建默认管理员账户"""
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    # 创建异步Session
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        try:
            # 检查admin是否已存在
            from sqlalchemy import select, text
            result = await session.execute(
                text("SELECT id FROM admins WHERE username = 'admin'")
            )
            existing_admin = result.fetchone()

            if existing_admin:
                print("✅ 管理员账户 'admin' 已存在，跳过创建")
                return

            # 创建管理员
            password_hash = pwd_context.hash("admin123")
            await session.execute(
                text("""
                    INSERT INTO admins (username, password_hash, email, role, is_active, created_at, updated_at)
                    VALUES (:username, :password_hash, :email, :role, :is_active, datetime('now'), datetime('now'))
                """),
                {
                    "username": "admin",
                    "password_hash": password_hash,
                    "email": "admin@example.com",
                    "role": "super_admin",
                    "is_active": True
                }
            )

            await session.commit()
            print("✅ 成功创建管理员账户")
            print("   用户名: admin")
            print("   密码: admin123")

        except Exception as e:
            await session.rollback()
            print(f"❌ 创建管理员失败: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin())
