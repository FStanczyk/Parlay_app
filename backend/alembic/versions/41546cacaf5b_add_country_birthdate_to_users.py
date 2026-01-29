"""add_country_birthdate_to_users

Revision ID: 41546cacaf5b
Revises: 495adcc0c342
Create Date: 2026-01-04 17:55:09.630406

"""
from alembic import op
import sqlalchemy as sa

revision = '41546cacaf5b'
down_revision = '495adcc0c342'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('country', sa.String(), nullable=True))
    op.add_column('users', sa.Column('birthdate', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'birthdate')
    op.drop_column('users', 'country')
