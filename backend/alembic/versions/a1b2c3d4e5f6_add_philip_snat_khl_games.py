"""add_philip_snat_khl_games

Revision ID: a1b2c3d4e5f6
Revises: f8ba46037f67
Create Date: 2026-02-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = 'f8ba46037f67'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'philip_snat_khl_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('khl_id', sa.Integer(), nullable=False),
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
        sa.Column('h_pk_pct', sa.String(), nullable=True),
        sa.Column('a_pk_pct', sa.String(), nullable=True),
        sa.Column('pk_pct_diff', sa.Float(), nullable=True),
        sa.Column('h_pm_pg', sa.String(), nullable=True),
        sa.Column('a_pm_pg', sa.String(), nullable=True),
        sa.Column('pm_pg_diff', sa.Float(), nullable=True),
        sa.Column('h_pp_pct', sa.String(), nullable=True),
        sa.Column('a_pp_pct', sa.String(), nullable=True),
        sa.Column('pp_pct_diff', sa.Float(), nullable=True),
        sa.Column('h_ppg_apg', sa.Float(), nullable=True),
        sa.Column('a_ppg_apg', sa.Float(), nullable=True),
        sa.Column('ppg_apg_diff', sa.Float(), nullable=True),
        sa.Column('h_sv_pct', sa.String(), nullable=True),
        sa.Column('a_sv_pct', sa.String(), nullable=True),
        sa.Column('sv_pct_diff', sa.Float(), nullable=True),
        sa.Column('h_svpg', sa.Float(), nullable=True),
        sa.Column('a_svpg', sa.Float(), nullable=True),
        sa.Column('svpg_diff', sa.Float(), nullable=True),
        sa.Column('h_spg', sa.Float(), nullable=True),
        sa.Column('a_spg', sa.Float(), nullable=True),
        sa.Column('spg_diff', sa.Float(), nullable=True),
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
        sa.Column('hom_score_no_ot', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_philip_snat_khl_games_id'), 'philip_snat_khl_games', ['id'], unique=False)
    op.create_index(op.f('ix_philip_snat_khl_games_khl_id'), 'philip_snat_khl_games', ['khl_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_philip_snat_khl_games_khl_id'), table_name='philip_snat_khl_games')
    op.drop_index(op.f('ix_philip_snat_khl_games_id'), table_name='philip_snat_khl_games')
    op.drop_table('philip_snat_khl_games')
