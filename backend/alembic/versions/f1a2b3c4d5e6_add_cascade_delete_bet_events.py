"""add_cascade_delete_bet_events

Revision ID: f1a2b3c4d5e6
Revises: e8f9a1b2c3d4
Create Date: 2026-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'e8f9a1b2c3d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('bet_events_game_id_fkey', 'bet_events', type_='foreignkey')
    op.create_foreign_key(
        'bet_events_game_id_fkey',
        'bet_events',
        'games',
        ['game_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('bet_events_game_id_fkey', 'bet_events', type_='foreignkey')
    op.create_foreign_key(
        'bet_events_game_id_fkey',
        'bet_events',
        'games',
        ['game_id'],
        ['id']
    )
