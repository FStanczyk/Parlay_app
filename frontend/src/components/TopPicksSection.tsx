import React, { useEffect, useState } from 'react';
import { FaCheckCircle } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { TopPick, tipsterApi } from '../services/tipsterService';
import '../styles/sections.scss';

interface TopPicksSectionProps {
  limit?: number;
  days?: number;
}

const TopPicksSection: React.FC<TopPicksSectionProps> = ({ limit = 10, days = 3 }) => {
  const [picks, setPicks] = useState<TopPick[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    tipsterApi.getTopPicks(limit, days)
      .then(setPicks)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [limit, days]);

  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

  return (
    <div className="top-section">
      <div className="top-section__header">
        <h2 className="top-section__title">Last Top Picks</h2>
        <span className="top-section__subtitle">Biggest odds won in last {days} days</span>
      </div>

      {loading ? (
        <div className="top-section__loading">Loading...</div>
      ) : picks.length === 0 ? (
        <div className="top-section__empty">No winning picks in this period</div>
      ) : (
        <div className="top-picks__list">
          {picks.map((pick, index) => (
            <div key={index} className="top-picks__card">
              <div className="top-picks__odds-badge">{pick.odds.toFixed(2)}</div>

              <div className="top-picks__match">
                <span className="top-picks__teams">
                  {pick.home_team} <span className="top-picks__vs">vs</span> {pick.away_team}
                </span>
                <span className="top-picks__event">{pick.event}</span>
              </div>

              <div className="top-picks__meta">
                <span
                  className="top-picks__tipster"
                  onClick={() => navigate(`/experts/${pick.tipster_id}`)}
                >
                  {pick.tipster_name}
                  {pick.tipster_verified && <FaCheckCircle className="top-picks__verified" />}
                </span>
                <span className="top-picks__date">{formatDate(pick.game_datetime)}</span>
              </div>

              <span className="top-picks__win-badge">WIN</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TopPicksSection;
