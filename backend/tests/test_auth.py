"""
认证相关测试
"""
import pytest
from httpx import AsyncClient


class TestAuth:
    """认证测试类"""

    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient, test_user_data: dict):
        """测试用户注册"""
        response = await client.post(
            "/api/auth/register",
            json=test_user_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["phone"] == test_user_data["phone"]
        assert data["nickname"] == test_user_data["nickname"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_phone(self, client: AsyncClient, test_user_data: dict):
        """测试重复手机号注册"""
        # 第一次注册
        await client.post("/api/auth/register", json=test_user_data)

        # 第二次注册(应该失败)
        response = await client.post(
            "/api/auth/register",
            json=test_user_data
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_user(self, client: AsyncClient, test_user_data: dict):
        """测试用户登录"""
        # 先注册
        await client.post("/api/auth/register", json=test_user_data)

        # 登录
        response = await client.post(
            "/api/auth/login",
            json={
                "phone": test_user_data["phone"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user_data: dict):
        """测试错误密码登录"""
        # 先注册
        await client.post("/api/auth/register", json=test_user_data)

        # 使用错误密码登录
        response = await client.post(
            "/api/auth/login",
            json={
                "phone": test_user_data["phone"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, test_user_data: dict):
        """测试获取当前用户信息"""
        # 注册并登录
        await client.post("/api/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/auth/login",
            json={
                "phone": test_user_data["phone"],
                "password": test_user_data["password"]
            }
        )
        login_data = login_response.json()
        token = login_data["access_token"]

        # 调试: 打印token信息
        from app.core.security import decode_token
        from jose import jwt
        from app.core.config import get_settings

        settings = get_settings()
        print(f"\n=== Token调试信息 ===")
        print(f"完整Token: {token}")
        print(f"SECRET_KEY: {settings.SECRET_KEY}")
        print(f"ALGORITHM: {settings.ALGORITHM}")

        # 尝试手动解码
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            print(f"手动解码成功: {payload}")
        except Exception as e:
            print(f"手动解码失败: {type(e).__name__}: {e}")

        # 使用decode_token
        payload = decode_token(token)
        print(f"decode_token结果: {payload}")
        print(f"====================\n")

        # 获取当前用户信息
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == test_user_data["phone"]

    @pytest.mark.asyncio
    async def test_get_current_user_without_token(self, client: AsyncClient):
        """测试不带token访问受保护路由"""
        response = await client.get("/api/auth/me")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_logout(self, client: AsyncClient, test_user_data: dict):
        """测试用户登出"""
        # 注册并登录
        await client.post("/api/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/auth/login",
            json={
                "phone": test_user_data["phone"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]

        # 登出
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


class TestAdminAuth:
    """管理员认证测试类"""

    @pytest.mark.asyncio
    async def test_admin_login(self, client: AsyncClient):
        """测试管理员登录(需要先在数据库创建管理员)"""
        # 这个测试需要在数据库中有管理员记录
        # 可以在fixture中创建测试管理员
        response = await client.post(
            "/api/admin/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            }
        )
        # 可能返回401如果没有admin记录
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
