import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../../contexts/TranslationContext';
import '../../styles/manage-recommendations.scss';
import { TipsterTier } from '../../types/interfaces';
import { apiGet } from '../../utils/api';

interface Game {
  id: number;
  datetime: string;
  home_team: string;
  away_team: string;
}

interface BetEvent {
  id: number;
  odds: number;
  event: string;
  game?: Game;
}

interface TipsterTierBasic {
  id: number;
  level: number;
  name?: string;
}

interface BetRecommendation {
  id: number;
  bet_event_id: number;
  tipster_id: number;
  tipster_tier_id?: number;
  tipster_description?: string;
  stake?: number;
  bet_event?: BetEvent;
  tipster_tier?: TipsterTierBasic;
}

const ManageRecommendations: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState<BetRecommendation[]>([]);
  const [tiers, setTiers] = useState<TipsterTier[]>([]);
  const [selectedTierId, setSelectedTierId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [recsData, tiersData] = await Promise.all([
          apiGet<BetRecommendation[]>('/tipsters/me/recommendations'),
          apiGet<TipsterTier[]>('/tipsters/me/tiers')
        ]);
        setRecommendations(recsData);
        setTiers(tiersData);
        if (tiersData.length > 0) {
          setSelectedTierId(tiersData[0].id);
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredRecommendations = selectedTierId
    ? recommendations.filter(rec => rec.tipster_tier_id === selectedTierId)
    : recommendations;

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="manage-recs">
      <div className="manage-recs__container">
        <h1 className="manage-recs__title italic-title">{t.expertPanel.manageRecommendations}</h1>

        <button
          className="button_primary"
          onClick={() => navigate('/expert-panel/recommendations/add')}
        >
          {t.manageRecommendations?.addRecommendations || 'Add recommendations'} +
        </button>

        <section className="manage-recs__current">
          <div className="manage-recs__current-header">
            <p className="wide__small__text">
              {t.manageRecommendations?.currentRecommendations || 'Your Recommendations'}
            </p>
            {tiers.length > 0 && (
              <select
                className="manage-recs__tier-filter"
                value={selectedTierId || ''}
                onChange={(e) => setSelectedTierId(e.target.value ? Number(e.target.value) : null)}
              >
                <option value="">{t.manageRecommendations?.allTiers || 'All Tiers'}</option>
                {tiers.map((tier) => (
                  <option key={tier.id} value={tier.id}>
                    {tier.name || `Tier ${tier.level}`}
                  </option>
                ))}
              </select>
            )}
          </div>

          {loading ? (
            <div className="manage-recs__loading">{t.common.loading}</div>
          ) : filteredRecommendations.length === 0 ? (
            <div className="manage-recs__empty">
              {t.manageRecommendations?.noRecommendations || 'No recommendations yet'}
            </div>
          ) : (
            <div className="manage-recs__games-list">
              {filteredRecommendations.map((rec) => (
                <div
                  key={rec.id}
                  className={`manage-recs__rec-row ${expandedId === rec.id ? 'manage-recs__rec-row--expanded' : ''}`}
                  onClick={() => toggleExpand(rec.id)}
                >
                  <div className="manage-recs__rec-row-main">
                    <div className="manage-recs__game-teams">
                      {rec.bet_event?.game ? (
                        <>
                          <span className="manage-recs__team">{rec.bet_event.game.home_team}</span>
                          <span className="manage-recs__vs-small">vs</span>
                          <span className="manage-recs__team">{rec.bet_event.game.away_team}</span>
                        </>
                      ) : (
                        <span className="manage-recs__team">Game unavailable</span>
                      )}
                    </div>
                    <div className="manage-recs__rec-details">
                      {rec.tipster_tier && (
                        <span className={`manage-recs__tier-badge ${rec.tipster_tier.level === 0 ? 'manage-recs__tier-badge--free' : ''}`}>
                          {rec.tipster_tier.level === 0 ? 'FREE' : rec.tipster_tier.name || `Tier ${rec.tipster_tier.level}`}
                        </span>
                      )}
                      <span className="manage-recs__rec-event">{rec.bet_event?.event}</span>
                      <span className="manage-recs__rec-odds">{rec.bet_event?.odds.toFixed(2)}</span>
                      {rec.bet_event?.game && (
                        <span className="manage-recs__time-tag">{formatDateTime(rec.bet_event.game.datetime)}</span>
                      )}
                    </div>
                  </div>
                  <div className={`manage-recs__rec-row-expanded ${expandedId === rec.id ? 'manage-recs__rec-row-expanded--open' : ''}`}>
                    <div className="manage-recs__rec-description">
                      {rec.tipster_description || t.manageRecommendations?.noDescription || 'No description provided'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default ManageRecommendations;
