import React, { useEffect, useState } from 'react';
import { FaCheckCircle } from 'react-icons/fa';
import { useNavigate, useParams } from 'react-router-dom';
import Flag from 'react-world-flags';
import { TipsterStats, tipsterApi } from '../../services/tipsterService';
import '../../styles/expert-stats.scss';
import { TipsterPublic } from '../../types/interfaces';

const fmt = (n: number, decimals = 1) =>
  isFinite(n) && !isNaN(n) ? n.toFixed(decimals) : '—';

const ExpertStatsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [tipster, setTipster] = useState<TipsterPublic | null>(null);
  const [stats, setStats] = useState<TipsterStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const tipsterId = parseInt(id);
    Promise.all([
      tipsterApi.getById(tipsterId),
      tipsterApi.getStats(tipsterId),
    ])
      .then(([tipsterData, statsData]) => {
        setTipster(tipsterData);
        setStats(statsData);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="expert-stats">Loading...</div>;
  if (!tipster) return <div className="expert-stats">Expert not found</div>;

  const winRate = stats && stats.total_picks > 0
    ? (stats.total_picks_won / stats.total_picks) * 100
    : 0;

  const avgOdds = stats && stats.total_picks > 0
    ? stats.sum_odds / stats.total_picks
    : 0;

  const roi = stats && stats.sum_stake > 0
    ? ((stats.total_return - stats.sum_stake) / stats.sum_stake) * 100
    : 0;

  const totalPicks = stats?.total_picks ?? 0;
  const picksWon = stats?.total_picks_won ?? 0;
  const sumStake = stats?.sum_stake ?? 0;
  const totalReturn = stats?.total_return ?? 0;
  const picksWithDesc = stats?.picks_with_description ?? 0;

  const tags = [tipster.tag_1, tipster.tag_2, tipster.tag_3].filter(Boolean) as string[];

  return (
    <section className="card expert-stats">
      <div className="expert-stats__header">
        <button
          className="expert-stats__back"
          onClick={() => navigate(`/experts/${id}`)}
          aria-label="Back to profile"
        >
          ← Back
        </button>

        <div className="expert-stats__identity">
          <h1 className="expert-stats__name">
            {tipster.full_name}
            {tipster.is_verified && <FaCheckCircle className="expert-stats__verified" />}
          </h1>
          {tags.length > 0 && (
            <span className="expert-stats__tags">| {tags.join(', ')}</span>
          )}
          {tipster.country && (
            <div className="expert-stats__flag">
              <Flag code={tipster.country} />
            </div>
          )}
        </div>
      </div>

      <h2 className="expert-stats__section-title">Performance Overview</h2>

      <div className="expert-stats__primary-grid">
        <div className="expert-stats__card expert-stats__card--highlight">
          <span className="expert-stats__card-value">{fmt(winRate)}%</span>
          <span className="expert-stats__card-label">Win Rate</span>
        </div>
        <div className={`expert-stats__card ${roi >= 0 ? 'expert-stats__card--positive' : 'expert-stats__card--negative'}`}>
          <span className="expert-stats__card-value">{roi >= 0 ? '+' : ''}{fmt(roi)}%</span>
          <span className="expert-stats__card-label">ROI</span>
        </div>
        <div className="expert-stats__card">
          <span className="expert-stats__card-value">{totalPicks}</span>
          <span className="expert-stats__card-label">Total Picks</span>
        </div>
        <div className="expert-stats__card">
          <span className="expert-stats__card-value">{fmt(avgOdds, 2)}</span>
          <span className="expert-stats__card-label">Avg Odds</span>
        </div>
      </div>

      <div className="expert-stats__secondary-grid">
        <div className="expert-stats__row-item">
          <span className="expert-stats__row-label">Picks Won</span>
          <span className="expert-stats__row-value">{picksWon} / {totalPicks}</span>
        </div>
        <div className="expert-stats__row-item">
          <span className="expert-stats__row-label">Total Stake</span>
          <span className="expert-stats__row-value">{fmt(sumStake, 2)}u</span>
        </div>
        <div className="expert-stats__row-item">
          <span className="expert-stats__row-label">Total Return</span>
          <span className="expert-stats__row-value">{fmt(totalReturn, 2)}u</span>
        </div>
        <div className="expert-stats__row-item">
          <span className="expert-stats__row-label">Picks with Analysis</span>
          <span className="expert-stats__row-value">{picksWithDesc}</span>
        </div>
      </div>

      {totalPicks === 0 && (
        <p className="expert-stats__empty">No resolved picks yet — stats will appear once picks are settled.</p>
      )}
    </section>
  );
};

export default ExpertStatsPage;
