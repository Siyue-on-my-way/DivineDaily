"""add daily fortune table

Revision ID: 003
Revises: 002
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建每日运势表
    op.create_table(
        'daily_fortunes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('wealth', sa.Text(), nullable=False),
        sa.Column('career', sa.Text(), nullable=False),
        sa.Column('love', sa.Text(), nullable=False),
        sa.Column('health', sa.Text(), nullable=False),
        sa.Column('lucky_color', sa.String(length=50), nullable=False),
        sa.Column('lucky_number', sa.String(length=50), nullable=False),
        sa.Column('lucky_direction', sa.String(length=50), nullable=False),
        sa.Column('lucky_time', sa.String(length=50), nullable=False),
        sa.Column('yi', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('ji', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('solar_term', sa.String(length=50), server_default='', nullable=False),
        sa.Column('festival', sa.String(length=100), server_default='', nullable=False),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_daily_fortunes_id', 'daily_fortunes', ['id'])
    op.create_index('ix_daily_fortunes_user_id', 'daily_fortunes', ['user_id'])
    op.create_index('ix_daily_fortunes_date', 'daily_fortunes', ['date'])
    
    # 创建唯一约束（每个用户每天只能有一条运势）
    op.create_index(
        'ix_daily_fortunes_user_date',
        'daily_fortunes',
        ['user_id', 'date'],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('ix_daily_fortunes_user_date', table_name='daily_fortunes')
    op.drop_index('ix_daily_fortunes_date', table_name='daily_fortunes')
    op.drop_index('ix_daily_fortunes_user_id', table_name='daily_fortunes')
    op.drop_index('ix_daily_fortunes_id', table_name='daily_fortunes')
    op.drop_table('daily_fortunes')
