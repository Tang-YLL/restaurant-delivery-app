"""
商品详情服务测试

测试ProductDetailService的业务逻辑：
- HTML安全过滤
- 内容区块CRUD操作
- 营养数据管理
- 批量更新功能
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Product, Category, ContentSection, NutritionFact, ProductStatus
from app.services.product_detail_service import ProductDetailService
from app.schemas import ContentSectionCreate, ContentSectionUpdate, NutritionFactsCreate


@pytest.mark.asyncio
async def test_sanitize_html_removes_xss(db_session: AsyncSession):
    """
    测试HTML安全过滤 - 移除XSS攻击代码

    Given: 包含恶意脚本的HTML内容
    When: 使用sanitize_html过滤
    Then: 恶意脚本应该被移除
    """
    # Arrange
    service = ProductDetailService()
    malicious_html = """
    <p>安全内容</p>
    <script>alert('XSS攻击')</script>
    <img src="x" onerror="alert('XSS')">
    <iframe src="http://evil.com"></iframe>
    """

    # Act
    cleaned = service.sanitize_html(malicious_html)

    # Assert
    assert "<script>" not in cleaned
    assert "onerror" not in cleaned
    assert "<iframe>" not in cleaned
    assert "<p>安全内容</p>" in cleaned


@pytest.mark.asyncio
async def test_sanitize_html_keeps_safe_tags(db_session: AsyncSession):
    """
    测试HTML安全过滤 - 保留安全标签

    Given: 包含安全HTML标签的内容
    When: 使用sanitize_html过滤
    Then: 安全标签应该被保留
    """
    # Arrange
    service = ProductDetailService()
    safe_html = """
    <h2>标题</h2>
    <p>段落内容</p>
    <strong>粗体</strong>
    <em>斜体</em>
    <ul>
        <li>列表项1</li>
        <li>列表项2</li>
    </ul>
    <img src="/images/safe.jpg" alt="安全图片">
    <a href="http://example.com" title="链接">链接文字</a>
    """

    # Act
    cleaned = service.sanitize_html(safe_html)

    # Assert
    assert "<h2>" in cleaned
    assert "<p>" in cleaned
    assert "<strong>" in cleaned
    assert "<em>" in cleaned
    assert "<ul>" in cleaned
    assert "<li>" in cleaned
    assert '<img src="/images/safe.jpg"' in cleaned
    assert '<a href="http://example.com"' in cleaned


@pytest.mark.asyncio
async def test_create_content_section(db_session: AsyncSession, sample_content_section_data):
    """
    测试创建内容区块

    Given: 商品和内容区块数据
    When: 调用save_content_section
    Then: 内容区块应该成功创建，HTML被过滤
    """
    # Arrange - 创建商品
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

    service = ProductDetailService()
    section_data = ContentSectionCreate(**sample_content_section_data)

    # Act
    section = await service.save_content_section(product.id, section_data, db_session)

    # Assert
    assert section.id is not None
    assert section.product_id == product.id
    assert section.section_type == "story"
    assert section.title == "品牌故事"
    assert section.content == "<p>这是一个精彩的品牌故事</p>"


@pytest.mark.asyncio
async def test_get_full_details(db_session: AsyncSession):
    """
    测试获取商品完整详情

    Given: 一个商品有内容区块和营养数据
    When: 调用get_full_details
    Then: 应该返回包含所有内容区块和营养数据的字典
    """
    # Arrange - 创建商品、内容区块和营养数据
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

    # 添加内容区块
    section1 = ContentSection(
        product_id=product.id,
        section_type="story",
        title="品牌故事",
        content="<p>故事</p>",
        display_order=1
    )
    section2 = ContentSection(
        product_id=product.id,
        section_type="nutrition",
        title="营养信息",
        content="<p>营养</p>",
        display_order=2
    )
    db_session.add(section1)
    db_session.add(section2)

    # 添加营养数据
    nutrition = NutritionFact(
        product_id=product.id,
        calories=150.0,
        protein=8.5
    )
    db_session.add(nutrition)
    await db_session.commit()

    service = ProductDetailService()

    # Act
    details = await service.get_full_details(product.id, db_session)

    # Assert
    assert details["product_id"] == product.id
    assert len(details["content_sections"]) == 2
    assert details["content_sections"][0].section_type == "story"
    assert details["content_sections"][1].section_type == "nutrition"
    assert details["nutrition_facts"] is not None
    assert details["nutrition_facts"].calories == 150.0


@pytest.mark.asyncio
async def test_update_content_section(db_session: AsyncSession):
    """
    测试更新内容区块

    Given: 一个存在的内容区块
    When: 调用update_content_section
    Then: 内容区块应该被更新，HTML被过滤
    """
    # Arrange - 创建商品和内容区块
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

    section = ContentSection(
        product_id=product.id,
        section_type="story",
        title="原标题",
        content="<p>原内容</p>",
        display_order=1
    )
    db_session.add(section)
    await db_session.commit()

    service = ProductDetailService()
    update_data = ContentSectionUpdate(
        title="新标题",
        content="<p>新内容<script>alert('XSS')</script></p>",
        display_order=2
    )

    # Act
    updated_section = await service.update_content_section(section.id, update_data, db_session)

    # Assert
    assert updated_section is not None
    assert updated_section.title == "新标题"
    assert "<script>" not in updated_section.content
    assert "<p>新内容</p>" in updated_section.content
    assert updated_section.display_order == 2


@pytest.mark.asyncio
async def test_update_nonexistent_content_section(db_session: AsyncSession):
    """
    测试更新不存在的内容区块

    Given: 一个不存在的section_id
    When: 调用update_content_section
    Then: 应该返回None
    """
    # Arrange
    service = ProductDetailService()
    update_data = ContentSectionUpdate(title="新标题")

    # Act
    result = await service.update_content_section(99999, update_data, db_session)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_delete_content_section(db_session: AsyncSession):
    """
    测试删除内容区块

    Given: 一个存在的内容区块
    When: 调用delete_content_section
    Then: 内容区块应该被删除，返回True
    """
    # Arrange - 创建商品和内容区块
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

    section = ContentSection(
        product_id=product.id,
        section_type="story",
        content="<p>内容</p>"
    )
    db_session.add(section)
    await db_session.commit()

    service = ProductDetailService()

    # Act
    result = await service.delete_content_section(section.id, db_session)

    # Assert
    assert result is True

    # 验证已删除
    deleted_section = await db_session.execute(
        select(ContentSection).where(ContentSection.id == section.id)
    )
    assert deleted_section.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_batch_update_sections(db_session: AsyncSession):
    """
    测试批量更新内容区块

    Given: 一个商品有旧的内容区块
    When: 调用batch_update_sections
    Then: 旧的区块应该被删除，新的区块被创建
    """
    # Arrange - 创建商品和旧内容区块
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

    old_section = ContentSection(
        product_id=product.id,
        section_type="old",
        content="<p>旧内容</p>"
    )
    db_session.add(old_section)
    await db_session.commit()

    service = ProductDetailService()

    new_sections = [
        ContentSectionCreate(
            section_type="story",
            title="故事",
            content="<p>新故事</p>",
            display_order=1
        ),
        ContentSectionCreate(
            section_type="nutrition",
            title="营养",
            content="<p>新营养</p>",
            display_order=2
        )
    ]

    # Act
    result = await service.batch_update_sections(product.id, new_sections, db_session)

    # Assert
    assert len(result) == 2
    assert result[0].section_type == "story"
    assert result[1].section_type == "nutrition"

    # 验证旧的区块已被删除
    old_result = await db_session.execute(
        select(ContentSection).where(ContentSection.id == old_section.id)
    )
    assert old_result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_create_nutrition_facts(db_session: AsyncSession, sample_nutrition_data):
    """
    测试创建营养数据

    Given: 商品和营养数据
    When: 调用create_or_update_nutrition_facts
    Then: 营养数据应该被创建
    """
    # Arrange - 创建商品
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

    service = ProductDetailService()
    nutrition_data = NutritionFactsCreate(**sample_nutrition_data)

    # Act
    nutrition = await service.create_or_update_nutrition_facts(
        product.id, nutrition_data, db_session
    )

    # Assert
    assert nutrition.id is not None
    assert nutrition.product_id == product.id
    assert nutrition.calories == 150.0
    assert nutrition.protein == 8.5


@pytest.mark.asyncio
async def test_update_nutrition_facts(db_session: AsyncSession):
    """
    测试更新营养数据

    Given: 一个商品已有营养数据
    When: 再次调用create_or_update_nutrition_facts
    Then: 营养数据应该被更新而不是创建新的
    """
    # Arrange - 创建商品和营养数据
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

    service = ProductDetailService()

    # 创建初始营养数据
    initial_data = NutritionFactsCreate(calories=100.0, protein=5.0)
    await service.create_or_update_nutrition_facts(product.id, initial_data, db_session)

    # Act - 更新营养数据
    update_data = NutritionFactsCreate(calories=200.0, protein=10.0)
    updated = await service.create_or_update_nutrition_facts(
        product.id, update_data, db_session
    )

    # Assert - 应该是更新而不是创建
    assert updated.calories == 200.0
    assert updated.protein == 10.0

    # 验证只有一个营养数据记录
    result = await db_session.execute(
        select(NutritionFact).where(NutritionFact.product_id == product.id)
    )
    all_nutrition = result.scalars().all()
    assert len(all_nutrition) == 1


@pytest.mark.asyncio
async def test_delete_nutrition_facts(db_session: AsyncSession):
    """
    测试删除营养数据

    Given: 一个商品有营养数据
    When: 调用delete_nutrition_facts
    Then: 营养数据应该被删除
    """
    # Arrange - 创建商品和营养数据
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
        calories=150.0
    )
    db_session.add(nutrition)
    await db_session.commit()

    service = ProductDetailService()

    # Act
    result = await service.delete_nutrition_facts(product.id, db_session)

    # Assert
    assert result is True

    # 验证已删除
    deleted_nutrition = await db_session.execute(
        select(NutritionFact).where(NutritionFact.product_id == product.id)
    )
    assert deleted_nutrition.scalar_one_or_none() is None
