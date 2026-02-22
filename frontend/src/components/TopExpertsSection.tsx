import React, { useEffect, useState } from 'react';
import { FaCheckCircle } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import Flag from 'react-world-flags';
import { TopExpert, tipsterApi } from '../services/tipsterService';
import '../styles/sections.scss';

interface TopExpertsSectionProps {
  limit?: number;
}

const TopExpertsSection: React.FC<TopExpertsSectionProps> = ({ limit = 10 }) => {
  const [experts, setExperts] = useState<TopExpert[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    tipsterApi.getLeaderboard(limit)
      .then(setExperts)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [limit]);

  return (
    <div className="top-section">
      <div className="top-section__header">
        <h2 className="top-section__title">Top Experts</h2>
        <span className="top-section__subtitle">Ranked by ROI</span>
      </div>

      {loading ? (
        <div className="top-section__loading">Loading...</div>
      ) : experts.length === 0 ? (
        <div className="top-section__empty">No stats available yet</div>
      ) : (
        <ol className="top-experts__list">
          {experts.map((expert, index) => (
            <li
              key={expert.id}
              className="top-experts__row"
              onClick={() => navigate(`/experts/${expert.id}`)}
            >
              <span className={`top-experts__rank ${index === 0 ? 'top-experts__rank--gold' : index === 1 ? 'top-experts__rank--silver' : index === 2 ? 'top-experts__rank--bronze' : ''}`}>
                {index + 1}
              </span>

              {expert.country && (
                <span className="top-experts__flag">
                  <Flag code={expert.country} />
                </span>
              )}

              <div className="top-experts__identity">
                <span className="top-experts__name">
                  {expert.full_name}
                  {expert.is_verified && <FaCheckCircle className="top-experts__verified" />}
                </span>
                {(expert.tag_1 || expert.tag_2) && (
                  <span className="top-experts__tags">
                    {[expert.tag_1, expert.tag_2, expert.tag_3].filter(Boolean).join(' · ')}
                  </span>
                )}
              </div>

              <div className="top-experts__stats">
                <span className="top-experts__picks">{expert.total_picks_won}/{expert.total_picks}</span>
                <span className={`top-experts__roi ${expert.roi >= 0 ? 'top-experts__roi--positive' : 'top-experts__roi--negative'}`}>
                  {expert.roi >= 0 ? '+' : ''}{expert.roi.toFixed(1)}%
                </span>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
};

export default TopExpertsSection;
