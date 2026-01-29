"""add_coupon_and_bet_event_on_coupon_tables

Revision ID: c6d70094dbf2
Revises: 88ce079f0936
Create Date: 2026-01-04 18:03:53.262821

"""
from alembic import op
import sqlalchemy as sa

revision = 'c6d70094dbf2'
down_revision = '88ce079f0936'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('coupons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coupons_id'), 'coupons', ['id'], unique=False)
    op.create_table('bet_events_on_coupons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coupon_id', sa.Integer(), nullable=False),
        sa.Column('bet_event_id', sa.Integer(), nullable=False),
        sa.Column('is_recommendation', sa.Boolean(), nullable=False),
        sa.Column('bet_recommendation_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['bet_event_id'], ['bet_events.id']),
        sa.ForeignKeyConstraint(['bet_recommendation_id'], ['bet_recommendations.id']),
        sa.ForeignKeyConstraint(['coupon_id'], ['coupons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bet_events_on_coupons_id'), 'bet_events_on_coupons', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_bet_events_on_coupons_id'), table_name='bet_events_on_coupons')
    op.drop_table('bet_events_on_coupons')
    op.drop_index(op.f('ix_coupons_id'), table_name='coupons')
    op.drop_table('coupons')
