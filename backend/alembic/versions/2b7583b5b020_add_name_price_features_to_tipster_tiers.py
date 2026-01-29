"""add_name_price_features_to_tipster_tiers

Revision ID: 2b7583b5b020
Revises: c6d70094dbf2
Create Date: 2026-01-05 22:39:52.511742

"""
from alembic import op
import sqlalchemy as sa

revision = '2b7583b5b020'
down_revision = 'c6d70094dbf2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tipster_tiers', sa.Column('name', sa.String(), nullable=True))
    op.add_column('tipster_tiers', sa.Column('price_monthly', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('tipster_tiers', sa.Column('features_description', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('tipster_tiers', 'features_description')
    op.drop_column('tipster_tiers', 'price_monthly')
    op.drop_column('tipster_tiers', 'name')
