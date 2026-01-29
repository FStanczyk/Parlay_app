"""Add subscription tables

Revision ID: 54c49433e4ef
Revises: 11c4e6d28be6
Create Date: 2025-01-28 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '54c49433e4ef'
down_revision = '11c4e6d28be6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # Check if ENUM types exist, create them if they don't
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'subscriptionstatus')"))
    if not result.scalar():
        op.execute("CREATE TYPE subscriptionstatus AS ENUM ('active', 'cancelled', 'expired', 'trial')")

    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'paymentstatus')"))
    if not result.scalar():
        op.execute("CREATE TYPE paymentstatus AS ENUM ('pending', 'succeeded', 'failed')")

    if 'subscription_plans' not in tables:
        op.create_table(
            'subscription_plans',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('price_monthly', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('price_yearly', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('features', postgresql.JSONB(astext_type=Text()), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
            sa.Column('sort_order', sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_subscription_plans_id'), 'subscription_plans', ['id'], unique=False)

    # Create user_subscriptions table (only if it doesn't exist)
    if 'user_subscriptions' not in tables:
        op.create_table(
            'user_subscriptions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('plan_id', sa.Integer(), nullable=False),
            sa.Column('status', postgresql.ENUM('active', 'cancelled', 'expired', 'trial', name='subscriptionstatus', create_type=False), nullable=False),
            sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False),
            sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'status', name='uq_user_subscription_status')
        )
        op.create_index(op.f('ix_user_subscriptions_id'), 'user_subscriptions', ['id'], unique=False)

    # Create subscription_payments table (only if it doesn't exist)
    if 'subscription_payments' not in tables:
        op.create_table(
            'subscription_payments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_subscription_id', sa.Integer(), nullable=False),
            sa.Column('external_id', sa.String(), nullable=False),
            sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('currency', sa.String(length=3), nullable=False),
            sa.Column('status', postgresql.ENUM('pending', 'succeeded', 'failed', name='paymentstatus', create_type=False), nullable=False),
            sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('invoice_pdf_url', sa.String(), nullable=True),
            sa.ForeignKeyConstraint(['user_subscription_id'], ['user_subscriptions.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_subscription_payments_id'), 'subscription_payments', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_subscription_payments_id'), table_name='subscription_payments')
    op.drop_table('subscription_payments')

    op.drop_index(op.f('ix_user_subscriptions_id'), table_name='user_subscriptions')
    op.drop_table('user_subscriptions')

    op.drop_index(op.f('ix_subscription_plans_id'), table_name='subscription_plans')
    op.drop_table('subscription_plans')

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS paymentstatus")
    op.execute("DROP TYPE IF EXISTS subscriptionstatus")
