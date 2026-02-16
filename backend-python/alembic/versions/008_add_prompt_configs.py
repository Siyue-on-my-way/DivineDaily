"""add prompt configs table

Revision ID: 008
Revises: 007
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建Prompt配置表
    op.create_table(
        'prompt_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('scene', sa.String(length=50), nullable=False),
        sa.Column('llm_config_id', sa.Integer(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=False, server_default='0.7'),
        sa.Column('max_tokens', sa.Integer(), nullable=False, server_default='2000'),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('prompt_type', sa.String(length=50), nullable=False),
        sa.Column('question_type', sa.String(length=50), server_default='', nullable=False),
        sa.Column('template', sa.Text(), nullable=False),
        sa.Column('variables', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('description', sa.Text(), server_default='', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['llm_config_id'], ['llm_configs.id'], ondelete='SET NULL')
    )
    
    op.create_index('ix_prompt_configs_id', 'prompt_configs', ['id'])
    op.create_index('ix_prompt_configs_name', 'prompt_configs', ['name'])
    op.create_index('ix_prompt_configs_scene', 'prompt_configs', ['scene'])
    op.create_index('ix_prompt_configs_llm_config_id', 'prompt_configs', ['llm_config_id'])
    
    # 插入默认易经占卜配置
    op.execute("""
        INSERT INTO prompt_configs (name, scene, llm_config_id, temperature, max_tokens, timeout_seconds, prompt_type, question_type, template, variables, is_default, is_enabled, description)
        VALUES (
            '易经-结果卡',
            'divination',
            1,
            0.7,
            500,
            30,
            'answer',
            '',
            '你是一位精通周易的占卜大师。用户问题：{question}。卦象：{hexagram_name}。请给出明确建议（100-150字）。',
            '["question", "hexagram_name", "hexagram_summary"]',
            true,
            true,
            '易经占卜结果卡Prompt'
        )
    """)
    
    # 插入默认易经详情配置
    op.execute("""
        INSERT INTO prompt_configs (name, scene, llm_config_id, temperature, max_tokens, timeout_seconds, prompt_type, question_type, template, variables, is_default, is_enabled, description)
        VALUES (
            '易经-详情',
            'divination',
            1,
            0.7,
            1500,
            30,
            'detail',
            '',
            '你是一位精通周易的占卜师。用户问题：{question}。卦象：{hexagram_name}。请详细解卦（300-500字）。',
            '["question", "hexagram_name", "hexagram_detail"]',
            true,
            true,
            '易经占卜详情Prompt'
        )
    """)


def downgrade() -> None:
    op.drop_index('ix_prompt_configs_llm_config_id', table_name='prompt_configs')
    op.drop_index('ix_prompt_configs_scene', table_name='prompt_configs')
    op.drop_index('ix_prompt_configs_name', table_name='prompt_configs')
    op.drop_index('ix_prompt_configs_id', table_name='prompt_configs')
    op.drop_table('prompt_configs')
