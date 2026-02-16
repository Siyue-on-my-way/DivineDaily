"""add llm configs table

Revision ID: 007
Revises: 006
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建LLM配置表
    op.create_table(
        'llm_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('url_type', sa.String(length=50), nullable=False, server_default='openai_compatible'),
        sa.Column('api_key', sa.Text(), nullable=False),
        sa.Column('endpoint', sa.String(length=500), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_llm_configs_id', 'llm_configs', ['id'])
    op.create_index('ix_llm_configs_name', 'llm_configs', ['name'], unique=True)
    op.create_index('ix_llm_configs_provider', 'llm_configs', ['provider'])
    op.create_index('ix_llm_configs_is_enabled', 'llm_configs', ['is_enabled'])
    
    # 插入默认DeepSeek配置（使用占位符，实际使用时需要配置真实API Key）
    op.execute("""
        INSERT INTO llm_configs (name, provider, url_type, api_key, endpoint, model_name, is_default, is_enabled, description)
        VALUES (
            'DeepSeek-V3',
            'deepseek',
            'openai_compatible',
            'sk-placeholder-key',
            'https://api.deepseek.com/v1',
            'deepseek-chat',
            true,
            true,
            'DeepSeek V3 模型，支持OpenAI兼容接口'
        )
    """)


def downgrade() -> None:
    op.drop_index('ix_llm_configs_is_enabled', table_name='llm_configs')
    op.drop_index('ix_llm_configs_provider', table_name='llm_configs')
    op.drop_index('ix_llm_configs_name', table_name='llm_configs')
    op.drop_index('ix_llm_configs_id', table_name='llm_configs')
    op.drop_table('llm_configs')
