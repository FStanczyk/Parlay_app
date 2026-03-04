"""add prediction columns

Revision ID: a1b2c3d4e5f8
Revises: a1b2c3d4e5f7
Create Date: 2026-03-04 21:48:15.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql

revision = "a1b2c3d4e5f8"
down_revision = "a1b2c3d4e5f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "philip_snat_nhl_games",
        sa.Column("prediction_winner", sa.Float(), nullable=True),
    )
    op.add_column(
        "philip_snat_nhl_games",
        sa.Column(
            "prediction_goals", postgresql.JSON(astext_type=Text()), nullable=True
        ),
    )
    op.add_column(
        "philip_snat_khl_games",
        sa.Column("prediction_winner", sa.Float(), nullable=True),
    )
    op.add_column(
        "philip_snat_khl_games",
        sa.Column(
            "prediction_goals", postgresql.JSON(astext_type=Text()), nullable=True
        ),
    )


def downgrade() -> None:
    op.drop_column("philip_snat_khl_games", "prediction_goals")
    op.drop_column("philip_snat_khl_games", "prediction_winner")
    op.drop_column("philip_snat_nhl_games", "prediction_goals")
    op.drop_column("philip_snat_nhl_games", "prediction_winner")
