import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Modal from '../../components/Modal';
import { useTranslation } from '../../contexts/TranslationContext';
import '../../styles/manage-recommendations.scss';
import { TipsterTier } from '../../types/interfaces';
import { apiGet, apiPost } from '../../utils/api';
import { translateEvent } from '../../utils/translateEvent';

interface Sport {
  id: number;
  name: string;
}

interface League {
  id: number;
  name: string;
  sport_id: number;
}

interface Game {
  id: number;
  datetime: string;
  home_team: string;
  away_team: string;
  sport_id: number;
  league_id: number;
  sport?: Sport;
  league?: League;
}

interface BetEvent {
  id: number;
  odds: number;
  event: string;
  game_id: number;
  game?: Game;
  category_name?: string;
  category_id?: string;
}

interface RecommendationForm {
  tipster_tier_id: number | null;
  stake: string;
  tipster_description: string;
}

const AddRecommendation: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [sports, setSports] = useState<Sport[]>([]);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [betEvents, setBetEvents] = useState<BetEvent[]>([]);
  const [popularGames, setPopularGames] = useState<Game[]>([]);
  const [tiers, setTiers] = useState<TipsterTier[]>([]);

  const [selectedSport, setSelectedSport] = useState<number | null>(null);
  const [selectedLeague, setSelectedLeague] = useState<number | null>(null);
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  const [loadingSports, setLoadingSports] = useState(true);
  const [loadingLeagues, setLoadingLeagues] = useState(false);
  const [loadingGames, setLoadingGames] = useState(false);
  const [loadingBetEvents, setLoadingBetEvents] = useState(false);
  const [loadingPopular, setLoadingPopular] = useState(true);

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [selectedBetEvent, setSelectedBetEvent] = useState<BetEvent | null>(null);
  const [formData, setFormData] = useState<RecommendationForm>({
    tipster_tier_id: null,
    stake: '',
    tipster_description: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [sportsData, popularData, tiersData] = await Promise.all([
          apiGet<Sport[]>('/sports'),
          apiGet<Game[]>('/games/popular?limit=5'),
          apiGet<TipsterTier[]>('/tipsters/me/tiers'),
        ]);
        setSports(sportsData);
        setPopularGames(popularData);
        setTiers(tiersData);
        if (tiersData.length > 0) {
          setFormData(prev => ({ ...prev, tipster_tier_id: tiersData[0].id }));
        }
      } catch (err) {
        console.error('Failed to fetch initial data:', err);
      } finally {
        setLoadingSports(false);
        setLoadingPopular(false);
      }
    };
    fetchInitialData();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  useEffect(() => {
    if (!selectedSport) {
      setLeagues([]);
      setSelectedLeague(null);
      return;
    }

    const fetchLeagues = async () => {
      setLoadingLeagues(true);
      try {
        const data = await apiGet<League[]>(`/leagues?sport_id=${selectedSport}`);
        setLeagues(data);
      } catch (err) {
        console.error('Failed to fetch leagues:', err);
      } finally {
        setLoadingLeagues(false);
      }
    };
    fetchLeagues();
  }, [selectedSport]);

  const fetchGames = useCallback(async () => {
    if (!selectedSport) return;

    setLoadingGames(true);
    try {
      const params = new URLSearchParams();
      params.append('sport_id', selectedSport.toString());
      if (selectedLeague) params.append('league_id', selectedLeague.toString());
      if (debouncedSearch) params.append('search', debouncedSearch);
      params.append('limit', '20');

      const data = await apiGet<Game[]>(`/games/search?${params}`);
      setGames(data);
    } catch (err) {
      console.error('Failed to fetch games:', err);
    } finally {
      setLoadingGames(false);
    }
  }, [selectedSport, selectedLeague, debouncedSearch]);

  useEffect(() => {
    if (selectedSport) {
      fetchGames();
    } else {
      setGames([]);
    }
  }, [selectedSport, selectedLeague, debouncedSearch, fetchGames]);

  const handleSelectGame = async (game: Game) => {
    setSelectedGame(game);
    setLoadingBetEvents(true);
    try {
      const data = await apiGet<BetEvent[]>(`/bet-events/by-game/${game.id}`);
      setBetEvents(data);
    } catch (err) {
      console.error('Failed to fetch bet events:', err);
    } finally {
      setLoadingBetEvents(false);
    }
  };

  const handleBackToGames = () => {
    setSelectedGame(null);
    setBetEvents([]);
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

  const handleAddRecommendation = (betEvent: BetEvent) => {
    setSelectedBetEvent(betEvent);
    setFormData({
      tipster_tier_id: tiers.length > 0 ? tiers[0].id : null,
      stake: '',
      tipster_description: '',
    });
    setSubmitError(null);
    setIsAddModalOpen(true);
  };

  const handleSubmitRecommendation = async () => {
    if (!selectedBetEvent) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await apiPost('/tipsters/me/recommendations', {
        bet_event_id: selectedBetEvent.id,
        tipster_tier_id: formData.tipster_tier_id,
        stake: formData.stake ? parseFloat(formData.stake) : null,
        tipster_description: formData.tipster_description || null,
      });

      setIsAddModalOpen(false);
      setSelectedBetEvent(null);
      navigate('/expert-panel/recommendations');
    } catch (err: any) {
      setSubmitError(t.manageRecommendations?.submitError || 'Failed to add recommendation');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCloseModal = () => {
    setIsAddModalOpen(false);
    setSelectedBetEvent(null);
    setSubmitError(null);
  };

  if (selectedGame) {
    return (
      <>
      <div className="manage-recs">
        <div className="manage-recs__container">
          <button className="manage-recs__back" onClick={handleBackToGames}>
            ← {t.manageRecommendations?.backToGames || 'Back to games'}
          </button>

          <div className="manage-recs__game-header">
            <h2 className="manage-recs__game-title">
              {selectedGame.home_team} vs {selectedGame.away_team}
            </h2>
            <span className="manage-recs__game-meta">
              {selectedGame.league?.name} • {formatDateTime(selectedGame.datetime)}
            </span>
          </div>

          <h3 className="manage-recs__section-title">
            {t.manageRecommendations?.availableBets || 'Available Bets'}
          </h3>

          {loadingBetEvents ? (
            <div className="manage-recs__loading">{t.common.loading}</div>
          ) : betEvents.length === 0 ? (
            <div className="manage-recs__empty">
              {t.manageRecommendations?.noBetsAvailable || 'No bets available for this game'}
            </div>
          ) : (() => {
            const groupedByCategory = betEvents.reduce((acc, betEvent) => {
              const categoryId = betEvent.category_id || 'other';
              if (!acc[categoryId]) {
                acc[categoryId] = [];
              }
              acc[categoryId].push(betEvent);
              return acc;
            }, {} as Record<string, BetEvent[]>);

            const sortedCategoryIds = Object.keys(groupedByCategory).sort((a, b) => {
              if (a === 'other') return 1;
              if (b === 'other') return -1;
              return a.localeCompare(b);
            });

            return (
              <div className="manage-recs__bets-container">
                {sortedCategoryIds.map((categoryId) => {
                  const categoryEvents = groupedByCategory[categoryId];
                  const categoryName = categoryEvents[0]?.category_name || 'Other';

                  return (
                    <div key={categoryId} className="manage-recs__category-group">
                      <div className="manage-recs__category-header">
                        <span className="manage-recs__category-name">{categoryName}</span>
                      </div>
                      <div className="manage-recs__bets-grid">
                        {categoryEvents.map((betEvent) => (
                          <div key={betEvent.id} className="manage-recs__bet-card">
                            <div className="manage-recs__bet-info">
                              <span className="manage-recs__bet-event">{translateEvent(betEvent.event, t.eventsDictionary)}</span>
                              <span className="manage-recs__bet-odds">{betEvent.odds.toFixed(2)}</span>
                            </div>
                            <button
                              className="manage-recs__add-btn"
                              onClick={() => handleAddRecommendation(betEvent)}
                            >
                              + {t.manageRecommendations?.addRecommendation || 'Add'}
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          })()}
        </div>
      </div>
      <Modal
        isOpen={isAddModalOpen}
        onClose={handleCloseModal}
        title={t.manageRecommendations?.addRecommendationTitle || 'Add Recommendation'}
        size="medium"
      >
        <div className="manage-recs__modal-content">
          <div className="manage-recs__modal-content-left">
            <p>{selectedGame?.home_team} vs {selectedGame?.away_team}</p>
            <p className="wide__small__text">{selectedGame?.league?.name}</p>
            <p className="wide__small__text">{formatDateTime(selectedGame?.datetime || '')}</p>
            <p>{selectedBetEvent?.event}</p>
            <p>{selectedBetEvent?.odds?.toFixed(2)}</p>
          </div>
          <div className="manage-recs__modal-content-right">
            <div>
              <p>{t.manageRecommendations?.tierLabel || 'Tier'}</p>
              <select
                value={formData.tipster_tier_id || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  tipster_tier_id: e.target.value ? Number(e.target.value) : null
                }))}
                disabled={tiers.length === 0}
              >
                {tiers.length === 0 ? (
                  <option value="">{t.manageRecommendations?.noTiers || 'No tiers available'}</option>
                ) : (
                  tiers.map((tier) => (
                    <option key={tier.id} value={tier.id}>
                      {tier.name || `Tier ${tier.level}`}
                    </option>
                  ))
                )}
              </select>
            </div>
            <div>
              <p>{t.manageRecommendations?.stakeLabel || 'Stake'}</p>
              <input
                type="number"
                placeholder={t.manageRecommendations?.stakePlaceholder || 'Enter stake'}
                value={formData.stake}
                onChange={(e) => setFormData(prev => ({ ...prev, stake: e.target.value }))}
                min="0"
                step="0.5"
              />
            </div>
            <div>
              <p>{t.manageRecommendations?.descriptionLabel || 'Description'}</p>
              <textarea
                placeholder={t.manageRecommendations?.descriptionPlaceholder || 'Enter description'}
                rows={4}
                value={formData.tipster_description}
                onChange={(e) => setFormData(prev => ({ ...prev, tipster_description: e.target.value }))}
              />
            </div>
            {submitError && (
              <div className="manage-recs__error">{submitError}</div>
            )}
            <div>
              <button
                className="button_primary"
                onClick={handleSubmitRecommendation}
                disabled={isSubmitting || tiers.length === 0}
              >
                {isSubmitting ? t.common.loading : t.common.save}
              </button>
            </div>
          </div>
        </div>
      </Modal>
      </>
    );
  }

  return (
    <div className="manage-recs">
      <div className="manage-recs__container">
        <button className="button_primary" onClick={() => navigate('/expert-panel/recommendations')}>
          {t.manageRecommendations?.backToRecommendations || 'Back'}
        </button>

        <h1 className="manage-recs__title italic-title">{t.manageRecommendations?.addRecommendationTitle || 'Add Recommendation'}</h1>

        <section className="manage-recs__popular">
          <h2 className="manage-recs__section-title">
            {t.manageRecommendations?.popularGames || '⭐ Popular Games'}
          </h2>
          {loadingPopular ? (
            <div className="manage-recs__loading">{t.common.loading}</div>
          ) : popularGames.length === 0 ? (
            <div className="manage-recs__empty">
              {t.manageRecommendations?.noPopularGames || 'No popular games available'}
            </div>
          ) : (
            <div className="manage-recs__popular-grid">
              {popularGames.map((game) => (
                <div
                  key={game.id}
                  className="manage-recs__popular-card"
                  onClick={() => handleSelectGame(game)}
                >
                  <div className="manage-recs__popular-teams">
                    <span>{game.home_team}</span>
                    <span className="manage-recs__vs">vs</span>
                    <span>{game.away_team}</span>
                  </div>
                  <div className="manage-recs__popular-meta">
                    <span className="manage-recs__popular-league">{game.league?.name}</span>
                    <span className="manage-recs__popular-time">{formatDateTime(game.datetime)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <div className="manage-recs__divider">
          <span>{t.manageRecommendations?.orSearch || 'OR SEARCH'}</span>
        </div>

        <section className="manage-recs__search">
          <div className="manage-recs__filters">
            <div className="manage-recs__filter-group">
              <label className="manage-recs__label">{t.filters.sport}</label>
              <select
                className="manage-recs__select"
                value={selectedSport || ''}
                onChange={(e) => {
                  setSelectedSport(e.target.value ? Number(e.target.value) : null);
                  setSelectedLeague(null);
                  setSearchTerm('');
                }}
                disabled={loadingSports}
              >
                <option value="">{loadingSports ? t.filters.loadingSports : t.filters.selectSport}</option>
                {sports.map((sport) => (
                  <option key={sport.id} value={sport.id}>{sport.name}</option>
                ))}
              </select>
            </div>

            <div className="manage-recs__filter-group">
              <label className="manage-recs__label">{t.filters.league}</label>
              <select
                className="manage-recs__select"
                value={selectedLeague || ''}
                onChange={(e) => setSelectedLeague(e.target.value ? Number(e.target.value) : null)}
                disabled={!selectedSport || loadingLeagues}
              >
                <option value="">
                  {!selectedSport
                    ? t.filters.selectSportFirst
                    : loadingLeagues
                    ? t.filters.loadingLeagues
                    : t.filters.selectLeague}
                </option>
                {leagues.map((league) => (
                  <option key={league.id} value={league.id}>{league.name}</option>
                ))}
              </select>
            </div>

            <div className="manage-recs__filter-group manage-recs__filter-group--search">
              <label className="manage-recs__label">
                {t.manageRecommendations?.searchTeams || 'Search Teams'}
              </label>
              <input
                type="text"
                className="manage-recs__input"
                placeholder={t.manageRecommendations?.searchPlaceholder || 'Lakers, Arsenal...'}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                disabled={!selectedSport}
              />
            </div>
          </div>

          {selectedSport && (
            <div className="manage-recs__results">
              <h3 className="manage-recs__section-title">
                {t.manageRecommendations?.games || 'Games'}
                {loadingGames && <span className="manage-recs__loading-inline"> ...</span>}
              </h3>

              {!loadingGames && games.length === 0 ? (
                <div className="manage-recs__empty">
                  {t.manageRecommendations?.noGamesFound || 'No games found'}
                </div>
              ) : (
                <div className="manage-recs__games-list">
                  {games.map((game) => (
                    <div
                      key={game.id}
                      className="manage-recs__game-row"
                      onClick={() => handleSelectGame(game)}
                    >
                      <div className="manage-recs__game-teams">
                        <span className="manage-recs__team">{game.home_team}</span>
                        <span className="manage-recs__vs-small">vs</span>
                        <span className="manage-recs__team">{game.away_team}</span>
                      </div>
                      <div className="manage-recs__game-details">
                        <span className="manage-recs__league-tag">{game.league?.name}</span>
                        <span className="manage-recs__time-tag">{formatDateTime(game.datetime)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default AddRecommendation;
