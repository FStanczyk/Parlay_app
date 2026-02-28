"""create tipster stats and ranges tables

Revision ID: 60eca98a44be
Revises: f1a2b3c4d5e7
Create Date: 2026-02-19 22:37:48.782994

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60eca98a44be'
down_revision = 'f1a2b3c4d5e7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tipster_ranges')"
    ))
    table_exists = result.scalar()

    if not table_exists:
        op.create_table(
            'tipster_ranges',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=True),
            sa.Column('range_start', sa.Float(), nullable=False),
            sa.Column('range_end', sa.Float(), nullable=False),
            sa.UniqueConstraint('range_start', 'range_end', name='uq_range_bounds'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_tipster_ranges_id'), 'tipster_ranges', ['id'], unique=False)
    else:
        op.alter_column('tipster_ranges', 'range_start',
                   existing_type=sa.INTEGER(),
                   type_=sa.Float(),
                   existing_nullable=False)
        op.alter_column('tipster_ranges', 'range_end',
                   existing_type=sa.INTEGER(),
                   type_=sa.Float(),
                   existing_nullable=False)


def downgrade() -> None:
    op.alter_column('tipster_ranges', 'range_end',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('tipster_ranges', 'range_start',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=False)
