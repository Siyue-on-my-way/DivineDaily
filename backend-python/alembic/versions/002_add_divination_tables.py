"""add divination tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # 创建占卜会话表
    op.create_table('divination_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=True),
        sa.Column('orientation', sa.String(length=50), nullable=True),
        sa.Column('spread', sa.String(length=50), nullable=True),
        sa.Column('intent', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('result_summary', sa.Text(), nullable=True),
        sa.Column('result_detail', sa.Text(), nullable=True),
        sa.Column('result_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('follow_up_count', sa.Integer(), nullable=True),
        sa.Column('follow_up_answers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_divination_sessions_user_id'), 'divination_sessions', ['user_id'], unique=False)

    # 创建占卜结果表
    op.create_table('divination_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('outcome', sa.String(length=20), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('detail', sa.Text(), nullable=False),
        sa.Column('hexagram_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('daily_fortune', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('cards', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('needs_follow_up', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_divination_results_id'), 'divination_results', ['id'], unique=False)
    op.create_index(op.f('ix_divination_results_session_id'), 'divination_results', ['session_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_divination_results_session_id'), table_name='divination_results')
    op.drop_index(op.f('ix_divination_results_id'), table_name='divination_results')
    op.drop_table('divination_results')
    
    op.drop_index(op.f('ix_divination_sessions_user_id'), table_name='divination_sessions')
    op.drop_table('divination_sessions')
