"""
测试配置和Fixture
"""
import pytest
import os
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.core.config import get_settings

# 确保测试环境标志已设置
os.environ["TESTING"] = "true"

settings = get_settings()

# 创建测试数据库引擎(使用SQLite内存数据库)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_db():
    """创建测试数据库"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        # 导入种子数据
        await _seed_test_data(session)
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


async def _seed_test_data(db: AsyncSession):
    """导入测试种子数据"""
    from app.models import Category, Product
    from sqlalchemy import select

    # 1. 创建分类
    categories_data = [
        {"name": "热菜", "code": "hot_dish", "description": "各类炒菜、烧菜、炖菜等", "sort_order": 1},
        {"name": "凉菜", "code": "cold_dish", "description": "凉拌菜、沙拉等", "sort_order": 2},
        {"name": "主食", "code": "staple_food", "description": "米饭、面食、包子等", "sort_order": 3},
        {"name": "汤类", "code": "soup", "description": "各类汤品", "sort_order": 4},
    ]

    category_map = {}
    for cat_data in categories_data:
        # 检查是否已存在
        result = await db.execute(
            select(Category).where(Category.name == cat_data["name"])
        )
        existing = result.scalar_one_or_none()

        if not existing:
            category = Category(**cat_data)
            db.add(category)
            await db.flush()
            category_map[category.name] = category
        else:
            category_map[existing.name] = existing

    # 2. 创建示例商品（每个分类3个）
    products_data = [
        # 热菜
        {"title": "青椒炒肉", "description": "经典家常菜，青椒配肉丝", "price": 28.00, "category_id": category_map["热菜"].id, "stock": 50, "local_image_path": "/images/青椒炒肉.png"},
        {"title": "红烧肉", "description": "肥而不腻，入口即化", "price": 48.00, "category_id": category_map["热菜"].id, "stock": 30, "local_image_path": "/images/红烧肉.png"},
        {"title": "鱼香肉丝", "description": "酸甜可口，经典川菜", "price": 32.00, "category_id": category_map["热菜"].id, "stock": 40, "local_image_path": "/images/鱼香肉丝.png"},

        # 凉菜
        {"title": "拍黄瓜", "description": "清爽解腻，夏日必备", "price": 12.00, "category_id": category_map["凉菜"].id, "stock": 100, "local_image_path": "/images/拍黄瓜.png"},
        {"title": "凉拌木耳", "description": "脆嫩爽口，营养丰富", "price": 18.00, "category_id": category_map["凉菜"].id, "stock": 80, "local_image_path": "/images/凉拌木耳.png"},
        {"title": "口水鸡", "description": "麻辣鲜香，开胃下饭", "price": 38.00, "category_id": category_map["凉菜"].id, "stock": 25, "local_image_path": "/images/口水鸡.png"},

        # 主食
        {"title": "白米饭", "description": "粒粒分明，香甜软糯", "price": 2.00, "category_id": category_map["主食"].id, "stock": 200, "local_image_path": "/images/白米饭.png"},
        {"title": "蛋炒饭", "description": "粒粒金黄，香气扑鼻", "price": 15.00, "category_id": category_map["主食"].id, "stock": 50, "local_image_path": "/images/蛋炒饭.png"},
        {"title": "牛肉面", "description": "汤浓面劲，肉烂入味", "price": 22.00, "category_id": category_map["主食"].id, "stock": 40, "local_image_path": "/images/牛肉面.png"},

        # 汤类
        {"title": "紫菜蛋花汤", "description": "清淡爽口，快速便捷", "price": 8.00, "category_id": category_map["汤类"].id, "stock": 150, "local_image_path": "/images/紫菜蛋花汤.png"},
        {"title": "冬瓜排骨汤", "description": "清热解腻，营养丰富", "price": 35.00, "category_id": category_map["汤类"].id, "stock": 30, "local_image_path": "/images/冬瓜排骨汤.png"},
        {"title": "番茄鸡蛋汤", "description": "酸甜开胃，家常美味", "price": 12.00, "category_id": category_map["汤类"].id, "stock": 100, "local_image_path": "/images/番茄鸡蛋汤.png"},
    ]

    for prod_data in products_data:
        # 检查是否已存在
        result = await db.execute(
            select(Product).where(Product.title == prod_data["title"])
        )
        existing = result.scalar_one_or_none()

        if not existing:
            product = Product(**prod_data)
            db.add(product)

    await db.commit()
    print(f"\n✓ 测试种子数据已加载: {len(category_map)} 个分类, {len(products_data)} 个商品")


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession):
    """创建测试客户端"""
    from app.core.database import get_db
    from tests import get_app

    app = get_app()

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "phone": "13800138000",
        "password": "test123456",
        "nickname": "测试用户"
    }


@pytest.fixture
def test_admin_data():
    """测试管理员数据"""
    return {
        "username": "testadmin",
        "password": "admin123456",
        "email": "testadmin@example.com"
    }


@pytest.fixture
def test_product_data():
    """测试商品数据"""
    return {
        "name": "测试商品",
        "description": "这是一个测试商品",
        "price": 29.99,
        "category_id": 1,
        "image_url": "https://example.com/image.jpg",
        "is_available": True,
        "is_hot": False
    }


@pytest.fixture
def test_category_data():
    """测试分类数据"""
    return {
        "name": "测试分类",
        "description": "测试分类描述",
        "sort_order": 1,
        "is_active": True
    }


@pytest.fixture(scope="function")
async def test_token(client: AsyncClient, test_user_data: dict):
    """创建测试用户并返回token"""
    # 先注册用户
    register_response = await client.post(
        "/api/auth/register",
        json=test_user_data
    )

    # 如果注册成功（201），则登录获取token
    # 如果注册失败（400，可能用户已存在），直接登录
    login_response = await client.post(
        "/api/auth/login",
        json={
            "phone": test_user_data["phone"],
            "password": test_user_data["password"]
        }
    )

    if login_response.status_code == 200:
        data = login_response.json()
        return data.get("access_token")
    return None


@pytest.fixture(scope="function")
async def test_admin_token(client: AsyncClient, test_admin_data: dict):
    """创建管理员并返回admin token"""
    # 先通过管理员接口登录
    login_response = await client.post(
        "/api/admin/auth/login",
        json={
            "username": test_admin_data["username"],
            "password": test_admin_data["password"]
        }
    )

    if login_response.status_code == 200:
        data = login_response.json()
        return data.get("access_token")
    return None
