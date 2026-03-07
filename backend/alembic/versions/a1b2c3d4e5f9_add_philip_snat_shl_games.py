"""add_philip_snat_shl_games

Revision ID: a1b2c3d4e5f9
Revises: a1b2c3d4e5f8
Create Date: 2026-03-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql

revision = 'a1b2c3d4e5f9'
down_revision = 'a1b2c3d4e5f8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'philip_snat_shl_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('shl_uuid', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('home_team', sa.String(), nullable=False),
        sa.Column('away_team', sa.String(), nullable=False),
        sa.Column('winner', sa.Integer(), nullable=True),
        sa.Column('home_score', sa.Integer(), nullable=True),
        sa.Column('away_score', sa.Integer(), nullable=True),
        sa.Column('home_score_no_ot', sa.Integer(), nullable=True),
        sa.Column('away_score_no_ot', sa.Integer(), nullable=True),
        sa.Column('total_goals', sa.Integer(), nullable=True),
        sa.Column('total_goals_no_ot', sa.Integer(), nullable=True),
        sa.Column('ot', sa.Boolean(), nullable=True),
        sa.Column('so', sa.Boolean(), nullable=True),
        sa.Column('home_rank', sa.Integer(), nullable=True),
        sa.Column('away_rank', sa.Integer(), nullable=True),
        sa.Column('rank_diff', sa.Integer(), nullable=True),
        sa.Column('h_gpg', sa.Float(), nullable=True),
        sa.Column('a_gpg', sa.Float(), nullable=True),
        sa.Column('gpg_diff', sa.Float(), nullable=True),
        sa.Column('gpmutual', sa.Float(), nullable=True),
        sa.Column('h_gapg', sa.Float(), nullable=True),
        sa.Column('a_gapg', sa.Float(), nullable=True),
        sa.Column('gapg_diff', sa.Float(), nullable=True),
        sa.Column('gapmutual', sa.Float(), nullable=True),
        sa.Column('h_pp_perc', sa.Float(), nullable=True),
        sa.Column('a_pp_perc', sa.Float(), nullable=True),
        sa.Column('h_pk_perc', sa.Float(), nullable=True),
        sa.Column('a_pk_perc', sa.Float(), nullable=True),
        sa.Column('h_s_eff', sa.Float(), nullable=True),
        sa.Column('a_s_eff', sa.Float(), nullable=True),
        sa.Column('h_svs_perc', sa.Float(), nullable=True),
        sa.Column('a_svs_perc', sa.Float(), nullable=True),
        sa.Column('h_fo_perc', sa.Float(), nullable=True),
        sa.Column('a_fo_perc', sa.Float(), nullable=True),
        sa.Column('h_cf_perc', sa.Float(), nullable=True),
        sa.Column('a_cf_perc', sa.Float(), nullable=True),
        sa.Column('h_ff_perc', sa.Float(), nullable=True),
        sa.Column('a_ff_perc', sa.Float(), nullable=True),
        sa.Column('h_close_cf_perc', sa.Float(), nullable=True),
        sa.Column('a_close_cf_perc', sa.Float(), nullable=True),
        sa.Column('h_close_ff_perc', sa.Float(), nullable=True),
        sa.Column('a_close_ff_perc', sa.Float(), nullable=True),
        sa.Column('h_pdo', sa.Float(), nullable=True),
        sa.Column('a_pdo', sa.Float(), nullable=True),
        sa.Column('h_st_perc', sa.Float(), nullable=True),
        sa.Column('a_st_perc', sa.Float(), nullable=True),
        sa.Column('h_pps_eff', sa.Float(), nullable=True),
        sa.Column('a_pps_eff', sa.Float(), nullable=True),
        sa.Column('h_sogpg', sa.Float(), nullable=True),
        sa.Column('a_sogpg', sa.Float(), nullable=True),
        sa.Column('sogpg_diff', sa.Float(), nullable=True),
        sa.Column('sogpg_mutual', sa.Float(), nullable=True),
        sa.Column('h_l5gw', sa.Integer(), nullable=True),
        sa.Column('a_l5gw', sa.Integer(), nullable=True),
        sa.Column('l5gw_diff', sa.Integer(), nullable=True),
        sa.Column('h_lmd_gpg1', sa.Float(), nullable=True),
        sa.Column('a_lmd_gpg1', sa.Float(), nullable=True),
        sa.Column('h_lmd_gpg2', sa.Float(), nullable=True),
        sa.Column('a_lmd_gpg2', sa.Float(), nullable=True),
        sa.Column('h_lmd_gapg1', sa.Float(), nullable=True),
        sa.Column('a_lmd_gapg1', sa.Float(), nullable=True),
        sa.Column('h_lmd_gapg2', sa.Float(), nullable=True),
        sa.Column('a_lmd_gapg2', sa.Float(), nullable=True),
        sa.Column('h_shame_factor', sa.Float(), nullable=True),
        sa.Column('a_shame_factor', sa.Float(), nullable=True),
        sa.Column('h_hunger_fg', sa.Float(), nullable=True),
        sa.Column('a_hunger_fg', sa.Float(), nullable=True),
        sa.Column('hunger_fg_diff', sa.Float(), nullable=True),
        sa.Column('hunger_fg_mutual', sa.Float(), nullable=True),
        sa.Column('prediction_winner', sa.Float(), nullable=True),
        sa.Column('prediction_goals', postgresql.JSON(astext_type=Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_philip_snat_shl_games_id'), 'philip_snat_shl_games', ['id'], unique=False)
    op.create_index(op.f('ix_philip_snat_shl_games_shl_uuid'), 'philip_snat_shl_games', ['shl_uuid'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_philip_snat_shl_games_shl_uuid'), table_name='philip_snat_shl_games')
    op.drop_index(op.f('ix_philip_snat_shl_games_id'), table_name='philip_snat_shl_games')
    op.drop_table('philip_snat_shl_games')
