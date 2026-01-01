"""调试token验证问题"""
import asyncio
import sys
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.security import decode_token
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.models import Base, User
from sqlalchemy import select


async def main():
    # 创建测试数据库
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        # 注入数据库依赖
        from app.core.database import get_db

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db

        # 创建测试客户端
        async with AsyncClient(
            app=app,
            base_url="http://test",
            transport=ASGITransport(app=app)
        ) as client:
            # 1. 注册用户
            print("=== 注册用户 ===")
            reg_resp = await client.post("/api/auth/register", json={
                "phone": "13900000001",
                "password": "test123456",
                "nickname": "测试用户"
            })
            print(f"注册状态: {reg_resp.status_code}")
            if reg_resp.status_code == 201:
                print(f"注册用户: {reg_resp.json()}")

            # 2. 查询数据库中的用户
            print("\n=== 查询数据库 ===")
            result = await session.execute(select(User).where(User.phone == "13900000001"))
            user = result.scalar_one_or_none()
            if user:
                print(f"用户ID: {user.id}")
                print(f"用户phone: {user.phone}")
                print(f"用户is_active: {user.is_active}")

            # 3. 登录
            print("\n=== 登录 ===")
            login_resp = await client.post("/api/auth/login", json={
                "phone": "13900000001",
                "password": "test123456"
            })
            print(f"登录状态: {login_resp.status_code}")
            if login_resp.status_code == 200:
                login_data = login_resp.json()
                token = login_data.get("access_token")
                print(f"Token: {token[:50]}...")

                # 4. 解码token
                print("\n=== 解码Token ===")
                payload = decode_token(token)
                print(f"Token payload: {payload}")
                if payload:
                    print(f"User ID from token: {payload.get('sub')}")
                    print(f"Token type: {payload.get('type')}")
                    print(f"Is admin: {payload.get('is_admin')}")
                    print(f"Expiration: {payload.get('exp')}")

                # 5. 访问受保护路由
                print("\n=== 访问 /api/auth/me ===")
                me_resp = await client.get(
                    "/api/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                print(f"状态码: {me_resp.status_code}")
                print(f"响应: {me_resp.text[:300]}")

        app.dependency_overrides.clear()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
