"""add question intent table

Revision ID: 005
Revises: 004
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建问题意图表
    op.create_table(
        'question_intents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('original_question', sa.Text(), nullable=False),
        sa.Column('intent_type', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('subcategory', sa.String(length=50), server_default='', nullable=False),
        sa.Column('enhanced_question', sa.Text(), server_default='', nullable=False),
        sa.Column('keywords', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_question_intents_id', 'question_intents', ['id'])
    op.create_index('ix_question_intents_user_id', 'question_intents', ['user_id'])
    op.create_index('ix_question_intents_intent_type', 'question_intents', ['intent_type'])


def downgrade() -> None:
    op.drop_index('ix_question_intents_intent_type', table_name='question_intents')
    op.drop_index('ix_question_intents_user_id', table_name='question_intents')
    op.drop_index('ix_question_intents_id', table_name='question_intents')
    op.drop_table('question_intents')
