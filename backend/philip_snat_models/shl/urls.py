from philip_snat_models.shl.const import SSGT_UUID, SEASON_UUID, SERIES_UUID, GAME_TYPE_UUID

STANDINGS = f"https://www.shl.se/api/statistics-v2/stats-info/standings_standings?ssgtUuid={SSGT_UUID}&count=50&moduleType=standings"
SCHEDULE = f"https://www.shl.se/api/sports-v2/game-schedule?seasonUuid={SEASON_UUID}&seriesUuid={SERIES_UUID}&gameTypeUuid={GAME_TYPE_UUID}&gamePlace=all&played=all"
TEAM_SIMPLE_STATS = "https://www.shl.se/api/statistics-v2/team-page/stats-header?teamUuid=__UUID__"
TEAM_STATS_OVERVIEW = "https://www.shl.se/api/statistics-v2/team-page/overview-team-stats?teamUuid=__UUID__"
TEAM_STATS_FENWICK_CORSI = f"https://www.shl.se/api/statistics-v2/stats-info/teams_extendedMetrics?count=25&moduleType=result&ssgtUuid={SSGT_UUID}"
TEAM_STATS_POWER_PLAY_KILL = f"https://www.shl.se/api/statistics-v2/stats-info/teams_penaltyKilling?count=25&moduleType=result&ssgtUuid={SSGT_UUID}"
TEAM_STATS_POWER_PLAY = f"https://www.shl.se/api/statistics-v2/stats-info/teams_powerplay?count=25&moduleType=result&ssgtUuid={SSGT_UUID}"
TEAM_STATS_OFFENSE = f"https://www.shl.se/api/statistics-v2/stats-info/teams_shotsForward?count=25&moduleType=result&ssgtUuid={SSGT_UUID}"
TEAM_LAST_5_GAMES = "https://www.shl.se/api/sports-v2/played-games/__UUID__"
SINGLE_GAME = "https://www.shl.se/api/sports-v2/game-info/__UUID__"
