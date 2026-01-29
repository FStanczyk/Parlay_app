"""add_odds_api_id_to_bet_events

Revision ID: f22297a468a6
Revises: 60c1150685b6
Create Date: 2026-01-27 16:57:58.923749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f22297a468a6'
down_revision = '60c1150685b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('bet_events', sa.Column('odds_api_id', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('bet_events', 'odds_api_id')
