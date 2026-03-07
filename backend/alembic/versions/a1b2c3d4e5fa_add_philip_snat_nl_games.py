"""add_philip_snat_nl_games

Revision ID: a1b2c3d4e5fa
Revises: a1b2c3d4e5f9
Create Date: 2026-03-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql

revision = 'a1b2c3d4e5fa'
down_revision = 'a1b2c3d4e5f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'philip_snat_nl_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nl_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('hour', sa.String(), nullable=True),
        sa.Column('home_team', sa.String(), nullable=False),
        sa.Column('away_team', sa.String(), nullable=False),
        sa.Column('winner', sa.String(), nullable=True),
        sa.Column('home_score', sa.Float(), nullable=True),
        sa.Column('away_score', sa.Float(), nullable=True),
        sa.Column('home_score_no_ot', sa.Float(), nullable=True),
        sa.Column('away_score_no_ot', sa.Float(), nullable=True),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('total_score_no_ot', sa.Float(), nullable=True),
        sa.Column('ot', sa.Boolean(), nullable=True),
        sa.Column('so', sa.Boolean(), nullable=True),
        sa.Column('h_rank', sa.Integer(), nullable=True),
        sa.Column('a_rank', sa.Integer(), nullable=True),
        sa.Column('rank_diff', sa.Integer(), nullable=True),
        sa.Column('h_gpg', sa.Float(), nullable=True),
        sa.Column('a_gpg', sa.Float(), nullable=True),
        sa.Column('gpg_diff', sa.Float(), nullable=True),
        sa.Column('h_gapg', sa.Float(), nullable=True),
        sa.Column('a_gapg', sa.Float(), nullable=True),
        sa.Column('gapg_diff', sa.Float(), nullable=True),
        sa.Column('h_sogpg', sa.Float(), nullable=True),
        sa.Column('a_sogpg', sa.Float(), nullable=True),
        sa.Column('sogpg_diff', sa.Float(), nullable=True),
        sa.Column('h_sslotpg', sa.Float(), nullable=True),
        sa.Column('a_sslotpg', sa.Float(), nullable=True),
        sa.Column('sslotpg_diff', sa.Float(), nullable=True),
        sa.Column('h_shmpg', sa.Float(), nullable=True),
        sa.Column('a_shmpg', sa.Float(), nullable=True),
        sa.Column('hmpg_diff', sa.Float(), nullable=True),
        sa.Column('h_shppg', sa.Float(), nullable=True),
        sa.Column('a_shppg', sa.Float(), nullable=True),
        sa.Column('hpppg_diff', sa.Float(), nullable=True),
        sa.Column('h_ppgpgg', sa.Float(), nullable=True),
        sa.Column('a_ppgpgg', sa.Float(), nullable=True),
        sa.Column('ppgpgg_diff', sa.Float(), nullable=True),
        sa.Column('h_ppgapg', sa.Float(), nullable=True),
        sa.Column('a_ppgapg', sa.Float(), nullable=True),
        sa.Column('ppgapg_diff', sa.Float(), nullable=True),
        sa.Column('h_ppgeff', sa.Float(), nullable=True),
        sa.Column('a_ppgeff', sa.Float(), nullable=True),
        sa.Column('ppgeff_diff', sa.Float(), nullable=True),
        sa.Column('h_pkeff', sa.Float(), nullable=True),
        sa.Column('a_pkeff', sa.Float(), nullable=True),
        sa.Column('pkeff_diff', sa.Float(), nullable=True),
        sa.Column('h_sapg', sa.Float(), nullable=True),
        sa.Column('a_sapg', sa.Float(), nullable=True),
        sa.Column('sapg_diff', sa.Float(), nullable=True),
        sa.Column('h_sslotapg', sa.Float(), nullable=True),
        sa.Column('a_sslotapg', sa.Float(), nullable=True),
        sa.Column('sslotapg_diff', sa.Float(), nullable=True),
        sa.Column('h_lgd', sa.String(), nullable=True),
        sa.Column('a_lgd', sa.String(), nullable=True),
        sa.Column('h_lgpa', sa.String(), nullable=True),
        sa.Column('a_lgpa', sa.String(), nullable=True),
        sa.Column('h_lgop', sa.String(), nullable=True),
        sa.Column('a_lgop', sa.String(), nullable=True),
        sa.Column('lgop_diff', sa.Integer(), nullable=True),
        sa.Column('h_l5gw', sa.Integer(), nullable=True),
        sa.Column('a_l5gw', sa.Integer(), nullable=True),
        sa.Column('l5gw_diff', sa.Integer(), nullable=True),
        sa.Column('prediction_winner', sa.Float(), nullable=True),
        sa.Column('prediction_goals', postgresql.JSON(astext_type=Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_philip_snat_nl_games_id'), 'philip_snat_nl_games', ['id'], unique=False)
    op.create_index(op.f('ix_philip_snat_nl_games_nl_id'), 'philip_snat_nl_games', ['nl_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_philip_snat_nl_games_nl_id'), table_name='philip_snat_nl_games')
    op.drop_index(op.f('ix_philip_snat_nl_games_id'), table_name='philip_snat_nl_games')
    op.drop_table('philip_snat_nl_games')
