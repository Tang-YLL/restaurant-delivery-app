"""
商品详情服务

提供商品详情内容相关的业务逻辑:
- 内容分区CRUD操作
- HTML安全过滤（防XSS）
- 批量更新功能
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models import ContentSection, NutritionFact
from app.schemas import ContentSectionCreate, ContentSectionUpdate, NutritionFactsCreate
from typing import List, Optional
import bleach


class ProductDetailService:
    """商品详情服务"""

    def sanitize_html(self, html_content: str) -> str:
        """
        HTML内容安全过滤（防XSS）

        允许的标签: p, h1-h3, strong, em, ul, ol, li, img, br, div, span
        允许的属性: class, src, alt, width, height, href, title

        Args:
            html_content: 原始HTML内容

        Returns:
            过滤后的安全HTML内容
        """
        allowed_tags = [
            'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'strong', 'b', 'em', 'i', 'u',
            'ul', 'ol', 'li',
            'img', 'br', 'hr',
            'div', 'span',
            'a', 'table', 'tr', 'td', 'th',
            'blockquote', 'pre', 'code'
        ]

        allowed_attributes = {
            '*': ['class', 'id'],
            'img': ['src', 'alt', 'width', 'height', 'style'],
            'a': ['href', 'title', 'target'],
            'td': ['colspan', 'rowspan'],
            'th': ['colspan', 'rowspan']
        }

        cleaned = bleach.clean(
            html_content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )

        return cleaned

    async def get_full_details(
        self,
        product_id: int,
        db: AsyncSession
    ) -> dict:
        """
        获取商品完整详情

        Args:
            product_id: 商品ID
            db: 数据库会话

        Returns:
            包含内容分区和营养数据的字典
        """
        # 获取内容分区
        result = await db.execute(
            select(ContentSection)
            .where(ContentSection.product_id == product_id)
            .order_by(ContentSection.display_order)
        )
        sections = result.scalars().all()

        # 获取营养数据
        result = await db.execute(
            select(NutritionFact)
            .where(NutritionFact.product_id == product_id)
        )
        nutrition = result.scalar_one_or_none()

        return {
            "product_id": product_id,
            "content_sections": sections,
            "nutrition_facts": nutrition
        }

    async def save_content_section(
        self,
        product_id: int,
        section_data: ContentSectionCreate,
        db: AsyncSession
    ) -> ContentSection:
        """
        保存内容分区（创建）

        Args:
            product_id: 商品ID
            section_data: 内容分区数据
            db: 数据库会话

        Returns:
            创建的内容分区对象
        """
        # 过滤HTML内容
        sanitized_content = self.sanitize_html(section_data.content)

        section = ContentSection(
            product_id=product_id,
            section_type=section_data.section_type,
            title=section_data.title,
            content=sanitized_content,
            display_order=section_data.display_order
        )

        db.add(section)
        await db.commit()
        await db.refresh(section)

        return section

    async def update_content_section(
        self,
        section_id: int,
        section_data: ContentSectionUpdate,
        db: AsyncSession
    ) -> Optional[ContentSection]:
        """
        更新内容分区

        Args:
            section_id: 内容分区ID
            section_data: 更新数据
            db: 数据库会话

        Returns:
            更新后的内容分区对象，不存在则返回None
        """
        result = await db.execute(
            select(ContentSection).where(ContentSection.id == section_id)
        )
        section = result.scalar_one_or_none()

        if not section:
            return None

        # 更新字段
        if section_data.title is not None:
            section.title = section_data.title

        if section_data.content is not None:
            section.content = self.sanitize_html(section_data.content)

        if section_data.display_order is not None:
            section.display_order = section_data.display_order

        await db.commit()
        await db.refresh(section)

        return section

    async def delete_content_section(
        self,
        section_id: int,
        db: AsyncSession
    ) -> bool:
        """
        删除内容分区

        Args:
            section_id: 内容分区ID
            db: 数据库会话

        Returns:
            删除成功返回True，否则返回False
        """
        result = await db.execute(
            delete(ContentSection).where(ContentSection.id == section_id)
        )

        await db.commit()
        return result.rowcount > 0

    async def batch_update_sections(
        self,
        product_id: int,
        sections: List[ContentSectionCreate],
        db: AsyncSession
    ) -> List[ContentSection]:
        """
        批量更新内容分区

        删除该商品的所有旧分区，然后创建新的分区

        Args:
            product_id: 商品ID
            sections: 内容分区列表
            db: 数据库会话

        Returns:
            创建的内容分区列表
        """
        # 删除旧的
        await db.execute(
            delete(ContentSection).where(ContentSection.product_id == product_id)
        )

        # 创建新的
        created_sections = []
        for section_data in sections:
            section = ContentSection(
                product_id=product_id,
                section_type=section_data.section_type,
                title=section_data.title,
                content=self.sanitize_html(section_data.content),
                display_order=section_data.display_order
            )
            db.add(section)
            created_sections.append(section)

        await db.commit()

        # 刷新所有创建的对象
        for section in created_sections:
            await db.refresh(section)

        return created_sections

    # ==================== 营养数据管理 ====================

    async def get_nutrition_facts(
        self,
        product_id: int,
        db: AsyncSession
    ) -> Optional[NutritionFact]:
        """
        获取商品营养数据

        Args:
            product_id: 商品ID
            db: 数据库会话

        Returns:
            营养数据对象，不存在则返回None
        """
        result = await db.execute(
            select(NutritionFact)
            .where(NutritionFact.product_id == product_id)
        )
        return result.scalar_one_or_none()

    async def create_or_update_nutrition_facts(
        self,
        product_id: int,
        nutrition_data: NutritionFactsCreate,
        db: AsyncSession
    ) -> NutritionFact:
        """
        创建或更新营养数据（Upsert操作）

        Args:
            product_id: 商品ID
            nutrition_data: 营养数据
            db: 数据库会话

        Returns:
            创建或更新后的营养数据对象
        """
        # 先尝试获取现有数据
        result = await db.execute(
            select(NutritionFact)
            .where(NutritionFact.product_id == product_id)
        )
        nutrition = result.scalar_one_or_none()

        if nutrition:
            # 更新现有数据
            for field, value in nutrition_data.model_dump(exclude_unset=True).items():
                setattr(nutrition, field, value)
        else:
            # 创建新数据
            nutrition = NutritionFact(
                product_id=product_id,
                **nutrition_data.model_dump()
            )
            db.add(nutrition)

        await db.commit()
        await db.refresh(nutrition)

        return nutrition

    async def delete_nutrition_facts(
        self,
        product_id: int,
        db: AsyncSession
    ) -> bool:
        """
        删除营养数据

        Args:
            product_id: 商品ID
            db: 数据库会话

        Returns:
            删除成功返回True，否则返回False
        """
        result = await db.execute(
            delete(NutritionFact)
            .where(NutritionFact.product_id == product_id)
        )

        await db.commit()
        return result.rowcount > 0
