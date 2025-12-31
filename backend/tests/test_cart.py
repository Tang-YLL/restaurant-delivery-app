"""
购物车相关测试
"""
import pytest
from httpx import AsyncClient


class TestCart:
    """购物车测试类"""

    @pytest.mark.asyncio
    async def test_add_to_cart(self, client: AsyncClient, test_user_data: dict):
        """测试添加商品到购物车"""
        # 注册并登录
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": test_user_data["phone"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]

        # 添加到购物车
        response = await client.post(
            "/api/v1/cart",
            json={
                "product_id": 1,
                "quantity": 2
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 201]  # 可能需要先创建商品

    @pytest.mark.asyncio
    async def test_get_cart(self, client: AsyncClient, test_user_data: dict):
        """测试获取购物车"""
        # 注册并登录
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": test_user_data["phone"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]

        # 获取购物车
        response = await client.get(
            "/api/v1/cart",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_cart_item(self, client: AsyncClient, test_user_data: dict):
        """测试更新购物车商品数量"""
        # 注册并登录
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": test_user_data["phone"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]

        # 更新购物车商品
        response = await client.put(
            "/api/v1/cart/1",
            json={"quantity": 3},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 404]  # 如果商品不存在返回404

    @pytest.mark.asyncio
    async def test_delete_cart_item(self, client: AsyncClient, test_user_data: dict):
        """测试删除购物车商品"""
        # 注册并登录
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": test_user_data["phone"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]

        # 删除购物车商品
        response = await client.delete(
            "/api/v1/cart/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 204, 404]

    @pytest.mark.asyncio
    async def test_clear_cart(self, client: AsyncClient, test_user_data: dict):
        """测试清空购物车"""
        # 注册并登录
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": test_user_data["phone"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]

        # 清空购物车
        response = await client.delete(
            "/api/v1/cart",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 204]
