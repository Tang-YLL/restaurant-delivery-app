"""初始化数据库表

Revision ID: 001
Revises:
Create Date: 2024-12-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建分类表
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='分类名称'),
        sa.Column('code', sa.String(length=50), nullable=False, comment='分类代码'),
        sa.Column('description', sa.Text(), nullable=True, comment='分类描述'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0', comment='排序'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true', comment='是否启用'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_categories_id', 'categories', ['id'])
    op.create_index('ix_categories_name', 'categories', ['name'], unique=True)
    op.create_index('ix_categories_code', 'categories', ['code'], unique=True)

    # 创建商品表
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False, comment='商品标题'),
        sa.Column('category_id', sa.Integer(), nullable=False, comment='分类ID'),
        sa.Column('detail_url', sa.String(length=1000), nullable=True, comment='详情链接'),
        sa.Column('image_url', sa.String(length=1000), nullable=True, comment='原始图片URL'),
        sa.Column('local_image_path', sa.String(length=1000), nullable=False, comment='本地图片路径'),
        sa.Column('ingredients', sa.Text(), nullable=True, comment='食材信息'),
        sa.Column('views', sa.Integer(), nullable=True, server_default='0', comment='浏览量'),
        sa.Column('favorites', sa.Integer(), nullable=True, server_default='0', comment='收藏量'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='active', comment='商品状态'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0', comment='排序'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text='now()'), comment='更新时间'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_id', 'products', ['id'])
    op.create_index('ix_products_category_id', 'products', ['category_id'])


def downgrade() -> None:
    op.drop_index('ix_products_category_id', table_name='products')
    op.drop_index('ix_products_id', table_name='products')
    op.drop_table('products')

    op.drop_index('ix_categories_code', table_name='categories')
    op.drop_index('ix_categories_name', table_name='categories')
    op.drop_index('ix_categories_id', table_name='categories')
    op.drop_table('categories')
