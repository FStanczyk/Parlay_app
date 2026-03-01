import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Modal from '../../components/Modal';
import { useTranslation } from '../../contexts/TranslationContext';
import '../../styles/manage-recommendations.scss';
import { TipsterTier } from '../../types/interfaces';
import { apiGet, apiPatch } from '../../utils/api';
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

interface RecommendationForm {
  tipster_tier_id: number | null;
  stake: string;
  tipster_description: string;
}

const EditRecommendation: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  const [recommendation, setRecommendation] = useState<BetRecommendation | null>(null);
  const [tiers, setTiers] = useState<TipsterTier[]>([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState<RecommendationForm>({
    tipster_tier_id: null,
    stake: '',
    tipster_description: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;

      try {
        const [recsData, tiersData] = await Promise.all([
          apiGet<BetRecommendation[]>('/tipsters/me/recommendations'),
          apiGet<TipsterTier[]>('/tipsters/me/tiers'),
        ]);

        const rec = recsData.find(r => r.id === parseInt(id));
        if (!rec) {
          navigate('/expert-panel/recommendations');
          return;
        }

        setRecommendation(rec);
        setTiers(tiersData);
        setFormData({
          tipster_tier_id: rec.tipster_tier_id || (tiersData.length > 0 ? tiersData[0].id : null),
          stake: rec.stake?.toString() || '',
          tipster_description: rec.tipster_description || '',
        });
      } catch (err) {
        console.error('Failed to fetch data:', err);
        navigate('/expert-panel/recommendations');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, navigate]);

  const handleSubmit = async () => {
    if (!recommendation) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const payload = {
        bet_event_id: recommendation.bet_event_id,
        tipster_tier_id: formData.tipster_tier_id,
        stake: formData.stake ? parseFloat(formData.stake) : null,
        tipster_description: formData.tipster_description || null,
      };

      await apiPatch(`/tipsters/me/recommendations/${recommendation.id}`, payload);
      navigate('/expert-panel/recommendations');
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || 'Failed to update recommendation');
      setIsSubmitting(false);
    }
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="manage-recs">
        <div className="manage-recs__container">
          <div className="manage-recs__loading">{t.common.loading}</div>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return null;
  }

  return (
    <div className="manage-recs">
      <div className="manage-recs__container">
        <button
          className="manage-recs__back"
          onClick={() => navigate('/expert-panel/recommendations')}
        >
          ← {t.manageRecommendations?.backToRecommendations || 'Back'}
        </button>

        <h1 className="manage-recs__title italic-title">Edit Recommendation</h1>

        <div className="manage-recs__game-header">
          <h2 className="manage-recs__game-title">
            {recommendation.bet_event?.game?.home_team} vs {recommendation.bet_event?.game?.away_team}
          </h2>
          <p className="manage-recs__game-meta">
            {translateEvent(recommendation.bet_event?.event ?? '', t.eventsDictionary)} • {recommendation.bet_event?.odds.toFixed(2)}
            {recommendation.bet_event?.game && (
              <> • {formatDateTime(recommendation.bet_event.game.datetime)}</>
            )}
          </p>
        </div>

        <div className="manage-recs__modal-content-right">
          <div>
            <p>{t.manageRecommendations?.tierLabel || 'Tier'}</p>
            <select
              value={formData.tipster_tier_id || ''}
              onChange={(e) => setFormData({ ...formData, tipster_tier_id: e.target.value ? Number(e.target.value) : null })}
              disabled={isSubmitting}
            >
              {tiers.length === 0 && (
                <option value="">{t.manageRecommendations?.noTiers || 'No tiers available'}</option>
              )}
              {tiers.map((tier) => (
                <option key={tier.id} value={tier.id}>
                  {tier.level === 0 ? 'FREE' : tier.name || `Tier ${tier.level}`}
                </option>
              ))}
            </select>
          </div>

          <div>
            <p>{t.manageRecommendations?.stakeLabel || 'Stake'} (optional)</p>
            <input
              type="number"
              step="0.1"
              min="0"
              placeholder={t.manageRecommendations?.stakePlaceholder || 'Enter stake'}
              value={formData.stake}
              onChange={(e) => setFormData({ ...formData, stake: e.target.value })}
              disabled={isSubmitting}
            />
          </div>

          <div>
            <p>{t.manageRecommendations?.descriptionLabel || 'Description'} (optional)</p>
            <textarea
              placeholder={t.manageRecommendations?.descriptionPlaceholder || 'Add your analysis'}
              value={formData.tipster_description}
              onChange={(e) => setFormData({ ...formData, tipster_description: e.target.value })}
              disabled={isSubmitting}
            />
          </div>

          {submitError && (
            <div className="manage-recs__error">{submitError}</div>
          )}

          <div style={{ display: 'flex', gap: 'var(--spacing-md)', marginTop: 'var(--spacing-md)' }}>
            <button
              className="button_secondary"
              onClick={() => navigate('/expert-panel/recommendations')}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              className="button_primary"
              onClick={handleSubmit}
              disabled={isSubmitting || tiers.length === 0}
            >
              {isSubmitting ? 'Updating...' : 'Update Recommendation'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditRecommendation;
