"""测试商品详情数据模型"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.models import Base, Product, ContentSection, NutritionFact, Category

# 使用同步SQLite引擎
DATABASE_URL = "sqlite:///./restaurant.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def test_models():
    """测试模型定义和关系"""
    print("=" * 60)
    print("测试商品详情数据模型")
    print("=" * 60)

    # 创建会话
    session = SessionLocal()

    try:
        # 1. 测试表是否存在
        print("\n1. 验证表是否存在...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert 'content_sections' in tables, "content_sections表不存在"
        assert 'nutrition_facts' in tables, "nutrition_facts表不存在"
        print("✅ content_sections表存在")
        print("✅ nutrition_facts表存在")

        # 2. 验证表结构
        print("\n2. 验证表结构...")
        columns = inspector.get_columns('content_sections')
        column_names = [col['name'] for col in columns]
        required_columns = ['id', 'product_id', 'section_type', 'title', 'content', 'display_order', 'created_at', 'updated_at']
        for col in required_columns:
            assert col in column_names, f"content_sections表缺少{col}列"
        print("✅ content_sections表结构正确")

        columns = inspector.get_columns('nutrition_facts')
        column_names = [col['name'] for col in columns]
        required_columns = ['id', 'product_id', 'serving_size', 'calories', 'protein', 'fat',
                          'carbohydrates', 'sodium', 'dietary_fiber', 'sugars', 'created_at']
        for col in required_columns:
            assert col in column_names, f"nutrition_facts表缺少{col}列"
        print("✅ nutrition_facts表结构正确")

        # 3. 验证外键约束
        print("\n3. 验证外键约束...")
        fk_constraints = inspector.get_foreign_keys('content_sections')
        assert len(fk_constraints) > 0, "content_sections表缺少外键约束"
        assert fk_constraints[0]['referred_table'] == 'products', "外键应该指向products表"
        print("✅ content_sections外键约束正确")

        fk_constraints = inspector.get_foreign_keys('nutrition_facts')
        assert len(fk_constraints) > 0, "nutrition_facts表缺少外键约束"
        assert fk_constraints[0]['referred_table'] == 'products', "外键应该指向products表"
        print("✅ nutrition_facts外键约束正确")

        # 4. 验证索引
        print("\n4. 验证索引...")
        indexes = inspector.get_indexes('content_sections')
        index_names = [idx['name'] for idx in indexes]
        assert 'idx_content_sections_product' in index_names, "缺少product_id索引"
        assert 'idx_content_sections_type' in index_names, "缺少section_type索引"
        print("✅ content_sections索引正确")

        indexes = inspector.get_indexes('nutrition_facts')
        index_names = [idx['name'] for idx in indexes]
        assert 'idx_nutrition_facts_product' in index_names, "缺少product_id索引"
        print("✅ nutrition_facts索引正确")

        # 5. 测试关系查询
        print("\n5. 测试SQLAlchemy关系...")

        # 查找一个商品
        product = session.query(Product).first()
        if product:
            print(f"✅ 找到测试商品: {product.title}")

            # 测试content_sections关系
            sections = product.content_sections
            print(f"✅ Product.content_sections关系正常 (当前数量: {len(sections)})")

            # 测试nutrition_fact关系
            nutrition = product.nutrition_fact
            print(f"✅ Product.nutrition_fact关系正常 ({'有数据' if nutrition else '无数据'})")
        else:
            print("⚠️  数据库中没有商品数据，跳过关系测试")

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()

    return True


if __name__ == "__main__":
    success = test_models()
    sys.exit(0 if success else 1)
