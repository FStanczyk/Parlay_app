import React from 'react';

interface LeagueStats {
  total_games: number;
  correct_picks: number;
  accuracy_percentage: number;
}

interface CircularProgressProps {
  percentage: number;
  size?: number;
}

const getAccuracyColor = (percentage: number): string => {
  if (percentage >= 60) {
    return '#3fb950';
  } else if (percentage < 50) {
    return '#f85149';
  } else {
    const range = 60 - 50;
    const position = percentage - 50;
    const ratio = position / range;
    const redStart = 248;
    const redEnd = 63;
    const greenStart = 81;
    const greenEnd = 185;
    const blueStart = 73;
    const blueEnd = 80;
    const red = Math.round(redStart - (redStart - redEnd) * ratio);
    const green = Math.round(greenStart + (greenEnd - greenStart) * ratio);
    const blue = Math.round(blueStart + (blueEnd - blueStart) * ratio);
    return `rgb(${red}, ${green}, ${blue})`;
  }
};

const CircularProgress: React.FC<CircularProgressProps> = ({
  percentage,
  size = 120,
}) => {
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;
  const color = getAccuracyColor(percentage);

  return (
    <div className="philip-snat-stats__circular-progress" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="philip-snat-stats__circular-svg">
        <circle
          className="philip-snat-stats__circular-bg"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--color-border-subtle)"
          strokeWidth="6"
        />
        <circle
          className="philip-snat-stats__circular-progress-bar"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="6"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div
        className="philip-snat-stats__circular-value"
        style={{ color }}
      >
        {percentage.toFixed(1)}%
      </div>
    </div>
  );
};

interface ModelLeagueStatsProps {
  leagueName: string;
  stats: LeagueStats;
  games: any;
  loadingGames: boolean;
  onShowGames: () => void;
  onHideGames: () => void;
}

const ModelLeagueStats: React.FC<ModelLeagueStatsProps> = ({
  leagueName,
  stats,
  games,
  loadingGames,
  onShowGames,
  onHideGames,
}) => {
  return (
    <div className="philip-snat-stats__league-card">
      <div className="philip-snat-stats__content">
        <div className="philip-snat-stats__stat-item philip-snat-stats__stat-item--league">
          <div className="philip-snat-stats__league-name">{leagueName}</div>
          {!games ? (
            <button
              className="button_primary philip-snat-stats__show-games-button"
              onClick={onShowGames}
              disabled={loadingGames}
            >
              Show all games
            </button>
          ) : (
            <button
              className="button_primary philip-snat-stats__show-games-button"
              onClick={onHideGames}
              disabled={loadingGames}
            >
              Hide games
            </button>
          )}
        </div>
        <div className="philip-snat-stats__stat-item philip-snat-stats__stat-item--right-group">
          <div className="philip-snat-stats__stat-item philip-snat-stats__stat-item--picks">
            <div className="philip-snat-stats__stat-label">Correct picks</div>
            <div className="philip-snat-stats__picks-value">
              {stats.correct_picks || 0}/{stats.total_games || 0}
            </div>
          </div>
          <div className="philip-snat-stats__stat-item philip-snat-stats__stat-item--accuracy">
            <CircularProgress percentage={stats.accuracy_percentage || 0} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelLeagueStats;
