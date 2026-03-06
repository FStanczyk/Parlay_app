import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bar, BarChart, Cell, ResponsiveContainer, XAxis } from 'recharts';
import iconSpinVideo from '../assets/branding/icon_spin.mp4';
import ModelLeagueStats from '../components/ModelLeagueStats';
import '../styles/philip-snat-stats.scss';
import { apiGet } from '../utils/api';

interface LeagueStats {
  total_games: number;
  correct_picks: number;
  accuracy_percentage: number;
}

interface StatsResponse {
  nhl: LeagueStats;
  khl: LeagueStats;
}

interface GameWithPrediction {
  id: number;
  date: string;
  home_team: string;
  away_team: string;
  home_score: number | null;
  away_score: number | null;
  predicted_winner: string;
  actual_winner: string;
  is_correct: boolean;
  prediction_goals: { [key: string]: number } | null;
}

interface PaginatedGamesResponse {
  games: GameWithPrediction[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const PhilipSnatStats: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [nhlGames, setNhlGames] = useState<PaginatedGamesResponse | null>(null);
  const [khlGames, setKhlGames] = useState<PaginatedGamesResponse | null>(null);
  const [loadingNhlGames, setLoadingNhlGames] = useState(false);
  const [loadingKhlGames, setLoadingKhlGames] = useState(false);
  const [nhlPage, setNhlPage] = useState(1);
  const [khlPage, setKhlPage] = useState(1);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiGet<StatsResponse>('/philip-snat/nhl/stats');
        setStats(data);
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleBack = () => {
    navigate('/philip-snat-models');
  };

  const fetchNhlGames = async (page: number = 1) => {
    setLoadingNhlGames(true);
    try {
      const data = await apiGet<PaginatedGamesResponse>(
        `/philip-snat/nhl/games?page=${page}&page_size=10`
      );
      setNhlGames(data);
      setNhlPage(page);
    } catch (err) {
      console.error('Failed to fetch NHL games:', err);
    } finally {
      setLoadingNhlGames(false);
    }
  };

  const fetchKhlGames = async (page: number = 1) => {
    setLoadingKhlGames(true);
    try {
      const data = await apiGet<PaginatedGamesResponse>(
        `/philip-snat/khl/games?page=${page}&page_size=10`
      );
      setKhlGames(data);
      setKhlPage(page);
    } catch (err) {
      console.error('Failed to fetch KHL games:', err);
    } finally {
      setLoadingKhlGames(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const prepareChartData = (
    predictionGoals: { [key: string]: number } | null,
    actualGoals: number | null
  ) => {
    if (!predictionGoals) return [];
    return Object.entries(predictionGoals)
      .map(([goals, prob]) => ({
        goals: parseInt(goals),
        probability: prob,
      }))
      .sort((a, b) => a.goals - b.goals)
      .map((item) => ({
        name: item.goals.toString(),
        value: item.probability,
        isActual: actualGoals !== null && item.goals === actualGoals,
      }));
  };

  if (loading) {
    return (
      <div className="philip-snat-stats">
        <div className="philip-snat-stats__container">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="philip-snat-stats">
      <div className="philip-snat-stats__container">
        <div className="philip-snat-stats__header">
          <h1 className="philip-snat-stats__title">Prediction Stats</h1>
          <button
            className="button_primary philip-snat-stats__back-button"
            onClick={handleBack}
          >
            Back
          </button>
        </div>

        {stats && stats.nhl && stats.khl ? (
          <>
            <ModelLeagueStats
              leagueName="NHL"
              stats={stats.nhl}
              games={nhlGames}
              loadingGames={loadingNhlGames}
              onShowGames={() => fetchNhlGames(1)}
              onHideGames={() => setNhlGames(null)}
            />

            {loadingNhlGames && (
                <div className="philip-snat-stats__loading">
                  <video
                    className="philip-snat-stats__loading-icon"
                    src={iconSpinVideo}
                    autoPlay
                    loop
                    muted
                    playsInline
                  />
                </div>
              )}

              {nhlGames && !loadingNhlGames && (
                <div className="philip-snat-stats__games-list">
                  {nhlGames.games.map((game) => {
                    const isHomeWinner = game.actual_winner.toLowerCase() === 'home';
                    const actualGoals =
                      game.home_score !== null && game.away_score !== null
                        ? game.home_score + game.away_score
                        : null;
                    const chartData = prepareChartData(game.prediction_goals, actualGoals);
                    return (
                      <div key={game.id} className="philip-snat-stats__game-item">
                        <div className="philip-snat-stats__game-info">
                          <span className="philip-snat-stats__game-date">
                            {formatDate(game.date)}.
                          </span>{' '}
                          <span
                            className={`philip-snat-stats__game-home ${
                              isHomeWinner ? 'philip-snat-stats__game-team--winner' : ''
                            }`}
                          >
                            {game.home_team}
                          </span>{' '}
                          {game.home_score !== null && game.away_score !== null ? (
                            <>
                              {game.home_score} - {game.away_score}
                            </>
                          ) : (
                            'N/A - N/A'
                          )}{' '}
                          <span
                            className={`philip-snat-stats__game-away ${
                              !isHomeWinner ? 'philip-snat-stats__game-team--winner' : ''
                            }`}
                          >
                            {game.away_team}
                          </span>{' '}
                          -{' '}
                          <span
                            className={`philip-snat-stats__game-prediction ${
                              game.is_correct
                                ? 'philip-snat-stats__game-prediction--correct'
                                : 'philip-snat-stats__game-prediction--incorrect'
                            }`}
                          >
                            {game.predicted_winner}
                          </span>
                        </div>
                        {chartData.length > 0 && (
                          <div className="philip-snat-stats__game-chart">
                            <ResponsiveContainer width="100%" height={60}>
                              <BarChart data={chartData} margin={{ top: 0, right: 0, bottom: -10, left: 0 }}>
                                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                  {chartData.map((entry, index) => (
                                    <Cell
                                      key={`cell-${index}`}
                                      fill={entry.isActual ? '#f85149' : '#58C9FA'}
                                    />
                                  ))}
                                </Bar>
                                <XAxis
                                  dataKey="name"
                                  axisLine={false}
                                  tickLine={false}
                                  tick={{ fontSize: 10, fill: 'var(--color-text-secondary)' }}
                                />
                              </BarChart>
                            </ResponsiveContainer>
                          </div>
                        )}
                      </div>
                    );
                  })}
                  {nhlGames.total_pages > 1 && (
                    <div className="philip-snat-stats__pagination">
                      <button
                        className="button_secondary philip-snat-stats__pagination-button"
                        onClick={() => fetchNhlGames(nhlPage - 1)}
                        disabled={nhlPage === 1}
                      >
                        Previous
                      </button>
                      <span className="philip-snat-stats__pagination-info">
                        Page {nhlPage} of {nhlGames.total_pages}
                      </span>
                      <button
                        className="button_secondary philip-snat-stats__pagination-button"
                        onClick={() => fetchNhlGames(nhlPage + 1)}
                        disabled={nhlPage === nhlGames.total_pages}
                      >
                        Next
                      </button>
                    </div>
                  )}
                </div>
              )}

            <ModelLeagueStats
              leagueName="KHL"
              stats={stats.khl}
              games={khlGames}
              loadingGames={loadingKhlGames}
              onShowGames={() => fetchKhlGames(1)}
              onHideGames={() => setKhlGames(null)}
            />

            {loadingKhlGames && (
                <div className="philip-snat-stats__loading">
                  <video
                    className="philip-snat-stats__loading-icon"
                    src={iconSpinVideo}
                    autoPlay
                    loop
                    muted
                    playsInline
                  />
                </div>
              )}

              {khlGames && !loadingKhlGames && (
                <div className="philip-snat-stats__games-list">
                  {khlGames.games.map((game) => {
                    const isHomeWinner = game.actual_winner.toLowerCase() === 'home';
                    const actualGoals =
                      game.home_score !== null && game.away_score !== null
                        ? game.home_score + game.away_score
                        : null;
                    const chartData = prepareChartData(game.prediction_goals, actualGoals);
                    return (
                      <div key={game.id} className="philip-snat-stats__game-item">
                        <div className="philip-snat-stats__game-info">
                          <span className="philip-snat-stats__game-date">
                            {formatDate(game.date)}.
                          </span>{' '}
                          <span
                            className={`philip-snat-stats__game-home ${
                              isHomeWinner ? 'philip-snat-stats__game-team--winner' : ''
                            }`}
                          >
                            {game.home_team}
                          </span>{' '}
                          {game.home_score !== null && game.away_score !== null ? (
                            <>
                              {game.home_score} - {game.away_score}
                            </>
                          ) : (
                            'N/A - N/A'
                          )}{' '}
                          <span
                            className={`philip-snat-stats__game-away ${
                              !isHomeWinner ? 'philip-snat-stats__game-team--winner' : ''
                            }`}
                          >
                            {game.away_team}
                          </span>{' '}
                          -{' '}
                          <span
                            className={`philip-snat-stats__game-prediction ${
                              game.is_correct
                                ? 'philip-snat-stats__game-prediction--correct'
                                : 'philip-snat-stats__game-prediction--incorrect'
                            }`}
                          >
                            {game.predicted_winner}
                          </span>
                        </div>
                        {chartData.length > 0 && (
                          <div className="philip-snat-stats__game-chart">
                            <ResponsiveContainer width="100%" height={60}>
                              <BarChart data={chartData} margin={{ top: 0, right: 0, bottom: -10, left: 0 }}>
                                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                  {chartData.map((entry, index) => (
                                    <Cell
                                      key={`cell-${index}`}
                                      fill={entry.isActual ? '#f85149' : '#58C9FA'}
                                    />
                                  ))}
                                </Bar>
                                <XAxis
                                  dataKey="name"
                                  axisLine={false}
                                  tickLine={false}
                                  tick={{ fontSize: 10, fill: 'var(--color-text-secondary)' }}
                                />
                              </BarChart>
                            </ResponsiveContainer>
                          </div>
                        )}
                      </div>
                    );
                  })}
                  {khlGames.total_pages > 1 && (
                    <div className="philip-snat-stats__pagination">
                      <button
                        className="button_secondary philip-snat-stats__pagination-button"
                        onClick={() => fetchKhlGames(khlPage - 1)}
                        disabled={khlPage === 1}
                      >
                        Previous
                      </button>
                      <span className="philip-snat-stats__pagination-info">
                        Page {khlPage} of {khlGames.total_pages}
                      </span>
                      <button
                        className="button_secondary philip-snat-stats__pagination-button"
                        onClick={() => fetchKhlGames(khlPage + 1)}
                        disabled={khlPage === khlGames.total_pages}
                      >
                        Next
                      </button>
                    </div>
                  )}
                </div>
              )}
          </>
        ) : (
          <p className="philip-snat-stats__empty">No stats available</p>
        )}
      </div>
    </div>
  );
};

export default PhilipSnatStats;
