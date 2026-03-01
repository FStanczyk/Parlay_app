import React, { useState } from 'react';
import { BetRecommendation } from '../services/tipsterService';
import { useTranslation } from '../contexts/TranslationContext';
import { translateEvent } from '../utils/translateEvent';

interface ExpertPickPanelProps {
  recommendation: BetRecommendation;
  resolved?: boolean;
  ongoing?: boolean;
}

const ExpertPickPanel: React.FC<ExpertPickPanelProps> = ({ recommendation, resolved = false, ongoing = false }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { t } = useTranslation();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const getResultLabel = (result?: string) => {
    switch (result) {
      case 'WIN':
        return 'Won';
      case 'LOOSE':
        return 'Lost';
      case 'VOID':
        return 'Void';
      default:
        return null;
    }
  };

  const result = recommendation.bet_event?.result;
  const resultLabel = getResultLabel(result);
  const resultClass = result ? `expert-pick-row--${result.toLowerCase()}` : '';
  const ongoingClass = ongoing ? 'expert-pick-row--ongoing' : '';

  return (
    <div
      className={`expert-pick-row ${isExpanded ? 'expert-pick-row--expanded' : ''} ${resultClass} ${ongoingClass}`.trim()}
      onClick={toggleExpand}
    >
      <div className="expert-pick-row__main">
        <div className="expert-pick-row__teams">
          {recommendation.bet_event?.game ? (
            <>
              <span className="expert-pick-row__team">{recommendation.bet_event.game.home_team}</span>
              <span className="expert-pick-row__vs">vs</span>
              <span className="expert-pick-row__team">{recommendation.bet_event.game.away_team}</span>
            </>
          ) : (
            <span className="expert-pick-row__team">Game unavailable</span>
          )}
        </div>
        <div className="expert-pick-row__details">
          {resolved && resultLabel && (
            <span className={`expert-pick-row__result-badge expert-pick-row__result-badge--${result?.toLowerCase()}`}>
              {resultLabel}
            </span>
          )}
          {recommendation.tipster_tier && !resolved && (
            <span className={`expert-pick-row__tier-badge ${recommendation.tipster_tier.level === 0 ? 'expert-pick-row__tier-badge--free' : ''}`}>
              {recommendation.tipster_tier.level === 0 ? 'FREE' : recommendation.tipster_tier.name || `Tier ${recommendation.tipster_tier.level}`}
            </span>
          )}
          <span className="expert-pick-row__event">{translateEvent(recommendation.bet_event?.event ?? '', t.eventsDictionary)}</span>
          <span className="expert-pick-row__odds">{recommendation.bet_event?.odds.toFixed(2)}</span>
          {recommendation.stake && (
            <span className="expert-pick-row__stake">{recommendation.stake}u</span>
          )}
          {recommendation.bet_event?.game && (
            <span className="expert-pick-row__time">{formatDate(recommendation.bet_event.game.datetime)}</span>
          )}
        </div>
      </div>
      {recommendation.tipster_description && (
        <div className={`expert-pick-row__expanded ${isExpanded ? 'expert-pick-row__expanded--open' : ''}`}>
          <div className="expert-pick-row__description">
            {recommendation.tipster_description}
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpertPickPanel;
