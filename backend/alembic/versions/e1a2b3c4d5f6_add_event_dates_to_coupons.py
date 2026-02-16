"""add_event_dates_to_coupons

Revision ID: e1a2b3c4d5f6
Revises: c005cdcd35c7
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa


revision = 'e1a2b3c4d5f6'
down_revision = 'c005cdcd35c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('coupons', sa.Column('first_event_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('coupons', sa.Column('last_event_date', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('coupons', 'last_event_date')
    op.drop_column('coupons', 'first_event_date')
