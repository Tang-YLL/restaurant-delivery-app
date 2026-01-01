"""
从Material目录批量导入100条商品数据
"""
import asyncio
import sys
import os
import random
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Product
from sqlalchemy import select, func

# Material目录
MATERIAL_DIR = "/Volumes/545S/general final/Material/material"

# 分类配置：关键词和价格区间
CATEGORY_CONFIG = {
    3: {  # 主食类
        "keywords": ["炒饭", "面条", "粉", "饺子", "包子", "馒头", "饼", "面", "米饭", "粥", "炒面", "烩面", "拉面", "拌面", "米线"],
        "price_range": (8, 68),
        "stock_range": (30, 200)
    },
    4: {  # 汤类
        "keywords": ["汤", "羹", "煲"],
        "price_range": (6, 48),
        "stock_range": (20, 100)
    },
    5: {  # 饮品类
        "keywords": ["汁", "茶", "饮", "奶", "咖啡", "豆浆"],
        "price_range": (4, 28),
        "stock_range": (50, 200)
    },
    6: {  # 甜品类
        "keywords": ["糕", "糖", "甜", "布丁", "果冻", "酥", "派", "挞"],
        "price_range": (6, 38),
        "stock_range": (20, 80)
    }
}


def guess_category(filename):
    """根据文件名猜测商品分类"""
    for category_id, config in CATEGORY_CONFIG.items():
        for keyword in config["keywords"]:
            if keyword in filename:
                return category_id
    # 默认分配到主食类
    return 3


def get_all_product_files(limit=100):
    """获取前N个商品图片文件"""
    files = []
    for filename in sorted(os.listdir(MATERIAL_DIR)):
        if filename.endswith('.png'):
            files.append(filename)
            if len(files) >= limit:
                break
    return files


def parse_product_name(filename):
    """从文件名解析商品名称"""
    # 移除.png扩展名
    name = filename.replace('.png', '')
    # 移除常见的修饰词
    name = name.replace('（粤菜版）', '')
    name = name.replace('（家常菜）', '')
    name = name.replace('宝宝辅食 ', '')
    name = name.replace('超简单的', '')
    name = name.replace('（2人餐）', '')
    return name.strip()


async def batch_insert_100_products():
    """批量插入100条商品数据"""
    print("=" * 120)
    print("从Material目录批量导入100条商品数据")
    print("=" * 120)

    # 获取前100个商品文件
    print("\n正在读取Material目录...")
    product_files = get_all_product_files(100)
    print(f"✓ 找到 {len(product_files)} 个商品图片")

    # 解析商品数据
    print("\n正在解析商品数据...")
    products_data = []

    for idx, filename in enumerate(product_files, 1):
        # 解析商品名称
        product_name = parse_product_name(filename)

        # 智能分配分类
        category_id = guess_category(filename)

        # 根据分类生成价格和库存
        config = CATEGORY_CONFIG[category_id]
        price = round(random.uniform(*config["price_range"]), 2)
        stock = random.randint(*config["stock_range"])

        # 生成描述
        descriptions = [
            f"{product_name}，精选食材，精心制作，口感丰富，营养美味。",
            f"传统工艺制作{product_name}，风味独特，老少皆宜。",
            f"新鲜食材制作的{product_name}，色香味俱全，值得一试。",
            f"招牌菜{product_name}，用料考究，制作精良，深受欢迎。",
            f"{product_name}，营养丰富，口感鲜美，是您的不二选择。",
        ]
        description = random.choice(descriptions)

        products_data.append({
            "title": product_name,
            "description": description,
            "price": price,
            "stock": stock,
            "category_id": category_id,
            "is_active": True,
            "sort_order": idx
        })

    print(f"✓ 解析完成 {len(products_data)} 个商品")

    # 统计各分类数量
    category_count = {}
    for p in products_data:
        cat = p['category_id']
        category_count[cat] = category_count.get(cat, 0) + 1

    print("\n商品分类统计:")
    for cat_id, count in sorted(category_count.items()):
        cat_name = {3: "主食类", 4: "汤类", 5: "饮品类", 6: "甜品类"}.get(cat_id, "其他")
        print(f"  {cat_name}: {count} 个商品")

    # 获取数据库会话
    async for db in get_db():
        try:
            # 检查现有商品数量
            result = await db.execute(select(func.count(Product.id)))
            count = result.scalar() or 0
            print(f"\n当前数据库商品数量: {count}")

            # 复制图片并创建商品
            print("\n开始导入商品...")
            print("-" * 120)

            products_created = 0
            target_dir = "/Volumes/545S/general final/backend/public/images/products"
            os.makedirs(target_dir, exist_ok=True)

            for idx, product_data in enumerate(products_data, 1):
                try:
                    # 找到对应的图片文件
                    filename = None
                    for f in product_files:
                        product_name = product_data['title']
                        if product_name in f or f.replace('.png', '') == product_name:
                            filename = f
                            break

                    if not filename:
                        # 使用文件名匹配
                        for f in product_files:
                            if any(keyword in f for keyword in CATEGORY_CONFIG[product_data['category_id']]["keywords"]):
                                filename = f
                                product_files.remove(f)
                                break

                    if not filename:
                        print(f"  ⚠️  跳过: {product_data['title']} (未找到匹配图片)")
                        continue

                    # 复制图片
                    source_path = os.path.join(MATERIAL_DIR, filename)
                    target_path = os.path.join(target_dir, filename)

                    if not os.path.exists(target_path):
                        import shutil
                        shutil.copy2(source_path, target_path)

                    # 添加图片路径
                    image_url = f"/images/products/{filename}"
                    product_with_image = {
                        **product_data,
                        "local_image_path": image_url,
                        "image_url": image_url
                    }

                    # 创建商品
                    product = Product(**product_with_image)
                    db.add(product)
                    products_created += 1

                    # 显示进度
                    cat_name = {3: "主食", 4: "汤", 5: "饮品", 6: "甜品"}[product_data['category_id']]
                    print(f"  [{products_created:3d}/{100}] {cat_name:4s} | {product_data['title']:30s} | ¥{product_data['price']:6.2f} | 库存:{product_data['stock']:3d} | {filename[:40]}")

                    if products_created >= 100:
                        break

                except Exception as e:
                    print(f"  ❌ 添加商品失败 {product_data['title']}: {e}")

            # 提交所有更改
            await db.commit()
            print("-" * 120)
            print(f"\n✅ 成功导入 {products_created} 个商品")

            # 验证插入结果
            result = await db.execute(select(func.count(Product.id)))
            total = result.scalar() or 0
            print(f"数据库中商品总数: {total}")

            # 按分类统计
            result = await db.execute(
                select(
                    Product.category_id,
                    func.count(Product.id).label('count'),
                    func.avg(Product.price).label('avg_price')
                )
                .group_by(Product.category_id)
                .order_by(Product.category_id)
            )

            print("\n分类统计:")
            print("-" * 80)
            for row in result:
                cat_id, count, avg_price = row
                cat_name = {3: "主食类", 4: "汤类", 5: "饮品类", 6: "甜品类"}.get(cat_id, f"分类{cat_id}")
                print(f"  {cat_name}: {count:3d} 个商品 | 平均价格: ¥{avg_price:.2f}")
            print("-" * 80)

        except Exception as e:
            print(f"❌ 批量插入失败: {e}")
            await db.rollback()
            raise
        finally:
            break


if __name__ == "__main__":
    import random
    random.seed(42)  # 设置随机种子，保证结果可重现

    asyncio.run(batch_insert_100_products())
    print("\n" + "=" * 120)
    print("导入完成！")
    print("=" * 120)
