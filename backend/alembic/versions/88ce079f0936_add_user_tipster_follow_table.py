"""add_user_tipster_follow_table

Revision ID: 88ce079f0936
Revises: 41546cacaf5b
Create Date: 2026-01-04 17:57:58.921138

"""
from alembic import op
import sqlalchemy as sa

revision = '88ce079f0936'
down_revision = '41546cacaf5b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('user_tipster_follows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tipster_id', sa.Integer(), nullable=False),
        sa.Column('followed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tipster_id'], ['tipsters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_tipster_follows_id'), 'user_tipster_follows', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_tipster_follows_id'), table_name='user_tipster_follows')
    op.drop_table('user_tipster_follows')
