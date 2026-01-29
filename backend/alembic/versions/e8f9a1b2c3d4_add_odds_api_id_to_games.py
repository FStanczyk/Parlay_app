"""add_odds_api_id_to_games

Revision ID: e8f9a1b2c3d4
Revises: 249c78459e76
Create Date: 2026-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8f9a1b2c3d4'
down_revision = '249c78459e76'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('games', sa.Column('odds_api_id', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('games', 'odds_api_id')
