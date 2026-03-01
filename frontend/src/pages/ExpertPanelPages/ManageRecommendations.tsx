import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Modal from '../../components/Modal';
import { useTranslation } from '../../contexts/TranslationContext';
import '../../styles/manage-recommendations.scss';
import { TipsterTier } from '../../types/interfaces';
import { apiDelete, apiGet } from '../../utils/api';
import { translateEvent } from '../../utils/translateEvent';

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
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [recommendationToDelete, setRecommendationToDelete] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const toggleExpand = (id: number, event: React.MouseEvent) => {
    event.stopPropagation();
    setExpandedId(expandedId === id ? null : id);
  };

  const canEditOrDelete = (gameDateTime: string): boolean => {
    const gameDate = new Date(gameDateTime);
    const now = new Date();
    const diffMinutes = (gameDate.getTime() - now.getTime()) / (1000 * 60);
    return diffMinutes >= 30;
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

  const handleDelete = async (recId: number, event: React.MouseEvent) => {
    event.stopPropagation();
    setRecommendationToDelete(recId);
    setDeleteModalOpen(true);
    setDeleteError(null);
  };

  const confirmDelete = async () => {
    if (!recommendationToDelete) return;

    setIsDeleting(true);
    setDeleteError(null);

    try {
      await apiDelete(`/tipsters/me/recommendations/${recommendationToDelete}`);
      setRecommendations(prev => prev.filter(r => r.id !== recommendationToDelete));
      setDeleteModalOpen(false);
      setRecommendationToDelete(null);
    } catch (error: any) {
      setDeleteError(error.response?.data?.detail || 'Failed to delete recommendation');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCancelDelete = () => {
    setDeleteModalOpen(false);
    setRecommendationToDelete(null);
    setDeleteError(null);
    setIsDeleting(false);
  };

  const handleEdit = (recId: number, event: React.MouseEvent) => {
    event.stopPropagation();
    navigate(`/expert-panel/recommendations/edit/${recId}`);
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
              {filteredRecommendations.map((rec) => {
                const canModify = rec.bet_event?.game ? canEditOrDelete(rec.bet_event.game.datetime) : false;

                return (
                  <div
                    key={rec.id}
                    className={`manage-recs__rec-row ${expandedId === rec.id ? 'manage-recs__rec-row--expanded' : ''}`}
                  >
                    <div className="manage-recs__rec-row-main" onClick={(e) => toggleExpand(rec.id, e)}>
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
                        <span className="manage-recs__rec-event">{translateEvent(rec.bet_event?.event ?? '', t.eventsDictionary)}</span>
                        <span className="manage-recs__rec-odds">{rec.bet_event?.odds.toFixed(2)}</span>
                        {rec.stake && (
                          <span className="manage-recs__rec-stake">{rec.stake}u</span>
                        )}
                        {rec.bet_event?.game && (
                          <span className="manage-recs__time-tag">{formatDateTime(rec.bet_event.game.datetime)}</span>
                        )}
                      </div>
                      {canModify && (
                        <div className="manage-recs__rec-actions">
                          <button
                            className="manage-recs__action-btn manage-recs__action-btn--edit"
                            onClick={(e) => handleEdit(rec.id, e)}
                            title="Edit"
                          >
                            Edit
                          </button>
                          <button
                            className="manage-recs__action-btn manage-recs__action-btn--delete"
                            onClick={(e) => handleDelete(rec.id, e)}
                            title="Delete"
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                    <div className={`manage-recs__rec-row-expanded ${expandedId === rec.id ? 'manage-recs__rec-row-expanded--open' : ''}`}>
                      <div className="manage-recs__rec-description">
                        {rec.tipster_description || t.manageRecommendations?.noDescription || 'No description provided'}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </div>

      <Modal
        isOpen={deleteModalOpen}
        onClose={handleCancelDelete}
        title="Delete Recommendation"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          <p>Are you sure you want to delete this recommendation? This action cannot be undone.</p>

          {deleteError && (
            <div className="manage-recs__error">{deleteError}</div>
          )}

          <div style={{ display: 'flex', gap: 'var(--spacing-md)', justifyContent: 'flex-end' }}>
            <button
              className="button_secondary"
              onClick={handleCancelDelete}
              disabled={isDeleting}
            >
              Cancel
            </button>
            <button
              className="manage-recs__action-btn manage-recs__action-btn--delete"
              onClick={confirmDelete}
              disabled={isDeleting}
              style={{ padding: 'var(--spacing-sm) var(--spacing-lg)' }}
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ManageRecommendations;
