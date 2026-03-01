import React from 'react';
import { FiLock, FiUnlock } from 'react-icons/fi';
import { useTranslation } from '../contexts/TranslationContext';
import { BetEvent } from '../types/interfaces';
import { Icon } from '../utils/Icon';
import { translateEvent } from '../utils/translateEvent';

interface BetEventPanelProps {
  betEvent: BetEvent;
  isLocked: boolean;
  onLockToggle: (eventId: number) => void;
  disabled?: boolean;
}

const BetEventPanel: React.FC<BetEventPanelProps> = ({
  betEvent,
  isLocked,
  onLockToggle,
  disabled = false,
}) => {
  const { t } = useTranslation();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={`bet-event-panel${isLocked ? ' bet-event-panel--locked' : ''}`}>
      <div className="bet-event-panel__content">
        <div className="bet-event-panel__header">
          <h3 className="bet-event-panel__teams">
            {betEvent.game?.home_team} — {betEvent.game?.away_team}
          </h3>
          <p className="bet-event-panel__event">{translateEvent(betEvent.event, t.eventsDictionary)}</p>
        </div>

        <div className="bet-event-panel__footer">
          <div className="bet-event-panel__odds">
            <span className="bet-event-panel__odds-value">{betEvent.odds}</span>
          </div>

          <div className="bet-event-panel__meta">
            <p className="bet-event-panel__league">
              {betEvent.game?.league?.name || `League ${betEvent.game?.league_id}`}
            </p>
            <p className="bet-event-panel__date">
              {betEvent.game?.datetime ? formatDate(betEvent.game.datetime) : t.betEventPanel.tbd}
            </p>
          </div>

          {!disabled && (
            <button
              className={`bet-event-panel__lock-button${isLocked ? ' bet-event-panel__lock-button--locked' : ''}`}
              onClick={() => onLockToggle(betEvent.id)}
              aria-label={isLocked ? t.betEventPanel.unlock : t.betEventPanel.lock}
            >
              {isLocked ? <Icon component={FiLock} aria-hidden={true} /> : <Icon component={FiUnlock} aria-hidden={true} />}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default BetEventPanel;
