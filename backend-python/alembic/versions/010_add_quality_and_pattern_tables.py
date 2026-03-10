"""add quality and pattern tables

Revision ID: 010
Revises: 009
Create Date: 2026-02-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    # 创建 question_quality_history 表
    op.create_table(
        'question_quality_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(36), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('original_question', sa.Text(), nullable=False),
        sa.Column('enhanced_question', sa.Text(), nullable=True),
        sa.Column('overall_score', sa.Integer(), nullable=False),
        sa.Column('specificity_score', sa.Integer(), nullable=False),
        sa.Column('personal_relevance_score', sa.Integer(), nullable=False),
        sa.Column('decision_value_score', sa.Integer(), nullable=False),
        sa.Column('temporal_relevance_score', sa.Integer(), nullable=False),
        sa.Column('quality_factors', postgresql.JSONB(), nullable=True),
        sa.Column('suggestions', postgresql.JSONB(), nullable=True),
        sa.Column('user_feedback', sa.Integer(), nullable=True),
        sa.Column('feedback_comment', sa.Text(), nullable=True),
        sa.Column('used_enhanced', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('idx_quality_user_id', 'question_quality_history', ['user_id'])
    op.create_index('idx_quality_session_id', 'question_quality_history', ['session_id'])
    op.create_index('idx_quality_created_at', 'question_quality_history', ['created_at'])

    # 创建 user_patterns 表
    op.create_table(
        'user_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('pattern_type', sa.String(50), nullable=False),
        sa.Column('pattern_data', postgresql.JSONB(), nullable=False),
        sa.Column('frequency', sa.Integer(), default=1),
        sa.Column('confidence', sa.Float(), default=0.5),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'pattern_type', name='uq_user_pattern_type')
    )
    op.create_index('idx_patterns_user_id', 'user_patterns', ['user_id'])
    op.create_index('idx_patterns_type', 'user_patterns', ['pattern_type'])

    # 创建 divination_feedback 表
    op.create_table(
        'divination_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('feedback_type', sa.String(50), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('is_helpful', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range')
    )
    op.create_index('idx_feedback_session', 'divination_feedback', ['session_id'])
    op.create_index('idx_feedback_user', 'divination_feedback', ['user_id'])
    op.create_index('idx_feedback_type', 'divination_feedback', ['feedback_type'])


def downgrade():
    op.drop_table('divination_feedback')
    op.drop_table('user_patterns')
    op.drop_table('question_quality_history')
