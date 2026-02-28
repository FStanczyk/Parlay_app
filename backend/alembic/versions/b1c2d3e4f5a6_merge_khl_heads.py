"""merge_khl_heads

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6, c9d0e1f2a3b4
Create Date: 2026-02-28 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b1c2d3e4f5a6'
down_revision = ('a1b2c3d4e5f6', 'c9d0e1f2a3b4')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
