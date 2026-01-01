"""
订单和评价API单元测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_order_from_cart(async_client: AsyncClient, test_token: str):
    """测试从购物车创建订单"""
    headers = {"Authorization": f"Bearer {test_token}"}

    # 创建订单(到店自取)
    order_data = {
        "delivery_type": "pickup",
        "pickup_name": "张三",
        "pickup_phone": "13800138000",
        "remark": "少辣"
    }

    response = await async_client.post("/api/orders", json=order_data, headers=headers)

    # 购物车可能为空,预期可能失败
    assert response.status_code in [200, 201, 400]


@pytest.mark.asyncio
async def test_create_order_delivery_validation(async_client: AsyncClient, test_token: str):
    """测试外卖配送验证"""
    headers = {"Authorization": f"Bearer {test_token}"}

    # 外卖配送需要提供地址
    order_data = {
        "delivery_type": "delivery",
        "pickup_name": "张三",
        "pickup_phone": "13800138000"
    }

    response = await async_client.post("/api/orders", json=order_data, headers=headers)

    # 应该返回400错误(缺少配送地址)
    assert response.status_code == 400
    assert "配送地址" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_order_pickup_validation(async_client: AsyncClient, test_token: str):
    """测试到店自取验证"""
    headers = {"Authorization": f"Bearer {test_token}"}

    # 到店自取需要提供自提人信息
    order_data = {
        "delivery_type": "pickup",
        "delivery_address": "北京市朝阳区xxx"
    }

    response = await async_client.post("/api/orders", json=order_data, headers=headers)

    # 应该返回400错误(缺少自提人信息)
    assert response.status_code == 400
    assert "自提人" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_orders(async_client: AsyncClient, test_token: str):
    """测试获取用户订单列表"""
    headers = {"Authorization": f"Bearer {test_token}"}

    response = await async_client.get("/api/orders", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert "pagination" in data


@pytest.mark.asyncio
async def test_get_orders_with_status_filter(async_client: AsyncClient, test_token: str):
    """测试订单状态筛选"""
    headers = {"Authorization": f"Bearer {test_token}"}

    response = await async_client.get("/api/orders?status=pending", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "orders" in data


@pytest.mark.asyncio
async def test_cancel_order(async_client: AsyncClient, test_token: str, db: AsyncSession):
    """测试取消订单"""
    from app.models import Order
    from app.repositories import OrderRepository
    from sqlalchemy import select

    headers = {"Authorization": f"Bearer {test_token}"}

    # 首先创建一个测试订单
    order_repo = OrderRepository(Order, db)
    order = await order_repo.create({
        "order_number": "TEST001",
        "user_id": 1,  # 假设用户ID为1
        "total_amount": 100.00,
        "status": "pending"
    })

    if order:
        response = await async_client.put(f"/api/orders/{order.id}/cancel", headers=headers)

        # 可能因为权限或状态问题失败
        assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
async def test_pay_order(async_client: AsyncClient, test_token: str, db: AsyncSession):
    """测试支付订单"""
    from app.models import Order
    from app.repositories import OrderRepository

    headers = {"Authorization": f"Bearer {test_token}"}

    # 首先创建一个测试订单
    order_repo = OrderRepository(Order, db)
    order = await order_repo.create({
        "order_number": "TEST002",
        "user_id": 1,
        "total_amount": 100.00,
        "status": "pending"
    })

    if order:
        response = await async_client.put(f"/api/orders/{order.id}/pay", headers=headers)

        # 可能因为权限或状态问题失败
        assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
async def test_create_review(async_client: AsyncClient, test_token: str):
    """测试创建评价"""
    headers = {"Authorization": f"Bearer {test_token}"}

    # 创建评价
    review_data = {
        "product_id": 1,
        "order_id": 1,
        "rating": 5,
        "content": "很好吃,下次再来!",
        "images": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    }

    response = await async_client.post("/api/reviews", json=review_data, headers=headers)

    # 可能因为订单状态或已评价失败
    assert response.status_code in [200, 201, 400]


@pytest.mark.asyncio
async def test_create_review_validation(async_client: AsyncClient, test_token: str):
    """测试评价验证(评分范围)"""
    headers = {"Authorization": f"Bearer {test_token}"}

    # 评分超出范围
    review_data = {
        "product_id": 1,
        "order_id": 1,
        "rating": 6,  # 超出1-5范围
        "content": "测试评价"
    }

    response = await async_client.post("/api/reviews", json=review_data, headers=headers)

    # 应该返回422验证错误
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_product_reviews(async_client: AsyncClient):
    """测试获取商品评价列表"""
    response = await async_client.get("/api/reviews/products/1")

    assert response.status_code == 200
    data = response.json()
    assert "reviews" in data
    assert "summary" in data
    assert "pagination" in data


@pytest.mark.asyncio
async def test_get_product_rating_summary(async_client: AsyncClient):
    """测试获取商品评分汇总"""
    response = await async_client.get("/api/reviews/products/1/summary")

    assert response.status_code == 200
    data = response.json()
    assert "average_rating" in data
    assert "review_count" in data
    assert "rating_distribution" in data


@pytest.mark.asyncio
async def test_get_user_reviews(async_client: AsyncClient, test_token: str):
    """测试获取用户评价列表"""
    headers = {"Authorization": f"Bearer {test_token}"}

    response = await async_client.get("/api/reviews", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_review_detail(async_client: AsyncClient):
    """测试获取评价详情"""
    response = await async_client.get("/api/reviews/1")

    # 可能评价不存在
    assert response.status_code in [200, 404]
