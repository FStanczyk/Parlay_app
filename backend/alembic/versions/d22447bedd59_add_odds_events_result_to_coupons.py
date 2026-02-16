"""add_odds_events_result_to_coupons

Revision ID: d22447bedd59
Revises: a92e528b8f61
Create Date: 2026-02-12 15:02:15.901188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd22447bedd59'
down_revision = 'a92e528b8f61'
branch_labels = None
depends_on = None


def upgrade() -> None:
    couponresult = sa.Enum('WON', 'LOST', 'PENDING', 'VOID', name='couponresult')
    couponresult.create(op.get_bind(), checkfirst=True)

    op.add_column('coupons', sa.Column('odds', sa.Float(), nullable=True))
    op.add_column('coupons', sa.Column('events', sa.Integer(), nullable=True))
    op.add_column('coupons', sa.Column('result', couponresult, nullable=True))


def downgrade() -> None:
    op.drop_column('coupons', 'result')
    op.drop_column('coupons', 'events')
    op.drop_column('coupons', 'odds')

    sa.Enum(name='couponresult').drop(op.get_bind(), checkfirst=True)
