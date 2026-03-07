"""change_nl_id_to_string

Revision ID: ee7d04ed9d57
Revises: 11e831cb54d6
Create Date: 2026-03-07 12:27:55.628441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee7d04ed9d57'
down_revision = '11e831cb54d6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('philip_snat_nl_games', 'nl_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.String(),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('philip_snat_nl_games', 'nl_id',
                    existing_type=sa.String(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)
