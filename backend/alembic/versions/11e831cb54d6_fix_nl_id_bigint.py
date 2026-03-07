"""fix_nl_id_bigint

Revision ID: 11e831cb54d6
Revises: a1b2c3d4e5fa
Create Date: 2026-03-07 12:17:08.569612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11e831cb54d6'
down_revision = 'a1b2c3d4e5fa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('philip_snat_nl_games', 'nl_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('philip_snat_nl_games', 'nl_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=False)
