"""add_odds_api_id_to_sports_and_rename_league_key

Revision ID: 6619be03a9a4
Revises: f22297a468a6
Create Date: 2026-01-27 18:24:39.203544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6619be03a9a4'
down_revision = 'f22297a468a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('sports', sa.Column('odds_api_id', sa.String(), nullable=True))

    op.add_column('leagues', sa.Column('odds_api_id', sa.String(), nullable=True))
    op.execute("UPDATE leagues SET odds_api_id = api_league_key")
    op.alter_column('leagues', 'odds_api_id', nullable=False)
    op.drop_column('leagues', 'api_league_key')


def downgrade() -> None:
    op.add_column('leagues', sa.Column('api_league_key', sa.String(), nullable=True))
    op.execute("UPDATE leagues SET api_league_key = odds_api_id")
    op.alter_column('leagues', 'api_league_key', nullable=False)
    op.drop_column('leagues', 'odds_api_id')
    op.drop_column('sports', 'odds_api_id')
