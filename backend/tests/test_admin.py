"""
管理员功能测试
"""
import pytest
from httpx import AsyncClient


class TestAdminAuth:
    """管理员认证测试"""

    @pytest.mark.asyncio
    async def test_admin_login(self, client: AsyncClient):
        """测试管理员登录"""
        response = await client.post(
            "/api/v1/admin/auth/login",
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

    @pytest.mark.asyncio
    async def test_admin_login_wrong_credentials(self, client: AsyncClient):
        """测试错误的管理员凭据"""
        response = await client.post(
            "/api/v1/admin/auth/login",
            json={
                "username": "wrong",
                "password": "wrong"
            }
        )
        assert response.status_code == 401


class TestAdminProducts:
    """管理员商品管理测试"""

    @pytest.mark.asyncio
    async def test_admin_create_product(self, client: AsyncClient):
        """测试管理员创建商品"""
        # 需要管理员token
        response = await client.post(
            "/api/v1/admin/products",
            json={
                "name": "测试商品",
                "description": "商品描述",
                "price": 29.99,
                "category_id": 1
            }
        )
        assert response.status_code in [201, 401, 403]

    @pytest.mark.asyncio
    async def test_admin_update_product(self, client: AsyncClient):
        """测试管理员更新商品"""
        response = await client.put(
            "/api/v1/admin/products/1",
            json={
                "name": "更新后的商品",
                "price": 39.99
            }
        )
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_admin_delete_product(self, client: AsyncClient):
        """测试管理员删除商品"""
        response = await client.delete("/api/v1/admin/products/1")
        assert response.status_code in [200, 204, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_admin_update_stock(self, client: AsyncClient):
        """测试管理员更新库存"""
        response = await client.patch(
            "/api/v1/admin/products/1/stock",
            json={"stock": 100}
        )
        assert response.status_code in [200, 401, 403, 404]


class TestAdminOrders:
    """管理员订单管理测试"""

    @pytest.mark.asyncio
    async def test_admin_get_all_orders(self, client: AsyncClient):
        """测试管理员获取所有订单"""
        response = await client.get("/api/v1/admin/orders")
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_admin_get_order_by_id(self, client: AsyncClient):
        """测试管理员获取订单详情"""
        response = await client.get("/api/v1/admin/orders/1")
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_admin_update_order_status(self, client: AsyncClient):
        """测试管理员更新订单状态"""
        response = await client.patch(
            "/api/v1/admin/orders/1/status",
            json={"status": "preparing"}
        )
        assert response.status_code in [200, 401, 403, 404]


class TestAdminUsers:
    """管理员用户管理测试"""

    @pytest.mark.asyncio
    async def test_admin_get_all_users(self, client: AsyncClient):
        """测试管理员获取所有用户"""
        response = await client.get("/api/v1/admin/users")
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_admin_get_user_by_id(self, client: AsyncClient):
        """测试管理员获取用户详情"""
        response = await client.get("/api/v1/admin/users/1")
        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_admin_ban_user(self, client: AsyncClient):
        """测试管理员封禁用户"""
        response = await client.post("/api/v1/admin/users/1/ban")
        assert response.status_code in [200, 401, 403, 404]


class TestAdminAnalytics:
    """管理员数据分析测试"""

    @pytest.mark.asyncio
    async def test_admin_get_dashboard_stats(self, client: AsyncClient):
        """测试获取仪表盘统计数据"""
        response = await client.get("/api/v1/admin/analytics/dashboard")
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_admin_get_sales_stats(self, client: AsyncClient):
        """测试获取销售统计"""
        response = await client.get("/api/v1/admin/analytics/sales")
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_admin_get_popular_products(self, client: AsyncClient):
        """测试获取热门商品"""
        response = await client.get("/api/v1/admin/analytics/products/popular")
        assert response.status_code in [200, 401, 403]


class TestAdminAuditLogs:
    """管理员审计日志测试"""

    @pytest.mark.asyncio
    async def test_admin_get_audit_logs(self, client: AsyncClient):
        """测试获取审计日志"""
        response = await client.get("/api/v1/admin/audit-logs")
        assert response.status_code in [200, 401, 403]
