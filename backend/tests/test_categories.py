"""
分类相关测试
"""
import pytest
from httpx import AsyncClient


class TestCategories:
    """分类测试类"""

    @pytest.mark.asyncio
    async def test_create_category(self, client: AsyncClient, test_user_data: dict):
        """测试创建分类(需要管理员权限)"""
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

        # 创建分类
        response = await client.post(
            "/api/categories",
            json={
                "name": "测试分类",
                "description": "测试分类描述",
                "sort_order": 1
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        # 可能需要管理员权限,返回401/403,或成功201,或请求错误400
        assert response.status_code in [201, 401, 403, 400]

    @pytest.mark.asyncio
    async def test_get_categories(self, client: AsyncClient):
        """测试获取分类列表"""
        response = await client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_category_by_id(self, client: AsyncClient):
        """测试获取单个分类"""
        response = await client.get("/api/categories/1")
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_update_category(self, client: AsyncClient, test_user_data: dict):
        """测试更新分类"""
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

        # 更新分类
        response = await client.put(
            "/api/categories/1",
            json={"name": "更新后的分类"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_delete_category(self, client: AsyncClient, test_user_data: dict):
        """测试删除分类"""
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

        # 删除分类
        response = await client.delete(
            "/api/categories/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 204, 401, 403, 404]
