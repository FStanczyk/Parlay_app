"""add_void_and_unknown_to_bet_result_enum

Revision ID: d7536c687150
Revises: 813a41fc29e7
Create Date: 2026-01-29 22:53:57.164961

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7536c687150'
down_revision = '813a41fc29e7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE betresult ADD VALUE IF NOT EXISTS 'VOID'")
    op.execute("ALTER TYPE betresult ADD VALUE IF NOT EXISTS 'UNKNOWN'")


def downgrade() -> None:
    pass
