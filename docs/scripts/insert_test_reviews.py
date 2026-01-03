"""
插入测试评价数据
"""
import asyncio
import sys
import random
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Product, User, Review, Order
from sqlalchemy import select

# 测试评价内容
TEST_COMMENTS = [
    "非常好吃的菜品，味道很棒！",
    "包装很仔细，送餐速度快，好评！",
    "分量很足，性价比很高，会回购。",
    "菜品新鲜，口味正宗，强烈推荐！",
    "服务态度好，送餐及时，菜品热乎。",
    "味道一般般，有点失望。",
    "分量有点少，不够吃。",
    "送餐太慢了，等了快一个小时。",
    "菜品还行，但是有点咸。",
    "非常满意的用餐体验，五星好评！",
    "菜品不错，但是包装可以改进。",
    "总体来说还是不错的，继续努力。",
    "期待下次还能吃到这么好吃的菜！",
    "朋友们都说好吃，果然名不虚传。",
    "虽然有点小贵，但是值得这个价格。"
]

async def insert_test_reviews():
    """插入测试评价数据"""
    print("=" * 120)
    print("插入测试评价数据")
    print("=" * 120)

    async for db in get_db():
        try:
            # 获取现有的商品、用户和订单
            products_result = await db.execute(select(Product).limit(20))
            products = products_result.scalars().all()

            users_result = await db.execute(select(User).limit(10))
            users = users_result.scalars().all()

            orders_result = await db.execute(select(Order).limit(30))
            orders = orders_result.scalars().all()

            if not products:
                print("❌ 没有找到商品，请先创建商品数据")
                return

            if not users:
                print("❌ 没有找到用户，请先创建用户数据")
                return

            if not orders:
                print("❌ 没有找到订单，请先创建订单数据")
                return

            print(f"✓ 找到 {len(products)} 个商品")
            print(f"✓ 找到 {len(users)} 个用户")
            print(f"✓ 找到 {len(orders)} 个订单")

            # 清除现有测试评价
            existing_reviews = await db.execute(select(Review).where(Review.id >= 1000))
            for review in existing_reviews.scalars().all():
                await db.delete(review)
            await db.commit()
            print("✓ 清除旧测试评价")

            # 插入新的测试评价
            reviews_created = 0
            target_reviews = 50

            print(f"\n开始插入 {target_reviews} 条评价...")
            print("-" * 120)

            for i in range(target_reviews):
                # 随机选择商品、用户和订单
                product = random.choice(products)
                user = random.choice(users)
                order = random.choice(orders)

                # 随机评分（偏向好评）
                rating = random.choices([1, 2, 3, 4, 5], weights=[1, 2, 3, 5, 10])[0]

                # 随机选择评价内容
                comment = random.choice(TEST_COMMENTS)

                # 随机是否有图片
                images = None
                if random.random() < 0.3:  # 30%概率有图片
                    images = f'["/images/products/{product.local_image_path.split("/")[-1]}"]'

                # 创建评价
                review = Review(
                    user_id=user.id,
                    product_id=product.id,
                    order_id=order.id,
                    rating=rating,
                    content=comment,
                    images=images,
                    is_visible=True,
                    admin_reply=None if random.random() < 0.7 else f"感谢您的评价！我们会继续努力提供更好的服务。"
                )

                db.add(review)
                reviews_created += 1

                if reviews_created % 10 == 0:
                    print(f"  [{reviews_created:3d}/{target_reviews}] 用户: {user.nickname[:10]:10s} | 商品: {product.title[:15]:15s} | {rating}星")

                # 每20条提交一次
                if reviews_created % 20 == 0:
                    await db.commit()
                    print(f"  已提交 {reviews_created} 条")

            # 最终提交
            await db.commit()
            print("-" * 120)

            # 验证插入结果
            result = await db.execute(select(func.count(Review.id)))
            total = result.scalar() or 0
            print(f"\n✅ 成功插入 {reviews_created} 条评价")
            print(f"数据库中评价总数: {total}")

        except Exception as e:
            print(f"❌ 插入评价失败: {e}")
            await db.rollback()
            raise
        finally:
            break


if __name__ == "__main__":
    import random
    random.seed(42)  # 设置随机种子
    from sqlalchemy import func

    asyncio.run(insert_test_reviews())
    print("\n" + "=" * 120)
    print("测试评价数据插入完成！")
    print("=" * 120)
