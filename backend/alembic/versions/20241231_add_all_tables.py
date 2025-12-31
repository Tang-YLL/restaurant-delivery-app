"""添加所有核心数据库表

Revision ID: 002
Revises: 001
Create Date: 2024-12-31

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建用户表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False, comment='手机号'),
        sa.Column('password_hash', sa.String(length=255), nullable=False, comment='密码哈希'),
        sa.Column('nickname', sa.String(length=100), nullable=True, comment='昵称'),
        sa.Column('avatar', sa.String(length=500), nullable=True, comment='头像URL'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true', comment='是否激活'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_phone', 'users', ['phone'], unique=True)

    # 创建管理员表
    op.create_table(
        'admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False, comment='用户名'),
        sa.Column('password_hash', sa.String(length=255), nullable=False, comment='密码哈希'),
        sa.Column('email', sa.String(length=255), nullable=True, comment='邮箱'),
        sa.Column('role', sa.String(length=50), nullable=True, server_default='admin', comment='角色'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true', comment='是否激活'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_admins_id', 'admins', ['id'])
    op.create_index('ix_admins_username', 'admins', ['username'], unique=True)

    # 创建购物车表
    op.create_table(
        'cart_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('product_id', sa.Integer(), nullable=False, comment='商品ID'),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1', comment='数量'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='更新时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cart_items_id', 'cart_items', ['id'])
    op.create_index('ix_cart_items_user_id', 'cart_items', ['user_id'])

    # 创建订单表
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(length=100), nullable=False, comment='订单号'),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False, comment='总金额'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='pending', comment='订单状态'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='更新时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_orders_id', 'orders', ['id'])
    op.create_index('ix_orders_order_number', 'orders', ['order_number'], unique=True)
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])

    # 创建订单商品表
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False, comment='订单ID'),
        sa.Column('product_id', sa.Integer(), nullable=False, comment='商品ID'),
        sa.Column('product_name', sa.String(length=500), nullable=False, comment='商品名称'),
        sa.Column('product_image', sa.String(length=1000), nullable=True, comment='商品图片'),
        sa.Column('quantity', sa.Integer(), nullable=False, comment='数量'),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False, comment='单价'),
        sa.Column('subtotal', sa.Numeric(precision=10, scale=2), nullable=False, comment='小计'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='创建时间'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_items_id', 'order_items', ['id'])
    op.create_index('ix_order_items_order_id', 'order_items', ['order_id'])

    # 创建评价表
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户ID'),
        sa.Column('product_id', sa.Integer(), nullable=False, comment='商品ID'),
        sa.Column('order_id', sa.Integer(), nullable=True, comment='订单ID'),
        sa.Column('rating', sa.Integer(), nullable=False, comment='评分 1-5'),
        sa.Column('content', sa.Text(), nullable=True, comment='评价内容'),
        sa.Column('is_visible', sa.Boolean(), nullable=True, server_default='true', comment='是否显示'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()'), comment='更新时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reviews_id', 'reviews', ['id'])
    op.create_index('ix_reviews_product_id', 'reviews', ['product_id'])

    # 插入默认管理员账户 (用户名: admin, 密码: admin123)
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    op.execute(
        f"""
        INSERT INTO admins (username, password_hash, email, role, is_active, created_at, updated_at)
        VALUES ('admin', '{pwd_context.hash('admin123')}', 'admin@example.com', 'super_admin', true, now(), now())
        """
    )


def downgrade() -> None:
    op.drop_index('ix_reviews_product_id', table_name='reviews')
    op.drop_index('ix_reviews_id', table_name='reviews')
    op.drop_table('reviews')

    op.drop_index('ix_order_items_order_id', table_name='order_items')
    op.drop_index('ix_order_items_id', table_name='order_items')
    op.drop_table('order_items')

    op.drop_index('ix_orders_user_id', table_name='orders')
    op.drop_index('ix_orders_order_number', table_name='orders')
    op.drop_index('ix_orders_id', table_name='orders')
    op.drop_table('orders')

    op.drop_index('ix_cart_items_user_id', table_name='cart_items')
    op.drop_index('ix_cart_items_id', table_name='cart_items')
    op.drop_table('cart_items')

    op.drop_index('ix_admins_username', table_name='admins')
    op.drop_index('ix_admins_id', table_name='admins')
    op.drop_table('admins')

    op.drop_index('ix_users_phone', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
