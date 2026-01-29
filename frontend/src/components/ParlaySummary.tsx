import React from 'react';
import { FiClock } from 'react-icons/fi';
import { BetEvent } from '../types/interfaces';
import { useTranslation } from '../contexts/TranslationContext';
import { Icon } from '../utils/Icon';

interface ParlaySummaryProps {
  betEvents: BetEvent[];
}

const ParlaySummary: React.FC<ParlaySummaryProps> = ({ betEvents }) => {
  const { t } = useTranslation();

  const calculateSummary = () => {
    if (!betEvents || betEvents.length === 0) {
      return {
        totalOdds: 0,
        minOdds: 0,
        maxOdds: 0,
        firstEventTime: null,
        lastEventTime: null,
      };
    }

    const totalOdds = betEvents.reduce((acc, event) => acc * event.odds, 1);

    const odds = betEvents.map(event => event.odds);
    const minOdds = Math.min(...odds);
    const maxOdds = Math.max(...odds);

    const gameTimes = betEvents
      .filter(event => event.game?.datetime)
      .map(event => new Date(event.game!.datetime))
      .sort((a, b) => a.getTime() - b.getTime());

    const firstEventTime = gameTimes.length > 0 ? gameTimes[0] : null;
    const lastEventTime = gameTimes.length > 0 ? gameTimes[gameTimes.length - 1] : null;

    return {
      totalOdds,
      minOdds,
      maxOdds,
      firstEventTime,
      lastEventTime,
    };
  };

  const formatDateTime = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const summary = calculateSummary();

  return (
    <div className="parlay-summary">
      <div className="parlay-summary__content">
        <div className="parlay-summary__odds-section">
          <div className="parlay-summary__odds-item">
            <p className="parlay-summary__label">{t.parlaySummary.totalOdds}</p>
            <p className="parlay-summary__value">{summary.totalOdds.toFixed(2)}</p>
          </div>

          <div className="parlay-summary__odds-item">
            <p className="parlay-summary__label">{t.parlaySummary.minMax}</p>
            <p className="parlay-summary__value">
              {summary.minOdds.toFixed(2)} - {summary.maxOdds.toFixed(2)}
            </p>
          </div>
        </div>

        <div className="parlay-summary__schedule-section">
          <Icon component={FiClock} className="parlay-summary__icon" aria-hidden={true} />
          <div className="parlay-summary__schedule">
            <p className="parlay-summary__schedule-item">
              {t.parlaySummary.firstEvent}: {summary.firstEventTime ? formatDateTime(summary.firstEventTime) : t.parlaySummary.na}
            </p>
            <p className="parlay-summary__schedule-item">
              {t.parlaySummary.lastEvent}: {summary.lastEventTime ? formatDateTime(summary.lastEventTime) : t.parlaySummary.na}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParlaySummary;
