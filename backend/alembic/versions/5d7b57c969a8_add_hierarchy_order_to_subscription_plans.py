"""Add hierarchy_order to subscription_plans

Revision ID: 5d7b57c969a8
Revises: 54c49433e4ef
Create Date: 2025-01-28 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d7b57c969a8'
down_revision = '54c49433e4ef'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add hierarchy_order column to subscription_plans
    op.add_column(
        'subscription_plans',
        sa.Column('hierarchy_order', sa.Integer(), nullable=True)
    )

    # Set default hierarchy_order based on sort_order (can be updated manually)
    # This assumes sort_order already represents hierarchy
    op.execute("""
        UPDATE subscription_plans
        SET hierarchy_order = sort_order
        WHERE hierarchy_order IS NULL
    """)

    # Make it NOT NULL after setting defaults
    op.alter_column('subscription_plans', 'hierarchy_order', nullable=False)


def downgrade() -> None:
    op.drop_column('subscription_plans', 'hierarchy_order')
