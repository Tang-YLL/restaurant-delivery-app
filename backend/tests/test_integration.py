"""
集成测试

测试完整的商品详情工作流：
1. 创建商品
2. 添加内容区块
3. 添加营养数据
4. 更新内容
5. 删除内容
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Product, Category, ContentSection, NutritionFact, ProductStatus
from app.services.product_detail_service import ProductDetailService
from app.schemas import ContentSectionCreate, NutritionFactsCreate


@pytest.mark.integration
async def test_full_product_detail_workflow(db_session: AsyncSession):
    """
    测试完整的商品详情工作流

    Given: 一个新创建的商品
    When:
      1. 添加内容区块
      2. 添加营养数据
      3. 获取完整详情
      4. 更新内容区块
      5. 删除内容区块
    Then: 所有操作应该成功完成
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
    await db_session.commit()

    service = ProductDetailService()

    # Step 1: 添加内容区块
    section_data = ContentSectionCreate(
        section_type="story",
        title="品牌故事",
        content="<p>这是一个精彩的品牌故事</p>",
        display_order=1
    )
    section = await service.save_content_section(product.id, section_data, db_session)

    assert section.id is not None
    assert section.title == "品牌故事"

    # Step 2: 添加营养数据
    nutrition_data = NutritionFactsCreate(
        serving_size="1份(200g)",
        calories=150.0,
        protein=8.5,
        fat=5.2
    )
    nutrition = await service.create_or_update_nutrition_facts(
        product.id, nutrition_data, db_session
    )

    assert nutrition.id is not None
    assert nutrition.calories == 150.0

    # Step 3: 获取完整详情
    details = await service.get_full_details(product.id, db_session)

    assert details["product_id"] == product.id
    assert len(details["content_sections"]) == 1
    assert details["nutrition_facts"] is not None
    assert details["nutrition_facts"].calories == 150.0

    # Step 4: 更新内容区块
    from app.schemas import ContentSectionUpdate
    update_data = ContentSectionUpdate(
        title="更新的品牌故事",
        content="<p>更新后的内容</p>"
    )
    updated_section = await service.update_content_section(
        section.id, update_data, db_session
    )

    assert updated_section is not None
    assert updated_section.title == "更新的品牌故事"
    assert "<p>更新后的内容</p>" in updated_section.content

    # Step 5: 删除内容区块
    deleted = await service.delete_content_section(section.id, db_session)

    assert deleted is True

    # 验证已删除
    result = await db_session.execute(
        select(ContentSection).where(ContentSection.id == section.id)
    )
    assert result.scalar_one_or_none() is None

    # 验证营养数据仍然存在
    details_after = await service.get_full_details(product.id, db_session)
    assert len(details_after["content_sections"]) == 0
    assert details_after["nutrition_facts"] is not None


@pytest.mark.integration
async def test_batch_update_workflow(db_session: AsyncSession):
    """
    测试批量更新内容区块工作流

    Given: 一个商品有多个内容区块
    When: 使用batch_update_sections批量替换
    Then: 旧的区块应该被删除，新的区块被创建
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

    # 添加初始内容区块
    initial_sections = [
        ContentSectionCreate(
            section_type="story",
            title="旧故事",
            content="<p>旧内容</p>",
            display_order=1
        )
    ]
    await service.batch_update_sections(product.id, initial_sections, db_session)

    # 验证初始内容
    details = await service.get_full_details(product.id, db_session)
    initial_count = len(details["content_sections"])
    assert initial_count == 1

    # Act - 批量更新为新内容
    new_sections = [
        ContentSectionCreate(
            section_type="story",
            title="新故事",
            content="<p>新故事内容</p>",
            display_order=1
        ),
        ContentSectionCreate(
            section_type="nutrition",
            title="营养信息",
            content="<p>营养内容</p>",
            display_order=2
        ),
        ContentSectionCreate(
            section_type="ingredients",
            title="食材信息",
            content="<p>食材内容</p>",
            display_order=3
        )
    ]
    await service.batch_update_sections(product.id, new_sections, db_session)

    # Assert - 验证更新结果
    updated_details = await service.get_full_details(product.id, db_session)
    assert len(updated_details["content_sections"]) == 3

    # 验证排序
    sections = updated_details["content_sections"]
    assert sections[0].section_type == "story"
    assert sections[1].section_type == "nutrition"
    assert sections[2].section_type == "ingredients"


@pytest.mark.integration
async def test_nutrition_upsert_workflow(db_session: AsyncSession):
    """
    测试营养数据的Upsert工作流

    Given: 一个商品
    When:
      1. 创建营养数据
      2. 再次调用create_or_update_nutrition_facts
    Then: 应该更新现有数据而不是创建新数据
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

    # Step 1: 创建营养数据
    initial_data = NutritionFactsCreate(
        serving_size="1份(100g)",
        calories=100.0,
        protein=5.0
    )
    nutrition1 = await service.create_or_update_nutrition_facts(
        product.id, initial_data, db_session
    )

    nutrition1_id = nutrition1.id

    # Step 2: 更新营养数据（Upsert）
    update_data = NutritionFactsCreate(
        serving_size="1份(200g)",
        calories=200.0,
        protein=10.0,
        fat=8.0
    )
    nutrition2 = await service.create_or_update_nutrition_facts(
        product.id, update_data, db_session
    )

    # Assert - 应该是同一个对象
    assert nutrition2.id == nutrition1_id
    assert nutrition2.serving_size == "1份(200g)"
    assert nutrition2.calories == 200.0
    assert nutrition2.protein == 10.0
    assert nutrition2.fat == 8.0

    # 验证只有一个记录
    result = await db_session.execute(
        select(NutritionFact).where(NutritionFact.product_id == product.id)
    )
    all_nutrition = result.scalars().all()
    assert len(all_nutrition) == 1
