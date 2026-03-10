"""add divination shares table

Revision ID: 011_add_divination_shares
Revises: 010_add_quality_and_pattern_tables
Create Date: 2026-03-01

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '011_add_divination_shares'
down_revision = '010_add_quality_and_pattern_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 divination_shares 表
    op.create_table(
        'divination_shares',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), nullable=False),
        sa.Column('share_token', sa.String(32), nullable=False, unique=True),
        sa.Column('share_url', sa.Text(), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    
    # 创建索引
    op.create_index('idx_share_token', 'divination_shares', ['share_token'])
    op.create_index('idx_session_id_shares', 'divination_shares', ['session_id'])
    
    # 创建外键
    op.create_foreign_key(
        'fk_divination_shares_session_id',
        'divination_shares', 'divination_sessions',
        ['session_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_table('divination_shares')
