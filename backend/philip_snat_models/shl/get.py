from datetime import datetime, timedelta
from app.models.philip_snat_shl_game import PhilipSnatShlGame
from philip_snat_models.shl import urls
from philip_snat_models.shl.utils import req
from philip_snat_models.shl.const import (
    today, is_after, is_before, uuid_by_code, detag,
    get_from_array_by_value, get_from_array_by_value2,
    CODE_NAME_MAP
)


class ShlGetter:
    def __init__(self):
        self.standings = self.get_league_standings()
        self.full_schedule = self.get_league_full_schedule()
        self.fenwick_corsi_stats = self.get_fenwick_corsi_stats()
        self.power_play_killing_stats = self.get_power_play_killing_stats()
        self.power_play_stats = self.get_power_play_stats()
        self.offense_stats = self.get_offense_stats()

    def get_league_standings(self):
        return req(urls.STANDINGS)

    def get_league_full_schedule(self):
        response = req(urls.SCHEDULE)
        return response.get("gameInfo", []) if response else []

    def get_fenwick_corsi_stats(self):
        response = req(urls.TEAM_STATS_FENWICK_CORSI)
        return response[0].get("stats", []) if response else []

    def get_power_play_killing_stats(self):
        response = req(urls.TEAM_STATS_POWER_PLAY_KILL)
        return response[0].get("stats", []) if response else []

    def get_power_play_stats(self):
        response = req(urls.TEAM_STATS_POWER_PLAY)
        return response[0].get("stats", []) if response else []

    def get_offense_stats(self):
        response = req(urls.TEAM_STATS_OFFENSE)
        return response[0].get("stats", []) if response else []

    def get_single_game(self, uuid):
        return req(urls.SINGLE_GAME.replace("__UUID__", uuid))

    def get_team_last_5_games(self, tag):
        uuid = uuid_by_code(detag(tag))
        if not uuid:
            return []
        response = req(urls.TEAM_LAST_5_GAMES.replace("__UUID__", uuid))
        return response.get("playedGames", []) if response else []

    def get_team_standings(self, tag):
        code = detag(tag)
        for team in self.standings[0].get("stats", []):
            if team.get("info", {}).get("teamCode") == code:
                return team.get("Rank")
        return None

    def get_games_for_day(self, date_str=None):
        if date_str is None:
            date_str = today()
        games = []
        for game in self.full_schedule:
            game_date = game.get("startDateTime", "").split(" ")[0]
            if is_before(game_date, date_str):
                continue
            if game_date == date_str:
                games.append(game)
        return games

    def get_team_stats(self, tag, is_home=True):
        code = detag(tag)
        uuid = uuid_by_code(code)
        if not uuid:
            return None

        simple_stats_url = urls.TEAM_SIMPLE_STATS.replace("__UUID__", uuid)
        simple_stats_response = req(simple_stats_url)
        if not simple_stats_response:
            return None
        simple_stats = simple_stats_response.get("stats", [])

        rank = self.get_team_standings(tag)
        overview_stats_url = urls.TEAM_STATS_OVERVIEW.replace("__UUID__", uuid)
        overview_stats_response = req(overview_stats_url)
        if not overview_stats_response:
            return None
        _overview_stats = overview_stats_response.get("barFieldStats", [])
        overview_stats = [s.get("center") for s in _overview_stats]

        last_games = self.get_team_last_5_games(tag)
        if not last_games:
            return None

        gpg = get_from_array_by_value(simple_stats, "field", "GPG", "value")
        gapg = get_from_array_by_value(simple_stats, "field", "GAPG", "value")

        if gpg is None or gapg is None:
            return None

        sf = self.get_shame_factor(tag, last_games, is_home)
        hfg = self.get_hunger_for_goals(tag, last_games, float(gpg), is_home)

        lmd1 = self.get_lmd(tag, last_games, 0, float(gpg), float(gapg))
        lmd2 = self.get_lmd(tag, last_games, 1, float(gpg), float(gapg)) if len(last_games) > 1 else {"LMDGPG": 0, "LMDGAPG": 0}

        return {
            "Rank": rank,
            "GPG": float(gpg),
            "GAPG": float(gapg),
            "PPPerc": float(get_from_array_by_value(simple_stats, "field", "PPPerc", "value") or 0),
            "PKPerc": float(get_from_array_by_value(simple_stats, "field", "PKPerc", "value") or 0),
            "SEff": float(get_from_array_by_value(overview_stats, "type", "SEff", "value") or 0),
            "SVSPerc": float(get_from_array_by_value(overview_stats, "type", "SVSPerc", "value") or 0),
            "FOPerc": float(get_from_array_by_value(overview_stats, "type", "FOPerc", "value") or 0),
            "CFPerc": float(get_from_array_by_value2(self.fenwick_corsi_stats, "teamCode", code, "CF_Perc") or 0),
            "FFPerc": float(get_from_array_by_value2(self.fenwick_corsi_stats, "teamCode", code, "FF_Perc") or 0),
            "CloseCFPerc": float(get_from_array_by_value2(self.fenwick_corsi_stats, "teamCode", code, "CloseCF_Perc") or 0),
            "CloseFFPerc": float(get_from_array_by_value2(self.fenwick_corsi_stats, "teamCode", code, "CloseFF_Perc") or 0),
            "PDO": float(get_from_array_by_value2(self.fenwick_corsi_stats, "teamCode", code, "PDO") or 0),
            "STPerc": float(get_from_array_by_value2(self.power_play_killing_stats, "teamCode", code, "STPerc") or 0),
            "PPSEff": float(get_from_array_by_value2(self.offense_stats, "teamCode", code, "PPSEff") or 0),
            "SOGPG": self._calculate_sogpg(code),
            "L5GW": self.get_l5gw(tag, last_games),
            "LmdGPG1": lmd1.get("LMDGPG", 0),
            "LmdGPG2": lmd2.get("LMDGPG", 0),
            "LmdGAPG1": lmd1.get("LMDGAPG", 0),
            "LmdGAPG2": lmd2.get("LMDGAPG", 0),
            "ShameFactor": sf,
            "HungerFG": hfg,
        }

    def _calculate_sogpg(self, code):
        sog = get_from_array_by_value2(self.offense_stats, "teamCode", code, "SOG")
        gp = get_from_array_by_value2(self.offense_stats, "teamCode", code, "GP")
        if sog and gp and float(gp) > 0:
            return float(sog) / float(gp)
        return 0.0

    def get_l5gw(self, tag, last_5_games):
        code = detag(tag)
        wins = 0
        for game in last_5_games:
            home_info = game.get("homeTeamInfo", {})
            away_info = game.get("awayTeamInfo", {})
            if home_info.get("code") == code and home_info.get("status") == "WIN":
                wins += 1
            elif away_info.get("code") == code and away_info.get("status") == "WIN":
                wins += 1
        return wins

    def get_lmd(self, tag, last_games, n, gpg, gapg):
        if n >= len(last_games):
            return {"LMDGPG": 0, "LMDGAPG": 0}
        game = last_games[n]
        code = detag(tag)

        ot = game.get("overtime", False)
        home_score_no_ot = game.get("homeTeamInfo", {}).get("score", 0)
        away_score_no_ot = game.get("awayTeamInfo", {}).get("score", 0)
        winner = 0 if game.get("homeTeamInfo", {}).get("status") == "WIN" else 1

        if ot:
            if winner == 0:
                home_score_no_ot -= 1
            elif winner == 1:
                away_score_no_ot -= 1

        if game.get("homeTeamInfo", {}).get("code") == code:
            return {
                "LMDGPG": float(gpg) - float(home_score_no_ot),
                "LMDGAPG": float(gapg) - float(away_score_no_ot),
            }
        elif game.get("awayTeamInfo", {}).get("code") == code:
            return {
                "LMDGPG": float(gpg) - float(away_score_no_ot),
                "LMDGAPG": float(gapg) - float(home_score_no_ot),
            }
        return {"LMDGPG": 0, "LMDGAPG": 0}

    def get_shame_factor(self, tag, last_5_games, is_home):
        if not last_5_games:
            return 0.0
        code = detag(tag)
        rank = self.get_team_standings(tag)
        if rank is None:
            return 0.0

        game = last_5_games[0]
        lgd = 0

        home_info = game.get("homeTeamInfo", {})
        away_info = game.get("awayTeamInfo", {})

        if home_info.get("code") == code and home_info.get("status") == "WIN":
            lgd = 1
        elif away_info.get("code") == code and away_info.get("status") == "WIN":
            lgd = 1

        lgop = None
        lgpa = 0
        if home_info.get("code") == code:
            lgop = self.get_team_standings(away_info.get("uuid"))
        elif away_info.get("code") == code:
            lgop = self.get_team_standings(home_info.get("uuid"))
            lgpa = 1

        if lgop is None:
            return 0.0

        multiplier = 0
        if is_home:
            if lgd == 0:
                multiplier = 1 if lgpa == 0 else 0.5
            elif lgd == 1:
                multiplier = 0 if lgpa == 0 else 0.2
        else:
            if lgd == 0:
                multiplier = 0.6 if lgpa == 0 else 0.3
            elif lgd == 1:
                multiplier = 0

        return (lgop - rank) * multiplier

    def get_hunger_for_goals(self, tag, last_games, gpg, is_home):
        home_multiplier_h_h = 1
        home_multiplier_h_a = 0.5
        home_multiplier_a_h = 0.7
        home_multiplier_a_a = 0.8

        code = detag(tag)
        hunger = 0
        for i in range(min(4, len(last_games))):
            game = last_games[i]
            home_info = game.get("homeTeamInfo", {})
            away_info = game.get("awayTeamInfo", {})

            if home_info.get("code") == code:
                goals = home_info.get("score", 0)
                multiplier = home_multiplier_h_h if is_home else home_multiplier_a_h
            else:
                goals = away_info.get("score", 0)
                multiplier = home_multiplier_h_a if is_home else home_multiplier_a_a

            hunger += ((gpg - goals) / (i + 1)) * multiplier

        return hunger

    def build_game_features(self, game, date_str):
        game_uuid = game.get("uuid")
        if not game_uuid:
            return None

        home_info = game.get("homeTeamInfo", {})
        away_info = game.get("awayTeamInfo", {})

        home_names = home_info.get("names", {})
        away_names = away_info.get("names", {})

        home_team = home_names.get("long", "")
        away_team = away_names.get("long", "")

        if not home_team or not away_team:
            return None

        home_uuid = home_info.get("uuid")
        away_uuid = away_info.get("uuid")

        home_stats = self.get_team_stats(home_uuid, is_home=True)
        away_stats = self.get_team_stats(away_uuid, is_home=False)

        if not home_stats or not away_stats:
            return None

        return {
            "shl_uuid": game_uuid,
            "date": datetime.strptime(date_str, "%Y-%m-%d").date(),
            "home_team": home_team,
            "away_team": away_team,
            "home_rank": home_stats.get("Rank"),
            "away_rank": away_stats.get("Rank"),
            "rank_diff": (home_stats.get("Rank") or 0) - (away_stats.get("Rank") or 0),
            "h_gpg": home_stats.get("GPG", 0),
            "a_gpg": away_stats.get("GPG", 0),
            "gpg_diff": home_stats.get("GPG", 0) - away_stats.get("GPG", 0),
            "gpmutual": home_stats.get("GPG", 0) + away_stats.get("GPG", 0),
            "h_gapg": home_stats.get("GAPG", 0),
            "a_gapg": away_stats.get("GAPG", 0),
            "gapg_diff": home_stats.get("GAPG", 0) - away_stats.get("GAPG", 0),
            "gapmutual": home_stats.get("GAPG", 0) + away_stats.get("GAPG", 0),
            "h_pp_perc": home_stats.get("PPPerc", 0),
            "a_pp_perc": away_stats.get("PPPerc", 0),
            "h_pk_perc": home_stats.get("PKPerc", 0),
            "a_pk_perc": away_stats.get("PKPerc", 0),
            "h_s_eff": home_stats.get("SEff", 0),
            "a_s_eff": away_stats.get("SEff", 0),
            "h_svs_perc": home_stats.get("SVSPerc", 0),
            "a_svs_perc": away_stats.get("SVSPerc", 0),
            "h_fo_perc": home_stats.get("FOPerc", 0),
            "a_fo_perc": away_stats.get("FOPerc", 0),
            "h_cf_perc": home_stats.get("CFPerc", 0),
            "a_cf_perc": away_stats.get("CFPerc", 0),
            "h_ff_perc": home_stats.get("FFPerc", 0),
            "a_ff_perc": away_stats.get("FFPerc", 0),
            "h_close_cf_perc": home_stats.get("CloseCFPerc", 0),
            "a_close_cf_perc": away_stats.get("CloseCFPerc", 0),
            "h_close_ff_perc": home_stats.get("CloseFFPerc", 0),
            "a_close_ff_perc": away_stats.get("CloseFFPerc", 0),
            "h_pdo": home_stats.get("PDO", 0),
            "a_pdo": away_stats.get("PDO", 0),
            "h_st_perc": home_stats.get("STPerc", 0),
            "a_st_perc": away_stats.get("STPerc", 0),
            "h_pps_eff": home_stats.get("PPSEff", 0),
            "a_pps_eff": away_stats.get("PPSEff", 0),
            "h_sogpg": home_stats.get("SOGPG", 0),
            "a_sogpg": away_stats.get("SOGPG", 0),
            "sogpg_diff": home_stats.get("SOGPG", 0) - away_stats.get("SOGPG", 0),
            "sogpg_mutual": home_stats.get("SOGPG", 0) + away_stats.get("SOGPG", 0),
            "h_l5gw": home_stats.get("L5GW", 0),
            "a_l5gw": away_stats.get("L5GW", 0),
            "l5gw_diff": home_stats.get("L5GW", 0) - away_stats.get("L5GW", 0),
            "h_lmd_gpg1": home_stats.get("LmdGPG1", 0),
            "a_lmd_gpg1": away_stats.get("LmdGPG1", 0),
            "h_lmd_gpg2": home_stats.get("LmdGPG2", 0),
            "a_lmd_gpg2": away_stats.get("LmdGPG2", 0),
            "h_lmd_gapg1": home_stats.get("LmdGAPG1", 0),
            "a_lmd_gapg1": away_stats.get("LmdGAPG1", 0),
            "h_lmd_gapg2": home_stats.get("LmdGAPG2", 0),
            "a_lmd_gapg2": away_stats.get("LmdGAPG2", 0),
            "h_shame_factor": home_stats.get("ShameFactor", 0),
            "a_shame_factor": away_stats.get("ShameFactor", 0),
            "h_hunger_fg": home_stats.get("HungerFG", 0),
            "a_hunger_fg": away_stats.get("HungerFG", 0),
            "hunger_fg_diff": home_stats.get("HungerFG", 0) - away_stats.get("HungerFG", 0),
            "hunger_fg_mutual": home_stats.get("HungerFG", 0) + away_stats.get("HungerFG", 0),
        }
