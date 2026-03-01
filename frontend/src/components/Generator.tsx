import React, { useEffect, useState } from 'react';
import { FiShuffle } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../contexts/TranslationContext';
import { betEventsApi } from '../services/betEventsService';
import { couponsApi } from '../services/couponsService';
import { BetEvent } from '../types/interfaces';
import { Icon } from '../utils/Icon';
import BetEventPanel from './BetEventPanel';
import Filters, { FilterValues } from './Filters';
import GoogleSignInButton from './GoogleSignInButton';
import Modal from './Modal';

interface GeneratorProps {
  isDemo?: boolean;
  maxEvents?: number;
  defaultEvents?: number;
}

const Generator: React.FC<GeneratorProps> = ({
  isDemo = false,
  maxEvents = 4,
  defaultEvents = 4
}) => {
  const { t } = useTranslation();
  const { isAuthenticated, isAdmin } = useAuth();
  const [betEvents, setBetEvents] = useState<BetEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lockedEventIds, setLockedEventIds] = useState<Set<number>>(new Set());
  const [animationKey, setAnimationKey] = useState(0);
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
  const [parlayName, setParlayName] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [filters, setFilters] = useState<FilterValues>({
    selectedSport: '',
    selectedLeague: '',
    minOdds: '',
    maxOdds: '',
    eventsNumber: '',
    fromDate: '',
    toDate: '',
  });

  useEffect(() => {
    const fetchBetEvents = async () => {
      try {
        setLoading(true);
        const limit = isDemo ? maxEvents : defaultEvents;
        const events = await betEventsApi.getRandom(limit);
        setBetEvents(events);
        setLockedEventIds(new Set());
      } catch (err) {
        console.error('Error fetching bet events:', err);
        setError(err instanceof Error ? err.message : t.errors.failedToFetchEvents);
      } finally {
        setLoading(false);
      }
    };
    fetchBetEvents();
  }, [isDemo, maxEvents, defaultEvents, t.errors.failedToFetchEvents]);

  const handleLockToggle = (eventId: number) => {
    if (isDemo) return;
    setLockedEventIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(eventId)) newSet.delete(eventId);
      else newSet.add(eventId);
      return newSet;
    });
  };

  const handleGenerateClick = async () => {
    try {
      setGenerating(true);

      let limit = defaultEvents;
      if (!isDemo && filters.eventsNumber) {
        const requestedLimit = parseInt(filters.eventsNumber);
        limit = requestedLimit > 0 ? requestedLimit : defaultEvents;
      }
      if (isDemo && limit > maxEvents) limit = maxEvents;

      const sportId = filters.selectedSport ? parseInt(filters.selectedSport) : undefined;
      const leagueId = filters.selectedLeague ? parseInt(filters.selectedLeague) : undefined;
      const minOdds = !isDemo && filters.minOdds ? parseFloat(filters.minOdds) : undefined;
      const maxOdds = !isDemo && filters.maxOdds ? parseFloat(filters.maxOdds) : undefined;
      const fromDate = !isDemo && filters.fromDate ? filters.fromDate : undefined;
      const toDate = !isDemo && filters.toDate ? filters.toDate : undefined;

      const lockedEvents = betEvents.filter(event => lockedEventIds.has(event.id));
      const newEventsNeeded = limit - lockedEvents.length;
      let newEvents: BetEvent[] = [];

      if (newEventsNeeded > 0) {
        const currentEventIds = betEvents.map(event => event.id);
        newEvents = await betEventsApi.getRandom(
          newEventsNeeded, sportId, leagueId, currentEventIds, minOdds, maxOdds, fromDate, toDate
        );
      }

      setBetEvents([...lockedEvents, ...newEvents]);
      setAnimationKey(prev => prev + 1);
    } catch (err) {
      console.error('Error generating bet events:', err);
      if (err instanceof Error && (err.message.includes('401') || err.message.includes('403'))) {
        let filterName = filters.eventsNumber ? t.filters.eventsNumber.toLowerCase()
          : filters.minOdds ? t.filters.minOdds.toLowerCase()
          : filters.maxOdds ? t.filters.maxOdds.toLowerCase()
          : filters.fromDate ? t.filters.fromDate.toLowerCase()
          : filters.toDate ? t.filters.toDate.toLowerCase()
          : 'advanced';
        setError(t.errors.loginRequiredForFilter.replace('{filter}', filterName));
      } else {
        setError(err instanceof Error ? err.message : t.errors.failedToGenerateEvents);
      }
    } finally {
      setGenerating(false);
    }
  };

  const handleClear = () => {
    setFilters({
      selectedSport: '',
      selectedLeague: '',
      minOdds: '',
      maxOdds: '',
      eventsNumber: '',
      fromDate: '',
      toDate: '',
    });
  };

  const handleSaveModalClose = () => {
    setIsSaveModalOpen(false);
    setParlayName('');
    setSaveError(null);
    setSaveSuccess(false);
  };

  const handleSaveParlay = async () => {
    if (!parlayName.trim() || betEvents.length === 0) return;
    try {
      setSaving(true);
      setSaveError(null);
      setSaveSuccess(false);
      await couponsApi.create({ name: parlayName.trim(), bet_event_ids: betEvents.map(e => e.id) });
      setSaveSuccess(true);
      setTimeout(() => handleSaveModalClose(), 1500);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : t.errors.genericError);
    } finally {
      setSaving(false);
    }
  };

  const totalOdds = betEvents.reduce((acc, e) => acc * e.odds, 1);
  const oddsValues = betEvents.map(e => e.odds);
  const minOddsVal = oddsValues.length ? Math.min(...oddsValues) : null;
  const maxOddsVal = oddsValues.length ? Math.max(...oddsValues) : null;

  const gameTimes = betEvents
    .filter(e => e.game?.datetime)
    .map(e => new Date(e.game!.datetime))
    .sort((a, b) => a.getTime() - b.getTime());
  const firstEvent = gameTimes[0];
  const lastEvent = gameTimes[gameTimes.length - 1];

  const formatShortDate = (d: Date) => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

  return (
    <div className="generator">
      <div className="generator__container">
        {loading && (
          <div className="generator__loading">
            <div className="generator__spinner"></div>
          </div>
        )}

        {error && (
          <div className="generator__error">
            <p>{error}</p>
            {(error.includes('Log in') || error.includes('Zaloguj')) && (
              <GoogleSignInButton className="error-google-button" />
            )}
          </div>
        )}

        {!loading && !error && (
          <>
            <div className="generator__panel">
              <div className="generator__panel-top">
                <h2 className="generator__title">{t.generator.title}</h2>
              </div>

              <Filters
                onFiltersChange={setFilters}
                onClear={handleClear}
                isDemo={isDemo}
              />

              <div className="generator__action-bar">
                <div className="generator__action-btns">
                  <button
                    className="button_primary generator__generate-button"
                    onClick={handleGenerateClick}
                    disabled={generating}
                  >
                    {generating ? t.common.loading : t.generator.generate}
                    {!generating && <Icon component={FiShuffle} aria-hidden={true} />}
                  </button>
                  {isAuthenticated && isAdmin && !isDemo && (
                    <button
                      className="button_primary generator__save-button"
                      onClick={() => setIsSaveModalOpen(true)}
                      disabled={betEvents.length === 0}
                    >
                      {t.generator.saveParlay}
                    </button>
                  )}
                </div>

                {betEvents.length > 0 && (
                  <div className="generator__stats-inline">
                    <span className="generator__stats-item generator__stats-item--total">
                      {totalOdds.toFixed(2)}×
                    </span>
                    {minOddsVal !== null && maxOddsVal !== null && (
                      <span className="generator__stats-item">
                        {minOddsVal.toFixed(2)}–{maxOddsVal.toFixed(2)}
                      </span>
                    )}
                    {firstEvent && lastEvent && (
                      <span className="generator__stats-item">
                        {formatShortDate(firstEvent)}
                        {firstEvent.toDateString() !== lastEvent.toDateString() && ` – ${formatShortDate(lastEvent)}`}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="generator__events">
              {betEvents.length > 0 ? (
                <div className="generator__events-grid">
                  {betEvents.map((betEvent, index) => {
                    const isLocked = lockedEventIds.has(betEvent.id);
                    return (
                      <div
                        key={isLocked ? betEvent.id : `${animationKey}-${betEvent.id}`}
                        className={`generator__event-item${isLocked ? '' : ' generator__event-item--animate'}`}
                        style={isLocked ? undefined : { animationDelay: `${index * 80}ms` }}
                      >
                        <BetEventPanel
                          betEvent={betEvent}
                          isLocked={isLocked}
                          onLockToggle={handleLockToggle}
                          disabled={isDemo}
                        />
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="generator__empty">
                  <p>{t.generator.noEvents}</p>
                </div>
              )}

              {generating && (
                <div className="generator__generating-overlay">
                  <div className="generator__spinner"></div>
                </div>
              )}
            </div>

            <Modal
              isOpen={isSaveModalOpen}
              onClose={handleSaveModalClose}
              title={t.generator.setParlayName}
            >
              <div className="save-parlay-modal">
                {saveSuccess ? (
                  <div className="save-parlay-modal__success">
                    <p>{t.success.parlaySaved}</p>
                  </div>
                ) : (
                  <>
                    <input
                      type="text"
                      className="save-parlay-modal__input"
                      value={parlayName}
                      onChange={(e) => setParlayName(e.target.value)}
                      placeholder={t.generator.setParlayName}
                      autoFocus
                      disabled={saving}
                    />
                    {saveError && (
                      <div className="save-parlay-modal__error"><p>{saveError}</p></div>
                    )}
                    <div className="save-parlay-modal__actions">
                      <button
                        className="button_primary save-parlay-modal__save-button"
                        onClick={handleSaveParlay}
                        disabled={!parlayName.trim() || saving}
                      >
                        {saving ? t.common.loading : t.common.save}
                      </button>
                      <button
                        className="save-parlay-modal__cancel-button"
                        onClick={handleSaveModalClose}
                        disabled={saving}
                      >
                        {t.common.cancel}
                      </button>
                    </div>
                  </>
                )}
              </div>
            </Modal>
          </>
        )}
      </div>
    </div>
  );
};

export default Generator;
