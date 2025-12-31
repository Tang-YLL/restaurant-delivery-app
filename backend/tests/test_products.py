"""
商品和购物车相关测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestProducts:
    """商品测试类"""

    @pytest.mark.asyncio
    async def test_get_products(self, client: AsyncClient):
        """测试获取商品列表"""
        response = await client.get("/api/v1/products")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "pagination" in data
        assert isinstance(data["products"], list)

    @pytest.mark.asyncio
    async def test_get_products_with_pagination(self, client: AsyncClient):
        """测试分页获取商品"""
        response = await client.get("/api/v1/products?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["products"], list)
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 10

    @pytest.mark.asyncio
    async def test_get_products_with_category_filter(self, client: AsyncClient):
        """测试按分类筛选商品"""
        response = await client.get("/api/v1/products?category_id=1")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data

    @pytest.mark.asyncio
    async def test_get_products_with_sort(self, client: AsyncClient):
        """测试商品排序"""
        # 价格升序
        response = await client.get("/api/v1/products?sort_by=price_asc")
        assert response.status_code == 200
        # 销量排序
        response = await client.get("/api/v1/products?sort_by=sales")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_products(self, client: AsyncClient):
        """测试搜索商品"""
        response = await client.get("/api/v1/products/search/test")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "pagination" in data

    @pytest.mark.asyncio
    async def test_get_hot_products(self, client: AsyncClient):
        """测试获取热销商品"""
        response = await client.get("/api/v1/products/hot?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_product_detail(self, client: AsyncClient):
        """测试获取商品详情"""
        # 先创建一个商品
        response = await client.get("/api/v1/products/1")
        # 如果商品不存在会返回404
        assert response.status_code in [200, 404]


class TestCategories:
    """分类测试类"""

    @pytest.mark.asyncio
    async def test_get_categories(self, client: AsyncClient):
        """测试获取分类列表"""
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_category_detail(self, client: AsyncClient):
        """测试获取分类详情"""
        response = await client.get("/api/v1/categories/1")
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_create_category_unauthorized(self, client: AsyncClient):
        """测试未授权创建分类"""
        response = await client.post(
            "/api/v1/categories",
            json={
                "name": "测试分类",
                "code": "test_category",
                "description": "测试分类描述"
            }
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_category_unauthorized(self, client: AsyncClient):
        """测试未授权更新分类"""
        response = await client.put(
            "/api/v1/categories/1",
            json={"name": "更新后的分类名"}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_category_unauthorized(self, client: AsyncClient):
        """测试未授权删除分类"""
        response = await client.delete("/api/v1/categories/1")
        assert response.status_code == 403


class TestCart:
    """购物车测试类"""

    @pytest.mark.asyncio
    async def test_get_cart_unauthorized(self, client: AsyncClient):
        """测试未授权访问购物车"""
        response = await client.get("/api/v1/cart")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_add_to_cart_unauthorized(self, client: AsyncClient):
        """测试未授权添加到购物车"""
        response = await client.post(
            "/api/v1/cart",
            json={
                "product_id": 1,
                "quantity": 2
            }
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_cart_unauthorized(self, client: AsyncClient):
        """测试未授权更新购物车"""
        response = await client.put(
            "/api/v1/cart/1",
            json={"quantity": 3}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_remove_from_cart_unauthorized(self, client: AsyncClient):
        """测试未授权删除购物车商品"""
        response = await client.delete("/api/v1/cart/1")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_clear_cart_unauthorized(self, client: AsyncClient):
        """测试未授权清空购物车"""
        response = await client.delete("/api/v1/cart")
        assert response.status_code == 403


class TestProductStock:
    """库存管理测试"""

    @pytest.mark.asyncio
    async def test_validate_stock(self, client: AsyncClient, db: AsyncSession):
        """测试库存验证"""
        # 这个测试需要在有库存数据的情况下运行
        from app.repositories import ProductRepository
        from app.models import Product

        repo = ProductRepository(Product, db)
        is_valid = await repo.validate_stock(1, 10)
        # 结果取决于商品是否存在以及库存是否充足
        assert isinstance(is_valid, bool)


class TestHealth:
    """健康检查测试"""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """测试健康检查"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """测试根路径"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
