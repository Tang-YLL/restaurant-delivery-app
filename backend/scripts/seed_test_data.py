"""
测试种子数据脚本
从Material/material目录导入食物数据到数据库
"""
import sys
import os
import json
import asyncio
from pathlib import Path
from sqlalchemy import select

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import async_session_maker
from app.models import Category, Product
from sqlalchemy.ext.asyncio import AsyncSession


# 定义分类映射规则
def categorize_food(title: str) -> str:
    """根据菜名确定分类"""
    category_keywords = {
        "热菜": ["炒", "烧", "炖", "焖", "煮", "烩", "熘", "爆", "煸", "煎", "炸", "蒸", "烤"],
        "凉菜": ["拌", "凉", "沙拉", "泡菜"],
        "主食": ["饭", "面", "馒头", "包子", "饺子", "饼", "粥", "粉", "面条", "面包", "糕"],
        "汤类": ["汤", "羹"],
        "甜品": ["糖", "甜", "奶昔", "布丁", "果冻"],
        "饮品": ["茶", "咖啡", "汁", "奶", "水"],
        "小吃": ["串", "卷", "薯条", "鸡翅", "鸡块", "丸子"],
    }

    for category, keywords in category_keywords.items():
        if any(keyword in title for keyword in keywords):
            return category

    return "热菜"  # 默认分类


async def import_categories(db: AsyncSession) -> dict:
    """导入分类数据"""
    categories_data = [
        {"name": "热菜", "description": "各类炒菜、烧菜、炖菜等", "sort_order": 1},
        {"name": "凉菜", "description": "凉拌菜、沙拉等", "sort_order": 2},
        {"name": "主食", "description": "米饭、面食、包子等", "sort_order": 3},
        {"name": "汤类", "description": "各类汤品", "sort_order": 4},
        {"name": "甜品", "description": "甜点、甜品", "sort_order": 5},
        {"name": "饮品", "description": "茶饮、果汁等", "sort_order": 6},
        {"name": "小吃", "description": "各类小吃、零食", "sort_order": 7},
    ]

    category_map = {}

    for cat_data in categories_data:
        # 检查分类是否已存在
        result = await db.execute(
            select(Category).where(Category.name == cat_data["name"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            category_map[existing.name] = existing
            print(f"✓ 分类已存在: {existing.name}")
        else:
            category = Category(**cat_data)
            db.add(category)
            await db.flush()
            category_map[category.name] = category
            print(f"✓ 创建分类: {category.name}")

    await db.commit()
    return category_map


async def import_products_from_material(
    db: AsyncSession,
    category_map: dict,
    material_dir: str,
    limit: int = 100
):
    """从Material目录导入商品数据"""
    material_path = Path(material_dir)

    if not material_path.exists():
        print(f"✗ Material目录不存在: {material_dir}")
        return

    # 获取所有JSON文件
    json_files = list(material_path.glob("*.json"))

    if not json_files:
        print(f"✗ 未找到JSON文件: {material_dir}")
        return

    print(f"\n找到 {len(json_files)} 个JSON文件")
    print(f"导入限制: {limit} 个商品\n")

    imported_count = 0
    skipped_count = 0

    for json_file in json_files[:limit]:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = data.get("title", "").strip()
            if not title:
                skipped_count += 1
                continue

            # 检查商品是否已存在
            result = await db.execute(
                select(Product).where(Product.name == title)
            )
            existing = result.scalar_one_or_none()

            if existing:
                skipped_count += 1
                continue

            # 确定分类
            category_name = categorize_food(title)
            category = category_map.get(category_name, category_map["热菜"])

            # 提取价格（基于浏览量的简单定价）
            views_str = data.get("views_and_favorites", "")
            views = int(''.join(filter(str.isdigit, views_str))) if views_str else 0

            # 简单定价规则
            if views > 50000:
                price = 68.0
            elif views > 30000:
                price = 48.0
            elif views > 10000:
                price = 38.0
            else:
                price = 28.0

            # 查找对应的图片文件
            image_name = json_file.stem + ".png"
            local_image = data.get("local_image_path", "")

            # 创建商品数据
            product = Product(
                name=title,
                description=data.get("ingredients", "")[:500],  # 限制长度
                price=price,
                category_id=category.id,
                image_url=local_image if local_image else f"/images/{image_name}",
                stock=100,  # 默认库存
                is_available=True,
                is_hot=views > 30000,  # 高浏览量标记为热门
            )

            db.add(product)
            await db.flush()

            imported_count += 1
            if imported_count % 10 == 0:
                print(f"  已导入 {imported_count} 个商品...")

        except Exception as e:
            print(f"✗ 导入失败 {json_file.name}: {e}")
            skipped_count += 1
            continue

    await db.commit()

    print(f"\n导入完成:")
    print(f"  ✓ 成功导入: {imported_count} 个商品")
    print(f"  - 跳过/已存在: {skipped_count} 个商品")


async def main():
    """主函数"""
    print("=" * 80)
    print("测试种子数据导入脚本")
    print("=" * 80)

    # Material目录路径
    material_dir = "/Volumes/545S/general final/Material/material"

    async with async_session_maker() as db:
        # 1. 导入分类
        print("\n步骤 1: 导入分类数据")
        print("-" * 80)
        category_map = await import_categories(db)

        # 2. 导入商品
        print("\n步骤 2: 导入商品数据")
        print("-" * 80)
        await import_products_from_material(
            db=db,
            category_map=category_map,
            material_dir=material_dir,
            limit=50  # 导入50个商品用于测试
        )

    print("\n" + "=" * 80)
    print("✓ 种子数据导入完成!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
