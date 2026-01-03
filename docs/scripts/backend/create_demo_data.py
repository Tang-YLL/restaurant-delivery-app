#!/usr/bin/env python3
"""
创建演示测试数据
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models import Category, Product
from app.core.security import get_password_hash
from sqlalchemy import select
import json


MATERIAL_PATH = Path("/Volumes/545S/general final/Material/material")


async def create_demo_data():
    """创建演示数据"""
    async with AsyncSessionLocal() as session:
        try:
            # 1. 创建分类
            print("📁 创建分类...")
            categories_data = [
                {"name": "热菜", "code": "hot_dish", "description": "各类炒菜、烧菜、炖菜等", "sort_order": 1},
                {"name": "凉菜", "code": "cold_dish", "description": "凉拌菜、沙拉等", "sort_order": 2},
                {"name": "主食", "code": "staple_food", "description": "米饭、面食、包子等", "sort_order": 3},
                {"name": "汤类", "code": "soup", "description": "各类汤品", "sort_order": 4},
                {"name": "饮品", "code": "drink", "description": "各类饮品", "sort_order": 5},
            ]

            category_map = {}
            for cat_data in categories_data:
                # 检查分类是否已存在
                result = await session.execute(
                    select(Category).where(Category.name == cat_data["name"])
                )
                existing = result.scalar_one_or_none()

                if existing:
                    category_map[cat_data["name"]] = existing
                    print(f"  ✓ 分类 '{cat_data['name']}' 已存在")
                else:
                    category = Category(**cat_data)
                    session.add(category)
                    await session.flush()
                    category_map[cat_data["name"]] = category
                    print(f"  ✓ 创建分类: {cat_data['name']}")

            # 2. 从Material导入商品数据
            print("\n🍜 导入商品数据...")

            # 读取Material目录中的recipe.json文件
            recipe_file = MATERIAL_PATH / "recipe.json"

            if not recipe_file.exists():
                print(f"  ⚠️  未找到 recipe.json 文件，使用内置数据")
                products_data = [
                    {
                        "title": "青椒炒肉",
                        "description": "经典家常菜，青椒配肉丝，鲜香下饭",
                        "price": 28.00,
                        "category": "热菜",
                        "stock": 50,
                        "local_image_path": "/images/青椒炒肉.png"
                    },
                    {
                        "title": "红烧肉",
                        "description": "肥而不腻，入口即化，经典名菜",
                        "price": 58.00,
                        "category": "热菜",
                        "stock": 30,
                        "local_image_path": "/images/红烧肉.png"
                    },
                    {
                        "title": "鱼香肉丝",
                        "description": "酸甜可口，川菜代表",
                        "price": 32.00,
                        "category": "热菜",
                        "stock": 40,
                        "local_image_path": "/images/鱼香肉丝.png"
                    },
                    {
                        "title": "拍黄瓜",
                        "description": "清爽开胃，简单美味",
                        "price": 12.00,
                        "category": "凉菜",
                        "stock": 60,
                        "local_image_path": "/images/拍黄瓜.png"
                    },
                    {
                        "title": "白米饭",
                        "description": "优质大米，香甜可口",
                        "price": 2.00,
                        "category": "主食",
                        "stock": 200,
                        "local_image_path": "/images/白米饭.png"
                    },
                    {
                        "title": "蛋炒饭",
                        "description": "粒粒分明，香气扑鼻",
                        "price": 15.00,
                        "category": "主食",
                        "stock": 80,
                        "local_image_path": "/images/蛋炒饭.png"
                    },
                    {
                        "title": "紫菜蛋花汤",
                        "description": "清淡营养，家常好汤",
                        "price": 8.00,
                        "category": "汤类",
                        "stock": 50,
                        "local_image_path": "/images/紫菜蛋花汤.png"
                    },
                    {
                        "title": "酸梅汤",
                        "description": "酸甜解腻，清热降火",
                        "price": 6.00,
                        "category": "饮品",
                        "stock": 100,
                        "local_image_path": "/images/酸梅汤.png"
                    },
                ]
            else:
                with open(recipe_file, 'r', encoding='utf-8') as f:
                    all_recipes = json.load(f)

                # 只取前20个作为演示数据
                products_data = []
                for recipe in all_recipes[:20]:
                    # 简单分类逻辑
                    title = recipe.get("title", "")
                    category_name = "热菜"  # 默认

                    if any(keyword in title for keyword in ["汤", "羹"]):
                        category_name = "汤类"
                    elif any(keyword in title for keyword in ["凉拌", "沙拉", "拍"]):
                        category_name = "凉菜"
                    elif any(keyword in title for keyword in ["饭", "面", "包子", "馒头"]):
                        category_name = "主食"
                    elif any(keyword in title for keyword in ["汁", "水", "茶", "奶"]):
                        category_name = "饮品"

                    # 根据浏览次数定价（简单算法）
                    views = recipe.get("views", 1000)
                    price = round(8 + (views / 1000) * 5, 1)

                    products_data.append({
                        "title": title,
                        "description": recipe.get("ingredients", "")[:100],
                        "price": price,
                        "category": category_name,
                        "stock": 50,
                        "views": views,
                        "local_image_path": recipe.get("image", "")
                    })

            # 插入商品数据
            created_count = 0
            for prod_data in products_data:
                category_name = prod_data.pop("category")
                category = category_map[category_name]

                # 检查商品是否已存在
                result = await session.execute(
                    select(Product).where(Product.title == prod_data["title"])
                )
                existing = result.scalar_one_or_none()

                if not existing:
                    product = Product(
                        **prod_data,
                        category_id=category.id,
                        status="ACTIVE",
                        is_active=True
                    )
                    session.add(product)
                    created_count += 1
                    if created_count <= 5:  # 只显示前5个
                        print(f"  ✓ 创建商品: {prod_data['title']} - ¥{prod_data['price']}")

            await session.commit()

            # 3. 统计信息
            print("\n📊 数据统计:")
            result = await session.execute(select(Category))
            cat_count = len(result.scalars().all())
            print(f"  分类总数: {cat_count}")

            result = await session.execute(select(Product))
            prod_count = len(result.scalars().all())
            print(f"  商品总数: {prod_count}")

            print("\n✅ 演示数据创建完成！")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ 创建演示数据失败: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(create_demo_data())
