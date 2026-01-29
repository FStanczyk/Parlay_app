"""add philip snat tables

Revision ID: 60c1150685b6
Revises: e8f9a1b2c3d4
Create Date: 2025-01-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60c1150685b6'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'philip_snat_sports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('sport', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_philip_snat_sports_id'), 'philip_snat_sports', ['id'], unique=False)

    op.create_table(
        'philip_snat_prediction_file',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['sport_id'], ['philip_snat_sports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_philip_snat_prediction_file_id'), 'philip_snat_prediction_file', ['id'], unique=False)

    op.execute("""
        INSERT INTO philip_snat_sports (name, sport) VALUES
        ('NHL', 'NHL'),
        ('KHL', 'KHL'),
        ('SHL', 'SHL'),
        ('NBA', 'NBA'),
        ('Football', 'Football'),
        ('CHL', 'CHL'),
        ('Extraliga', 'Extraliga')
    """)


def downgrade() -> None:
    op.drop_index(op.f('ix_philip_snat_prediction_file_id'), table_name='philip_snat_prediction_file')
    op.drop_table('philip_snat_prediction_file')
    op.drop_index(op.f('ix_philip_snat_sports_id'), table_name='philip_snat_sports')
    op.drop_table('philip_snat_sports')
