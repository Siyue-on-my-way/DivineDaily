"""add user profile table

Revision ID: 004
Revises: 003
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建用户档案表
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('nickname', sa.String(length=50), server_default='', nullable=False),
        sa.Column('avatar', sa.String(length=255), server_default='', nullable=False),
        sa.Column('gender', sa.String(length=10), server_default='未知', nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('birth_time', sa.String(length=20), server_default='', nullable=False),
        sa.Column('birth_place', sa.String(length=100), server_default='', nullable=False),
        sa.Column('lunar_birth', sa.String(length=50), server_default='', nullable=False),
        sa.Column('animal', sa.String(length=10), server_default='', nullable=False),
        sa.Column('zodiac_sign', sa.String(length=20), server_default='', nullable=False),
        sa.Column('bazi', sa.String(length=100), server_default='', nullable=False),
        sa.Column('preferred_divination', sa.String(length=20), server_default='iching', nullable=False),
        sa.Column('notification_enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('notification_time', sa.String(length=10), server_default='08:00', nullable=False),
        sa.Column('bio', sa.Text(), server_default='', nullable=False),
        sa.Column('interests', sa.Text(), server_default='', nullable=False),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # 创建索引
    op.create_index('ix_user_profiles_id', 'user_profiles', ['id'])
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_user_profiles_user_id', table_name='user_profiles')
    op.drop_index('ix_user_profiles_id', table_name='user_profiles')
    op.drop_table('user_profiles')
