"""reset sequences after csv import

Revision ID: a1b2c3d4e5f7
Revises: 687f6b9f2a47
Create Date: 2026-03-01 12:00:00.000000

"""
from alembic import op

revision = 'a1b2c3d4e5f7'
down_revision = '687f6b9f2a47'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        SELECT setval(
            pg_get_serial_sequence('philip_snat_nhl_games', 'id'),
            COALESCE((SELECT MAX(id) FROM philip_snat_nhl_games), 0) + 1,
            false
        )
    """)
    op.execute("""
        SELECT setval(
            pg_get_serial_sequence('philip_snat_khl_games', 'id'),
            COALESCE((SELECT MAX(id) FROM philip_snat_khl_games), 0) + 1,
            false
        )
    """)
    op.execute("""
        SELECT setval(
            pg_get_serial_sequence('philip_snat_leagues', 'id'),
            COALESCE((SELECT MAX(id) FROM philip_snat_leagues), 0) + 1,
            false
        )
    """)
    op.execute("""
        SELECT setval(
            pg_get_serial_sequence('philip_snat_ai_models', 'id'),
            COALESCE((SELECT MAX(id) FROM philip_snat_ai_models), 0) + 1,
            false
        )
    """)


def downgrade():
    pass
