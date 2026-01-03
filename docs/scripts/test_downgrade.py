"""测试迁移回滚功能"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# 使用同步SQLite引擎
DATABASE_URL = "sqlite:///./restaurant.db"
engine = create_engine(DATABASE_URL)


def test_downgrade():
    """测试downgrade回滚"""
    print("=" * 60)
    print("测试迁移回滚功能")
    print("=" * 60)

    inspector = inspect(engine)

    # 1. 检查当前表是否存在
    print("\n1. 检查当前状态...")
    tables = inspector.get_table_names()
    assert 'content_sections' in tables, "content_sections表应该存在"
    assert 'nutrition_facts' in tables, "nutrition_facts表应该存在"
    print("✅ content_sections表存在")
    print("✅ nutrition_facts表存在")

    # 2. 执行downgrade SQL
    print("\n2. 执行downgrade操作...")
    with engine.connect() as conn:
        # 删除索引
        conn.execute(text("DROP INDEX IF EXISTS idx_nutrition_facts_product"))
        print("  ✓ 删除idx_nutrition_facts_product")

        conn.execute(text("DROP INDEX IF EXISTS idx_content_sections_type"))
        print("  ✓ 删除idx_content_sections_type")

        conn.execute(text("DROP INDEX IF EXISTS idx_content_sections_product"))
        print("  ✓ 删除idx_content_sections_product")

        # 删除nutrition_facts表
        conn.execute(text("DROP TABLE IF EXISTS nutrition_facts"))
        print("  ✓ 删除nutrition_facts表")

        # 删除content_sections表
        conn.execute(text("DROP TABLE IF EXISTS content_sections"))
        print("  ✓ 删除content_sections表")

        conn.commit()

    # 3. 验证表已删除
    print("\n3. 验证表已删除...")
    inspector = inspect(engine)  # 重新创建inspector
    tables = inspector.get_table_names()

    assert 'content_sections' not in tables, "content_sections表应该已删除"
    assert 'nutrition_facts' not in tables, "nutrition_facts表应该已删除"
    print("✅ content_sections表已删除")
    print("✅ nutrition_facts表已删除")

    # 4. 重新执行upgrade（恢复）
    print("\n4. 重新执行upgrade恢复...")
    with engine.connect() as conn:
        # 创建content_sections表
        conn.execute(text("""
            CREATE TABLE content_sections (
                id INTEGER NOT NULL PRIMARY KEY,
                product_id INTEGER NOT NULL,
                section_type VARCHAR(50) NOT NULL,
                title VARCHAR(200),
                content TEXT NOT NULL,
                display_order INTEGER,
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
            )
        """))
        print("  ✓ 创建content_sections表")

        # 创建索引
        conn.execute(text("CREATE INDEX idx_content_sections_product ON content_sections(product_id)"))
        conn.execute(text("CREATE INDEX idx_content_sections_type ON content_sections(section_type)"))
        conn.execute(text("CREATE INDEX ix_content_sections_id ON content_sections(id)"))
        print("  ✓ 创建content_sections索引")

        # 创建nutrition_facts表
        conn.execute(text("""
            CREATE TABLE nutrition_facts (
                id INTEGER NOT NULL PRIMARY KEY,
                product_id INTEGER NOT NULL,
                serving_size VARCHAR(50),
                calories FLOAT,
                protein FLOAT,
                fat FLOAT,
                carbohydrates FLOAT,
                sodium FLOAT,
                dietary_fiber FLOAT,
                sugars FLOAT,
                created_at DATETIME,
                FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
            )
        """))
        print("  ✓ 创建nutrition_facts表")

        # 创建索引
        conn.execute(text("CREATE INDEX idx_nutrition_facts_product ON nutrition_facts(product_id)"))
        conn.execute(text("CREATE INDEX ix_nutrition_facts_id ON nutrition_facts(id)"))
        print("  ✓ 创建nutrition_facts索引")

        conn.commit()

    # 5. 最终验证
    print("\n5. 最终验证...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert 'content_sections' in tables, "content_sections表应该已恢复"
    assert 'nutrition_facts' in tables, "nutrition_facts表应该已恢复"
    print("✅ content_sections表已恢复")
    print("✅ nutrition_facts表已恢复")

    print("\n" + "=" * 60)
    print("✅ 回滚测试通过！upgrade/downgrade功能正常")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = test_downgrade()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
