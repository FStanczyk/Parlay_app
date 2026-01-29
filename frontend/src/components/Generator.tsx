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
import ParlaySummary from './ParlaySummary';

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
  const { isAuthenticated } = useAuth();
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
      if (newSet.has(eventId)) {
        newSet.delete(eventId);
      } else {
        newSet.add(eventId);
      }
      return newSet;
    });
  };

  const handleGenerateClick = async () => {
    try {
      setGenerating(true);

      let limit = defaultEvents;
      if (!isDemo) {
        if (filters.eventsNumber) {
        const requestedLimit = parseInt(filters.eventsNumber);
        limit = requestedLimit > 0 ? requestedLimit : defaultEvents;
        }
        // For authenticated users, allow higher limits
        // The backend will handle the actual limit based on authentication
      } else {
        limit = maxEvents;
      }

      if (isDemo && limit > maxEvents) {
        limit = maxEvents;
      }

      const sportId = filters.selectedSport && filters.selectedSport !== '' ? parseInt(filters.selectedSport) : undefined;
      const leagueId = filters.selectedLeague && filters.selectedLeague !== '' ? parseInt(filters.selectedLeague) : undefined;

      let minOdds: number | undefined;
      let maxOdds: number | undefined;
      let fromDate: string | undefined;
      let toDate: string | undefined;

      if (!isDemo) {
        minOdds = filters.minOdds ? parseFloat(filters.minOdds) : undefined;
        maxOdds = filters.maxOdds ? parseFloat(filters.maxOdds) : undefined;
        fromDate = filters.fromDate && filters.fromDate !== '' ? filters.fromDate : undefined;
        toDate = filters.toDate && filters.toDate !== '' ? filters.toDate : undefined;
      }

      const lockedEvents = betEvents.filter(event => lockedEventIds.has(event.id));
      const newEventsNeeded = limit - lockedEvents.length;

      let newEvents: BetEvent[] = [];

      if (newEventsNeeded > 0) {
        const currentEventIds = betEvents.map(event => event.id);
        newEvents = await betEventsApi.getRandom(
          newEventsNeeded,
          sportId,
          leagueId,
          currentEventIds,
          minOdds,
          maxOdds,
          fromDate,
          toDate
        );
      }

      const combinedEvents = [...lockedEvents, ...newEvents];
      setBetEvents(combinedEvents);
      setAnimationKey(prev => prev + 1);
    } catch (err) {
      console.error('Error generating bet events:', err);

      // Check if it's an authentication error
      if (err instanceof Error && (err.message.includes('HTTP error! status: 401') || err.message.includes('HTTP error! status: 403'))) {
        // Determine which filter might require authentication
        let filterName = '';
        if (filters.eventsNumber) filterName = t.filters.eventsNumber.toLowerCase();
        else if (filters.minOdds) filterName = t.filters.minOdds.toLowerCase();
        else if (filters.maxOdds) filterName = t.filters.maxOdds.toLowerCase();
        else if (filters.fromDate) filterName = t.filters.fromDate.toLowerCase();
        else if (filters.toDate) filterName = t.filters.toDate.toLowerCase();
        else filterName = 'advanced';

        setError(t.errors.loginRequiredForFilter.replace('{filter}', filterName));
      } else {
      setError(err instanceof Error ? err.message : t.errors.failedToGenerateEvents);
      }
    } finally {
      setGenerating(false);
    }
  };

  const handleFiltersChange = (newFilters: FilterValues) => {
    setFilters(newFilters);
  };

  const handleSaveParlayClick = () => {
    setIsSaveModalOpen(true);
  };

  const handleSaveModalClose = () => {
    setIsSaveModalOpen(false);
    setParlayName('');
    setSaveError(null);
    setSaveSuccess(false);
  };

  const handleSaveParlay = async () => {
    if (!parlayName.trim() || betEvents.length === 0) {
      return;
    }

    try {
      setSaving(true);
      setSaveError(null);
      setSaveSuccess(false);

      const betEventIds = betEvents.map(event => event.id);
      await couponsApi.create({
        name: parlayName.trim(),
        bet_event_ids: betEventIds,
      });

      setSaveSuccess(true);
      setTimeout(() => {
        handleSaveModalClose();
      }, 1500);
    } catch (err) {
      console.error('Error saving parlay:', err);
      setSaveError(err instanceof Error ? err.message : t.errors.genericError);
    } finally {
      setSaving(false);
    }
  };

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
            {(error.includes('Log in or register') || error.includes('Zaloguj się lub zarejestruj')) && (
              <GoogleSignInButton className="error-google-button" />
            )}
          </div>
        )}

        {!loading && !error && (
          <>
            <section className="generator__header">
              <h2 className="generator__title">{t.generator.title}</h2>
            </section>

            <section className="generator__filters">
              <Filters onFiltersChange={handleFiltersChange} isDemo={isDemo} />
            </section>

            <section className="generator__actions">
              <button
                className="button_primary generator__generate-button"
                onClick={handleGenerateClick}
                disabled={generating}
              >
                {t.generator.generate}
                <Icon component={FiShuffle} aria-hidden={true} />
              </button>
              {isAuthenticated && !isDemo && (
                <button
                  className="button_primary generator__save-button"
                  onClick={handleSaveParlayClick}
                  disabled={betEvents.length === 0}
                >
                  {t.generator.saveParlay}
                </button>
              )}
            </section>

            {betEvents.length > 0 && (
              <section className="generator__summary">
                <ParlaySummary betEvents={betEvents} />
              </section>
            )}

            <section className="generator__events">
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
            </section>

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
                      <div className="save-parlay-modal__error">
                        <p>{saveError}</p>
                      </div>
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
