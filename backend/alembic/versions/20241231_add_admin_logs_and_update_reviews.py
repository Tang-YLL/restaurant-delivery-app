"""add admin logs table and update reviews table

Revision ID: 20241231_add_admin_logs
Revises: 20241231_add_all_tables
Create Date: 2024-12-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20241231_add_admin_logs'
down_revision = '20241231_add_all_tables'
branch_labels = None
depends_on = None


def upgrade():
    """添加admin_logs表和更新reviews表"""

    # 添加admin_reply列到reviews表
    op.add_column('reviews',
                  sa.Column('admin_reply', sa.Text(), nullable=True)
                  )

    # 创建admin_logs表
    op.create_table(
        'admin_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 创建索引
    op.create_index(op.f('ix_admin_logs_action'), 'admin_logs', ['action'], unique=False)
    op.create_index(op.f('ix_admin_logs_id'), 'admin_logs', ['id'], unique=False)


def downgrade():
    """回滚更改"""

    # 删除admin_logs表
    op.drop_index(op.f('ix_admin_logs_id'), table_name='admin_logs')
    op.drop_index(op.f('ix_admin_logs_action'), table_name='admin_logs')
    op.drop_table('admin_logs')

    # 删除reviews表的admin_reply列
    op.drop_column('reviews', 'admin_reply')
