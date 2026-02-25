import time
import requests
from datetime import datetime, timedelta
from threading import Semaphore

_api_semaphore = Semaphore(2)


def _safe_get(url, max_retries=3, base_delay=0.5):
    response = None
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(base_delay * (attempt + 1))
            with _api_semaphore:
                response = requests.get(url, timeout=10)
                time.sleep(base_delay)
            if response.status_code == 200 and response.text.strip():
                return response
            elif response.status_code == 429:
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2**attempt) * 3)
                    continue
                raise requests.exceptions.RequestException("Rate limited")
            else:
                if attempt < max_retries - 1:
                    continue
                raise requests.exceptions.RequestException(
                    f"HTTP {response.status_code}"
                )
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(base_delay * (attempt + 1))
                continue
            raise
    raise requests.exceptions.RequestException("Failed after retries")


NHL_FROM_ID_MAP = {
    24: "Anaheim Ducks",
    53: "Arizona Coyotes",
    6: "Boston Bruins",
    7: "Buffalo Sabres",
    20: "Calgary Flames",
    12: "Carolina Hurricanes",
    16: "Chicago Blackhawks",
    21: "Colorado Avalanche",
    29: "Columbus Blue Jackets",
    25: "Dallas Stars",
    17: "Detroit Red Wings",
    22: "Edmonton Oilers",
    13: "Florida Panthers",
    26: "Los Angeles Kings",
    30: "Minnesota Wild",
    8: "Montréal Canadiens",
    18: "Nashville Predators",
    1: "New Jersey Devils",
    2: "New York Islanders",
    3: "New York Rangers",
    9: "Ottawa Senators",
    4: "Philadelphia Flyers",
    5: "Pittsburgh Penguins",
    28: "San Jose Sharks",
    55: "Seattle Kraken",
    19: "St. Louis Blues",
    14: "Tampa Bay Lightning",
    10: "Toronto Maple Leafs",
    23: "Vancouver Canucks",
    54: "Vegas Golden Knights",
    15: "Washington Capitals",
    52: "Winnipeg Jets",
    68: "Utah Mammoth",
}

NHL_ID_MAP = {v: k for k, v in NHL_FROM_ID_MAP.items()}
NHL_ID_MAP["Montreal Canadiens"] = 8
NHL_ID_MAP["St Louis Blues"] = 19

NHL_TEAM_MAP = {
    "Anaheim Ducks": "ANA",
    "Arizona Coyotes": "ARI",
    "Boston Bruins": "BOS",
    "Buffalo Sabres": "BUF",
    "Calgary Flames": "CGY",
    "Carolina Hurricanes": "CAR",
    "Chicago Blackhawks": "CHI",
    "Colorado Avalanche": "COL",
    "Columbus Blue Jackets": "CBJ",
    "Dallas Stars": "DAL",
    "Detroit Red Wings": "DET",
    "Edmonton Oilers": "EDM",
    "Florida Panthers": "FLA",
    "Los Angeles Kings": "LAK",
    "Minnesota Wild": "MIN",
    "Montréal Canadiens": "MTL",
    "Montreal Canadiens": "MTL",
    "Nashville Predators": "NSH",
    "New Jersey Devils": "NJD",
    "New York Islanders": "NYI",
    "New York Rangers": "NYR",
    "Ottawa Senators": "OTT",
    "Philadelphia Flyers": "PHI",
    "Pittsburgh Penguins": "PIT",
    "San Jose Sharks": "SJS",
    "Seattle Kraken": "SEA",
    "St. Louis Blues": "STL",
    "Tampa Bay Lightning": "TBL",
    "Toronto Maple Leafs": "TOR",
    "Vancouver Canucks": "VAN",
    "Vegas Golden Knights": "VGK",
    "Washington Capitals": "WSH",
    "Winnipeg Jets": "WPG",
    "Utah Mammoth": "UTA",
}


class GameMatch:
    def __init__(
        self,
        home,
        away,
        home_id,
        away_id,
        home_score,
        away_score,
        ot,
        goals_total,
        goals_no_ot,
    ):
        self.home = home
        self.away = away
        self.home_id = home_id
        self.away_id = away_id
        self.home_score = home_score
        self.away_score = away_score
        self.ot = ot
        self.goals_total = goals_total
        self.goals_no_ot = goals_no_ot

    def get_goals_for_team(self, team_id):
        return self.home_score if team_id == self.home_id else self.away_score


class LastGameDetails:
    def __init__(self, LGD, LGPA, LGOP, DaysBetween, OT, SO):
        self.LGD = LGD
        self.LGPA = LGPA
        self.LGOP = LGOP
        self.DaysBetween = DaysBetween
        self.OT = OT
        self.SO = SO


class NhlGetter:
    NHL_API_BASE = "https://api.nhle.com"
    NHL_WEB_API_BASE = "https://api-web.nhle.com"

    TEAM_SUMMARY_FULL_TEMPLATE = (
        f"{NHL_API_BASE}/stats/rest/en/team/summary"
        "?isAggregate=false&isGame=false&limit=1"
        "&factCayenneExp=teamId={team_id}"
        "&factCayenneExp=gamesPlayed%3E=1"
        "&cayenneExp=gameTypeId=2%20and%20seasonId%3C={season}%20and%20seasonId%3E={season}"
    )
    STANDINGS_NOW = f"{NHL_WEB_API_BASE}/v1/standings/now"
    CLUB_SCHEDULE_SEASON_TEMPLATE = (
        f"{NHL_WEB_API_BASE}/v1/club-schedule-season/{{abbr}}/{{season}}"
    )
    GAMECENTER_BOXSCORE_TEMPLATE = (
        f"{NHL_WEB_API_BASE}/v1/gamecenter/{{game_id}}/boxscore"
    )
    SCHEDULE_TEMPLATE = f"{NHL_WEB_API_BASE}/v1/schedule/{{date}}"

    H_H = 1
    H_A = 0.5
    A_H = 0.7
    A_A = 0.8

    def __init__(self):
        self._season = self._compute_season()

    @staticmethod
    def _compute_season():
        now = datetime.now()
        y = now.year
        return f"{y}{y + 1}" if now.month >= 9 else f"{y - 1}{y}"

    def get_team_name(self, team_id):
        return NHL_FROM_ID_MAP[team_id]

    def get_team_id(self, name):
        return NHL_ID_MAP[name]

    def get_team_abbr(self, team_id):
        return NHL_TEAM_MAP[NHL_FROM_ID_MAP[team_id]]

    def get_conference_rank(self, team_id):
        response = _safe_get(self.STANDINGS_NOW)
        target = self.get_team_name(team_id)
        for place in response.json()["standings"]:
            if place["teamName"]["default"] == target:
                return int(place["conferenceSequence"])
        return 0

    def get_team_stats(self, team_id):
        url = self.TEAM_SUMMARY_FULL_TEMPLATE.format(
            team_id=team_id, season=self._season
        )
        return _safe_get(url).json()["data"][0]

    def get_schedule(self, date_str):
        url = self.SCHEDULE_TEMPLATE.format(date=date_str)
        data = _safe_get(url).json()
        return data["gameWeek"][0]["games"]

    def get_game_boxscore(self, game_id):
        url = self.GAMECENTER_BOXSCORE_TEMPLATE.format(game_id=game_id)
        return _safe_get(url).json()

    def get_last_games(self, team_id, n, skip_first=False, custom_date=None):
        abbr = self.get_team_abbr(team_id).lower()
        url = self.CLUB_SCHEDULE_SEASON_TEMPLATE.format(abbr=abbr, season=self._season)
        schedule_data = _safe_get(url).json()

        if "games" not in schedule_data:
            return []

        cutoff_str = custom_date if custom_date else self.today()
        cutoff_dt = datetime.strptime(cutoff_str, "%Y-%m-%d")

        completed = []
        for game in schedule_data["games"]:
            if game.get("gameType") != 2:
                continue
            game_date_str = game.get("gameDate")
            if not game_date_str:
                continue
            if datetime.strptime(game_date_str, "%Y-%m-%d") >= cutoff_dt:
                continue
            if "score" not in game.get("awayTeam", {}) or "score" not in game.get(
                "homeTeam", {}
            ):
                continue
            h_id = game["homeTeam"]["id"]
            a_id = game["awayTeam"]["id"]
            if h_id != team_id and a_id != team_id:
                continue
            completed.append(game)

        completed.sort(key=lambda g: g["gameDate"], reverse=True)

        if skip_first and completed:
            completed = completed[1:]

        result = []
        for game in completed[:n]:
            h_id = game["homeTeam"]["id"]
            a_id = game["awayTeam"]["id"]
            h_score = game["homeTeam"]["score"]
            a_score = game["awayTeam"]["score"]

            overtime = False
            if "gameOutcome" in game and "lastPeriodType" in game["gameOutcome"]:
                overtime = game["gameOutcome"]["lastPeriodType"] != "REG"
            elif "periodDescriptor" in game:
                pd = game["periodDescriptor"]
                if "number" in pd:
                    overtime = pd["number"] > 3
                elif "periodType" in pd:
                    overtime = pd["periodType"] != "REG"

            goals_total = h_score + a_score
            goals_no_ot = goals_total - 1 if overtime else goals_total

            result.append(
                GameMatch(
                    home=self.get_team_name(h_id),
                    away=self.get_team_name(a_id),
                    home_id=h_id,
                    away_id=a_id,
                    home_score=h_score,
                    away_score=a_score,
                    ot=overtime,
                    goals_total=goals_total,
                    goals_no_ot=goals_no_ot,
                )
            )

        return result

    def get_last_game_details(self, team_id, skip_first=False, custom_date=None):
        abbr = self.get_team_abbr(team_id).lower()
        url = self.CLUB_SCHEDULE_SEASON_TEMPLATE.format(abbr=abbr, season=self._season)
        schedule_data = _safe_get(url).json()

        if "games" not in schedule_data:
            return None

        cutoff_str = custom_date if custom_date else self.today()
        cutoff_dt = datetime.strptime(cutoff_str, "%Y-%m-%d")

        completed = []
        for game in schedule_data["games"]:
            if game.get("gameType") != 2:
                continue
            game_date_str = game.get("gameDate")
            if not game_date_str:
                continue
            if datetime.strptime(game_date_str, "%Y-%m-%d") >= cutoff_dt:
                continue
            if "score" not in game.get("awayTeam", {}) or "score" not in game.get(
                "homeTeam", {}
            ):
                continue
            h_id = game["homeTeam"]["id"]
            a_id = game["awayTeam"]["id"]
            if h_id != team_id and a_id != team_id:
                continue
            completed.append(game)

        completed.sort(key=lambda g: g["gameDate"], reverse=True)

        if skip_first and completed:
            completed = completed[1:]

        if not completed:
            return None

        game = completed[0]
        h_id = game["homeTeam"]["id"]
        a_id = game["awayTeam"]["id"]
        h_score = game["homeTeam"]["score"]
        a_score = game["awayTeam"]["score"]
        game_date = game["gameDate"]

        days = self._days_between(game_date, cutoff_str)

        OT, SO = 0, 0
        if "gameOutcome" in game and "lastPeriodType" in game["gameOutcome"]:
            lp = game["gameOutcome"]["lastPeriodType"]
            if lp == "OT":
                OT = 1
            elif lp == "SO":
                OT, SO = 1, 1
        elif "periodDescriptor" in game:
            pd = game["periodDescriptor"]
            if "number" in pd:
                n = pd["number"]
                OT = 1 if n > 3 else 0
                SO = 1 if n > 4 else 0

        if h_id == team_id:
            return LastGameDetails(
                LGD=1 if h_score > a_score else 0,
                LGPA=0,
                LGOP=self.get_conference_rank(a_id),
                DaysBetween=days,
                OT=OT,
                SO=SO,
            )
        else:
            return LastGameDetails(
                LGD=0 if h_score > a_score else 1,
                LGPA=1,
                LGOP=self.get_conference_rank(h_id),
                DaysBetween=days,
                OT=OT,
                SO=SO,
            )

    def get_last_match_difference(self, games, team_id, game_number, stat_provider):
        gpg = stat_provider["goalsForPerGame"]
        goals = games[game_number].get_goals_for_team(team_id)
        return round(gpg - goals, 2)

    def get_hunger_for_goals(
        self, home_id, away_id, home_games, away_games, home_gpg, away_gpg
    ):
        hunger_home = 0
        hunger_away = 0
        for i in range(min(4, len(home_games))):
            game = home_games[i]
            goals = game.get_goals_for_team(home_id)
            mult = self.H_H if game.home_id == home_id else self.H_A
            hunger_home += ((home_gpg - goals) / (i + 1)) * mult
        for i in range(min(4, len(away_games))):
            game = away_games[i]
            goals = game.get_goals_for_team(away_id)
            mult = self.A_A if game.away_id == away_id else self.A_H
            hunger_away += ((away_gpg - goals) / (i + 1)) * mult
        return round(hunger_home + hunger_away, 3)

    def get_shame_factor(self, last_game, standing, is_home=True):
        lgd, lgpa, lgop = last_game.LGD, last_game.LGPA, last_game.LGOP
        if is_home:
            if lgd == 0 and lgpa == 0:
                mult = 1
            elif lgd == 1 and lgpa == 0:
                mult = 0
            elif lgd == 0 and lgpa == 1:
                mult = 0.5
            else:
                mult = 0.2
        else:
            if lgd == 0 and lgpa == 0:
                mult = 0.6
            elif lgd == 1 and lgpa == 0:
                mult = 0
            elif lgd == 0 and lgpa == 1:
                mult = 0.3
            else:
                mult = 0
        return (lgop - standing) * mult

    def get_fatigue_factor(self, last_game, is_home):
        days, ot, so, lgpa = (
            last_game.DaysBetween,
            last_game.OT,
            last_game.SO,
            last_game.LGPA,
        )
        fatigue = 0
        if days == 1:
            fatigue = 2
            if ot:
                fatigue += 0.5
            if so:
                fatigue += 0.2
            if is_home and lgpa == 1:
                fatigue += 0.2
            elif not is_home and lgpa == 0:
                fatigue += 0.2
        elif days == 2:
            fatigue = 1
            if ot:
                fatigue += 0.3
            if so:
                fatigue += 0.1
            if is_home and lgpa == 1:
                fatigue += 0.1
            elif not is_home and lgpa == 0:
                fatigue += 0.1
        return fatigue

    def get_l5gw(self, team_id, last5games):
        name = self.get_team_name(team_id)
        wins = 0
        for game in last5games:
            if game.home == name and game.home_score > game.away_score:
                wins += 1
            elif game.away == name and game.home_score < game.away_score:
                wins += 1
        return wins

    def build_game_features(self, game, date_str):
        """
        Compute all feature columns for a single NHL schedule game dict.
        Returns a dict mapping directly to PhilipSnatNhlGame fields.
        Returns None if data cannot be collected.
        """
        home_id = game["homeTeam"]["id"]
        away_id = game["awayTeam"]["id"]

        try:
            home_data = self.get_team_stats(home_id)
            away_data = self.get_team_stats(away_id)
        except Exception as e:
            print(f"  [get] Failed team stats for game {game['id']}: {e}")
            return None

        home_games = self.get_last_games(
            home_id, 5, skip_first=True, custom_date=date_str
        )
        away_games = self.get_last_games(
            away_id, 5, skip_first=True, custom_date=date_str
        )

        if len(home_games) < 2 or len(away_games) < 2:
            print(f"  [get] Not enough history for game {game['id']}, skipping")
            return None

        home_gpg = round(home_data["goalsForPerGame"], 3)
        away_gpg = round(away_data["goalsForPerGame"], 3)
        home_lgpg = round(home_data["goalsAgainstPerGame"], 3)
        away_lgpg = round(away_data["goalsAgainstPerGame"], 3)

        home_lmd1 = self.get_last_match_difference(home_games, home_id, 0, home_data)
        away_lmd1 = self.get_last_match_difference(away_games, away_id, 0, away_data)
        home_lmd2 = self.get_last_match_difference(home_games, home_id, 1, home_data)
        away_lmd2 = self.get_last_match_difference(away_games, away_id, 1, away_data)

        home_spg = round(home_data["shotsForPerGame"], 3)
        away_spg = round(away_data["shotsForPerGame"], 3)
        home_spga = round(home_data["shotsAgainstPerGame"], 3)
        away_spga = round(away_data["shotsAgainstPerGame"], 3)

        home_standing = self.get_conference_rank(home_id)
        away_standing = self.get_conference_rank(away_id)

        home_sv = round(
            1 - (home_data["goalsAgainstPerGame"] / home_data["shotsAgainstPerGame"]), 3
        )
        away_sv = round(
            1 - (away_data["goalsAgainstPerGame"] / away_data["shotsAgainstPerGame"]), 3
        )

        lg_home = self.get_last_game_details(
            home_id, skip_first=True, custom_date=date_str
        )
        lg_away = self.get_last_game_details(
            away_id, skip_first=True, custom_date=date_str
        )

        if lg_home is None or lg_away is None:
            print(f"  [get] Missing last game details for game {game['id']}, skipping")
            return None

        sf_home = self.get_shame_factor(lg_home, home_standing, is_home=True)
        sf_away = self.get_shame_factor(lg_away, away_standing, is_home=False)

        l5gw_home = self.get_l5gw(home_id, home_games)
        l5gw_away = self.get_l5gw(away_id, away_games)

        hunger_fg = self.get_hunger_for_goals(
            home_id, away_id, home_games, away_games, home_gpg, away_gpg
        )

        winner = None
        home_goals_no_ot = None
        away_goals_no_ot = None
        total_goals_no_ot = None

        if "score" in game.get("homeTeam", {}) and "score" in game.get("awayTeam", {}):
            h_score = game["homeTeam"]["score"]
            a_score = game["awayTeam"]["score"]
            overtime = False
            if "gameOutcome" in game:
                overtime = game["gameOutcome"].get("lastPeriodType", "REG") != "REG"
            home_goals_no_ot = h_score
            away_goals_no_ot = a_score
            total = h_score + a_score
            if overtime:
                total -= 1
                if h_score > a_score:
                    home_goals_no_ot -= 1
                else:
                    away_goals_no_ot -= 1
            total_goals_no_ot = total
            winner = 0 if home_goals_no_ot > away_goals_no_ot else 1

        return {
            "nhl_id": game["id"],
            "date": datetime.strptime(date_str, "%Y-%m-%d").date(),
            "home_team": home_data["teamFullName"],
            "away_team": away_data["teamFullName"],
            "winner": winner,
            "home_goals_no_ot": home_goals_no_ot,
            "away_goals_no_ot": away_goals_no_ot,
            "total_goals_no_ot": total_goals_no_ot,
            "home_standing": home_standing,
            "away_standing": away_standing,
            "diff_standing": home_standing - away_standing,
            "home_gpg": home_gpg,
            "away_gpg": away_gpg,
            "home_gpga": home_lgpg,
            "away_gpga": away_lgpg,
            "home_sv": home_sv,
            "away_sv": away_sv,
            "home_lgd": lg_home.LGD,
            "away_lgd": lg_away.LGD,
            "home_lgpa": lg_home.LGPA,
            "away_lgpa": lg_away.LGPA,
            "home_lgop": lg_home.LGOP,
            "away_lgop": lg_away.LGOP,
            "home_shame_factor": sf_home,
            "away_shame_factor": sf_away,
            "outcome_shame_factor": sf_home - sf_away,
            "home_l5gw": l5gw_home,
            "away_l5gw": l5gw_away,
            "diff_l5gw": l5gw_home - l5gw_away,
            "diff_gpg": round(home_gpg - away_gpg, 3),
            "diff_gpga": round(home_lgpg - away_lgpg, 3),
            "diff_sv": round(home_sv - away_sv, 3),
            "home_dflg": lg_home.DaysBetween,
            "away_dflg": lg_away.DaysBetween,
            "home_lgot": bool(lg_home.OT),
            "away_lgot": bool(lg_away.OT),
            "home_lgso": bool(lg_home.SO),
            "away_lgso": bool(lg_away.SO),
            "home_lmd1": home_lmd1,
            "away_lmd1": away_lmd1,
            "home_lmd2": home_lmd2,
            "away_lmd2": away_lmd2,
            "home_spg": int(round(home_spg)),
            "away_spg": int(round(away_spg)),
            "home_spga": int(round(home_spga)),
            "away_spga": int(round(away_spga)),
            "hunger_fg": int(round(hunger_fg)),
            "lmd1_mutual": int(round(home_lmd1 + away_lmd1)),
            "mutual_gpg": int(round(home_gpg + away_gpg)),
            "home_fatigue": int(self.get_fatigue_factor(lg_home, is_home=True)),
            "away_fatigue": int(self.get_fatigue_factor(lg_away, is_home=False)),
        }

    @staticmethod
    def _days_between(date1, date2):
        fmt = "%Y-%m-%d"
        return abs((datetime.strptime(date2, fmt) - datetime.strptime(date1, fmt)).days)

    def today(self):
        return datetime.today().strftime("%Y-%m-%d")

    def day_before(self, day):
        return (datetime.strptime(day, "%Y-%m-%d") - timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )

    def day_after(self, day):
        return (datetime.strptime(day, "%Y-%m-%d") + timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
