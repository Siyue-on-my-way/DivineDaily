"""add system config tables

Revision ID: 006
Revises: 005
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建系统配置表
    op.create_table(
        'system_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('value_type', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('is_public', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_system_configs_id', 'system_configs', ['id'])
    op.create_index('ix_system_configs_key', 'system_configs', ['key'], unique=True)
    op.create_index('ix_system_configs_category', 'system_configs', ['category'])
    
    # 创建 Prompt 模板表
    op.create_table(
        'prompt_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('template', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('variables', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('usage_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_prompt_templates_id', 'prompt_templates', ['id'])
    op.create_index('ix_prompt_templates_name', 'prompt_templates', ['name'], unique=True)
    op.create_index('ix_prompt_templates_category', 'prompt_templates', ['category'])
    
    # 创建系统统计表
    op.create_table(
        'system_statistics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Integer(), nullable=False),
        sa.Column('metric_data', postgresql.JSON(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_system_statistics_id', 'system_statistics', ['id'])
    op.create_index('ix_system_statistics_date', 'system_statistics', ['date'])
    op.create_index('ix_system_statistics_metric_name', 'system_statistics', ['metric_name'])


def downgrade() -> None:
    op.drop_index('ix_system_statistics_metric_name', table_name='system_statistics')
    op.drop_index('ix_system_statistics_date', table_name='system_statistics')
    op.drop_index('ix_system_statistics_id', table_name='system_statistics')
    op.drop_table('system_statistics')
    
    op.drop_index('ix_prompt_templates_category', table_name='prompt_templates')
    op.drop_index('ix_prompt_templates_name', table_name='prompt_templates')
    op.drop_index('ix_prompt_templates_id', table_name='prompt_templates')
    op.drop_table('prompt_templates')
    
    op.drop_index('ix_system_configs_category', table_name='system_configs')
    op.drop_index('ix_system_configs_key', table_name='system_configs')
    op.drop_index('ix_system_configs_id', table_name='system_configs')
    op.drop_table('system_configs')
