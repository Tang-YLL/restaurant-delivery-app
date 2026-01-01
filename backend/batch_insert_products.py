"""
批量插入商品数据
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Product
from sqlalchemy import select, func


# 商品数据列表
PRODUCTS_DATA = [
    # 主食类 (category_id=3)
    {
        "title": "青椒炒肉",
        "description": "新鲜青椒搭配嫩滑猪肉，口感鲜美，营养丰富。选用优质五花肉，经过特殊工艺处理，肉质鲜嫩不腻。",
        "price": 28.00,
        "stock": 50,
        "category_id": 3,
        "local_image_path": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "image_url": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "is_active": True,
        "sort_order": 1
    },
    {
        "title": "红烧肉",
        "description": "精选五花肉，传统工艺红烧，肥而不腻，入口即化。色泽红亮，香气扑鼻，是下饭神器。",
        "price": 58.00,
        "stock": 30,
        "category_id": 3,
        "local_image_path": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "image_url": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "is_active": True,
        "sort_order": 2
    },
    {
        "title": "鱼香肉丝",
        "description": "经典川菜，酸甜微辣，口感丰富。选用猪里脊肉，配以木耳、胡萝卜丝，色香味俱全。",
        "price": 32.00,
        "stock": 40,
        "category_id": 3,
        "local_image_path": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "image_url": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "is_active": True,
        "sort_order": 3
    },
    {
        "title": "宫保鸡丁",
        "description": "正宗川菜，鸡肉嫩滑，花生香脆，麻辣适中。选用鸡胸肉，配以干辣椒、花生米，口感层次丰富。",
        "price": 35.00,
        "stock": 45,
        "category_id": 3,
        "local_image_path": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "image_url": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "is_active": True,
        "sort_order": 4
    },
    {
        "title": "蛋炒饭",
        "description": "经典家常炒饭，米饭粒粒分明，鸡蛋香味浓郁。选用优质大米，配以新鲜鸡蛋，简单而美味。",
        "price": 15.00,
        "stock": 100,
        "category_id": 3,
        "local_image_path": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "image_url": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "is_active": True,
        "sort_order": 5
    },
    {
        "title": "白米饭",
        "description": "优质大米蒸制，颗粒饱满，口感软糯。选用东北大米，清香扑鼻，是各种菜肴的最佳搭配。",
        "price": 2.00,
        "stock": 200,
        "category_id": 3,
        "local_image_path": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "image_url": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "is_active": True,
        "sort_order": 6
    },
    {
        "title": "扬州炒饭",
        "description": "经典江苏菜，配料丰富，色彩鲜艳。米饭、鸡蛋、虾仁、火腿、青豆等多种食材，营养均衡。",
        "price": 22.00,
        "stock": 60,
        "category_id": 3,
        "local_image_path": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "image_url": "/images/products/4e94c936-4c85-408b-a336-0fc20d59144b.png",
        "is_active": True,
        "sort_order": 7
    },

    # 汤类 (category_id=4)
    {
        "title": "紫菜蛋花汤",
        "description": "清淡爽口，营养丰富。新鲜紫菜配以嫩滑蛋花，汤色清澈，味道鲜美。",
        "price": 8.00,
        "stock": 80,
        "category_id": 4,
        "local_image_path": "/images/products/e8087f54-85bc-4b1a-ac0b-b9f22719cf95.jpg",
        "image_url": "/images/products/e8087f54-85bc-4b1a-ac0b-b9f22719cf95.jpg",
        "is_active": True,
        "sort_order": 1
    },
    {
        "title": "酸梅汤",
        "description": "传统饮品，酸甜解腻。选用优质乌梅、山楂等原料，经过长时间熬制，口感醇厚。",
        "price": 6.00,
        "stock": 100,
        "category_id": 4,
        "local_image_path": "/images/products/e8087f54-85bc-4b1a-ac0b-b9f22719cf95.jpg",
        "image_url": "/images/products/e8087f54-85bc-4b1a-ac0b-b9f22719cf95.jpg",
        "is_active": True,
        "sort_order": 2
    },
    {
        "title": "番茄鸡蛋汤",
        "description": "家常汤品，酸甜开胃。新鲜番茄配以嫩滑鸡蛋，汤汁浓郁，营养丰富。",
        "price": 10.00,
        "stock": 70,
        "category_id": 4,
        "local_image_path": "/images/products/e8087f54-85bc-4b1a-ac0b-b9f22719cf95.jpg",
        "image_url": "/images/products/e8087f54-85bc-4b1a-ac0b-b9f22719cf95.jpg",
        "is_active": True,
        "sort_order": 3
    },
    {
        "title": "冬瓜排骨汤",
        "description": "营养丰富，清热解暑。新鲜冬瓜配以精选排骨，经过长时间炖煮，汤清味美。",
        "price": 38.00,
        "stock": 40,
        "category_id": 4,
        "local_image_path": "/images/products/e8087f54-85bc-4b1a-ac0b-b9f22719cf95.jpg",
        "image_url": "/images/products/e8087f54-85bc-4b1a-ac0b-b9f22719cf95.jpg",
        "is_active": True,
        "sort_order": 4
    },

    # 饮品类 (category_id=5)
    {
        "title": "鲜榨橙汁",
        "description": "100%鲜榨橙汁，维生素C含量丰富。选用新鲜橙子，现场榨制，口感纯正。",
        "price": 12.00,
        "stock": 60,
        "category_id": 5,
        "local_image_path": "/images/products/64a389d2-26a3-4fd4-a9b1-38c4a2fdd122.png",
        "image_url": "/images/products/64a389d2-26a3-4fd4-a9b1-38c4a2fdd122.png",
        "is_active": True,
        "sort_order": 1
    },
    {
        "title": "冰镇酸梅汤",
        "description": "夏日解暑佳品，冰镇后口感更佳。传统配方熬制，酸甜适中，清爽可口。",
        "price": 8.00,
        "stock": 90,
        "category_id": 5,
        "local_image_path": "/images/products/64a389d2-26a3-4fd4-a9b1-38c4a2fdd122.png",
        "image_url": "/images/products/64a389d2-26a3-4fd4-a9b1-38c4a2fdd122.png",
        "is_active": True,
        "sort_order": 2
    },
    {
        "title": "柠檬蜂蜜茶",
        "description": "清香怡人，润喉养颜。新鲜柠檬配以优质蜂蜜，酸甜可口，老少皆宜。",
        "price": 15.00,
        "stock": 70,
        "category_id": 5,
        "local_image_path": "/images/products/64a389d2-26a3-4fd4-a9b1-38c4a2fdd122.png",
        "image_url": "/images/products/64a389d2-26a3-4fd4-a9b1-38c4a2fdd122.png",
        "is_active": True,
        "sort_order": 3
    },
    {
        "title": "绿豆汤",
        "description": "清热解暑，消暑佳品。精选绿豆，经过长时间熬煮，豆烂汤清，甘甜爽口。",
        "price": 6.00,
        "stock": 100,
        "category_id": 5,
        "local_image_path": "/images/products/64a389d2-26a3-4fd4-a9b1-38c4a2fdd122.png",
        "image_url": "/images/products/64a389d2-26a3-4fd4-a9b1-38c4a2fdd122.png",
        "is_active": True,
        "sort_order": 4
    },

    # 甜品类 (category_id=6)
    {
        "title": "拍黄瓜",
        "description": "清爽开胃，制作简单。新鲜黄瓜配以特制酱料，口感脆嫩，是夏日必备凉菜。",
        "price": 12.00,
        "stock": 50,
        "category_id": 6,
        "local_image_path": "/images/products/c6b14e69-d28d-43fc-83df-b77b52579674.png",
        "image_url": "/images/products/c6b14e69-d28d-43fc-83df-b77b52579674.png",
        "is_active": True,
        "sort_order": 1
    },
    {
        "title": "糖醋排骨",
        "description": "酸甜可口，色泽红亮。精选小排，配以特制糖醋汁，外酥里嫩，老少皆宜。",
        "price": 48.00,
        "stock": 35,
        "category_id": 6,
        "local_image_path": "/images/products/c6b14e69-d28d-43fc-83df-b77b52579674.png",
        "image_url": "/images/products/c6b14e69-d28d-43fc-83df-b77b52579674.png",
        "is_active": True,
        "sort_order": 2
    },
    {
        "title": "红豆沙",
        "description": "传统甜品，香甜软糯。精选红豆，经过长时间熬煮，豆沙细腻，甜而不腻。",
        "price": 10.00,
        "stock": 60,
        "category_id": 6,
        "local_image_path": "/images/products/c6b14e69-d28d-43fc-83df-b77b52579674.png",
        "image_url": "/images/products/c6b14e69-d28d-43fc-83df-b77b52579674.png",
        "is_active": True,
        "sort_order": 3
    },
    {
        "title": "水果沙拉",
        "description": "新鲜水果，营养健康。当季新鲜水果，配以特制沙拉酱，清爽可口。",
        "price": 18.00,
        "stock": 40,
        "category_id": 6,
        "local_image_path": "/images/products/c6b14e69-d28d-43fc-83df-b77b52579674.png",
        "image_url": "/images/products/c6b14e69-d28d-43fc-83df-b77b52579674.png",
        "is_active": True,
        "sort_order": 4
    },
    {
        "title": "银耳莲子汤",
        "description": "滋补养颜，清甜滋润。优质银耳配以精选莲子，经过长时间炖煮，胶质丰富。",
        "price": 16.00,
        "stock": 50,
        "category_id": 6,
        "local_image_path": "/images/products/c6b14e69-d28d-43fc-83df-b77b52579674.png",
        "image_url": "/images/products/c6b14e69-d28d-43fc-83df-b77b52579674.png",
        "is_active": True,
        "sort_order": 5
    },
]


async def batch_insert_products():
    """批量插入商品数据"""
    print("开始批量插入商品数据...")

    # 获取数据库会话
    async for db in get_db():
        try:
            # 检查现有商品数量
            result = await db.execute(select(func.count(Product.id)))
            count = result.scalar() or 0
            print(f"当前商品数量: {count}")

            # 批量创建商品
            products_created = 0
            for product_data in PRODUCTS_DATA:
                try:
                    product = Product(**product_data)
                    db.add(product)
                    products_created += 1
                    print(f"  添加商品: {product_data['title']} - ¥{product_data['price']}")
                except Exception as e:
                    print(f"  添加商品失败 {product_data['title']}: {e}")

            # 提交所有更改
            await db.commit()
            print(f"\n✅ 成功创建 {products_created} 个商品")

            # 验证插入结果
            result = await db.execute(select(func.count(Product.id)))
            total = result.scalar() or 0
            print(f"数据库中商品总数: {total}")

            # 显示商品列表
            result = await db.execute(
                select(Product).order_by(Product.category_id, Product.sort_order)
            )
            products = result.scalars().all()

            print("\n商品列表:")
            print("-" * 80)
            for p in products:
                print(f"ID:{p.id:3d} | {p.title:12s} | ¥{str(p.price):6s} | 库存:{p.stock:3d} | 分类ID:{p.category_id}")
            print("-" * 80)

        except Exception as e:
            print(f"❌ 批量插入失败: {e}")
            await db.rollback()
            raise
        finally:
            break


if __name__ == "__main__":
    print("=" * 80)
    print("批量商品数据导入工具")
    print("=" * 80)
    asyncio.run(batch_insert_products())
    print("\n导入完成！")
