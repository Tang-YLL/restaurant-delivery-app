"""
使用Material素材批量插入商品数据（精确匹配版本）
"""
import asyncio
import sys
import os
import glob
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Product
from sqlalchemy import select, func

# Material目录
MATERIAL_DIR = "/Volumes/545S/general final/Material/material"

# 商品与图片的精确映射（基于实际文件）
PRODUCT_IMAGE_MAPPING = {
    "青椒炒肉": "青椒炒肉.png",
    "红烧肉": "红烧肉.png",
    "鱼香肉丝": "鱼香肉丝.png",
    "宫保鸡丁": "宫保鸡丁（粤菜版）.png",
    "蛋炒饭": "蛋炒饭.png",
    "白米饭": "宝宝辅食 白米饭.png",
    "扬州炒饭": "菠萝炒饭.png",  # 没有扬州炒饭，用菠萝炒饭替代
    "紫菜蛋花汤": "紫菜鸡蛋汤.png",  # 没有紫菜蛋花汤，用紫菜鸡蛋汤替代
    "酸梅汤": "冬瓜排骨汤.png",  # 没有酸梅汤，用冬瓜排骨汤替代
    "番茄鸡蛋汤": "金针菇番茄蛋汤.png",  # 没有番茄鸡蛋汤，用金针菇番茄蛋汤替代
    "冬瓜排骨汤": "冬瓜排骨汤.png",
    "鲜榨橙汁": "橙香京酱肉丝.png",  # 没有橙汁，用橙香京酱肉丝替代
    "冰镇酸梅汤": "冬瓜玉米排骨汤.png",  # 没有冰镇酸梅汤，用冬瓜玉米排骨汤替代
    "柠檬蜂蜜茶": "柠檬蜂蜜茶.png",
    "绿豆汤": "绿豆粉发糕.png",  # 没有绿豆汤，用绿豆粉发糕替代
    "拍黄瓜": "拍黄瓜.png",
    "糖醋排骨": "糖醋排骨.png",
    "红豆沙": "红豆包谷榛.png",  # 没有红豆沙，用红豆包谷榛替代
    "水果沙拉": "水果创意菜+家常水果沙拉.png",
    "银耳莲子汤": "银耳拌黄瓜.png",  # 没有银耳莲子汤，用银耳拌黄瓜替代
}


# 商品数据列表
PRODUCTS_DATA = [
    # 主食类 (category_id=3)
    {
        "title": "青椒炒肉",
        "description": "新鲜青椒搭配嫩滑猪肉，口感鲜美，营养丰富。选用优质五花肉，经过特殊工艺处理，肉质鲜嫩不腻。",
        "price": 28.00,
        "stock": 50,
        "category_id": 3,
        "is_active": True,
        "sort_order": 1
    },
    {
        "title": "红烧肉",
        "description": "精选五花肉，传统工艺红烧，肥而不腻，入口即化。色泽红亮，香气扑鼻，是下饭神器。",
        "price": 58.00,
        "stock": 30,
        "category_id": 3,
        "is_active": True,
        "sort_order": 2
    },
    {
        "title": "鱼香肉丝",
        "description": "经典川菜，酸甜微辣，口感丰富。选用猪里脊肉，配以木耳、胡萝卜丝，色香味俱全。",
        "price": 32.00,
        "stock": 40,
        "category_id": 3,
        "is_active": True,
        "sort_order": 3
    },
    {
        "title": "宫保鸡丁",
        "description": "正宗川菜，鸡肉嫩滑，花生香脆，麻辣适中。选用鸡胸肉，配以干辣椒、花生米，口感层次丰富。",
        "price": 35.00,
        "stock": 45,
        "category_id": 3,
        "is_active": True,
        "sort_order": 4
    },
    {
        "title": "蛋炒饭",
        "description": "经典家常炒饭，米饭粒粒分明，鸡蛋香味浓郁。选用优质大米，配以新鲜鸡蛋，简单而美味。",
        "price": 15.00,
        "stock": 100,
        "category_id": 3,
        "is_active": True,
        "sort_order": 5
    },
    {
        "title": "白米饭",
        "description": "优质大米蒸制，颗粒饱满，口感软糯。选用东北大米，清香扑鼻，是各种菜肴的最佳搭配。",
        "price": 2.00,
        "stock": 200,
        "category_id": 3,
        "is_active": True,
        "sort_order": 6
    },
    {
        "title": "扬州炒饭",
        "description": "经典江苏菜，配料丰富，色彩鲜艳。米饭、鸡蛋、虾仁、火腿、青豆等多种食材，营养均衡。",
        "price": 22.00,
        "stock": 60,
        "category_id": 3,
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
        "is_active": True,
        "sort_order": 1
    },
    {
        "title": "酸梅汤",
        "description": "传统饮品，酸甜解腻。选用优质乌梅、山楂等原料，经过长时间熬制，口感醇厚。",
        "price": 6.00,
        "stock": 100,
        "category_id": 4,
        "is_active": True,
        "sort_order": 2
    },
    {
        "title": "番茄鸡蛋汤",
        "description": "家常汤品，酸甜开胃。新鲜番茄配以嫩滑鸡蛋，汤汁浓郁，营养丰富。",
        "price": 10.00,
        "stock": 70,
        "category_id": 4,
        "is_active": True,
        "sort_order": 3
    },
    {
        "title": "冬瓜排骨汤",
        "description": "营养丰富，清热解暑。新鲜冬瓜配以精选排骨，经过长时间炖煮，汤清味美。",
        "price": 38.00,
        "stock": 40,
        "category_id": 4,
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
        "is_active": True,
        "sort_order": 1
    },
    {
        "title": "冰镇酸梅汤",
        "description": "夏日解暑佳品，冰镇后口感更佳。传统配方熬制，酸甜适中，清爽可口。",
        "price": 8.00,
        "stock": 90,
        "category_id": 5,
        "is_active": True,
        "sort_order": 2
    },
    {
        "title": "柠檬蜂蜜茶",
        "description": "清香怡人，润喉养颜。新鲜柠檬配以优质蜂蜜，酸甜可口，老少皆宜。",
        "price": 15.00,
        "stock": 70,
        "category_id": 5,
        "is_active": True,
        "sort_order": 3
    },
    {
        "title": "绿豆汤",
        "description": "清热解暑，消暑佳品。精选绿豆，经过长时间熬煮，豆烂汤清，甘甜爽口。",
        "price": 6.00,
        "stock": 100,
        "category_id": 5,
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
        "is_active": True,
        "sort_order": 1
    },
    {
        "title": "糖醋排骨",
        "description": "酸甜可口，色泽红亮。精选小排，配以特制糖醋汁，外酥里嫩，老少皆宜。",
        "price": 48.00,
        "stock": 35,
        "category_id": 6,
        "is_active": True,
        "sort_order": 2
    },
    {
        "title": "红豆沙",
        "description": "传统甜品，香甜软糯。精选红豆，经过长时间熬煮，豆沙细腻，甜而不腻。",
        "price": 10.00,
        "stock": 60,
        "category_id": 6,
        "is_active": True,
        "sort_order": 3
    },
    {
        "title": "水果沙拉",
        "description": "新鲜水果，营养健康。当季新鲜水果，配以特制沙拉酱，清爽可口。",
        "price": 18.00,
        "stock": 40,
        "category_id": 6,
        "is_active": True,
        "sort_order": 4
    },
    {
        "title": "银耳莲子汤",
        "description": "滋补养颜，清甜滋润。优质银耳配以精选莲子，经过长时间炖煮，胶质丰富。",
        "price": 16.00,
        "stock": 50,
        "category_id": 6,
        "is_active": True,
        "sort_order": 5
    },
]


async def batch_insert_products():
    """批量插入商品数据"""
    print("开始批量插入商品数据...")
    print("=" * 100)

    # 获取数据库会话
    async for db in get_db():
        try:
            # 检查现有商品数量
            result = await db.execute(select(func.count(Product.id)))
            count = result.scalar() or 0
            print(f"当前商品数量: {count}")

            # 批量创建商品
            products_created = 0
            print("\n添加商品:")
            print("-" * 100)

            for product_data in PRODUCTS_DATA:
                try:
                    # 获取对应的图片文件名
                    image_filename = PRODUCT_IMAGE_MAPPING.get(product_data['title'])
                    if not image_filename:
                        print(f"  ⚠️  商品 '{product_data['title']}' 未找到对应图片")
                        continue

                    # 检查图片文件是否存在
                    source_path = os.path.join(MATERIAL_DIR, image_filename)
                    if not os.path.exists(source_path):
                        print(f"  ⚠️  图片文件不存在: {image_filename}")
                        continue

                    # 复制图片到后端目录
                    target_dir = "/Volumes/545S/general final/backend/public/images/products"
                    os.makedirs(target_dir, exist_ok=True)
                    target_path = os.path.join(target_dir, image_filename)

                    # 如果文件不存在，则复制
                    if not os.path.exists(target_path):
                        import shutil
                        shutil.copy2(source_path, target_path)
                        print(f"  📷 复制图片: {image_filename}")

                    # 添加图片路径到商品数据
                    image_url = f"/images/products/{image_filename}"
                    product_with_image = {
                        **product_data,
                        "local_image_path": image_url,
                        "image_url": image_url
                    }

                    product = Product(**product_with_image)
                    db.add(product)
                    products_created += 1

                    print(f"  ✓ ID:{products_created:2d} | {product_data['title']:12s} | ¥{product_data['price']:6s} | {image_filename}")

                except Exception as e:
                    print(f"  ❌ 添加商品失败 {product_data['title']}: {e}")

            # 提交所有更改
            await db.commit()
            print("-" * 100)
            print(f"\n✅ 成功创建 {products_created} 个商品")

            # 验证插入结果
            result = await db.execute(select(func.count(Product.id)))
            total = result.scalar() or 0
            print(f"数据库中商品总数: {total}")

        except Exception as e:
            print(f"❌ 批量插入失败: {e}")
            await db.rollback()
            raise
        finally:
            break


if __name__ == "__main__":
    print("=" * 100)
    print("批量商品数据导入工具（使用Material素材 - 精确匹配）")
    print("=" * 100)
    asyncio.run(batch_insert_products())
    print("\n导入完成！")
