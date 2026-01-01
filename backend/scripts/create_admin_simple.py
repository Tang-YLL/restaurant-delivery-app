#!/usr/bin/env python3
"""
创建默认管理员账户 - 使用现有服务
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models import Admin
from app.core.security import get_password_hash
from sqlalchemy import select


async def create_admin():
    """创建默认管理员账户"""
    async with AsyncSessionLocal() as session:
        try:
            # 检查admin是否已存在
            result = await session.execute(
                select(Admin).where(Admin.username == "admin")
            )
            existing_admin = result.scalar_one_or_none()

            if existing_admin:
                print("✅ 管理员账户 'admin' 已存在，跳过创建")
                print(f"   用户名: {existing_admin.username}")
                print(f"   邮箱: {existing_admin.email}")
                return

            # 创建管理员
            admin = Admin(
                username="admin",
                password_hash=get_password_hash("admin123"),
                email="admin@example.com",
                role="super_admin",
                is_active=True
            )

            session.add(admin)
            await session.commit()
            await session.refresh(admin)

            print("✅ 成功创建管理员账户")
            print(f"   ID: {admin.id}")
            print(f"   用户名: {admin.username}")
            print(f"   邮箱: {admin.email}")
            print(f"   密码: admin123")
            print(f"   角色: {admin.role}")

        except Exception as e:
            await session.rollback()
            print(f"❌ 创建管理员失败: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(create_admin())
