"""
数据库模型测试

测试商品详情相关的数据库模型：
- ContentSection
- NutritionFact
- 与Product的关联关系
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product, Category, ContentSection, NutritionFact, ProductStatus


@pytest.mark.asyncio
async def test_content_section_creation(db_session: AsyncSession):
    """
    测试内容区块创建

    Given: 一个有效的商品和内容区块数据
    When: 创建内容区块
    Then: 内容区块成功创建，字段值正确
    """
    # Arrange - 创建分类和商品
    category = Category(name="测试分类", code="test", description="测试")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        title="测试商品",
        category_id=category.id,
        local_image_path="/images/test.jpg",
        price=29.99,
        status=ProductStatus.ACTIVE
    )
    db_session.add(product)
    await db_session.flush()

    # Act - 创建内容区块
    section = ContentSection(
        product_id=product.id,
        section_type="story",
        title="品牌故事",
        content="<p>这是一个精彩的故事</p>",
        display_order=1
    )
    db_session.add(section)
    await db_session.commit()
    await db_session.refresh(section)

    # Assert - 验证结果
    assert section.id is not None
    assert section.product_id == product.id
    assert section.section_type == "story"
    assert section.title == "品牌故事"
    assert section.content == "<p>这是一个精彩的故事</p>"
    assert section.display_order == 1
    assert section.created_at is not None
    assert isinstance(section.created_at, datetime)


@pytest.mark.asyncio
async def test_nutrition_fact_creation(db_session: AsyncSession):
    """
    测试营养成分表创建

    Given: 一个有效的商品和营养数据
    When: 创建营养数据
    Then: 营养数据成功创建，所有字段值正确
    """
    # Arrange - 创建分类和商品
    category = Category(name="测试分类", code="test", description="测试")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        title="测试商品",
        category_id=category.id,
        local_image_path="/images/test.jpg",
        price=29.99,
        status=ProductStatus.ACTIVE
    )
    db_session.add(product)
    await db_session.flush()

    # Act - 创建营养数据
    nutrition = NutritionFact(
        product_id=product.id,
        serving_size="1份(200g)",
        calories=150.0,
        protein=8.5,
        fat=5.2,
        carbohydrates=18.0,
        sodium=450.0,
        dietary_fiber=2.5,
        sugars=3.0
    )
    db_session.add(nutrition)
    await db_session.commit()
    await db_session.refresh(nutrition)

    # Assert - 验证结果
    assert nutrition.id is not None
    assert nutrition.product_id == product.id
    assert nutrition.serving_size == "1份(200g)"
    assert nutrition.calories == 150.0
    assert nutrition.protein == 8.5
    assert nutrition.fat == 5.2
    assert nutrition.carbohydrates == 18.0
    assert nutrition.sodium == 450.0
    assert nutrition.dietary_fiber == 2.5
    assert nutrition.sugars == 3.0
    assert nutrition.created_at is not None


@pytest.mark.asyncio
async def test_content_section_cascade_delete(db_session: AsyncSession):
    """
    测试内容区块级联删除

    Given: 一个商品有多个内容区块
    When: 删除该商品
    Then: 所有相关的内容区块应该被级联删除
    """
    # Arrange - 创建分类、商品和内容区块
    category = Category(name="测试分类", code="test", description="测试")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        title="测试商品",
        category_id=category.id,
        local_image_path="/images/test.jpg",
        price=29.99,
        status=ProductStatus.ACTIVE
    )
    db_session.add(product)
    await db_session.flush()

    section1 = ContentSection(
        product_id=product.id,
        section_type="story",
        title="品牌故事",
        content="<p>故事内容</p>",
        display_order=1
    )
    section2 = ContentSection(
        product_id=product.id,
        section_type="ingredients",
        title="食材信息",
        content="<p>食材内容</p>",
        display_order=2
    )
    db_session.add(section1)
    db_session.add(section2)
    await db_session.commit()

    section1_id = section1.id
    section2_id = section2.id

    # Act - 删除商品
    await db_session.delete(product)
    await db_session.commit()

    # Assert - 验证内容区块被级联删除
    from sqlalchemy import select
    result = await db_session.execute(
        select(ContentSection).where(ContentSection.id.in_([section1_id, section2_id]))
    )
    remaining_sections = result.scalars().all()

    assert len(remaining_sections) == 0


@pytest.mark.asyncio
async def test_nutrition_fact_cascade_delete(db_session: AsyncSession):
    """
    测试营养数据级联删除

    Given: 一个商品有营养数据
    When: 删除该商品
    Then: 营养数据应该被级联删除
    """
    # Arrange - 创建分类、商品和营养数据
    category = Category(name="测试分类", code="test", description="测试")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        title="测试商品",
        category_id=category.id,
        local_image_path="/images/test.jpg",
        price=29.99,
        status=ProductStatus.ACTIVE
    )
    db_session.add(product)
    await db_session.flush()

    nutrition = NutritionFact(
        product_id=product.id,
        serving_size="1份(200g)",
        calories=150.0
    )
    db_session.add(nutrition)
    await db_session.commit()

    nutrition_id = nutrition.id

    # Act - 删除商品
    await db_session.delete(product)
    await db_session.commit()

    # Assert - 验证营养数据被级联删除
    from sqlalchemy import select
    result = await db_session.execute(
        select(NutritionFact).where(NutritionFact.id == nutrition_id)
    )
    remaining_nutrition = result.scalar_one_or_none()

    assert remaining_nutrition is None


@pytest.mark.asyncio
async def test_product_with_multiple_content_sections(db_session: AsyncSession):
    """
    测试商品与多个内容区块的一对多关系

    Given: 一个商品
    When: 添加多个不同类型的内容区块
    Then: 商品应该能够正确获取所有内容区块
    """
    # Arrange - 创建分类和商品
    category = Category(name="测试分类", code="test", description="测试")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        title="测试商品",
        category_id=category.id,
        local_image_path="/images/test.jpg",
        price=29.99,
        status=ProductStatus.ACTIVE
    )
    db_session.add(product)
    await db_session.flush()

    # Act - 添加多个内容区块
    sections = [
        ContentSection(
            product_id=product.id,
            section_type="story",
            title="品牌故事",
            content="<p>故事内容</p>",
            display_order=1
        ),
        ContentSection(
            product_id=product.id,
            section_type="nutrition",
            title="营养信息",
            content="<p>营养内容</p>",
            display_order=2
        ),
        ContentSection(
            product_id=product.id,
            section_type="ingredients",
            title="食材信息",
            content="<p>食材内容</p>",
            display_order=3
        )
    ]
    for section in sections:
        db_session.add(section)
    await db_session.commit()

    # Assert - 验证关系
    from sqlalchemy import select
    result = await db_session.execute(
        select(ContentSection)
        .where(ContentSection.product_id == product.id)
        .order_by(ContentSection.display_order)
    )
    product_sections = result.scalars().all()

    assert len(product_sections) == 3
    assert product_sections[0].section_type == "story"
    assert product_sections[1].section_type == "nutrition"
    assert product_sections[2].section_type == "ingredients"


@pytest.mark.asyncio
async def test_product_with_nutrition_fact_one_to_one(db_session: AsyncSession):
    """
    测试商品与营养数据的一对一关系

    Given: 一个商品
    When: 添加营养数据
    Then: 商品应该只能有一个营养数据记录
    """
    # Arrange - 创建分类和商品
    category = Category(name="测试分类", code="test", description="测试")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        title="测试商品",
        category_id=category.id,
        local_image_path="/images/test.jpg",
        price=29.99,
        status=ProductStatus.ACTIVE
    )
    db_session.add(product)
    await db_session.flush()

    # Act - 添加营养数据
    nutrition = NutritionFact(
        product_id=product.id,
        serving_size="1份(200g)",
        calories=150.0,
        protein=8.5
    )
    db_session.add(nutrition)
    await db_session.commit()
    await db_session.refresh(product)

    # Assert - 验证一对一关系
    assert product.nutrition_fact is not None
    assert product.nutrition_fact.serving_size == "1份(200g)"
    assert product.nutrition_fact.calories == 150.0


@pytest.mark.asyncio
async def test_content_section_default_values(db_session: AsyncSession):
    """
    测试内容区块的默认值

    Given: 创建内容区块时只提供必需字段
    When: 保存到数据库
    Then: 可选字段应该使用默认值
    """
    # Arrange - 创建分类和商品
    category = Category(name="测试分类", code="test", description="测试")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        title="测试商品",
        category_id=category.id,
        local_image_path="/images/test.jpg",
        price=29.99,
        status=ProductStatus.ACTIVE
    )
    db_session.add(product)
    await db_session.flush()

    # Act - 创建内容区块（不提供可选字段）
    section = ContentSection(
        product_id=product.id,
        section_type="story",
        content="<p>内容</p>"
        # title 和 display_order 使用默认值
    )
    db_session.add(section)
    await db_session.commit()
    await db_session.refresh(section)

    # Assert - 验证默认值
    assert section.title is None  # title 允许为空
    assert section.display_order == 0  # 默认值为0
    assert section.created_at is not None
    assert section.updated_at is not None
