"""add_tags_to_tipsters

Revision ID: a92e528b8f61
Revises: d7536c687150
Create Date: 2026-02-05 21:12:27.567004

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a92e528b8f61'
down_revision = 'd7536c687150'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tipsters', sa.Column('tag_1', sa.String(length=20), nullable=True))
    op.add_column('tipsters', sa.Column('tag_2', sa.String(length=20), nullable=True))
    op.add_column('tipsters', sa.Column('tag_3', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('tipsters', 'tag_3')
    op.drop_column('tipsters', 'tag_2')
    op.drop_column('tipsters', 'tag_1')
