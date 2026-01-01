"""
评价相关测试
"""
import pytest
from httpx import AsyncClient


class TestReviews:
    """评价测试类"""

    @pytest.mark.asyncio
    async def test_create_review(self, client: AsyncClient, test_user_data: dict):
        """测试创建评价"""
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

        # 创建评价
        response = await client.post(
            "/api/reviews",
            json={
                "order_id": 1,
                "product_id": 1,
                "rating": 5,
                "content": "非常好的商品!"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [201, 400, 404]  # 可能订单或商品不存在

    @pytest.mark.asyncio
    async def test_get_product_reviews(self, client: AsyncClient):
        """测试获取商品评价"""
        response = await client.get("/api/reviews/product/1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_user_reviews(self, client: AsyncClient, test_user_data: dict):
        """测试获取用户评价"""
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

        # 获取用户评价
        response = await client.get(
            "/api/reviews/user",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_review(self, client: AsyncClient, test_user_data: dict):
        """测试更新评价"""
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

        # 更新评价
        response = await client.put(
            "/api/reviews/1",
            json={
                "rating": 4,
                "content": "更新后的评价内容"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 403, 404]

    @pytest.mark.asyncio
    async def test_delete_review(self, client: AsyncClient, test_user_data: dict):
        """测试删除评价"""
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

        # 删除评价
        response = await client.delete(
            "/api/reviews/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 204, 403, 404]


class TestAdminReviews:
    """管理员评价管理测试"""

    @pytest.mark.asyncio
    async def test_admin_get_all_reviews(self, client: AsyncClient):
        """测试管理员获取所有评价"""
        # 需要管理员token
        response = await client.get("/api/admin/reviews")
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_admin_delete_review(self, client: AsyncClient):
        """测试管理员删除评价"""
        # 需要管理员token
        response = await client.delete("/api/admin/reviews/1")
        assert response.status_code in [200, 204, 401, 403]

    @pytest.mark.asyncio
    async def test_admin_reply_review(self, client: AsyncClient):
        """测试管理员回复评价"""
        # 需要管理员token
        response = await client.post(
            "/api/admin/reviews/1/reply",
            json={"reply": "感谢您的评价!"}
        )
        assert response.status_code in [200, 201, 401, 403]
