"""merge_heads

Revision ID: c9d0e1f2a3b4
Revises: 3493bf64ff43, b2c3d4e5f6a7
Create Date: 2026-02-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c9d0e1f2a3b4'
down_revision = ('3493bf64ff43', 'b2c3d4e5f6a7')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
