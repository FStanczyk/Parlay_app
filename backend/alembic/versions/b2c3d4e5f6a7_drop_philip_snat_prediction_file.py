"""drop_philip_snat_prediction_file

Revision ID: b2c3d4e5f6a7
Revises: e8f9a1b2c3d4
Create Date: 2026-02-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b2c3d4e5f6a7'
down_revision = 'e8f9a1b2c3d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('philip_snat_prediction_file')


def downgrade() -> None:
    op.create_table(
        'philip_snat_prediction_file',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['sport_id'], ['philip_snat_sports.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_philip_snat_prediction_file_id'), 'philip_snat_prediction_file', ['id'], unique=False)
