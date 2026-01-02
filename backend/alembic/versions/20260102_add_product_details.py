"""add product details tables

Revision ID: 20260102_add_product_details
Revises: 20241231_add_admin_logs
Create Date: 2026-01-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260102_add_product_details'
down_revision = '20241231_add_admin_logs'
branch_labels = None
depends_on = None


def upgrade():
    """添加商品详情相关表"""

    # 创建content_sections表
    op.create_table(
        'content_sections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('section_type', sa.String(length=50), nullable=False, comment='内容类型: story/nutrition/ingredients/process/tips'),
        sa.Column('title', sa.String(length=200), nullable=True, comment='标题'),
        sa.Column('content', sa.Text(), nullable=False, comment='富文本HTML内容'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0', comment='显示顺序'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 创建content_sections索引
    op.create_index('idx_content_sections_product', 'content_sections', ['product_id'], unique=False)
    op.create_index('idx_content_sections_type', 'content_sections', ['section_type'], unique=False)

    # 创建nutrition_facts表
    op.create_table(
        'nutrition_facts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('serving_size', sa.String(length=50), nullable=True, comment='份量大小，如"1份(200g)"'),
        sa.Column('calories', sa.Float(), nullable=True, comment='热量 (kcal/100g)'),
        sa.Column('protein', sa.Float(), nullable=True, comment='蛋白质 (g/100g)'),
        sa.Column('fat', sa.Float(), nullable=True, comment='脂肪 (g/100g)'),
        sa.Column('carbohydrates', sa.Float(), nullable=True, comment='碳水化合物 (g/100g)'),
        sa.Column('sodium', sa.Float(), nullable=True, comment='钠 (mg/100g)'),
        sa.Column('dietary_fiber', sa.Float(), nullable=True, comment='膳食纤维 (g/100g)'),
        sa.Column('sugars', sa.Float(), nullable=True, comment='糖 (g/100g)'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 创建nutrition_facts索引
    op.create_index('idx_nutrition_facts_product', 'nutrition_facts', ['product_id'], unique=False)


def downgrade():
    """回滚更改"""

    # 删除nutrition_facts表
    op.drop_index('idx_nutrition_facts_product', table_name='nutrition_facts')
    op.drop_table('nutrition_facts')

    # 删除content_sections表
    op.drop_index('idx_content_sections_type', table_name='content_sections')
    op.drop_index('idx_content_sections_product', table_name='content_sections')
    op.drop_table('content_sections')
