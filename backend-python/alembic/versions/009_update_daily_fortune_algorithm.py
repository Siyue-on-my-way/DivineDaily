"""update daily fortune table with algorithm fields

Revision ID: 009
Revises: 008
Create Date: 2026-02-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 检查表是否存在
    conn = op.get_bind()
    inspector = inspect(conn)
    
    if 'daily_fortunes' not in inspector.get_table_names():
        # 表不存在，创建新表
        op.create_table(
            'daily_fortunes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('fortune_date', sa.Date(), nullable=False),
            sa.Column('overall_score', sa.Integer(), nullable=False, server_default='70'),
            sa.Column('wealth_score', sa.Integer(), nullable=False, server_default='70'),
            sa.Column('career_score', sa.Integer(), nullable=False, server_default='70'),
            sa.Column('love_score', sa.Integer(), nullable=False, server_default='70'),
            sa.Column('health_score', sa.Integer(), nullable=False, server_default='70'),
            sa.Column('content', sa.Text(), nullable=False, server_default=''),
            sa.Column('lucky_color', sa.String(length=50), nullable=False, server_default='白色'),
            sa.Column('lucky_number', sa.Integer(), nullable=False, server_default='8'),
            sa.Column('lucky_direction', sa.String(length=50), nullable=False, server_default='东'),
            sa.Column('lucky_time', sa.String(length=50), nullable=False, server_default='辰时(07:00-09:00)'),
            sa.Column('yi', sa.String(length=200), nullable=False, server_default=''),
            sa.Column('ji', sa.String(length=200), nullable=False, server_default=''),
            sa.Column('solar_term', sa.String(length=50), server_default='', nullable=False),
            sa.Column('festival', sa.String(length=100), server_default='', nullable=False),
            sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        
        # 创建索引
        op.create_index('ix_daily_fortunes_id', 'daily_fortunes', ['id'])
        op.create_index('ix_daily_fortunes_user_id', 'daily_fortunes', ['user_id'])
        op.create_index('ix_daily_fortunes_fortune_date', 'daily_fortunes', ['fortune_date'])
        op.create_index('ix_daily_fortunes_user_fortune_date', 'daily_fortunes', ['user_id', 'fortune_date'], unique=True)
    else:
        # 表存在，进行迁移
        columns = [col['name'] for col in inspector.get_columns('daily_fortunes')]
        
        # 重命名字段
        if 'date' in columns and 'fortune_date' not in columns:
            op.alter_column('daily_fortunes', 'date', new_column_name='fortune_date')
        
        # 修改 user_id 类型
        if 'user_id' in columns:
            op.alter_column('daily_fortunes', 'user_id', type_=sa.Integer(), postgresql_using='user_id::integer')
        
        # 删除旧字段（如果存在）
        if 'score' in columns:
            op.drop_column('daily_fortunes', 'score')
        if 'summary' in columns:
            op.drop_column('daily_fortunes', 'summary')
        if 'wealth' in columns:
            op.drop_column('daily_fortunes', 'wealth')
        if 'career' in columns:
            op.drop_column('daily_fortunes', 'career')
        if 'love' in columns:
            op.drop_column('daily_fortunes', 'love')
        if 'health' in columns:
            op.drop_column('daily_fortunes', 'health')
        
        # 添加新的评分字段（如果不存在）
        if 'overall_score' not in columns:
            op.add_column('daily_fortunes', sa.Column('overall_score', sa.Integer(), nullable=False, server_default='70'))
        if 'wealth_score' not in columns:
            op.add_column('daily_fortunes', sa.Column('wealth_score', sa.Integer(), nullable=False, server_default='70'))
        if 'career_score' not in columns:
            op.add_column('daily_fortunes', sa.Column('career_score', sa.Integer(), nullable=False, server_default='70'))
        if 'love_score' not in columns:
            op.add_column('daily_fortunes', sa.Column('love_score', sa.Integer(), nullable=False, server_default='70'))
        if 'health_score' not in columns:
            op.add_column('daily_fortunes', sa.Column('health_score', sa.Integer(), nullable=False, server_default='70'))
        
        # 添加内容字段（如果不存在）
        if 'content' not in columns:
            op.add_column('daily_fortunes', sa.Column('content', sa.Text(), nullable=False, server_default=''))
        
        # 修改 lucky_number 类型（如果需要）
        if 'lucky_number' in columns:
            op.alter_column('daily_fortunes', 'lucky_number', type_=sa.Integer(), postgresql_using='lucky_number::integer')
        
        # 修改宜忌字段类型（从 JSON 改为 String）
        if 'yi' in columns:
            op.alter_column('daily_fortunes', 'yi', type_=sa.String(200), postgresql_using="COALESCE(array_to_string(ARRAY(SELECT jsonb_array_elements_text(yi)), ','), '')")
        if 'ji' in columns:
            op.alter_column('daily_fortunes', 'ji', type_=sa.String(200), postgresql_using="COALESCE(array_to_string(ARRAY(SELECT jsonb_array_elements_text(ji)), ','), '')")
        
        # 更新索引
        indexes = [idx['name'] for idx in inspector.get_indexes('daily_fortunes')]
        
        if 'ix_daily_fortunes_date' in indexes:
            op.drop_index('ix_daily_fortunes_date', table_name='daily_fortunes')
        if 'ix_daily_fortunes_fortune_date' not in indexes:
            op.create_index('ix_daily_fortunes_fortune_date', 'daily_fortunes', ['fortune_date'])
        
        if 'ix_daily_fortunes_user_date' in indexes:
            op.drop_index('ix_daily_fortunes_user_date', table_name='daily_fortunes')
        if 'ix_daily_fortunes_user_fortune_date' not in indexes:
            op.create_index('ix_daily_fortunes_user_fortune_date', 'daily_fortunes', ['user_id', 'fortune_date'], unique=True)


def downgrade() -> None:
    # 简化的降级：直接删除表
    op.drop_table('daily_fortunes')
