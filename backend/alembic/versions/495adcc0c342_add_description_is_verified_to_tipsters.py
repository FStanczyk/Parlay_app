"""add_description_is_verified_to_tipsters

Revision ID: 495adcc0c342
Revises: 5d7b57c969a8
Create Date: 2026-01-04 17:48:57.290282

"""
from alembic import op
import sqlalchemy as sa

revision = '495adcc0c342'
down_revision = '5d7b57c969a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tipsters', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('tipsters', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('tipsters', 'is_verified')
    op.drop_column('tipsters', 'description')
